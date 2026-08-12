from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_check_secrets():
    script = Path(__file__).resolve().parents[1] / "scripts" / "check_secrets.py"
    spec = importlib.util.spec_from_file_location("galileo_check_secrets", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scanner_uses_current_python_module() -> None:
    check_secrets = _load_check_secrets()
    assert check_secrets._scanner_command() == [sys.executable, "-m", "detect_secrets"]
