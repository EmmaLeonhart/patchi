"""Smoke tests — the package imports and the entry point runs.

These exist so CI has something real to run from the first commit, before any
domain logic lands. As MVC-1+ are implemented, real unit tests join them here.
"""

import subprocess
import sys
from pathlib import Path

import patchi

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_package_imports_with_version():
    assert isinstance(patchi.__version__, str)
    assert patchi.__version__.count(".") == 2  # semver-ish: major.minor.patch


def test_run_entrypoint_exits_zero():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "run.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "PATCHi v" in result.stdout
