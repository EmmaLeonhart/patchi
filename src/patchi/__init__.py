"""PATCHi — a reference implementation of Pygmalion's relation/agreement-based
theory of cognition.

The package is built layer by layer following ``todo.md`` / ``queue.md``:
WordClasses (MVC-1), a signed relation graph (MVC-2), the similarity-weighted
blending operator (MVC-3), an infon/situation layer (MVC-4), and a Proof(walk)
trace (MVC-5). This ``__init__`` only exposes the version until those land, so
the package is importable and testable from the very first commit.

The original framework is the intellectual work of Pygmalion; see
``data_lake/`` and ``literature/REVIEW.md``.
"""

__version__ = "0.0.1"

__all__ = ["__version__"]
