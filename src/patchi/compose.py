"""LT-4 (first slice) — phrase composition.

The first concrete step of the syntax→semantics pipeline: combine *several* given
word-vectors into one phrase representation. This is distinct from the single-word
:func:`patchi.blend.blend_word` (which *reconstructs* one word from its
neighbourhood); here all the words are given and we compose them.

Three operators, the standard compositional-distributional baselines plus the
project's similarity-weighting:

* ``additive`` — ``Σ vec`` (Mitchell & Lapata additive model).
* ``multiplicative`` — elementwise ``Π vec`` (Mitchell & Lapata multiplicative
  model; the practical "tensor-ish" Hadamard baseline).
* ``weighted`` — similarity-weighted toward the phrase centroid: each word is
  weighted by ``max(cos(word, centroid), 0)^power`` and convex-combined. This
  down-weights an off-topic word, and it **reuses** the same operator as the
  blending benchmark (`blend_from_neighbors`) so the weighting is identical code.

See ``literature/REVIEW.md`` §"Distributional & compositional semantics" (Mitchell
& Lapata, DisCoCat) and ``todo.md`` LT-4.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .blend import blend_from_neighbors
from .wordclass import Lexicon, cosine


def compose_phrase(
    lex: Lexicon,
    words: Sequence[str],
    method: str = "additive",
    *,
    power: float = 1.0,
) -> np.ndarray:
    """Compose ``words`` into one phrase vector by ``method``.

    Raises ``KeyError`` for an unknown word, ``ValueError`` for an empty phrase or
    an unknown method.
    """
    if not words:
        raise ValueError("cannot compose an empty phrase")
    vecs = np.asarray([lex[w].vector for w in words], dtype=float)  # KeyError if missing

    if method == "additive":
        return vecs.sum(axis=0)
    if method == "multiplicative":
        return np.prod(vecs, axis=0)
    if method == "weighted":
        centroid = vecs.mean(axis=0)
        sims = [cosine(v, centroid) for v in vecs]
        return blend_from_neighbors(vecs, sims, weighting="similarity", power=power)
    raise ValueError(f"unknown method {method!r}")
