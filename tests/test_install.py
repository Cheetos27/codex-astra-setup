import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("skill_installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.skills = self.root / "profile" / "skills"

    def test_preview_does_not_create_directories(self):
        result = installer.install(self.skills)
        self.assertEqual(result["status"], "preview")
        self.assertFalse(self.skills.parent.exists())

    def test_install_and_repeat_preserve_configuration(self):
        self.skills.parent.mkdir()
        config = self.skills.parent / "config.toml"
        agents = self.skills.parent / "AGENTS.md"
        config.write_bytes(b'model = "existing-model"\n')
        agents.write_bytes(b"Existing personal guidance\n")
        first = installer.install(self.skills, apply=True)
        second = installer.install(self.skills, apply=True)
        self.assertEqual(first["status"], "installed")
        self.assertEqual(second["status"], "unchanged")
        self.assertEqual(config.read_bytes(), b'model = "existing-model"\n')
        self.assertEqual(agents.read_bytes(), b"Existing personal guidance\n")
        self.assertFalse((self.skills.parent / "skill-backups").exists())

    def test_different_version_requires_explicit_update(self):
        installer.install(self.skills, apply=True)
        personal = self.skills / installer.NAME / "personal.txt"
        personal.write_text("Keep my addition", encoding="utf-8")
        with self.assertRaises(ValueError):
            installer.install(self.skills, apply=True)
        self.assertEqual(personal.read_text(), "Keep my addition")

    def test_update_preserves_all_old_files_in_backup(self):
        installer.install(self.skills, apply=True)
        target = self.skills / installer.NAME
        (target / "SKILL.md").write_bytes(b"Older skill\r\n")
        (target / "personal.txt").write_bytes(b"Personal addition")
        before = installer.inventory(target)
        preview = installer.install(self.skills, update=True)
        self.assertEqual(preview["removed_files"], ["personal.txt"])
        self.assertEqual(installer.inventory(target), before)
        result = installer.install(self.skills, update=True, apply=True)
        self.assertEqual(installer.inventory(Path(result["backup"])), before)
        self.assertEqual(installer.inventory(target), installer.inventory(installer.SOURCE))

    def test_failed_update_restores_old_directory(self):
        installer.install(self.skills, apply=True)
        target = self.skills / installer.NAME
        (target / "personal.txt").write_bytes(b"Keep this")
        before = installer.inventory(target)
        real_rename = Path.rename

        def fail_stage(path, destination):
            if ".stage-" in path.name:
                raise OSError("Simulated final rename failure")
            return real_rename(path, destination)

        with patch.object(Path, "rename", fail_stage):
            with self.assertRaises(OSError):
                installer.install(self.skills, update=True, apply=True)
        self.assertEqual(installer.inventory(target), before)

    def test_destination_file_is_not_overwritten(self):
        self.skills.mkdir(parents=True)
        target = self.skills / installer.NAME
        target.write_bytes(b"Unrelated file")
        with self.assertRaises(ValueError):
            installer.install(self.skills, update=True, apply=True)
        self.assertEqual(target.read_bytes(), b"Unrelated file")

    def test_source_destination_overlap_is_rejected(self):
        with self.assertRaises(ValueError):
            installer.install(installer.SOURCE.parent, apply=True)

    def test_symlink_destination_is_rejected(self):
        actual = self.root / "actual"
        actual.mkdir()
        redirected = self.root / "redirected"
        try:
            redirected.symlink_to(actual, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink creation unavailable for this account")
        with self.assertRaises(ValueError):
            installer.install(redirected / "skills", apply=True)
        self.assertEqual(list(actual.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
