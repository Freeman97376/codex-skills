#!/usr/bin/env python3
"""Copy a benchmark fixture byte-for-byte and verify the copied payload."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def emit_result(source: Path, destination: Path, digest: str, size: int, copied: bool) -> None:
    print(
        json.dumps(
            {
                "source": str(source),
                "destination": str(destination),
                "sha256": digest,
                "bytes": size,
                "copied": copied,
            },
            sort_keys=True,
        )
    )


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Copy a supplied fixture without changing its bytes."
    )
    parser.add_argument("source", help="Existing fixture file")
    parser.add_argument("destination", help="Destination file")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing destination only when its bytes differ",
    )
    args = parser.parse_args(argv)

    source = Path(args.source).resolve()
    destination = Path(args.destination).resolve()

    if not source.is_file():
        return fail(f"Source fixture is not a file: {source}")
    if source == destination:
        return fail("Source and destination must be different files")

    source_hash, source_size = sha256_file(source)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        if not destination.is_file():
            return fail(f"Destination exists but is not a file: {destination}")
        destination_hash, destination_size = sha256_file(destination)
        if (destination_hash, destination_size) == (source_hash, source_size):
            emit_result(
                source, destination, source_hash, source_size, copied=False
            )
            return 0
        if not args.overwrite:
            return fail(
                "Destination differs from the source fixture; rerun with "
                "--overwrite only when replacement is intended"
            )

    temp_fd, temp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(temp_fd)
    temp_path = Path(temp_name)
    try:
        shutil.copyfile(source, temp_path)
        copied_hash, copied_size = sha256_file(temp_path)
        if (copied_hash, copied_size) != (source_hash, source_size):
            return fail("Copied fixture failed the byte-for-byte verification")
        os.replace(temp_path, destination)
    finally:
        temp_path.unlink(missing_ok=True)

    emit_result(source, destination, source_hash, source_size, copied=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
