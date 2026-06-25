"""MVC-5 tests — ProofWalk + the explained blend/support variants."""

import numpy as np
import pytest

from patchi.blend import blend_word, blend_word_explained
from patchi.proof import Contribution, ProofWalk, Step
from patchi.situation import Infon, Situation
from patchi.wordclass import Lexicon

FIXTURE = {
    "cat": [1.0, 0.0, 0.0], "dog": [0.95, 0.05, 0.0], "pup": [0.9, 0.1, 0.0],
    "car": [0.0, 1.0, 0.0], "van": [0.0, 0.95, 0.05],
}
ANIMALS = {
    "fish": [1.0, 0.0, 0.0], "whale": [0.95, 0.05, 0.0], "dolphin": [0.9, 0.1, 0.0],
    "car": [0.0, 1.0, 0.0],
}


# -- ProofWalk data structure ------------------------------------------------

def test_proofwalk_add_iter_contributors():
    pw = ProofWalk()
    out = pw.add(Step("op1", "did a thing", [Contribution("x", 0.6), Contribution("y", 0.4)]))
    assert out is pw and len(pw) == 1
    assert pw.contributors() == ["x", "y"]
    assert [s.op for s in pw] == ["op1"]


def test_proofwalk_to_dict_and_explain():
    pw = ProofWalk().add(Step("blend", "r", [Contribution("n", 0.5, "sim=0.9")], {"k": 3}))
    d = pw.to_dict()
    assert d["steps"][0]["op"] == "blend"
    assert d["steps"][0]["contributions"][0]["name"] == "n"
    assert d["steps"][0]["detail"] == {"k": 3}
    assert "blend" in pw.explain() and "n: 0.500" in pw.explain()


# -- blend_word_explained ----------------------------------------------------

def test_explained_vector_matches_plain_blend():
    lex = Lexicon.from_embeddings(FIXTURE)
    plain = blend_word(lex, "cat", k=3, weighting="similarity", power=2.0)
    vec, proof = blend_word_explained(lex, "cat", k=3, weighting="similarity", power=2.0)
    assert np.allclose(plain, vec)


def test_blend_proof_records_neighbours_and_normalised_weights():
    lex = Lexicon.from_embeddings(FIXTURE)
    _, proof = blend_word_explained(lex, "cat", k=3, weighting="similarity", power=2.0)
    assert len(proof) == 1
    step = proof.steps[0]
    assert step.op == "blend"
    assert len(step.contributions) == 3            # k neighbours
    assert "cat" not in proof.contributors()       # self excluded
    weights = [c.weight for c in step.contributions]
    assert sum(weights) == pytest.approx(1.0)      # convex combination


def test_uniform_weighting_gives_equal_weights_in_proof():
    lex = Lexicon.from_embeddings(FIXTURE)
    _, proof = blend_word_explained(lex, "cat", k=2, weighting="uniform")
    weights = [c.weight for c in proof.steps[0].contributions]
    assert weights == pytest.approx([0.5, 0.5])


# -- supports_explained ------------------------------------------------------

def test_support_explained_score_matches_supports():
    lex = Lexicon.from_embeddings(ANIMALS)
    s = Situation(lexicon=lex)
    s.assert_infon(Infon("swims", ("fish",), 1))
    q = Infon("swims", ("dolphin",), 1)
    score, proof = s.supports_explained(q)
    assert score == s.supports(q)
    assert proof.steps[0].detail["rule"] == "vector"
    assert 0.0 <= score <= 1.0


def test_support_explained_exact_and_contradiction_rules():
    s = Situation()
    s.assert_infon(Infon("flies", ("bird",), 1))
    score_x, px = s.supports_explained(Infon("flies", ("bird",), 1))
    assert score_x == 1.0 and px.steps[0].detail["rule"] == "exact"
    score_c, pc = s.supports_explained(Infon("flies", ("bird",), -1))
    assert score_c == 0.0 and pc.steps[0].detail["rule"] == "contradiction"


def test_support_explained_structural_rule_without_lexicon():
    s = Situation()
    s.assert_infon(Infon("near", ("a", "b"), 1))
    score, proof = s.supports_explained(Infon("near", ("a", "c"), 1))
    assert score == pytest.approx(1 / 3)
    assert proof.steps[0].detail["rule"] == "structural"
    assert proof.contributors() == ["near(a, b)[+]"]
