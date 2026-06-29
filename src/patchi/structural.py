"""Graph-degree structural similarity — Pygmalion's "shared-neighbour distance".

The notebook's most-repeated *untested* empirical claim is that the similarity of
two words is carried by their **relational neighbourhood**, not their vector
geometry:

    "distance between words corresponds to the number of words they have in common"
    "Two words are similar if their neighbourhood structures overlap significantly"
    — data_lake/proto.txt, L229–235 and L308–316

Every Patchi empirical result so far measures a *geometric* signal (vector
reconstruction: ``blend ≤ raw``, 0 of 6). Structural similarity is a different
signal entirely: it reads only the **graph** of word–word relations and never
looks at the embedding. This module implements it over a generic adjacency so it
is decoupled from :class:`~patchi.wordclass.Lexicon` — the experiment
(``scripts/run_structural.py``) feeds it a WordNet-derived graph, an *independent*
relation source, which is what makes the test of Pygmalion's claim fair.

Three unsigned overlap measures and one **sign-aware** variant that honours the
stimulator/inhibitor spectrum (shared ``+`` neighbours pull together, shared
``−`` neighbours push apart):

* :func:`common_neighbors` — raw count of shared neighbours.
* :func:`jaccard` — ``|N(a) ∩ N(b)| / |N(a) ∪ N(b)|`` (size-normalised).
* :func:`adamic_adar` — shared neighbours weighted by ``1/log(degree)``, so a
  rare common neighbour counts for more than a hub.
* :func:`signed_overlap` — Pygmalion's spectrum: a neighbour shared with the same
  sign adds, shared with opposite sign subtracts.

An adjacency is a ``Mapping[str, Set[str]]`` (unsigned) or
``Mapping[str, Mapping[str, int]]`` (signed: neighbour → ±1). A word absent from
the adjacency simply has an empty neighbourhood.

See ``literature/REVIEW.md`` §"Distributional…", todo MVC-2 / the GD thread.
"""

from __future__ import annotations

import math
from typing import Mapping, Set

# An unsigned adjacency: word -> set of neighbour words.
Adjacency = Mapping[str, Set[str]]
# A signed adjacency: word -> {neighbour: +1 | -1}.
SignedAdjacency = Mapping[str, Mapping[str, int]]


def neighbours(adj: Adjacency, word: str) -> Set[str]:
    """Neighbour set of ``word`` (empty if the word is absent from ``adj``)."""
    return set(adj.get(word, set()))


def common_neighbors(adj: Adjacency, a: str, b: str) -> int:
    """Number of neighbours ``a`` and ``b`` share — the literal "words in common"."""
    return len(neighbours(adj, a) & neighbours(adj, b))


def jaccard(adj: Adjacency, a: str, b: str) -> float:
    """``|N(a) ∩ N(b)| / |N(a) ∪ N(b)|`` ∈ [0, 1]; 0 when both are isolated.

    Size-normalised so a hub with hundreds of neighbours is not automatically
    "similar" to everything it touches.
    """
    na, nb = neighbours(adj, a), neighbours(adj, b)
    union = na | nb
    if not union:
        return 0.0
    return len(na & nb) / len(union)


def adamic_adar(adj: Adjacency, a: str, b: str) -> float:
    """Shared neighbours weighted by ``1 / log(degree(c))``.

    A common neighbour that is itself rare (low degree) is stronger evidence of a
    real relation than a high-degree hub everyone connects to. Neighbours of
    degree ≤ 1 contribute nothing (``log`` undefined / non-positive), matching the
    standard definition.
    """
    score = 0.0
    for c in neighbours(adj, a) & neighbours(adj, b):
        deg = len(neighbours(adj, c))
        if deg > 1:
            score += 1.0 / math.log(deg)
    return score


def _signed_neighbours(adj: SignedAdjacency, word: str) -> Mapping[str, int]:
    return adj.get(word, {})


def signed_overlap(adj: SignedAdjacency, a: str, b: str) -> float:
    """Sign-aware shared-neighbour score (Pygmalion's stimulator/inhibitor spectrum).

    For each neighbour shared by ``a`` and ``b``: ``+1`` if the two edges agree in
    sign (both stimulate or both inhibit it — concordant), ``−1`` if they
    disagree (one stimulates, one inhibits — a contrast), normalised by the number
    of shared neighbours so the result is in ``[-1, 1]``. Words with no shared
    neighbour score 0.
    """
    na, nb = _signed_neighbours(adj, a), _signed_neighbours(adj, b)
    shared = set(na) & set(nb)
    if not shared:
        return 0.0
    total = sum(1 if na[c] == nb[c] else -1 for c in shared)
    return total / len(shared)
