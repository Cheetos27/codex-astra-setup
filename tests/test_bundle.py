import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('bundle', ROOT / 'skills/codex-astra-setup/scripts/install_bundle.py')
bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bundle)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'profile'

    def fake_fetch(self, entry, destination):
        destination.mkdir(parents=True)
        (destination / 'SKILL.md').write_text('---\nname: zaebal\ndescription: Test\n---\n', encoding='utf-8')

    def test_preview_no_home_or_network(self):
        with patch.object(bundle, 'fetch_external', side_effect=AssertionError('Unexpected network')):
            result = bundle.full_install(self.home / 'skills', home=self.home)
        self.assertFalse(self.home.exists())
        self.assertEqual(len(result['skills']), 6)

    def test_full_install_and_repeat_preserve_unrelated_files(self):
        self.home.mkdir()
        config = self.home / 'config.toml'
        config.write_text('model = "old"\n[shell_environment_policy.set]\nMY_VALUE = "keep"\n[projects."/work"]\ntrust_level = "trusted"\n', encoding='utf-8')
        agents = self.home / 'AGENTS.md'
        agents.write_text('# My rules\n\nPreserve this instruction.\n', encoding='utf-8')
        with patch.object(bundle, 'fetch_external', side_effect=self.fake_fetch):
            bundle.full_install(self.home / 'skills', home=self.home, apply=True)
        self.assertEqual(tomllib.loads(config.read_text())['projects']['/work']['trust_level'], 'trusted')
        self.assertEqual(tomllib.loads(config.read_text())['shell_environment_policy']['set']['MY_VALUE'], 'keep')
        self.assertIn('Preserve this instruction.', agents.read_text(encoding='utf-8'))
        self.assertEqual(len(list((self.home / 'skills').iterdir())), 7)
        before = agents.read_bytes()
        # The test fixture is intentionally not the pinned external skill.
        with patch.object(bundle, 'fetch_external', side_effect=self.fake_fetch):
            bundle.full_install(self.home / 'skills', home=self.home, apply=True, update=True)
        self.assertEqual(before, agents.read_bytes())
        self.assertTrue(list((self.home / 'setup-backups').rglob('config.toml')))

    def test_invalid_toml_stops_before_skills_are_installed(self):
        self.home.mkdir()
        (self.home / 'config.toml').write_text('broken = [', encoding='utf-8')
        with self.assertRaises(tomllib.TOMLDecodeError):
            bundle.full_install(self.home / 'skills', home=self.home, apply=True)
        self.assertFalse((self.home / 'skills').exists())

    def test_download_failure_stops_before_installation(self):
        with patch.object(bundle, 'fetch_external', side_effect=OSError('Offline')):
            with self.assertRaises(OSError):
                bundle.full_install(self.home / 'skills', home=self.home, apply=True)
        self.assertFalse(self.home.exists())

    def test_concurrent_settings_edit_is_preserved(self):
        plans = bundle.settings_plan(self.home)
        self.home.mkdir()
        config = self.home / 'config.toml'
        config.write_text('model = "new-user-choice"\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            bundle.write_settings(plans, self.home)
        self.assertIn('new-user-choice', config.read_text())

    def test_managed_preferences_idempotent_and_updateable(self):
        one = bundle.merge_preferences('Personal\n', '# Profile\n\n## A\n\n- first\n')
        self.assertEqual(one, bundle.merge_preferences(one, '# Profile\n\n## A\n\n- first\n'))
        two = bundle.merge_preferences(one, '# Profile\n\n## A\n\n- second\n')
        self.assertIn('Personal', two)
        self.assertIn('- second', two)
        self.assertNotIn('- first', two)

    def test_restore_from_installed_skill(self):
        installed = self.home / 'skills/codex-astra-setup'
        bundle.install(self.home / 'skills', apply=True)
        with patch.object(bundle, 'fetch_external', side_effect=self.fake_fetch):
            bundle.full_install(self.home / 'skills', home=self.home, source=installed, apply=True)
        self.assertTrue((self.home / 'skills/researcher/SKILL.md').exists())

    def test_windows_environment_and_preserved_plugin_table(self):
        self.home.mkdir()
        config = self.home / 'config.toml'
        config.write_text('[plugins."test"]\nenabled = true\n', encoding='utf-8')
        data = tomllib.loads(bundle.settings_plan(self.home, windows=True)[0]['new'].decode())
        self.assertTrue(data['plugins']['test']['enabled'])
        self.assertEqual(data['shell_environment_policy']['set']['PYTHONUTF8'], '1')

    def test_selected_skills_only_and_no_external_download(self):
        with patch.object(bundle, 'fetch_external', side_effect=AssertionError('Unexpected download')):
            bundle.full_install(self.home / 'skills', home=self.home, apply=True,
                                selected=['researcher', 'css-graphics'])
        names = sorted(p.name for p in (self.home / 'skills').iterdir())
        self.assertEqual(names, ['codex-astra-setup', 'css-graphics', 'researcher'])
        entrypoints = list((self.home / 'skills').rglob('SKILL.md'))
        self.assertEqual(len(entrypoints), 3)
        preferences = (self.home / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertNotIn('Автоматическое сохранение при лимитах Codex', preferences)
        self.assertNotIn('`voice-summary`', preferences)
        self.assertIn('`researcher`', preferences)

    def test_empty_selection_creates_no_companion_skills(self):
        with patch.object(bundle, 'fetch_external', side_effect=AssertionError('Unexpected download')):
            bundle.full_install(self.home / 'skills', home=self.home, apply=True, selected=[])
        self.assertEqual([p.name for p in (self.home / 'skills').iterdir()], ['codex-astra-setup'])
        self.assertEqual(len(list((self.home / 'skills').rglob('SKILL.md'))), 1)
        selection = json.loads((self.home / 'astra-setup-selection.json').read_text())
        self.assertEqual(selection['selected'], [])

    def test_assisted_choices_are_pending_not_falsely_installed(self):
        with patch.object(bundle, 'fetch_external', side_effect=AssertionError('Unexpected download')):
            result = bundle.full_install(self.home / 'skills', home=self.home, apply=True,
                                         selected=['graphify', 'ponytail'])
        self.assertEqual(result['status'], 'needs_assisted_setup')
        self.assertFalse((self.home / 'skills/graphify').exists())
        state = json.loads((self.home / 'astra-setup-selection.json').read_text())
        self.assertEqual(state['pending_assisted'], ['graphify', 'ponytail'])

    def test_invalid_selection_fails_without_writes(self):
        with self.assertRaises(ValueError):
            bundle.full_install(self.home / 'skills', home=self.home, apply=True, selected=['typo'])
        self.assertFalse(self.home.exists())

    def test_unselected_existing_skill_is_preserved(self):
        existing = self.home / 'skills/voice-summary'
        existing.mkdir(parents=True)
        (existing / 'SKILL.md').write_text('Personal version', encoding='utf-8')
        bundle.full_install(self.home / 'skills', home=self.home, apply=True, selected=[])
        self.assertEqual((existing / 'SKILL.md').read_text(), 'Personal version')

    def test_main_skill_alone_has_only_one_discoverable_entrypoint(self):
        bundle.install(self.home / 'skills', apply=True)
        self.assertEqual(len(list((self.home / 'skills').rglob('SKILL.md'))), 1)


if __name__ == '__main__':
    unittest.main()
