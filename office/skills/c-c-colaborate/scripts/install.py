"""Install thin personal adapters; preserve all unowned or locally edited files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

NAME = "c-c-colaborate"
OWNER = "codex-claude-collab-adapter-v1"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def rendered(source, provider):
    source = Path(source).resolve()
    extra = "disable-model-invocation: true\n" if provider == "claude" else ""
    description = "Explicitly start Codex-Claude collaboration with per-run model confirmation, independent reviews, shared project facts, and governed test evidence."
    entry = (f"---\nname: {NAME}\ndescription: {description}\n{extra}---\n\n"
             "# C-C colaborate\n\n"
             "Run only after the human explicitly invokes this workflow. Ordinary coding requests do not activate it.\n\n"
             f"Read the canonical skill at `{source.as_posix()}/SKILL.md` using the local file tool. "
             "Resolve its relative references and scripts against that canonical directory, not this adapter. "
             "If the source is unavailable, stop and report the missing source; do not substitute an improvised workflow.\n\n"
             "Confirm both exact models, effort levels, roles, billing routes, and extra-usage permission for this run before any external model call. "
             "The active conversation is the lead. This entry does not authorize recursively invoking another collaboration skill.\n\n"
             "Use the target project's AGENTS.md and Office governance. The maintained library's project governance is not copied into the target. "
             "Shared facts may be reused immediately; independent first-round findings are exchanged only after both reports exist.\n")
    files = {"SKILL.md": entry.encode("utf-8")}
    if provider == "codex":
        files["agents/openai.yaml"] = (source / "agents/openai.yaml").read_bytes()
    return files


def plan(source, home):
    source, home = Path(source).resolve(), Path(home).resolve()
    for name in ("SKILL.md", "agents/openai.yaml", "scripts/bridge.py", "scripts/runtime.py", "references/workflow.md", "references/bridge.md"):
        if not (source / name).is_file():
            raise ValueError(f"Canonical source is incomplete: {name}")
    plans = []
    for provider, parent in (("codex", ".agents/skills"), ("claude", ".claude/skills")):
        target = home / parent / NAME
        if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
            raise ValueError(f"Refusing to replace linked adapter: {target}")
        files = rendered(source, provider)
        manifest = target / "INSTALLATION.json"
        if target.exists():
            if not manifest.is_file():
                raise ValueError(f"Unowned destination; preserve it: {target}")
            old = json.loads(manifest.read_text(encoding="utf-8"))
            if old.get("owner") != OWNER or old.get("source") != str(source) or old.get("provider") != provider:
                raise ValueError(f"Ownership/source conflict: {target}")
            if set(old.get("files", {})) != set(files):
                raise ValueError(f"Unexpected owned file set: {target}")
            for relative, expected_hash in old["files"].items():
                path = target / relative
                if path.is_symlink() or not path.resolve().is_relative_to(target.resolve()) or not path.is_file() or sha(path.read_bytes()) != expected_hash:
                    raise ValueError(f"Local adapter edit; preserve it: {path}")
            for path in target.rglob("*"):
                if path.is_file() and path.relative_to(target).as_posix() not in set(files) | {"INSTALLATION.json"}:
                    raise ValueError(f"Unowned file in adapter: {path}")
        new = {"owner": OWNER, "provider": provider, "source": str(source),
               "files": {k: sha(v) for k, v in files.items()}}
        plans.append((target, files, new))
    return plans


def install(source, home, apply=False):
    plans = plan(source, home)  # Validate both destinations before changing either.
    result = []
    for target, files, manifest in plans:
        changed = any(not (target / name).is_file() or (target / name).read_bytes() != data for name, data in files.items())
        if apply:
            for name, data in files.items():
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists() or path.read_bytes() != data:
                    path.write_bytes(data)
            (target / "INSTALLATION.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        result.append({"target": str(target), "changed": changed, "applied": apply})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(install(args.source, args.home, args.apply), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
