from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class LauncherSmokeTest(unittest.TestCase):
    def test_chart_launcher_exposes_main(self) -> None:
        module = load_module(
            "stella_plugin_chart_launcher",
            PLUGIN_ROOT / "scripts" / "stella_kerykeion.py",
        )
        self.assertTrue(callable(module.main))

    def test_guardrail_launcher_exposes_main(self) -> None:
        module = load_module(
            "stella_plugin_guardrail_launcher",
            PLUGIN_ROOT / "hooks" / "stella_guardrail.py",
        )
        self.assertTrue(callable(module.main))


if __name__ == "__main__":
    unittest.main()
