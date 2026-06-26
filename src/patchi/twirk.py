"""LT-2 — "twirking": constraint-checked reconfiguration of neural blocks.

Pygmalion's notebook describes "twirking" as VHDL-style reconfiguration —
altering a block's implementation or rewiring how blocks connect — guarded by
validity rules (the Prolog `valid_twirk`: compatible interfaces, no cycle
introduced, semantics/bijectivity preserved). With the block *category*
(`category.py`) already supplying the invariant checks, a twirk is just: propose
a change, and **accept it only if the category-level invariant still holds.**

Two twirks are implemented:

* :func:`twirk_block` — re-implement a single block's parameters (scale/offset).
  Rejected if the result is not invertible (the "preserve bijectivity" rule).
* :func:`rewire` — propose a new composition order of blocks. Rejected if the
  composite is not invertible (uses ``category.preserves_invertibility``).

This is the topos-shadow checker (LT-1) put to work *gating* reconfiguration —
exactly the meta-reasoning role the notebook wants ("does this twirk maintain
full-image coverage / bijectivity?"). What is *not* modelled here: cycle
detection and interface *retyping* across a wiring graph — the current
linear/affine block model has no graph of connections, so "no cycle introduced"
is N/A until blocks live in a real wiring graph (named, not faked).

See ``literature/REVIEW.md`` §3(5) and ``todo.md`` LT-2.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from .block import NeuralBlock
from .category import compose_all, preserves_invertibility


class TwirkRejected(Exception):
    """Raised when a proposed twirk violates a required invariant."""


def twirk_block(
    block: NeuralBlock,
    *,
    scale=None,
    offset=None,
    label: Optional[str] = None,
) -> NeuralBlock:
    """Re-implement ``block``'s parameters; reject if it breaks invertibility.

    ``scale``/``offset`` default to the block's existing values (so you can twirk
    just one). The new scale and offset must have matching length (a coordinated
    re-type); a mismatch is a hard ``ValueError`` from :class:`NeuralBlock`.
    Raises :class:`TwirkRejected` if the result is not invertible.
    """
    new_scale = block.scale if scale is None else np.asarray(scale, dtype=float)
    new_offset = block.offset if offset is None else np.asarray(offset, dtype=float)
    # re-implementing a word's circuit keeps its identity -> preserve the payload
    candidate = NeuralBlock(label or f"{block.label}~twirk", new_scale, new_offset,
                            payload=block.payload)
    if not candidate.is_invertible:
        raise TwirkRejected(
            f"twirk of {block.label!r} breaks invertibility (zero in scale)"
        )
    return candidate


def is_valid_twirk(block: NeuralBlock, *, scale=None, offset=None) -> bool:
    """Non-raising check: would this parameter twirk be accepted?"""
    try:
        twirk_block(block, scale=scale, offset=offset)
        return True
    except TwirkRejected:
        return False


def rewire(blocks: Sequence[NeuralBlock]) -> NeuralBlock:
    """Propose a new composition (a rewiring); accept only if it stays invertible.

    Returns the composed block; raises :class:`TwirkRejected` if any factor or the
    composite is non-invertible (via ``category.preserves_invertibility``).
    """
    if not preserves_invertibility(blocks):
        raise TwirkRejected("rewire breaks invertibility")
    return compose_all(blocks)


def is_valid_rewire(blocks: Sequence[NeuralBlock]) -> bool:
    """Non-raising check for :func:`rewire`."""
    return bool(blocks) and preserves_invertibility(blocks)
