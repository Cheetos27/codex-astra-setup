#!/usr/bin/env python3
"""Repository entry point; the installer also travels inside the skill."""
from pathlib import Path
import importlib.util
import sys
sys.dont_write_bytecode = True
_script = Path(__file__).resolve().parent / 'skills/codex-astra-setup/scripts/install_bundle.py'
_spec = importlib.util.spec_from_file_location('astra_bundle', _script)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
NAME, SOURCE = _module.NAME, _module.SOURCE
inventory, install = _module.inventory, _module.install
full_install, settings_plan = _module.full_install, _module.settings_plan
merge_preferences, patch_scalars = _module.merge_preferences, _module.patch_scalars
if __name__ == '__main__':
    raise SystemExit(_module.main())
