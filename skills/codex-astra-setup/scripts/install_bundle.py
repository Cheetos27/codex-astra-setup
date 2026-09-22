#!/usr/bin/env python3
"""Portable Codex setup. Preview by default; --full includes skills and settings."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import re
import tempfile
import tomllib
import urllib.request
from datetime import datetime, timezone
from uuid import uuid4

NAME = "codex-astra-setup"
SOURCE = Path(__file__).resolve().parents[1]


def is_link(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def inventory(folder):
    if is_link(folder) or not folder.is_dir():
        raise ValueError(f"Expected a real directory: {folder}")
    result = {}
    for current, dirs, files in os.walk(folder, followlinks=False):
        current = Path(current)
        dirs[:] = [name for name in dirs if name != '__pycache__']
        files = [name for name in files if not name.endswith(('.pyc', '.pyo'))]
        for name in dirs + files:
            if is_link(current / name):
                raise ValueError(f"Links are not supported inside skill folders: {current / name}")
        for name in files:
            path = current / name
            if not path.is_file():
                raise ValueError(f"Expected a regular file: {path}")
            result[path.relative_to(folder).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def default_skills_dir():
    configured = os.environ.get("CODEX_HOME")
    home = Path(configured).expanduser() if configured else Path.home() / ".codex"
    return home / "skills"


def install(skills_dir, *, apply=False, update=False, source=SOURCE, name=NAME):
    source = Path(source).absolute()
    skills_dir = Path(skills_dir).expanduser().absolute()
    target = skills_dir / name
    # Resolve only after rejecting a redirected destination, including junctions.
    for part in (target, *target.parents):
        if is_link(part):
            raise ValueError(f"Destination contains a link or junction: {part}")
    source_files = inventory(source)
    if "SKILL.md" not in source_files:
        raise ValueError("Source is missing SKILL.md")
    source_resolved, target_resolved = source.resolve(), target.resolve()
    if (source_resolved == target_resolved or source_resolved in target_resolved.parents
            or target_resolved in source_resolved.parents):
        raise ValueError("Source and destination must be separate directories")
    old_files = inventory(target) if target.exists() else None
    if old_files == source_files:
        return {"status": "unchanged", "target": str(target)}
    if old_files is not None and not update:
        raise ValueError("A different skill already exists. Preview with --update before applying.")
    action = "update" if old_files is not None else "install"
    changed = sorted(key for key in source_files if (old_files or {}).get(key) != source_files[key])
    removed = sorted(set(old_files or {}) - set(source_files))
    result = {"status": "preview", "action": action, "target": str(target),
              "changed_files": changed, "removed_files": removed}
    if not apply:
        return result

    skills_dir.mkdir(parents=True, exist_ok=True)
    stage = skills_dir / f".{name}.stage-{uuid4().hex}"
    shutil.copytree(source, stage, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
    if inventory(stage) != source_files:
        raise ValueError(f"Source changed while copying; staged files retained at {stage}")
    current_files = inventory(target) if target.exists() else None
    if current_files != old_files:
        raise ValueError(f"Destination changed during installation; staged files retained at {stage}")

    backup = None
    if old_files is not None:
        backup_root = skills_dir.parent / "skill-backups"
        if is_link(backup_root):
            raise ValueError("Backup directory must not be a link or junction")
        backup_root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = backup_root / f"{name}-{stamp}-{uuid4().hex[:8]}"
        target.rename(backup)
    try:
        # A concurrent new directory must never be silently overwritten.
        if target.exists():
            raise ValueError("Destination appeared before final installation")
        stage.rename(target)
    except Exception:
        if backup is not None and not target.exists():
            backup.rename(target)
        raise
    if inventory(target) != source_files:
        raise ValueError(f"Installed files failed verification. Backup: {backup}")
    result["status"] = "installed"
    if backup is not None:
        result["backup"] = str(backup)
    return result


BEGIN = '<!-- codex-astra-setup:begin -->'
END = '<!-- codex-astra-setup:end -->'


def file_plan(path, content):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if is_link(part):
            raise ValueError(f"Settings path contains a link: {part}")
    old = path.read_bytes() if path.exists() else None
    return {'path': path, 'old': old, 'new': content.encode('utf-8')}


def merge_preferences(existing, profile):
    if existing.count(BEGIN) != existing.count(END) or existing.count(BEGIN) > 1:
        raise ValueError('Malformed managed preference block; review AGENTS.md manually')
    if BEGIN in existing:
        start, end = existing.index(BEGIN), existing.index(END) + len(END)
        if start > existing.index(END):
            raise ValueError('Reversed preference markers')
        outside = existing[:start] + existing[end:]
    else:
        outside = existing
    missing = []
    for section in re.split(r'(?m)(?=^## )', profile):
        lines = section.strip().splitlines()
        if not lines:
            continue
        heading = lines[0] if lines[0].startswith('#') else ''
        body = lines[1:] if heading else lines
        absent = [line for line in body if line.strip() and line.strip() not in outside]
        if absent:
            missing.append((heading + '\n\n' if heading else '') + '\n'.join(absent))
    if not missing:
        return outside if BEGIN in existing else existing
    block = BEGIN + '\n' + '\n\n'.join(missing) + '\n' + END
    if BEGIN in existing:
        return existing[:start] + block + existing[end:]
    return existing.rstrip() + ('\n\n' if existing.strip() else '') + block + '\n'


def patch_scalars(text, table, values):
    """Patch known scalar assignments, preserving unrelated TOML."""
    lines = text.splitlines(keepends=True)
    headers = [(i, line.strip()) for i, line in enumerate(lines)
               if re.match(r'^\s*\[', line)]
    if table is None:
        start, end = 0, headers[0][0] if headers else len(lines)
    else:
        matches = [j for j, (_, header) in enumerate(headers) if header == f'[{table}]']
        if not matches:
            return text.rstrip() + '\n\n[' + table + ']\n' + ''.join(
                f'{key} = {json.dumps(value)}\n' for key, value in values.items())
        j = matches[0]
        start = headers[j][0] + 1
        end = headers[j + 1][0] if j + 1 < len(headers) else len(lines)
    chunk = ''.join(lines[start:end])
    for key, value in values.items():
        pattern = rf'(?m)^\s*{re.escape(key)}\s*=.*$'
        replacement = f'{key} = {json.dumps(value)}'
        if re.search(pattern, chunk):
            chunk = re.sub(pattern, replacement, chunk, count=1)
        else:
            chunk = chunk.rstrip() + ('\n' if chunk.strip() else '') + replacement + '\n'
    return ''.join(lines[:start]) + chunk + ''.join(lines[end:])


def settings_plan(home, source=SOURCE, windows=None):
    home = Path(home).absolute()
    assets = source / 'assets'
    desired = json.loads((assets / 'settings.json').read_text(encoding='utf-8'))
    config = home / 'config.toml'
    old_text = config.read_text(encoding='utf-8-sig') if config.exists() else ''
    before = tomllib.loads(old_text)
    changes = {k: v for k, v in desired['defaults'].items() if before.get(k) != v}
    updated = patch_scalars(old_text, None, changes) if changes else old_text
    if (windows if windows is not None else sys.platform == 'win32'):
        current = before.get('shell_environment_policy', {}).get('set', {})
        utf8 = {k: v for k, v in desired['windows_environment'].items() if current.get(k) != v}
        if utf8:
            updated = patch_scalars(updated, 'shell_environment_policy.set', utf8)
    parsed = tomllib.loads(updated)
    for key, value in desired['defaults'].items():
        if parsed.get(key) != value:
            raise ValueError(f'Could not safely merge setting: {key}')
    plans = [file_plan(config, updated)]
    for name, values in desired['profiles'].items():
        path = home / (name + '.config.toml')
        content = path.read_text(encoding='utf-8-sig') if path.exists() else ''
        current = tomllib.loads(content)
        delta = {k: v for k, v in values.items() if current.get(k) != v}
        new = patch_scalars(content, None, delta) if delta else content
        tomllib.loads(new)
        plans.append(file_plan(path, new))
    agents = home / 'AGENTS.md'
    existing = agents.read_text(encoding='utf-8-sig') if agents.exists() else ''
    profile = (assets / 'working-preferences.md').read_text(encoding='utf-8')
    plans.append(file_plan(agents, merge_preferences(existing, profile)))
    return plans


def write_settings(plans, home):
    results = []
    backup_dir = Path(home) / 'setup-backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8])
    for plan in plans:
        path, old, new = plan['path'], plan['old'], plan['new']
        if old == new:
            results.append({'path': str(path), 'status': 'unchanged'})
            continue
        current = file_plan(path, new.decode('utf-8'))
        if current['old'] != old:
            raise ValueError(f'Settings changed since preview: {path}')
        for parent in (backup_dir, *backup_dir.parents):
            if is_link(parent):
                raise ValueError(f'Backup path contains a link: {parent}')
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / path.name
        if old is not None:
            backup.write_bytes(old)
        else:
            (backup_dir / (path.name + '.previously-absent')).write_text('', encoding='utf-8')
        path.parent.mkdir(parents=True, exist_ok=True)
        stage = path.with_name('.' + path.name + '.' + uuid4().hex + '.tmp')
        stage.write_bytes(new)
        stage.replace(path)
        if path.read_bytes() != new:
            raise ValueError(f'Settings verification failed: {path}')
        results.append({'path': str(path), 'status': 'written', 'backup': str(backup_dir)})
    return results


def fetch_external(entry, destination):
    for relative, expected in entry['files'].items():
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
            raise ValueError('Unsafe external path')
        url = f"https://raw.githubusercontent.com/{entry['repository']}/{entry['revision']}/{entry['path']}/{relative}"
        with urllib.request.urlopen(url, timeout=45) as response:
            data = response.read(2 * 1024 * 1024)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'External content hash mismatch: {relative}')
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def full_install(skills_dir, *, home, apply=False, update=False, source=SOURCE):
    skills_dir, home, source = Path(skills_dir), Path(home), Path(source)
    manifest = json.loads((source / 'assets/bundle.json').read_text(encoding='utf-8'))
    sources = [(NAME, source)] + [(name, source / 'assets/skills' / name) for name in manifest['bundled_skills']]
    # An installed setup skill may install its companion skills in the same home.
    sources = [(n, p) for n, p in sources if p.resolve() != (skills_dir / n).resolve()]
    plans = [install(skills_dir, source=p, name=n, update=update) for n, p in sources]
    settings = settings_plan(home, source)
    external = []
    for entry in manifest['external_skills']:
        target = skills_dir / entry['name']
        if any(is_link(p) for p in (target, *target.absolute().parents)):
            raise ValueError('External skill destination contains a link')
        old = inventory(target) if target.exists() else None
        if old is not None and old != entry['files'] and not update:
            raise ValueError(f"Existing {entry['name']} differs; inspect before --update")
        external.append({'name': entry['name'], 'status': 'unchanged' if old == entry['files'] else 'download-required'})
    if not apply:
        return {'status': 'preview', 'skills': plans, 'external': external,
                'settings': [{'path': str(p['path']), 'status': 'unchanged' if p['old'] == p['new'] else 'change'} for p in settings]}
    with tempfile.TemporaryDirectory(prefix='codex-astra-') as temporary:
        downloads = []
        for entry, state in zip(manifest['external_skills'], external):
            if state['status'] != 'unchanged':
                directory = Path(temporary) / entry['name']
                fetch_external(entry, directory)
                downloads.append((entry['name'], directory))
        results = [install(skills_dir, source=p, name=n, apply=True, update=update) for n, p in sources + downloads]
        result_settings = write_settings(settings, home)
        for state in external:
            if state['status'] == 'download-required':
                state['status'] = 'installed'
    return {'status': 'applied', 'skills': results, 'external': external,
            'settings': result_settings, 'activation': 'Verify skill discovery in a new Codex task; plugins and account connections are separate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, default=default_skills_dir())
    parser.add_argument("--apply", action="store_true", help="Write the skill after reviewing the preview")
    parser.add_argument("--update", action="store_true", help="Allow a changed existing skill; keep a backup")
    parser.add_argument('--full', action='store_true', help='Restore all bundled skills, pinned zaebal, preferences and model settings')
    parser.add_argument('--codex-home', type=Path, help='Configuration directory (defaults to parent of --skills-dir)')
    args = parser.parse_args()
    try:
        if args.full:
            result = full_install(args.skills_dir, home=args.codex_home or args.skills_dir.parent,
                                  apply=args.apply, update=args.update)
        else:
            result = install(args.skills_dir, apply=args.apply, update=args.update)
    except (OSError, ValueError) as error:
        print(f"Installation stopped: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
