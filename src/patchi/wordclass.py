"""MVC-1 — the WordClass lexicon.

A ``WordClass`` is the atomic object of the whole stack: a word paired with a
geometric representation (a vector — Pygmalion's "words as coordinates") and a
small bag of parameters, optionally seeded with a dictionary gloss. A
``Lexicon`` holds many of them and answers nearest-neighbour queries by cosine
similarity (Pygmalion's "similarity as geometric overlap").

This is deliberately the *minimum* WordClass. The richer notebook version carries
polynomial, geometric and axiomatic attributes; those grow in later MVC items.
The vectors here come from pretrained embeddings in real use (GloVe/word2vec);
tests use a small offline fixture so the suite runs without a network. Dictionary
gloss *ingestion* (parsing WordNet/Wiktionary) is deferred — for now ``gloss`` is
just an optional string the caller may attach.

See ``literature/REVIEW.md`` §2 (words-as-coordinates) and ``todo.md`` MVC-1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class WordClass:
    """A word with a vector and a small parameter bag.

    Frozen so a WordClass can be used as a stable key; the vector is stored as a
    read-only float array.
    """

    word: str
    vector: np.ndarray
    gloss: Optional[str] = None
    params: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        vec = np.asarray(self.vector, dtype=float)
        if vec.ndim != 1:
            raise ValueError(f"vector for {self.word!r} must be 1-D, got shape {vec.shape}")
        if vec.size == 0:
            raise ValueError(f"vector for {self.word!r} is empty")
        vec.flags.writeable = False
        # bypass frozen to normalise the stored array
        object.__setattr__(self, "vector", vec)

    @property
    def dim(self) -> int:
        return int(self.vector.shape[0])


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity of two vectors; 0.0 if either has zero norm."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


class Lexicon:
    """A collection of WordClasses with nearest-neighbour lookup."""

    def __init__(self, entries: Iterable[WordClass] = ()) -> None:
        self._by_word: Dict[str, WordClass] = {}
        self._dim: Optional[int] = None
        for wc in entries:
            self.add(wc)

    # -- construction --------------------------------------------------------

    def add(self, wc: WordClass) -> None:
        if self._dim is None:
            self._dim = wc.dim
        elif wc.dim != self._dim:
            raise ValueError(
                f"dimension mismatch: lexicon is {self._dim}-D, {wc.word!r} is {wc.dim}-D"
            )
        self._by_word[wc.word] = wc

    @classmethod
    def from_embeddings(
        cls,
        embeddings: Mapping[str, Iterable[float]],
        glosses: Optional[Mapping[str, str]] = None,
    ) -> "Lexicon":
        """Build a lexicon from a ``{word: vector}`` mapping.

        In production ``embeddings`` is a slice of pretrained vectors; in tests it
        is a small fixture. ``glosses`` optionally attaches a dictionary gloss per
        word.
        """
        glosses = glosses or {}
        lex = cls()
        for word, vec in embeddings.items():
            lex.add(WordClass(word=word, vector=np.asarray(list(vec), dtype=float),
                              gloss=glosses.get(word)))
        return lex

    # -- access --------------------------------------------------------------

    @property
    def dim(self) -> Optional[int]:
        return self._dim

    def __len__(self) -> int:
        return len(self._by_word)

    def __contains__(self, word: object) -> bool:
        return word in self._by_word

    def __getitem__(self, word: str) -> WordClass:
        return self._by_word[word]

    def get(self, word: str) -> Optional[WordClass]:
        return self._by_word.get(word)

    def words(self) -> List[str]:
        return list(self._by_word)

    # -- queries -------------------------------------------------------------

    def nearest(self, word: str, k: int = 5) -> List[Tuple[str, float]]:
        """The ``k`` most cosine-similar words to ``word`` (excluding itself).

        Raises ``KeyError`` if ``word`` is not in the lexicon. Returns a list of
        ``(word, similarity)`` sorted by descending similarity.
        """
        if word not in self._by_word:
            raise KeyError(word)
        return self.nearest_to_vector(self._by_word[word].vector, k=k, exclude={word})

    def nearest_to_vector(
        self, vector: Iterable[float], k: int = 5, exclude: Optional[set] = None
    ) -> List[Tuple[str, float]]:
        """The ``k`` most cosine-similar words to an arbitrary query vector."""
        exclude = exclude or set()
        q = np.asarray(list(vector), dtype=float)
        scored = [
            (w, cosine(q, wc.vector))
            for w, wc in self._by_word.items()
            if w not in exclude
        ]
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:k]
