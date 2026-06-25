"""MVC-5 — the Proof(walk) explainability trace.

Pygmalion's outputs are not bare values: "Output == tuple< Final Set of words,
Proof(walk) >". The Proof(walk) records *which* words / infons / relations, with
what weight, produced an output — the traceability the framework promises at both
the semantic and circuit levels.

This module is the data structure; the operators thread it through:

* :func:`patchi.blend.blend_word_explained` returns ``(vector, ProofWalk)`` where
  the walk lists each neighbour and the (normalised) weight it contributed.
* :meth:`patchi.situation.Situation.supports_explained` returns
  ``(score, ProofWalk)`` recording which rule fired (exact / contradiction /
  vector-graded / structural) and the asserted infon that drove the score.

A key discipline: the explained variants are the **single source of truth** for
the maths (the plain ``blend_word`` / ``supports`` delegate to the same weight
computation), so a Proof(walk) can never describe a computation different from the
one that actually ran.

See ``literature/REVIEW.md`` §4 ("Proof(walk)") and ``todo.md`` MVC-5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class Contribution:
    """One contributor to a step: a name, the weight it carried, and a note."""

    name: str
    weight: float
    note: str = ""


@dataclass
class Step:
    """One operation in the walk: what ran, its result, and what fed it."""

    op: str
    result: str
    contributions: List[Contribution] = field(default_factory=list)
    detail: Dict[str, Any] = field(default_factory=dict)


class ProofWalk:
    """An ordered, serialisable trace of the steps that produced an output."""

    def __init__(self) -> None:
        self.steps: List[Step] = []

    def add(self, step: Step) -> "ProofWalk":
        self.steps.append(step)
        return self

    def __len__(self) -> int:
        return len(self.steps)

    def __iter__(self):
        return iter(self.steps)

    def contributors(self) -> List[str]:
        """Flat list of every contributor name across all steps (in order)."""
        return [c.name for s in self.steps for c in s.contributions]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps": [
                {
                    "op": s.op,
                    "result": s.result,
                    "contributions": [
                        {"name": c.name, "weight": c.weight, "note": c.note}
                        for c in s.contributions
                    ],
                    "detail": s.detail,
                }
                for s in self.steps
            ]
        }

    def explain(self) -> str:
        """Human-readable multi-line rendering of the walk."""
        lines: List[str] = []
        for i, s in enumerate(self.steps, 1):
            lines.append(f"{i}. {s.op}: {s.result}")
            for c in s.contributions:
                tail = f" ({c.note})" if c.note else ""
                lines.append(f"     - {c.name}: {c.weight:.3f}{tail}")
        return "\n".join(lines)
