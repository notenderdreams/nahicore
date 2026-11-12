import hashlib
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def test_reproducible_archive_is_installable_without_private_config(self):
        with tempfile.TemporaryDirectory(prefix='release test ') as temporary:
            base = Path(temporary)
            output = base / 'dist'
            command = [sys.executable, str(ROOT / 'scripts/build_release.py'), '--output', str(output)]
            subprocess.run(command, check=True, capture_output=True)
            archive = next(output.glob('*.tar.gz'))
            first = archive.read_bytes()
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(first, archive.read_bytes())
            self.assertTrue(archive.with_name(archive.name + '.sha256').read_text().startswith(hashlib.sha256(first).hexdigest()))
            with tarfile.open(archive) as tar:
                names = tar.getnames()
                self.assertFalse(any(Path(name).name in {'vault.conf', 'projects.map'} for name in names))
                self.assertTrue(any(name.endswith('vault.conf.example') for name in names))
                tar.extractall(base / 'unpacked', filter='data') if sys.version_info >= (3, 12) else tar.extractall(base / 'unpacked')
            unpacked = next((base / 'unpacked').iterdir())
            subprocess.run([sys.executable, str(unpacked / 'scripts/install.py'), '--dest', str(base / 'installed'), '--skill', 'notex'], check=True, capture_output=True)
            self.assertTrue((base / 'installed/notex/SKILL.md').is_file())


if __name__ == '__main__':
    unittest.main()
