import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='nahicore test ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.dest = self.base / 'installed skills'

    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), '--dest', str(self.dest), *args],
                                text=True, capture_output=True, cwd=self.base)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def test_copy_upgrade_and_uninstall_preserve_other_skills(self):
        self.run_cli('--skill', 'notex')
        unrelated = self.dest / 'other'
        unrelated.mkdir()
        (unrelated / 'keep.txt').write_text('keep')
        self.assertTrue((self.dest / 'notex/SKILL.md').is_file())
        self.run_cli('--skill', 'notex')
        self.run_cli('--uninstall')
        self.assertFalse((self.dest / 'notex').exists())
        self.assertEqual((unrelated / 'keep.txt').read_text(), 'keep')

    def test_all_skills_and_private_config_exclusion(self):
        self.run_cli()
        receipt = json.loads((self.dest / '.nahicore-install.json').read_text())
        self.assertEqual(set(receipt['skills']), {'notex', 'brain-dump', 'name-scout', 'liquid-metal', 'release-man', 'chop-chop'})
        self.assertFalse((self.dest / 'brain-dump/vault.conf').exists())
        self.assertFalse((self.dest / 'brain-dump/projects.map').exists())
        self.assertTrue((self.dest / 'brain-dump/vault.conf.example').exists())

    def test_conflict_preflight_and_force_backup(self):
        folder = self.dest / 'notex'
        folder.mkdir(parents=True)
        (folder / 'mine').write_text('personal content')
        self.run_cli('--skill', 'brain-dump', '--skill', 'notex', ok=False)
        self.assertFalse((self.dest / 'brain-dump').exists())
        self.run_cli('--skill', 'notex', '--force')
        backups = list((self.dest / '.nahicore-backups').glob('*/notex/mine'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'personal content')

    def test_edited_managed_files_are_not_deleted(self):
        self.run_cli('--skill', 'notex')
        note = self.dest / 'notex/my-notes.txt'
        note.write_text('save me')
        self.run_cli('--uninstall', ok=False)
        self.assertEqual(note.read_text(), 'save me')
        self.run_cli('--uninstall', '--force')
        self.assertEqual(next((self.dest / '.nahicore-backups').glob('*/notex/my-notes.txt')).read_text(), 'save me')

    def test_symlink_uninstall_keeps_source(self):
        self.run_cli('--skill', 'notex', '--symlink')
        self.assertTrue((self.dest / 'notex').is_symlink())
        self.run_cli('--skill', 'notex', '--symlink')
        self.run_cli('--uninstall')
        self.assertTrue((ROOT / 'skills/notex/SKILL.md').is_file())

    def test_dry_run_and_invalid_names(self):
        self.run_cli('--dry-run')
        self.assertFalse(self.dest.exists())
        self.run_cli('--skill', '../outside', ok=False)
        self.run_cli('--skill', 'unknown', ok=False)
        self.assertFalse(self.dest.exists())

    def test_target_presets_and_shell_entrypoint(self):
        env = dict(os.environ, HOME=str(self.base))
        for target, suffix in [('agents', '.agents/skills'), ('codex', '.codex/skills'), ('claude', '.claude/skills'), ('claude-project', '.claude/skills'), ('project', '.agents/skills')]:
            result = subprocess.run(['bash', str(ROOT / 'install.sh'), '--target', target, '--skill', 'notex'],
                                    cwd=self.base, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((self.base / suffix / 'notex/SKILL.md').is_file())

    def test_broken_unowned_symlink_is_preserved(self):
        self.dest.mkdir()
        path = self.dest / 'notex'
        path.symlink_to(self.base / 'missing')
        self.run_cli('--skill', 'notex', ok=False)
        self.assertTrue(path.is_symlink())


if __name__ == '__main__':
    unittest.main()
