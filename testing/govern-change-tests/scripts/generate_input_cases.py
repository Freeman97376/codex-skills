#!/usr/bin/env python3
"""Build a bounded, reproducible JSON corpus; never execute the target application."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import sys
import unicodedata

VERSION = 1
FAMILIES = ("boundary", "structure", "unicode", "noise", "syntax")
MAX_SOURCE_BYTES = 1_048_576


def encode(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def reject_constant(value):
    raise ValueError(f"Non-finite JSON number: {value}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate seed object key: {key!r}")
        result[key] = value
    return result


def walk(value, path=()):
    if len(path) > 32:
        raise ValueError("Seed nesting exceeds 32 levels")
    yield path, value
    if isinstance(value, dict):
        for key in sorted(value):
            yield from walk(value[key], path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, path + (index,))


def replaced(root, path, value):
    if not path:
        return copy.deepcopy(value)
    result = copy.deepcopy(root)
    parent = result
    for part in path[:-1]:
        parent = parent[part]
    parent[path[-1]] = copy.deepcopy(value)
    return result


def variants(value, family, rng, max_bytes):
    if family == "boundary":
        if isinstance(value, str):
            for label, item in (
                ("empty", ""), ("space", " "), ("whitespace", "\t\r\n"),
                ("long-text", "x" * (max_bytes // 2)),
            ):
                yield label, item
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            for item in (0, -1, 1, value - 1, value + 1,
                         -(2**31), 2**31 - 1, 2**31, 2**53 - 1, 2**53, 2**53 + 1):
                if not isinstance(item, float) or math.isfinite(item):
                    yield "numeric-boundary", item
        elif isinstance(value, list):
            yield "empty-array", []
            if value:
                yield "singleton-array", value[:1]
        elif isinstance(value, dict):
            yield "empty-object", {}
    elif family == "structure":
        for item in (None, False, 0, "", [], {}):
            if type(item) is not type(value):
                yield "type-substitution", item
        if isinstance(value, dict):
            for key in sorted(value):
                item = copy.deepcopy(value)
                del item[key]
                yield "missing-field", item
            key = "__unexpected__"
            while key in value:
                key += "_"
            yield "extra-field", {**value, key: "unexpected"}
        elif isinstance(value, list) and value:
            yield "duplicate-item", value + [value[0]]
            yield "reverse-array", value[::-1]
            yield "remove-first-item", value[1:]
    elif family == "unicode":
        if isinstance(value, str):
            at = rng.randrange(len(value) + 1)
            yield "zero-width-space", value[:at] + "\u200b" + value[at:]
            yield "nonbreaking-space", "\u00a0" + value + "\u00a0"
            yield "bidi-markers", "\u202e" + value + "\u202c"
            yield "fullwidth-ascii", "".join(
                chr(ord(ch) + 0xFEE0) if "!" <= ch <= "~" else ch for ch in value)
            yield "unicode-nfc", unicodedata.normalize("NFC", value)
            yield "unicode-nfd", unicodedata.normalize("NFD", value)
            yield "confusable-letters", value.translate(str.maketrans(
                {"a": "\u0430", "c": "\u0441", "e": "\u0435", "o": "\u043e",
                 "p": "\u0440", "x": "\u0445", "A": "\u0410", "O": "\u041e"}))
        elif isinstance(value, dict):
            for key in sorted(value):
                changed = key + "\u200b"
                if changed not in value:
                    item = copy.deepcopy(value)
                    item[changed] = item.pop(key)
                    yield "zero-width-field-name", item
    elif family == "noise" and isinstance(value, str):
        at = rng.randrange(len(value) + 1)
        marker = rng.choice(("#", "?", "\x00", "\n", "\ufffd"))
        yield "insert-noise", value[:at] + marker + value[at:]
        yield "irrelevant-suffix", value + " [unrelated note]"
        yield "duplicate-text", value + value
        if value:
            at = rng.randrange(len(value))
            yield "delete-character", value[:at] + value[at + 1:]
            yield "replace-character", value[:at] + marker + value[at + 1:]


def candidates(root, family, rng, max_bytes):
    if family == "syntax":
        raw = encode(root)
        for label, value in (
            ("truncated-json", raw[:-1]), ("trailing-junk", raw + " trailing"),
            ("raw-null-byte", raw + "\x00"), ("empty-body", ""),
            ("nonstandard-number", "NaN"),
        ):
            yield label, (), "raw_json", value
        if isinstance(root, (dict, list)) and root:
            yield "trailing-comma", (), "raw_json", raw[:-1] + "," + raw[-1]
        if isinstance(root, dict) and root:
            key = sorted(root)[0]
            pair = encode(key) + ":" + encode(root[key])
            yield "duplicate-json-key", (), "raw_json", raw[:-1] + "," + pair + "}"
        return
    for path, value in walk(root):
        for label, item in variants(value, family, rng, max_bytes):
            yield label, path, "json_value", replaced(root, path, item)


def build_corpus(seeds, *, seed=0, max_cases=100, max_bytes=8192,
                 families=FAMILIES, source_sha256=None):
    if not 1 <= max_cases <= 1000:
        raise ValueError("max-cases must be between 1 and 1000")
    if not 32 <= max_bytes <= 65536:
        raise ValueError("max-input-bytes must be between 32 and 65536")
    if not families or any(family not in FAMILIES for family in families):
        raise ValueError("Select at least one supported family: " + ",".join(FAMILIES))
    families = tuple(family for family in FAMILIES if family in families)
    if not isinstance(seeds, list) or not seeds or len(seeds) > min(32, max_cases):
        raise ValueError("Input must be an array of 1..32 seed values, no more than max-cases")
    for value in seeds:
        if len(encode(value).encode("ascii")) > max_bytes:
            raise ValueError("A seed exceeds max-input-bytes; use a smaller synthetic seed")
        # Check all depths before writing any result.
        for _ in walk(value):
            pass

    cases, seen = [], set()
    skipped_oversize = 0

    def add(index, family, label, path, transport, value):
        nonlocal skipped_oversize
        payload = value.encode("utf-8") if transport == "raw_json" else encode(value).encode("ascii")
        if len(payload) > max_bytes:
            skipped_oversize += 1
            return
        digest = hashlib.sha256(transport.encode("ascii") + b"\0" + payload).hexdigest()
        if digest in seen:
            return
        seen.add(digest)
        cases.append({
            "id": digest, "seed_index": index, "family": family,
            "mutation": label, "path": list(path), "transport": transport,
            "input": value,
        })

    for index, value in enumerate(seeds):
        add(index, "baseline", "unchanged-seed", (), "json_value", copy.deepcopy(value))

    streams = [
        (index, family, iter(candidates(value, family,
          random.Random(f"{seed}:{index}:{family}"), max_bytes)))
        for index, value in enumerate(seeds) for family in families
    ]
    # Round robin prevents one seed or family from using the entire budget first.
    while streams and len(cases) < max_cases:
        remaining = []
        for index, family, stream in streams:
            if len(cases) >= max_cases:
                remaining.append((index, family, stream))
                continue
            try:
                label, path, transport, value = next(stream)
            except StopIteration:
                continue
            add(index, family, label, path, transport, value)
            remaining.append((index, family, stream))
        streams = remaining

    return {
        "schema_version": 1, "generator_version": VERSION,
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python_version": platform.python_version(), "random_seed": seed,
        "source_sha256": source_sha256 or hashlib.sha256(encode(seeds).encode("ascii")).hexdigest(),
        "families": list(families),
        "limits": {"max_cases": max_cases, "max_input_bytes": max_bytes, "max_depth": 32},
        "case_count": len(cases), "skipped_oversize": skipped_oversize,
        "stop_reason": "case_budget" if streams else "candidates_exhausted",
        "cases": cases,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="UTF-8 JSON array of synthetic seed values")
    parser.add_argument("--output", type=Path, required=True,
                        help="New corpus JSON file; existing files are never overwritten")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-cases", type=int, default=100)
    parser.add_argument("--max-input-bytes", type=int, default=8192)
    parser.add_argument("--families", default=",".join(FAMILIES),
                        help="Comma-separated subset of " + ",".join(FAMILIES))
    args = parser.parse_args(argv)
    try:
        with args.input.open("rb") as stream:
            raw = stream.read(MAX_SOURCE_BYTES + 1)
        if len(raw) > MAX_SOURCE_BYTES:
            raise ValueError("Seed file exceeds 1 MiB")
        seeds = json.loads(raw.decode("utf-8-sig"), parse_constant=reject_constant,
                           object_pairs_hook=unique_object)
        corpus = build_corpus(
            seeds, seed=args.seed, max_cases=args.max_cases,
            max_bytes=args.max_input_bytes,
            families=tuple(part.strip() for part in args.families.split(",")),
            source_sha256=hashlib.sha256(raw).hexdigest(),
        )
        serialized = json.dumps(corpus, ensure_ascii=True, indent=2, allow_nan=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
        print(f"Generated {corpus['case_count']} cases: {args.output.resolve()}")
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print(f"Input generation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
