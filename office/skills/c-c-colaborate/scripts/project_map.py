"""Offline project source inventory; explicit roots, no inference or credential reads."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

from runtime import BridgeError

EXTENSIONS = {'.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.vue', '.html', '.css',
              '.scss', '.md', '.json', '.yaml', '.yml', '.toml', '.sql', '.sh', '.ps1',
              '.rs', '.go', '.java', '.c', '.h', '.cpp', '.cs'}
EXCLUDED = {'.git', '.aws', '.ssh', '.codex', '.claude', '.venv', 'venv', 'node_modules',
            '__pycache__', '.work_tmp', '.worktrees', 'vendor', 'dist', 'build', 'coverage',
            'data', 'uploads', 'artifacts', 'logs', 'backups', 'fixtures', 'testset', 'testset1',
            'testset2', 'testsset2', 'collaboration', 'credentials', 'secrets'}


def safe_source(root, name):
    from bridge import confined
    path = confined(root, name, source=True)
    parts = Path(name).parts
    if (any(p.lower() in EXCLUDED or p.lower().startswith('.env') for p in parts)
            or path.suffix.lower() not in EXTENSIONS
            or any(word in path.name.lower() for word in ('credential', 'secret', 'password', 'token'))):
        raise BridgeError('Not an eligible project code/document path: ' + name)
    cursor = root
    for part in parts:
        cursor = cursor / part
        info = cursor.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise BridgeError('Project reading rejects links and reparse points: ' + name)
    return path


def inventory(root, includes):
    from bridge import confined
    root = Path(root).resolve()
    if not includes:
        raise BridgeError('Select explicit source directories or files')
    found = {}; total = 0; excluded_count = 0
    for name in includes:
        selected = confined(root, name, source=True)
        # Reject a linked selected directory before walking it, even if its target is internal.
        current = root
        for part in Path(name).parts:
            current /= part
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise BridgeError('Do not inventory linked directories')
        if any(p.lower() in EXCLUDED for p in Path(name).parts):
            raise BridgeError('Excluded source root')
        candidates = []
        if selected.is_file():
            candidates = [selected]
        else:
            def failed(error):
                raise BridgeError('Source directory could not be listed') from error
            for directory, dirs, files in os.walk(selected, followlinks=False, onerror=failed):
                allowed = []
                for child in dirs:
                    path = Path(directory)/child
                    info = path.lstat()
                    if (child.lower() in EXCLUDED or child.startswith('.') or stat.S_ISLNK(info.st_mode)
                            or getattr(info, 'st_file_attributes', 0) & 0x400):
                        excluded_count += 1
                    else:
                        allowed.append(child)
                dirs[:] = sorted(allowed)
                candidates.extend(Path(directory)/n for n in sorted(files))
        for path in candidates:
            relative = path.relative_to(root).as_posix()
            if relative in found:
                continue
            try:
                path = safe_source(root, relative)
            except BridgeError:
                excluded_count += 1
                continue
            if path.stat().st_size > 2_000_000:
                raise BridgeError('Source exceeds 2 MB; narrow selection: ' + relative)
            raw = path.read_bytes()
            try:
                text = raw.decode('utf-8-sig')
            except UnicodeError:
                excluded_count += 1
                continue
            if '\x00' in text:
                excluded_count += 1
                continue
            total += len(raw)
            if len(found) >= 2000 or total > 20_000_000:
                raise BridgeError('Source inventory exceeds 2000 files / 20 MB; split scope')
            found[relative] = {'sha256': hashlib.sha256(raw).hexdigest(), 'lines': len(text.splitlines())}
    if not found:
        raise BridgeError('No eligible source files found')
    return {'schema': 1, 'files': dict(sorted(found.items())), 'excluded_count': excluded_count,
            'note': 'Candidate inventory only. Inspect contents and nested rules before confirming access. Filename filtering is not secret detection.'}


def render(data):
    lines = ['# Project code structure — read on demand', '',
             'This is a source inventory, not proof that code was read or audited. Start with the',
             'project entry points and Office architecture; search symbols to follow callers and dependencies.',
             'Then read exact source ranges. Search results and file presence do not establish coverage.', '',
             'Only files included in the confirmed reader catalog are accessible. The helper freezes their',
             'contents and rejects stale snapshots. No credentials, business documents, or runtime databases',
             'should be selected. Manually inspect the candidate list before external review.', '',
             '| Directory | Files |', '| --- | ---: |']
    counts = {}
    for name in data['files']:
        group = str(Path(name).parent).replace('\\', '/')
        counts[group] = counts.get(group, 0) + 1
    lines += [f'| `{name}` | {count} |' for name, count in sorted(counts.items())]
    lines += ['', '## Source catalog', '', '| Path | Lines | Fingerprint prefix |', '| --- | ---: | --- |']
    lines += [f'| `{name}` | {item["lines"]} | {item["sha256"][:12]} |' for name, item in data['files'].items()]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--include', nargs='+', required=True)
    parser.add_argument('--output', required=True, help='New project-relative Office markdown path')
    parser.add_argument('--manifest', required=True, help='New project-relative candidate JSON path')
    args = parser.parse_args()
    from bridge import confined
    root = Path(args.root).resolve()
    if not args.output.startswith('office/') or not args.output.endswith('.md'):
        raise BridgeError('Structure document must be under office/ with .md suffix')
    output = confined(root, args.output); manifest = confined(root, args.manifest)
    if output == manifest or output.exists() or manifest.exists():
        raise BridgeError('Refuse to overwrite existing structure or manifest')
    data = inventory(root, args.include)
    for path, text in ((output, render(data)), (manifest, json.dumps(data, ensure_ascii=False, indent=2))):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8') as stream:
            stream.write(text)
    print(json.dumps({'files': len(data['files']), 'structure': str(output), 'model_calls': 0}))


if __name__ == '__main__':
    main()
