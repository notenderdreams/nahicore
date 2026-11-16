#!/usr/bin/env python3
"""Validate the repository's intentionally small skill metadata format."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    version = (root / 'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('VERSION must contain a stable semantic version')
    skills = sorted((root / 'skills').iterdir())
    if not skills:
        raise ValueError('No skills found')
    for skill in skills:
        text = (skill / 'SKILL.md').read_text()
        match = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
        if not match:
            raise ValueError(f'{skill.name}: missing YAML frontmatter')
        # These skills use plain, single-line name and description fields.
        fields = dict(line.split(': ', 1) for line in match[1].splitlines())
        if fields.get('name') != skill.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', skill.name):
            raise ValueError(f'{skill.name}: invalid or mismatched name')
        if not fields.get('description') or len(fields['description']) > 1024:
            raise ValueError(f'{skill.name}: missing or overlong description')
        metadata = (skill / 'agents/openai.yaml').read_text()
        values = {}
        for line in metadata.splitlines():
            if line.startswith('  ') and ': ' in line:
                key, value = line.strip().split(': ', 1)
                values[key] = json.loads(value)
        if not values.get('display_name') or not 25 <= len(values.get('short_description', '')) <= 64:
            raise ValueError(f'{skill.name}: invalid UI metadata')
        if f'${skill.name}' not in values.get('default_prompt', ''):
            raise ValueError(f'{skill.name}: prompt must invoke the skill')
        prose = re.sub(r'```.*?```', '', text, flags=re.S)
        for link in re.findall(r'\]\(([^)]+)\)', prose):
            if '://' not in link and not link.startswith('#') and not (skill / link.split('#')[0]).exists():
                raise ValueError(f'{skill.name}: missing local reference {link}')
        print(f'Validated {skill.name}')
    for script in root.rglob('*.py'):
        if not any(part in {'.git', '__pycache__', 'dist'} for part in script.parts):
            ast.parse(script.read_text(), filename=str(script))
    for script in [root / 'install.sh', root / 'skills/brain-dump/scripts/resolve_target.sh']:
        subprocess.run(['bash', '-n', str(script)], check=True)
    manifest = json.loads((root / '.claude-plugin/plugin.json').read_text())
    if manifest.get('name') != 'nahicore' or manifest.get('version') != version:
        raise ValueError('.claude-plugin/plugin.json name or version does not match VERSION')
    marketplace = json.loads((root / '.claude-plugin/marketplace.json').read_text())
    entries = {entry.get('name'): entry for entry in marketplace.get('plugins', [])}
    if entries.get('nahicore', {}).get('source') != './' or entries['nahicore'].get('version') != version:
        raise ValueError('.claude-plugin/marketplace.json must list nahicore at ./ with the current VERSION')
    print(f'Validated nahicore {version}')


if __name__ == '__main__':
    try:
        validate()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Validation failed: {error}', file=sys.stderr)
        sys.exit(1)
