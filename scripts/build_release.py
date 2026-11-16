#!/usr/bin/env python3
"""Build a deterministic, personal-config-free release archive and checksum."""
import argparse
import gzip
import hashlib
import io
from pathlib import Path
import tarfile

from validate import ROOT, validate

ROOT_FILES = {'README.md', 'LICENSE', 'VERSION', 'CHANGELOG.md', 'CONTRIBUTING.md', 'install.sh', '.gitignore', '.gitattributes'}
ROOT_DIRS = {'.claude-plugin', 'skills', 'scripts', 'tests', 'docs', '.github'}
PRIVATE = {'vault.conf', 'projects.map', '__pycache__', '.DS_Store'}


def release_files(root):
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part in PRIVATE or part.endswith('.pyc') for part in relative.parts):
            continue
        if relative.parts[0] not in ROOT_DIRS and str(relative) not in ROOT_FILES:
            continue
        if path.is_symlink():
            raise ValueError(f'Release files must not be symlinks: {relative}')
        if path.is_file():
            yield path


def build(root, output):
    validate(root)
    version = (root / 'VERSION').read_text().strip()
    prefix = f'nahicore-{version}'
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'{prefix}.tar.gz'
    with archive.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as tar:
                for path in release_files(root):
                    data = path.read_bytes()
                    info = tarfile.TarInfo(f'{prefix}/{path.relative_to(root).as_posix()}')
                    info.size = len(data)
                    info.mode = 0o755 if path.suffix == '.sh' else 0o644
                    tar.addfile(info, io.BytesIO(data))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / f'{archive.name}.sha256').write_text(f'{digest}  {archive.name}\n')
    print(archive)
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    build(ROOT, args.output.resolve())
