"""LT-1 (reduced) — the computable shadow of topos meta-reasoning over blocks.

Pygmalion wants a topos whose internal logic can *prove* properties of neural
blocks: "this composition preserves bijectivity", "these two blocks are
equivalent up to isomorphism", and so on. A full elementary topos is far more
than is needed (or de-risked) at this stage. **What is buildable and honest now**
is the operational core that the topos idea reduces to:

  * a **category** of blocks — objects are vector spaces (indexed by dimension),
    morphisms are ``NeuralBlock`` affine maps, with associative ``compose`` and
    an ``identity`` (the category laws);
  * a **property checker** that decides, for a concrete composition, whether a
    property holds — the role the subobject classifier plays for "properties" in
    a topos, here realised as an ordinary boolean test.

This is explicitly *not* a topos; it is the decidable fragment that lets us make
the meta-reasoning claims testable instead of aspirational. The two checks below
("preserves invertibility", "equivalent") are the ones Pygmalion names first.

See ``literature/REVIEW.md`` §3(5) and ``todo.md`` LT-1.
"""

from __future__ import annotations

from functools import reduce
from typing import List, Sequence

import numpy as np

from .block import NeuralBlock


def compose_all(blocks: Sequence[NeuralBlock]) -> NeuralBlock:
    """Compose a non-empty sequence left-to-right: ``blocks[0] ∘ blocks[1] ∘ …``.

    (So the last block is applied to the input first, standard ``∘`` order.)
    """
    if not blocks:
        raise ValueError("cannot compose an empty sequence")
    return reduce(lambda f, g: f.compose(g), blocks)


def preserves_invertibility(blocks: Sequence[NeuralBlock]) -> bool:
    """Does composing ``blocks`` yield an invertible block?

    The topos-style claim "this composition preserves bijectivity" reduces here
    to: every factor is invertible *and* the composite is invertible. (For affine
    blocks the second follows from the first, but the checker tests the composite
    directly so it still rejects a sequence containing a degenerate block.)
    """
    if not blocks:
        return False
    if not all(b.is_invertible for b in blocks):
        return False
    return compose_all(blocks).is_invertible


def equivalent(a: NeuralBlock, b: NeuralBlock, *, tol: float = 1e-9) -> bool:
    """Are two blocks the same morphism (equal as affine maps within ``tol``)?

    The "equivalent up to isomorphism" claim, in this affine fragment, is exact
    equality of the (scale, offset) maps — checked numerically with a tolerance.
    """
    if a.dim != b.dim:
        return False
    return bool(
        np.allclose(a.scale, b.scale, atol=tol)
        and np.allclose(a.offset, b.offset, atol=tol)
    )


def round_trips(block: NeuralBlock, x, *, tol: float = 1e-9) -> bool:
    """Operational invertibility witness: ``invert(apply(x)) == x`` within ``tol``."""
    if not block.is_invertible:
        return False
    x = np.asarray(x, dtype=float)
    return bool(np.allclose(block.invert(block.apply(x)), x, atol=tol))


def obeys_identity_law(block: NeuralBlock, *, tol: float = 1e-9) -> bool:
    """Category law: ``block ∘ id == block == id ∘ block``."""
    idb = NeuralBlock.identity(block.dim)
    return equivalent(block.compose(idb), block, tol=tol) and equivalent(
        idb.compose(block), block, tol=tol
    )


def is_associative(
    a: NeuralBlock, b: NeuralBlock, c: NeuralBlock, *, tol: float = 1e-9
) -> bool:
    """Category law: ``(a ∘ b) ∘ c == a ∘ (b ∘ c)`` within ``tol``."""
    return equivalent(a.compose(b).compose(c), a.compose(b.compose(c)), tol=tol)
