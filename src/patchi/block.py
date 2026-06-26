"""BR-1 — neural blocks and the bijective WordClass <-> NeuralBlock translator.

Pygmalion's keystone is a *bijective* translator that maps each WordClass to a
reconfigurable "VHDL-style" neural circuit block and back. The stated risk is
that a true bijection over an open, growing vocabulary is too strong a claim.

**The way through (reduction, not hand-waving):** make the bijection a
*registry over the lexicon that grows on demand*. The ``Translator`` keeps a
structurally 1:1 registry word <-> block; an unseen word is *registered*
(minting a fresh block) rather than assumed to already have one. So at every
moment the map is an exact bijection over the registered set, and the open
vocabulary is handled by extension, not by pretending a closed-form bijection
over an infinite set exists. That is the honest, implementable form of the claim.

A ``NeuralBlock`` here is the *minimum* version: an **invertible affine map**
``y = d ⊙ x + b`` (elementwise scale + offset) derived deterministically from
the WordClass vector. Invertibility is what lets the later category-level checker
(``category.py``) reason about whether a composition "preserves bijectivity" —
the computable shadow of the topos meta-reasoning layer. Richer block internals
(the polynomial/twirk machinery) grow later; the algebra below is real now.

See ``literature/REVIEW.md`` §3(1) and ``todo.md`` BR-1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

import numpy as np

from .wordclass import WordClass


@dataclass(frozen=True)
class NeuralBlock:
    """An invertible affine map ``y = d ⊙ x + b`` with a label.

    ``scale`` (d) must be all-nonzero for the block to be invertible; the
    constructor enforces matching dimensions but allows non-invertible blocks to
    exist (so the category checker has something to *reject*).

    ``payload`` carries the originating WordClass's structured attributes
    (gloss, params, source vector) — the "richer" content the notebook wants the
    word↔block correspondence to preserve. It is **semantics, not the morphism**:
    ``apply``/``invert``/``compose`` and the category/twirk invariants depend only
    on (scale, offset), and ``category.equivalent`` ignores the payload. So a block
    can carry a word's meaning while still being reasoned about purely as an
    affine map. (At this stage the affine map is still *derived from* the vector;
    using the polynomial/region payload *in* the computation is future work.)
    """

    label: str
    scale: np.ndarray  # d, shape (n,)
    offset: np.ndarray  # b, shape (n,)
    payload: Mapping[str, Any] = field(default_factory=dict)  # carried WordClass attributes

    def __post_init__(self) -> None:
        d = np.asarray(self.scale, dtype=float)
        b = np.asarray(self.offset, dtype=float)
        if d.ndim != 1 or b.ndim != 1:
            raise ValueError("scale and offset must be 1-D")
        if d.shape != b.shape:
            raise ValueError(f"scale {d.shape} and offset {b.shape} must match")
        d.flags.writeable = False
        b.flags.writeable = False
        object.__setattr__(self, "scale", d)
        object.__setattr__(self, "offset", b)

    @property
    def dim(self) -> int:
        return int(self.scale.shape[0])

    @property
    def is_invertible(self) -> bool:
        return bool(np.all(self.scale != 0.0))

    def apply(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        return self.scale * x + self.offset

    def invert(self, y) -> np.ndarray:
        if not self.is_invertible:
            raise ValueError(f"block {self.label!r} is not invertible")
        y = np.asarray(y, dtype=float)
        return (y - self.offset) / self.scale

    def compose(self, other: "NeuralBlock") -> "NeuralBlock":
        """``self ∘ other``: apply ``other`` then ``self`` (affine ∘ affine)."""
        if self.dim != other.dim:
            raise ValueError(f"dim mismatch: {self.dim} vs {other.dim}")
        scale = self.scale * other.scale
        offset = self.scale * other.offset + self.offset
        return NeuralBlock(f"({self.label}∘{other.label})", scale, offset)

    @staticmethod
    def identity(dim: int, label: str = "id") -> "NeuralBlock":
        return NeuralBlock(label, np.ones(dim), np.zeros(dim))

    @staticmethod
    def from_wordclass(wc: WordClass) -> "NeuralBlock":
        """Deterministically mint a block from a WordClass.

        ``scale = 1 + |vector|`` (always >= 1, hence always invertible) and
        ``offset = vector``. Deterministic, so the same WordClass always yields
        the same block — a prerequisite for the bijection being well-defined. The
        block also **carries the WordClass's structured attributes** in ``payload``
        (gloss, params, source vector), so the correspondence preserves the word's
        semantics, not only the affine map derived from its vector.
        """
        vec = wc.vector
        payload = {
            "word": wc.word,
            "gloss": wc.gloss,
            "params": dict(wc.params),
            "source_vector": vec.copy(),
        }
        return NeuralBlock(wc.word, 1.0 + np.abs(vec), vec.copy(), payload=payload)


class Translator:
    """A bijective, on-demand registry between WordClasses and NeuralBlocks.

    Invariant: ``label`` <-> WordClass is exactly 1:1 over the registered set.
    """

    def __init__(self) -> None:
        self._word_to_wc: Dict[str, WordClass] = {}
        self._word_to_block: Dict[str, NeuralBlock] = {}

    def register(self, wc: WordClass) -> NeuralBlock:
        """Register a WordClass, minting its block. Idempotent for the same word.

        Raises ``ValueError`` if a *different* WordClass is registered under a
        word already present (which would break the bijection).
        """
        existing = self._word_to_wc.get(wc.word)
        if existing is not None:
            if not np.array_equal(existing.vector, wc.vector):
                raise ValueError(
                    f"{wc.word!r} already registered with a different vector"
                )
            return self._word_to_block[wc.word]
        block = NeuralBlock.from_wordclass(wc)
        self._word_to_wc[wc.word] = wc
        self._word_to_block[wc.word] = block
        return block

    def to_block(self, wc: WordClass) -> NeuralBlock:
        """The block for a WordClass, registering it on demand (open vocab)."""
        return self.register(wc)

    def to_wordclass(self, block: NeuralBlock) -> WordClass:
        """Inverse direction: recover the WordClass that minted a block."""
        wc = self._word_to_wc.get(block.label)
        if wc is None:
            raise KeyError(f"no registered WordClass for block label {block.label!r}")
        return wc

    def __len__(self) -> int:
        return len(self._word_to_wc)

    def __contains__(self, word: object) -> bool:
        return word in self._word_to_wc

    def words(self) -> List[str]:
        return list(self._word_to_wc)

    def is_bijective(self) -> bool:
        """Check the 1:1 invariant holds: distinct words -> distinct block labels."""
        labels = [b.label for b in self._word_to_block.values()]
        return (
            len(self._word_to_wc) == len(self._word_to_block) == len(set(labels))
        )
