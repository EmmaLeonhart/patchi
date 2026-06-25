"""MVC-4 — the infon / situation layer.

Devlin's situation theory gives the *infon* ``⟨relation, args, polarity⟩`` and a
*binary* support relation ``s ⊨ σ`` ("situation s supports infon σ"). The
literature review flagged the open move (§3.4): make support **graded and
computational** — a continuous ``support(s, σ) ∈ [0,1]`` instead of true/false.

This builds exactly that:

* :class:`Infon` — the ``⟨relation, args, polarity⟩`` triple (polarity ±1).
* :class:`Situation` — a context that asserts some infons and can *score* how
  much it supports any queried infon, graded in [0,1]:
    - an asserted infon is supported 1.0;
    - its direct contradiction (same relation+args, opposite polarity) → 0.0;
    - otherwise a graded score. With a :class:`~patchi.wordclass.Lexicon`, the
      score is the best cosine similarity between the query's infon-vector and a
      same-polarity asserted infon-vector (clamped to [0,1]); without one, a
      structural fallback (argument-overlap among same-relation, same-polarity
      asserted infons).

Because support depends on *what the situation asserts*, the **same infon gets
different support in different situations** — that is "context as the base
relation" made measurable, and the property the tests pin down.

See ``literature/REVIEW.md`` §"Situation semantics" and ``todo.md`` MVC-4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import numpy as np

from .proof import Contribution, ProofWalk, Step
from .wordclass import Lexicon, cosine


def _fmt(infon: "Infon") -> str:
    """Compact human label for an infon: ``relation(arg1, arg2)[+/-]``."""
    sign = "+" if infon.polarity == 1 else "-"
    return f"{infon.relation}({', '.join(infon.args)})[{sign}]"


@dataclass(frozen=True)
class Infon:
    """A unit of information: ``⟨relation, args, polarity⟩`` (polarity ±1)."""

    relation: str
    args: Tuple[str, ...]
    polarity: int = 1

    def __post_init__(self) -> None:
        if self.polarity not in (1, -1):
            raise ValueError("polarity must be +1 or -1")
        object.__setattr__(self, "args", tuple(self.args))

    def negate(self) -> "Infon":
        return Infon(self.relation, self.args, -self.polarity)


def infon_vector(lex: Lexicon, infon: Infon) -> Optional[np.ndarray]:
    """Mean vector of an infon's relation+arg tokens that are in the lexicon.

    Returns ``None`` if none of the tokens are present (so similarity is undefined).
    """
    toks = [infon.relation, *infon.args]
    vecs = [lex[t].vector for t in toks if t in lex]
    if not vecs:
        return None
    return np.mean(vecs, axis=0)


class Situation:
    """A context that asserts infons and grades its support for any queried one."""

    def __init__(self, name: str = "", lexicon: Optional[Lexicon] = None) -> None:
        self.name = name
        self.lex = lexicon
        self._asserted: List[Infon] = []

    def assert_infon(self, infon: Infon) -> None:
        self._asserted.append(infon)

    def asserted(self) -> List[Infon]:
        return list(self._asserted)

    def supports(self, query: Infon) -> float:
        """Graded support ``∈ [0,1]``; delegates to :meth:`supports_explained`."""
        return self.supports_explained(query)[0]

    def supports_explained(self, query: Infon):
        """``(score, ProofWalk)`` — the score plus which rule/infon produced it.

        This is the single source of truth for support; :meth:`supports` returns
        just its score, so the trace can never disagree with the value.
        """
        if query in self._asserted:
            proof = ProofWalk().add(Step("support", "exact match — asserted",
                [Contribution(_fmt(query), 1.0, "asserted")], {"rule": "exact"}))
            return 1.0, proof
        if query.negate() in self._asserted:
            proof = ProofWalk().add(Step("support", "contradiction — opposite asserted",
                [Contribution(_fmt(query.negate()), 0.0, "asserted opposite")],
                {"rule": "contradiction"}))
            return 0.0, proof

        same_pol = [a for a in self._asserted if a.polarity == query.polarity]

        # vector-backed grading, if a lexicon is available and the query embeds
        if self.lex is not None:
            qv = infon_vector(self.lex, query)
            if qv is not None:
                best, best_a = 0.0, None
                for a in same_pol:
                    av = infon_vector(self.lex, a)
                    if av is not None:
                        c = max(0.0, cosine(qv, av))
                        if c >= best:
                            best, best_a = c, a
                contribs = [Contribution(_fmt(best_a), best, "max infon-vector cosine")] \
                    if best_a is not None else []
                proof = ProofWalk().add(Step("support",
                    f"graded by infon-vector cosine = {best:.3f}", contribs,
                    {"rule": "vector"}))
                return best, proof

        # structural fallback: best argument-overlap (Jaccard) among
        # same-relation, same-polarity asserted infons
        best, best_a = 0.0, None
        for a in same_pol:
            if a.relation == query.relation:
                qa, aa = set(query.args), set(a.args)
                if qa or aa:
                    j = len(qa & aa) / len(qa | aa)
                    if j >= best:
                        best, best_a = j, a
        contribs = [Contribution(_fmt(best_a), best, "argument Jaccard")] \
            if best_a is not None else []
        proof = ProofWalk().add(Step("support",
            f"structural argument overlap = {best:.3f}", contribs,
            {"rule": "structural"}))
        return best, proof

    def contextual_polarity(self, relation: str, args: Sequence[str]) -> float:
        """A signed, context-conditioned output in [-1, 1].

        ``support(positive infon) - support(negative infon)`` — positive when the
        situation leans toward the fact holding, negative when it leans against.
        The same (relation, args) query yields different values in different
        situations: context conditioning, made into a number.
        """
        args = tuple(args)
        pos = self.supports(Infon(relation, args, +1))
        neg = self.supports(Infon(relation, args, -1))
        return pos - neg
