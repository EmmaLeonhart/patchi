"""MVC-3 — the similarity-weighted blending operator.

Pygmalion's distinctive composition primitive (notebook: "Polynomial_of(w) =
Σ [ Similarity(w, sᵢ) × Encapsulated_Polynomial(sᵢ) ]"): a word's working
representation is rebuilt from its *similar* words, each weighted by how similar
it is. At this MVC stage the "encapsulated polynomial" of a neighbour is just its
vector, so the operator is

    blend(w) = ( Σ_i sim(w, sᵢ)^p · vec(sᵢ) ) / Σ_i sim(w, sᵢ)^p

over the ``k`` nearest neighbours sᵢ of w (w itself excluded — so this is a
*held-out reconstruction* of w from its neighbourhood). Two knobs make the
comparison in the benchmark fair and meaningful:

* ``weighting="uniform"`` collapses it to the **additive baseline** — the plain
  (unweighted) mean of the neighbours. This is the natural control: it isolates
  exactly what the *similarity weighting* buys over a flat average.
* ``power`` (p) sharpens or softens the weighting (p=0 → uniform, larger p →
  winner-take-most).

What this operator is NOT: a two-argument binding/composition (a⊗b). The
multiplicative/tensor family (Smolensky, DisCoCat) composes *two* meanings; this
reconstructs *one* from its neighbourhood. That distinction is made explicit in
`FINDINGS.md` rather than shoehorning a tensor baseline onto a 1-arg operator.

See ``literature/REVIEW.md`` §3(2) and ``todo.md`` MVC-3.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np

from .wordclass import Lexicon


def blend_from_neighbors(
    neighbor_vectors: Sequence[np.ndarray],
    similarities: Sequence[float],
    *,
    weighting: str = "similarity",
    power: float = 1.0,
) -> np.ndarray:
    """Core operator: weighted convex combination of neighbour vectors.

    ``weighting="similarity"`` uses ``max(sim, 0)^power`` as weights (negative
    similarities contribute nothing); ``weighting="uniform"`` uses equal weights
    (the additive baseline). Falls back to a flat mean if all weights are zero.
    """
    if len(neighbor_vectors) == 0:
        raise ValueError("need at least one neighbour to blend")
    vecs = np.asarray(neighbor_vectors, dtype=float)
    if weighting == "uniform":
        weights = np.ones(len(vecs))
    elif weighting == "similarity":
        weights = np.maximum(np.asarray(similarities, dtype=float), 0.0) ** power
    else:
        raise ValueError(f"unknown weighting {weighting!r}")
    total = float(weights.sum())
    if total == 0.0:
        return vecs.mean(axis=0)
    return (weights[:, None] * vecs).sum(axis=0) / total


def blend_word(
    lex: Lexicon,
    word: str,
    *,
    k: int = 5,
    weighting: str = "similarity",
    power: float = 1.0,
) -> np.ndarray:
    """Reconstruct ``word``'s vector from its ``k`` nearest neighbours.

    ``word`` itself is excluded (``Lexicon.nearest`` already excludes it), so the
    result is a held-out reconstruction — the quantity the benchmark scores.
    """
    neighbors = lex.nearest(word, k=k)
    if not neighbors:
        raise ValueError(f"{word!r} has no neighbours to blend from")
    vecs = [lex[w].vector for w, _ in neighbors]
    sims = [s for _, s in neighbors]
    return blend_from_neighbors(vecs, sims, weighting=weighting, power=power)
