import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESOLVER = ROOT / 'skills/brain-dump/scripts/resolve_target.sh'


class ResolverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='brain dump test ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.config = self.base / 'config/brain-dump'
        self.config.mkdir(parents=True)
        self.vault = self.base / 'Obsidian Vault'
        (self.config / 'vault.conf').write_text(f'VAULT_PATH={self.vault}\nDEFAULT_PROJECTS_DIR=Projects\n')
        self.env = dict(os.environ, NAHICORE_CONFIG_DIR=str(self.base / 'config'))
        self.env.pop('NAHICORE_VAULT_PATH', None)

    def resolve(self, *args, ok=True):
        result = subprocess.run(['bash', str(RESOLVER), *args], cwd=self.base, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return dict(line.split('=', 1) for line in result.stdout.splitlines()) if ok else result

    def test_local_creates_ignore_and_is_idempotent(self):
        result = self.resolve('--local')
        self.assertEqual(result['TARGET_DIR'], str(self.base / '.dead-brain'))
        self.resolve('--local')
        self.assertEqual((self.base / '.gitignore').read_text().count('.dead-brain/'), 1)

    def test_exact_project_mapping_and_registration(self):
        (self.config / 'projects.map').write_text('a.b|Special Path\naxb|Wrong\n')
        self.assertEqual(self.resolve('a.b')['TARGET_DIR'], str(self.vault / 'Special Path'))
        self.resolve('new-project')
        self.assertIn('new-project|Projects/new-project\n', (self.config / 'projects.map').read_text())

    def test_config_is_literal_and_rejects_escape(self):
        marker = self.base / 'executed'
        (self.config / 'vault.conf').write_text(f'VAULT_PATH={self.vault}\nDEFAULT_PROJECTS_DIR=$(touch {marker.name})\n')
        self.resolve('demo')
        self.assertFalse(marker.exists())
        self.resolve('demo', '../../outside', ok=False)
        self.resolve('../bad', ok=False)

    def test_symlink_escape(self):
        self.vault.mkdir()
        (self.vault / 'outside').symlink_to(self.base, target_is_directory=True)
        self.resolve('demo', 'outside/escape', ok=False)
        self.assertFalse((self.base / 'escape').exists())


if __name__ == '__main__':
    unittest.main()
