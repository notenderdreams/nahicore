#!/usr/bin/env python3
"""Resolve a Brain Dump destination without executing configuration."""
import argparse
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--local', '--in-project', '-l', action='store_true')
    modes.add_argument('--vault', '-v', action='store_true')
    parser.add_argument('project', nargs='?', default=Path.cwd().name)
    parser.add_argument('subdir', nargs='?')
    args = parser.parse_args()
    if not args.project or args.project in {'.', '..'} or any(c in args.project for c in '/\\|\n\r'):
        parser.error('Project must be a nonempty name without path separators, pipes, or newlines')
    if args.local:
        target = Path.cwd() / '.dead-brain'
        target.mkdir(parents=True, exist_ok=True)
        ignore = Path.cwd() / '.gitignore'
        text = ignore.read_text() if ignore.exists() else ''
        if '.dead-brain/' not in text.splitlines():
            with ignore.open('a') as handle:
                handle.write(('\n' if text and not text.endswith('\n') else '') + '# Brain Dump local notes\n.dead-brain/\n')
    else:
        config_dir = Path(os.environ.get('NAHICORE_CONFIG_DIR', str(Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'nahicore'))) / 'brain-dump'
        skill_dir = Path(__file__).resolve().parents[1]
        config = config_dir / 'vault.conf'
        if not config.exists() and (skill_dir / 'vault.conf').exists():
            config = skill_dir / 'vault.conf'
        if not config.exists():
            parser.error(f'Configure {config_dir / "vault.conf"} using vault.conf.example, or use --local')
        values = {}
        for line in config.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#'):
                key, separator, value = line.partition('=')
                if not separator:
                    parser.error(f'Invalid config line: {line}')
                values[key.strip()] = value.strip().strip('"\'')
        vault_value = os.environ.get('NAHICORE_VAULT_PATH') or values.get('VAULT_PATH')
        if not vault_value:
            parser.error('VAULT_PATH is required')
        vault = Path(vault_value).expanduser()
        if not vault.is_absolute():
            parser.error('VAULT_PATH must be absolute')
        config_dir.mkdir(parents=True, exist_ok=True)
        mapping_file = config_dir / 'projects.map'
        mapping_source = mapping_file if mapping_file.exists() else skill_dir / 'projects.map'
        mappings = {}
        if mapping_source.exists():
            for line in mapping_source.read_text().splitlines():
                if not line.strip() or line.lstrip().startswith('#'):
                    continue
                key, separator, value = line.partition('|')
                if not separator or not key or not value or key in mappings:
                    parser.error(f'Invalid or duplicate project mapping: {line}')
                mappings[key] = value
        subdir = args.subdir or mappings.get(args.project) or f'{values.get("DEFAULT_PROJECTS_DIR", "Projects")}/{args.project}'
        relative = Path(subdir)
        if relative.is_absolute() or '..' in relative.parts or any(c in subdir for c in '\n\r|'):
            parser.error('Project destinations must be relative paths inside the vault')
        target = (vault / relative).resolve()
        if not target.is_relative_to(vault.resolve()):
            parser.error('Project destination escapes the vault through a symlink')
        target.mkdir(parents=True, exist_ok=True)
        if mappings.get(args.project) != subdir or not mapping_file.exists():
            mappings[args.project] = subdir
            mapping_file.write_text(''.join(f'{key}|{value}\n' for key, value in mappings.items()))
    print(f'MODE={"local" if args.local else "vault"}')
    print(f'PROJECT_NAME={args.project}')
    print(f'TARGET_DIR={target}')
    print(f'INDEX_FILE={target / "Index.md"}')


if __name__ == '__main__':
    try:
        main()
    except OSError as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
