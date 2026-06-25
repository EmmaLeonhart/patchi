"""MVC-2 — the signed relation graph.

Two threads of Pygmalion's framework meet here:

* **Relations as vector offsets** (the "king − man + woman ≈ queen" / TransE
  reading): a relation *type* has a characteristic offset, so that for an edge
  ``head --rel--> tail`` we have ``tail ≈ head + offset(rel)``. Estimating the
  offset from known edges lets us *predict* the tail of a held-out edge by
  arithmetic + nearest-neighbour — the testable content of "relations as offsets".

* **The signed stimulator/inhibitor spectrum**: synonyms are stimulators (+1),
  antonyms are inhibitors (−1). Every edge carries a polarity, turning the graph
  into a signed graph whose net polarity around a word measures how much it is
  reinforced vs. opposed by its neighbourhood.

Vectors come from a :class:`~patchi.wordclass.Lexicon`. This is the minimum graph;
graded/learned offsets and richer relation algebra come later (todo BR-2).

See ``literature/REVIEW.md`` §"Distributional…" and §"Neuro-symbolic…", todo MVC-2.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from .wordclass import Lexicon

SYNONYM = "synonym"
ANTONYM = "antonym"


@dataclass(frozen=True)
class Relation:
    head: str
    tail: str
    rel_type: str
    polarity: int  # +1 stimulator (synonym-like), -1 inhibitor (antonym-like)


class SignedRelationGraph:
    """A signed, multi-relational graph with offset-based tail prediction."""

    def __init__(self, lexicon: Lexicon) -> None:
        self._lex = lexicon
        self._edges: List[Relation] = []
        self._by_type: Dict[str, List[Relation]] = defaultdict(list)

    # -- construction --------------------------------------------------------

    def add_relation(self, head: str, tail: str, rel_type: str, polarity: int) -> None:
        for w in (head, tail):
            if w not in self._lex:
                raise KeyError(f"{w!r} is not in the lexicon")
        if polarity not in (1, -1):
            raise ValueError("polarity must be +1 or -1")
        rel = Relation(head, tail, rel_type, polarity)
        self._edges.append(rel)
        self._by_type[rel_type].append(rel)

    def add_synonym(self, a: str, b: str) -> None:
        self.add_relation(a, b, SYNONYM, +1)

    def add_antonym(self, a: str, b: str) -> None:
        self.add_relation(a, b, ANTONYM, -1)

    # -- access --------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._edges)

    def relations(self, rel_type: Optional[str] = None) -> List[Relation]:
        return list(self._by_type[rel_type]) if rel_type is not None else list(self._edges)

    def relation_types(self) -> List[str]:
        return list(self._by_type)

    # -- relations as offsets ------------------------------------------------

    def offset(self, rel_type: str) -> np.ndarray:
        """Mean ``tail - head`` over all edges of ``rel_type`` (the TransE offset)."""
        edges = self._by_type.get(rel_type)
        if not edges:
            raise KeyError(f"no edges for relation type {rel_type!r}")
        diffs = [self._lex[e.tail].vector - self._lex[e.head].vector for e in edges]
        return np.mean(diffs, axis=0)

    def predict_tail(self, head: str, rel_type: str, k: int = 1) -> List[Tuple[str, float]]:
        """Predict the tail of ``head --rel_type--> ?`` by offset arithmetic.

        ``query = vec(head) + offset(rel_type)``, then nearest-neighbour in the
        lexicon (excluding ``head`` itself).
        """
        if head not in self._lex:
            raise KeyError(head)
        query = self._lex[head].vector + self.offset(rel_type)
        return self._lex.nearest_to_vector(query, k=k, exclude={head})

    # -- the signed spectrum -------------------------------------------------

    def polarity_between(self, a: str, b: str) -> int:
        """Net polarity of direct edges between ``a`` and ``b`` (either direction)."""
        total = 0
        for e in self._edges:
            if {e.head, e.tail} == {a, b}:
                total += e.polarity
        return total

    def neighbors(self, word: str, polarity: Optional[int] = None) -> List[str]:
        """Words directly linked to ``word``, optionally filtered by edge sign."""
        out: List[str] = []
        for e in self._edges:
            if word not in (e.head, e.tail):
                continue
            if polarity is not None and e.polarity != polarity:
                continue
            out.append(e.tail if e.head == word else e.head)
        return out

    def net_effect(self, word: str) -> int:
        """Stimulator/inhibitor balance: signed sum of edges incident to ``word``."""
        return sum(e.polarity for e in self._edges if word in (e.head, e.tail))
