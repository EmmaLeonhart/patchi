"""MVC-4 tests — infons, graded situation support, and context-conditioning."""

import numpy as np
import pytest

from patchi.situation import Infon, Situation, infon_vector
from patchi.wordclass import Lexicon

# animals cluster vs vehicles cluster, so infon-vectors separate by topic
FIXTURE = {
    "fish": [1.0, 0.0, 0.0], "whale": [0.95, 0.05, 0.0], "dolphin": [0.9, 0.1, 0.0],
    "car": [0.0, 1.0, 0.0], "swims": [0.8, 0.2, 0.0], "drives": [0.1, 0.9, 0.0],
}


# -- Infon -------------------------------------------------------------------

def test_infon_normalises_args_and_validates_polarity():
    inf = Infon("swims", ["fish"], 1)
    assert inf.args == ("fish",)
    with pytest.raises(ValueError):
        Infon("swims", ("fish",), 0)


def test_infon_negate():
    inf = Infon("swims", ("fish",), 1)
    assert inf.negate() == Infon("swims", ("fish",), -1)


# -- exact / contradiction ---------------------------------------------------

def test_asserted_infon_is_fully_supported():
    s = Situation()
    s.assert_infon(Infon("swims", ("fish",), 1))
    assert s.supports(Infon("swims", ("fish",), 1)) == 1.0


def test_direct_contradiction_is_zero():
    s = Situation()
    s.assert_infon(Infon("swims", ("fish",), 1))
    assert s.supports(Infon("swims", ("fish",), -1)) == 0.0


# -- graded support is in range and reflects similarity ----------------------

def test_support_is_always_in_unit_interval():
    lex = Lexicon.from_embeddings(FIXTURE)
    s = Situation(lexicon=lex)
    s.assert_infon(Infon("swims", ("fish",), 1))
    for q in [Infon("swims", ("dolphin",), 1), Infon("drives", ("car",), 1),
              Infon("swims", ("car",), 1)]:
        assert 0.0 <= s.supports(q) <= 1.0


def test_graded_support_higher_for_more_similar_infon():
    lex = Lexicon.from_embeddings(FIXTURE)
    s = Situation(lexicon=lex)
    s.assert_infon(Infon("swims", ("fish",), 1))
    # dolphin is in the same (animal/swimming) region as fish; car is not
    near = s.supports(Infon("swims", ("dolphin",), 1))
    far = s.supports(Infon("swims", ("car",), 1))
    assert near > far


def test_structural_fallback_without_lexicon():
    s = Situation()  # no lexicon -> argument-overlap Jaccard
    s.assert_infon(Infon("near", ("a", "b"), 1))
    # query shares one of two args -> Jaccard 1/3
    assert s.supports(Infon("near", ("a", "c"), 1)) == pytest.approx(1 / 3)
    # different relation -> 0
    assert s.supports(Infon("far", ("a", "b"), 1)) == 0.0


# -- the headline property: context conditioning changes the output ----------

def test_same_infon_gets_different_support_across_situations():
    lex = Lexicon.from_embeddings(FIXTURE)
    water = Situation("water", lexicon=lex)
    water.assert_infon(Infon("swims", ("fish",), 1))
    road = Situation("road", lexicon=lex)
    road.assert_infon(Infon("drives", ("car",), 1))

    query = Infon("swims", ("dolphin",), 1)
    assert water.supports(query) != road.supports(query)
    assert water.supports(query) > road.supports(query)


def test_contextual_polarity_flips_with_context():
    a = Situation("affirm")
    a.assert_infon(Infon("flies", ("penguin",), 1))
    n = Situation("deny")
    n.assert_infon(Infon("flies", ("penguin",), -1))
    assert a.contextual_polarity("flies", ("penguin",)) == pytest.approx(1.0)
    assert n.contextual_polarity("flies", ("penguin",)) == pytest.approx(-1.0)
