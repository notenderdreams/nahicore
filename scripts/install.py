#!/usr/bin/env python3
"""Install skills with ownership tracking and conflict backups."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = '.nahicore-install.json'
PRIVATE = {'vault.conf', 'projects.map', '__pycache__', '.DS_Store'}


def exists(path):
    return path.exists() or path.is_symlink()


def fingerprint(path):
    if path.is_symlink():
        return {'link': os.readlink(path)}
    if not path.is_dir():
        return {'file': hashlib.sha256(path.read_bytes()).hexdigest()}
    digest = hashlib.sha256()
    for item in sorted(path.rglob('*')):
        digest.update(item.relative_to(path).as_posix().encode() + b'\0')
        if item.is_symlink():
            digest.update(b'L' + os.readlink(item).encode())
        elif item.is_file():
            digest.update(b'F' + item.read_bytes())
        else:
            digest.update(b'D')
    return {'tree': digest.hexdigest()}


def remove(path):
    if path.is_symlink() or not path.is_dir():
        path.unlink()
    else:
        shutil.rmtree(path)


def save_receipt(destination, records):
    with tempfile.NamedTemporaryFile(mode='w', dir=destination, delete=False) as handle:
        json.dump({'schema': 1, 'skills': records}, handle, indent=2)
        handle.write('\n')
        temporary = handle.name
    os.replace(temporary, destination / RECEIPT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=['agents', 'codex', 'claude', 'claude-project', 'project'], default='agents')
    parser.add_argument('--dest', type=Path, help='Custom skills directory; overrides --target')
    parser.add_argument('--project', action='store_true', help='Alias for --target project')
    parser.add_argument('--global', dest='global_scope', action='store_true', help='Alias for --target agents')
    parser.add_argument('--skill', action='append', help='Select a skill; repeatable')
    parser.add_argument('--symlink', action='store_true', help='Link to this checkout')
    parser.add_argument('--uninstall', action='store_true', help='Remove recorded installations')
    parser.add_argument('--force', action='store_true', help='Back up conflicts before replacing/removing')
    parser.add_argument('--dry-run', action='store_true', help='Show actions without writing')
    parser.add_argument('--list', action='store_true', help='List bundled skills')
    args = parser.parse_args()
    available = {p.name: p for p in sorted((ROOT / 'skills').iterdir()) if (p / 'SKILL.md').is_file()}
    if args.list:
        print('\n'.join(available))
        return
    if args.project and args.global_scope:
        parser.error('--project and --global are mutually exclusive')
    target = 'project' if args.project else 'agents' if args.global_scope else args.target
    destinations = {'agents': Path.home() / '.agents/skills', 'codex': Path.home() / '.codex/skills',
                    'claude': Path.home() / '.claude/skills', 'claude-project': Path.cwd() / '.claude/skills',
                    'project': Path.cwd() / '.agents/skills'}
    destination = (args.dest or destinations[target]).expanduser().absolute()
    receipt = destination / RECEIPT
    records = {}
    if exists(receipt):
        if receipt.is_symlink():
            parser.error('Refusing a symlinked installation receipt')
        data = json.loads(receipt.read_text())
        if data.get('schema') != 1 or not isinstance(data.get('skills'), dict):
            parser.error('Unsupported installation receipt')
        records = data['skills']
    names = list(dict.fromkeys(args.skill or (sorted(records) if args.uninstall else available)))
    for name in names:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            parser.error(f'Invalid skill name: {name}')
        if not args.uninstall and name not in available:
            parser.error(f'Unknown skill: {name}')
    actions = []
    for name in names:
        dest = destination / name
        if args.uninstall and name not in records:
            parser.error(f'{name} is not owned by this installer')
        if not args.uninstall and available[name].resolve() == dest.resolve():
            if dest.is_symlink() and args.symlink:
                actions.append((name, 'adopt'))
                continue
            if not dest.is_symlink():
                parser.error(f'{dest} is the source checkout; choose another destination')
        conflict = exists(dest) and (name not in records or fingerprint(dest) != records[name])
        if conflict and not args.force:
            parser.error(f'{dest} contains unowned or modified files; use --force to back them up')
        actions.append((name, 'backup' if conflict else 'replace'))
    for name, action in actions:
        dest = destination / name
        verb = 'Uninstall' if args.uninstall else 'Link' if args.symlink else 'Install'
        print(f'{verb} {dest}' + (' (back up existing content)' if action == 'backup' else ''))
        if args.dry_run:
            continue
        destination.mkdir(parents=True, exist_ok=True)
        staged = None
        if not args.uninstall and action != 'adopt':
            staging = Path(tempfile.mkdtemp(prefix='.nahicore-stage-', dir=destination))
            staged = staging / name
            try:
                if args.symlink:
                    staged.symlink_to(available[name].resolve(), target_is_directory=True)
                else:
                    shutil.copytree(available[name], staged,
                                    ignore=lambda directory, entries: [e for e in entries if e in PRIVATE or e.endswith('.pyc')])
            except Exception:
                shutil.rmtree(staging)
                raise
        try:
            if action == 'backup' and exists(dest):
                backup = destination / '.nahicore-backups' / uuid.uuid4().hex / name
                backup.parent.mkdir(parents=True)
                shutil.move(str(dest), str(backup))
                print(f'Backup: {backup}')
            elif exists(dest) and action != 'adopt':
                remove(dest)
            if args.uninstall:
                records.pop(name, None)
            else:
                if staged is not None:
                    os.replace(staged, dest)
                records[name] = fingerprint(dest)
            save_receipt(destination, records)
        finally:
            if staged is not None:
                shutil.rmtree(staged.parent)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
