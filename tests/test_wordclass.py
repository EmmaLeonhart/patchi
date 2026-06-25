"""MVC-1 tests — WordClass + Lexicon construction and nearest-neighbour lookup.

Uses a small offline fixture (no network): two clear clusters in 3-D so the
expected nearest neighbours are unambiguous.
"""

import numpy as np
import pytest

from patchi.wordclass import Lexicon, WordClass, cosine

# Two clusters: {cat, dog, puppy} vs {car, truck}.
FIXTURE = {
    "cat": [1.0, 0.0, 0.0],
    "dog": [0.9, 0.1, 0.0],
    "puppy": [0.85, 0.15, 0.0],
    "car": [0.0, 1.0, 0.0],
    "truck": [0.0, 0.9, 0.1],
}


def make_lexicon() -> Lexicon:
    return Lexicon.from_embeddings(FIXTURE, glosses={"cat": "a small feline"})


# -- WordClass ---------------------------------------------------------------

def test_wordclass_stores_vector_and_dim():
    wc = WordClass("cat", [1.0, 0.0, 0.0])
    assert wc.word == "cat"
    assert wc.dim == 3
    assert np.allclose(wc.vector, [1.0, 0.0, 0.0])


def test_wordclass_vector_is_read_only():
    wc = WordClass("cat", [1.0, 0.0, 0.0])
    with pytest.raises(ValueError):
        wc.vector[0] = 9.0  # array marked non-writeable


def test_wordclass_rejects_non_1d_and_empty():
    with pytest.raises(ValueError):
        WordClass("bad", [[1.0, 2.0], [3.0, 4.0]])
    with pytest.raises(ValueError):
        WordClass("empty", [])


# -- cosine ------------------------------------------------------------------

def test_cosine_identical_and_orthogonal_and_zero():
    assert cosine([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine([0, 0], [1, 1]) == 0.0  # zero-norm guard


# -- Lexicon construction ----------------------------------------------------

def test_lexicon_construction_and_access():
    lex = make_lexicon()
    assert len(lex) == 5
    assert lex.dim == 3
    assert "cat" in lex and "missing" not in lex
    assert lex["cat"].gloss == "a small feline"
    assert lex.get("missing") is None
    assert set(lex.words()) == set(FIXTURE)


def test_lexicon_rejects_dimension_mismatch():
    lex = Lexicon([WordClass("a", [1.0, 0.0])])
    with pytest.raises(ValueError):
        lex.add(WordClass("b", [1.0, 0.0, 0.0]))


# -- nearest-neighbour -------------------------------------------------------

def test_nearest_neighbour_within_cluster():
    lex = make_lexicon()
    assert lex.nearest("cat", k=1)[0][0] == "dog"
    assert lex.nearest("car", k=1)[0][0] == "truck"


def test_nearest_excludes_self_and_respects_k():
    lex = make_lexicon()
    result = lex.nearest("cat", k=2)
    assert len(result) == 2
    assert "cat" not in [w for w, _ in result]
    # both nearest to cat should be its cluster-mates, in order
    assert [w for w, _ in result] == ["dog", "puppy"]
    # similarities are sorted descending
    sims = [s for _, s in result]
    assert sims == sorted(sims, reverse=True)


def test_nearest_to_arbitrary_vector():
    lex = make_lexicon()
    # a query right next to the animal cluster
    assert lex.nearest_to_vector([0.95, 0.05, 0.0], k=1)[0][0] == "cat"


def test_nearest_unknown_word_raises():
    lex = make_lexicon()
    with pytest.raises(KeyError):
        lex.nearest("dragon")
