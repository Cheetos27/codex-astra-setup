#!/usr/bin/env python3
"""Install only the bundled skill. Preview by default; no network or config edits."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone
from uuid import uuid4

NAME = "codex-astra-setup"
SOURCE = Path(__file__).resolve().parent / "skills" / NAME


def is_link(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def inventory(folder):
    if is_link(folder) or not folder.is_dir():
        raise ValueError(f"Expected a real directory: {folder}")
    result = {}
    for current, dirs, files in os.walk(folder, followlinks=False):
        current = Path(current)
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


def install(skills_dir, *, apply=False, update=False, source=SOURCE):
    source = Path(source).absolute()
    skills_dir = Path(skills_dir).expanduser().absolute()
    target = skills_dir / NAME
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
    stage = skills_dir / f".{NAME}.stage-{uuid4().hex}"
    shutil.copytree(source, stage)
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
        backup = backup_root / f"{NAME}-{stamp}-{uuid4().hex[:8]}"
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, default=default_skills_dir())
    parser.add_argument("--apply", action="store_true", help="Write the skill after reviewing the preview")
    parser.add_argument("--update", action="store_true", help="Allow a changed existing skill; keep a backup")
    args = parser.parse_args()
    try:
        result = install(args.skills_dir, apply=args.apply, update=args.update)
    except (OSError, ValueError) as error:
        print(f"Installation stopped: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
