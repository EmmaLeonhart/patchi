"""BR-2 (probe) — Gärdenfors regions vs. VSA binding.

The literature review flagged an open consistency question (§3.3): Conceptual
Spaces represent a concept as a **convex region**; Vector-Symbolic Architectures
**bind** vectors (here: elementwise product, the MAP-style binding). Pygmalion's
framework wants both at once — set theory over class *perimeters* AND binding on
the *same* objects. Do they cohere? Concretely: **is a region closed under
binding** (if `a, b ∈ R`, is `a ⊙ b ∈ R`), and **does binding preserve
convexity**?

This module is the minimal machinery to *probe* that, not to force a positive
answer. The accompanying tests record where it holds and where it breaks; the
write-up is in `FINDINGS.md`.

See ``literature/REVIEW.md`` §3(3) and ``todo.md`` BR-2.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np


def bind(a, b) -> np.ndarray:
    """VSA (MAP-style) binding: elementwise product."""
    return np.asarray(a, dtype=float) * np.asarray(b, dtype=float)


class BallRegion:
    """A Gärdenfors-style convex region: a Euclidean ball (centre, radius)."""

    def __init__(self, center: Sequence[float], radius: float) -> None:
        self.center = np.asarray(center, dtype=float)
        if radius < 0:
            raise ValueError("radius must be non-negative")
        self.radius = float(radius)

    def contains(self, p, *, tol: float = 1e-9) -> bool:
        return bool(np.linalg.norm(np.asarray(p, dtype=float) - self.center)
                    <= self.radius + tol)


def closed_under_binding(
    region: BallRegion, members: Sequence[Sequence[float]]
) -> Tuple[bool, Optional[Tuple[int, int]]]:
    """Are all pairwise bindings of ``members`` still inside ``region``?

    Returns ``(closed, failing_pair_indices)``; ``failing_pair_indices`` is the
    first ``(i, j)`` whose binding escapes the region, or ``None`` if closed.
    Assumes every member is itself in the region (the caller's setup).
    """
    pts = [np.asarray(m, dtype=float) for m in members]
    for i in range(len(pts)):
        for j in range(len(pts)):
            if not region.contains(bind(pts[i], pts[j])):
                return False, (i, j)
    return True, None


def fixed_key_commutes_with_convex_combination(
    a, b, key, lam: float = 0.5
) -> bool:
    """Binding by a fixed key is linear, so it should commute with convex
    combination: ``bind(λa+(1-λ)b, key) == λ·bind(a,key)+(1-λ)·bind(b,key)``.

    When this holds, fixed-key binding maps convex sets to convex sets (it
    preserves convexity). Returned as a checkable boolean.
    """
    a, b, key = map(lambda v: np.asarray(v, dtype=float), (a, b, key))
    lhs = bind(lam * a + (1 - lam) * b, key)
    rhs = lam * bind(a, key) + (1 - lam) * bind(b, key)
    return bool(np.allclose(lhs, rhs))
