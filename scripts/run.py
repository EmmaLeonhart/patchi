"""PATCHi entry point.

CI invokes this; it is the single command that runs whatever the project's
current headline experiment is. Right now the package is freshly scaffolded and
there is no experiment yet, so it just reports the package version and the
current build stage. As MVC items land (the WordClass lexicon, the
similarity-weighted blending benchmark, ...), this grows into the runner that
produces metrics into ``results/``.
"""

import sys
from pathlib import Path

# Allow running directly (`python scripts/run.py`) without an install.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import patchi  # noqa: E402


def main() -> int:
    print(f"PATCHi v{patchi.__version__}")
    print("stage: scaffolded — no experiment wired yet (see queue.md MVC-1..5)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
