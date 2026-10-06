#!/usr/bin/env python3
"""Manage small frontend demo rounds. No model calls or third-party dependencies."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

IDS = tuple("ABCDE")
BASE = Path("office/frontend-gacha")
MARKER = "<!-- frontend-gacha gallery v1 -->"
TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "gallery.html"


def text_file(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: object) -> None:
    text_file(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def is_link(path: Path) -> bool:
    return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)())


def confined(root: Path, path: Path) -> Path:
    root = root.resolve(strict=True)
    candidate = path if path.is_absolute() else root / path
    if ".." in candidate.parts:
        raise ValueError("Parent traversal is not allowed.")
    relative = candidate.relative_to(root)
    current = root
    for part in relative.parts:
        current /= part
        if is_link(current):
            raise ValueError("Linked paths and junctions are not allowed: " + str(current))
    resolved = candidate.resolve()
    base = (root / BASE).resolve()
    if not base.is_relative_to(root) or resolved == base or not resolved.is_relative_to(base):
        raise ValueError("Output must be below the project's office/frontend-gacha/.")
    return candidate


def get_run(root: Path, raw: str) -> Path:
    run = confined(root, Path(raw))
    parts = run.relative_to(root.resolve()).parts
    if len(parts) != 4 or parts[:2] != ("office", "frontend-gacha"):
        raise ValueError("Expected office/frontend-gacha/<name>/round-NN.")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", parts[2]):
        raise ValueError("Invalid demo name.")
    if not re.fullmatch(r"round-\d{2,}", parts[3]):
        raise ValueError("Invalid round name.")
    if not run.is_dir():
        raise ValueError("Round does not exist.")
    return run


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " must be non-empty text.")
    return value


def files_in(root: Path, directory: Path) -> list[Path]:
    confined(root, directory)
    result = []
    for child in sorted(directory.rglob("*")):
        confined(root, child)
        if child.is_file():
            result.append(child)
        elif not child.is_dir():
            raise ValueError("Unsupported file type: " + str(child))
    return result


def validate(root: Path, run: Path) -> dict:
    for name in ("manifest.json", "brief.md", "fixture.json"):
        path = confined(root, run / name)
        if not path.is_file():
            raise ValueError("Missing " + name)
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("Manifest schema_version must be 1.")
    require_text(manifest.get("title"), "title")
    require_text(manifest.get("summary"), "summary")
    variants = manifest.get("variants")
    if not isinstance(variants, list) or any(not isinstance(v, dict) for v in variants):
        raise ValueError("variants must be an array of objects.")
    if [v.get("id") for v in variants] != list(IDS):
        raise ValueError("Provide A, B, C, D, E once, in that order.")
    require_text((run / "brief.md").read_text(encoding="utf-8-sig"), "brief.md")
    json.loads((run / "fixture.json").read_text(encoding="utf-8-sig"))
    for item in variants:
        require_text(item.get("name"), "variant name")
        require_text(item.get("rationale"), "variant rationale")
        directory = confined(root, run / "variants" / item["id"])
        entry = confined(root, directory / "index.html")
        if not entry.is_file() or not entry.stat().st_size:
            raise ValueError("Missing or empty demo: " + item["id"])
        files_in(root, directory)
    return manifest


def initialize(root: Path, name: str) -> dict:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", name):
        raise ValueError("Use a lowercase slug, starting with a letter, up to 48 characters.")
    number = 1
    while True:
        run = confined(root, root / BASE / name / ("round-" + str(number).zfill(2)))
        if not run.exists():
            break
        number += 1
    run.mkdir(parents=True, exist_ok=False)
    for letter in IDS:
        (run / "variants" / letter).mkdir(parents=True)
    write_json(run / "manifest.json", {
        "schema_version": 1,
        "title": name,
        "summary": "Compare five small demonstrations of the same task.",
        "variants": [{"id": letter, "name": "方案 " + letter, "rationale": ""} for letter in IDS],
    })
    return {"run": run.relative_to(root).as_posix(), "absolute_path": str(run)}


def build(root: Path, raw: str) -> dict:
    run = get_run(root, raw)
    manifest = validate(root, run)
    destination = confined(root, run / "index.html")
    if destination.exists() and not destination.read_text(encoding="utf-8").startswith(MARKER):
        raise ValueError("Refusing to replace an index.html not generated by frontend-gacha.")
    cards = []
    for variant in manifest["variants"]:
        letter = variant["id"]
        name = html.escape(variant["name"], quote=True)
        rationale = html.escape(variant["rationale"], quote=True)
        entry = "variants/" + letter + "/index.html"
        cards.append(
            '<article class="card" data-variant="' + letter + '">'
            '<div class="card-heading"><span class="badge">' + letter + '</span>'
            '<div><h2>' + name + '</h2><p>' + rationale + '</p></div></div>'
            '<div class="frame-wrap"><iframe title="' + letter + ' · ' + name + '" src="' + entry
            + '" sandbox="allow-scripts" loading="eager"></iframe></div>'
            '<div class="card-actions"><a href="' + entry
            + '" target="_blank" rel="noopener">单独查看</a>'
            '<button class="choose" type="button" data-id="' + letter + '" data-name="' + name
            + '" aria-pressed="false">选这套</button></div></article>'
        )
    substitutions = {
        "TITLE": html.escape(manifest["title"], quote=True),
        "SUMMARY": html.escape(manifest["summary"], quote=True),
        "RUN": html.escape(run.relative_to(root).as_posix(), quote=True),
        "CARDS": "\n".join(cards),
    }
    rendered = re.sub(
        r"@@GACHA_(TITLE|SUMMARY|RUN|CARDS)@@",
        lambda match: substitutions[match.group(1)],
        TEMPLATE.read_text(encoding="utf-8"),
    )
    text_file(destination, rendered)
    return {"gallery": str(destination), "variants": len(IDS)}


def select(root: Path, raw: str, letter: str, note: str = "") -> dict:
    if letter not in IDS:
        raise ValueError("Choose one of A, B, C, D, E.")
    run = get_run(root, raw)
    manifest = validate(root, run)
    source = confined(root, run / "variants" / letter)
    hashes = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in files_in(root, source)}
    now = datetime.now(timezone.utc)
    selection_id = now.strftime("%Y%m%dT%H%M%SZ") + "-" + letter + "-" + uuid4().hex[:8]
    destination = confined(root, run / "selections" / selection_id)
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source, destination / "code")
    copied = {p.relative_to(destination / "code").as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in files_in(root, destination / "code")}
    if hashes != copied:
        raise ValueError("Selection copy verification failed; do not use this partial selection.")
    record = {
        "schema_version": 1, "selected_at": now.isoformat(),
        "source_run": run.relative_to(root).as_posix(),
        "variant": letter,
        "name": next(v["name"] for v in manifest["variants"] if v["id"] == letter),
        "note": note, "source_sha256": hashes,
        "entry": "code/index.html",
    }
    write_json(destination / "selection.json", record)
    return {"selection": str(destination / "selection.json"), "entry": str(destination / "code/index.html")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "build", "select"):
        sub = commands.add_parser(command)
        sub.add_argument("--project-root", required=True)
        if command == "init":
            sub.add_argument("--name", required=True)
        else:
            sub.add_argument("--run", required=True)
        if command == "select":
            sub.add_argument("--variant", required=True, choices=IDS)
            sub.add_argument("--note", default="")
    args = parser.parse_args()
    try:
        root = Path(args.project_root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("project-root must be an existing directory.")
        if args.command == "init":
            result = initialize(root, args.name)
        elif args.command == "build":
            result = build(root, args.run)
        else:
            result = select(root, args.run, args.variant, args.note)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print("frontend-gacha: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
