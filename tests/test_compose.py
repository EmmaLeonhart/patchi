"""LT-4 (first slice) tests — phrase composition operators."""

import numpy as np
import pytest

from patchi.compose import compose_phrase
from patchi.wordclass import Lexicon, cosine


def test_additive_is_vector_sum():
    lex = Lexicon.from_embeddings({"a": [1.0, 2.0], "b": [3.0, 0.5]})
    assert np.allclose(compose_phrase(lex, ["a", "b"], "additive"), [4.0, 2.5])


def test_multiplicative_is_elementwise_product():
    lex = Lexicon.from_embeddings({"a": [2.0, 3.0], "b": [4.0, 0.5]})
    assert np.allclose(compose_phrase(lex, ["a", "b"], "multiplicative"), [8.0, 1.5])


def test_weighted_downweights_an_outlier_word():
    # 3 words near [1,0], 1 outlier near [0,1]
    lex = Lexicon.from_embeddings({
        "a": [1.0, 0.0], "b": [1.0, 0.05], "c": [1.0, 0.1], "d": [0.0, 1.0],
    })
    words = ["a", "b", "c", "d"]
    cluster = np.array([1.0, 0.0])
    additive = compose_phrase(lex, words, "additive")
    weighted = compose_phrase(lex, words, "weighted", power=4.0)
    # similarity weighting pulls the phrase toward the cluster, away from the outlier
    assert cosine(weighted, cluster) > cosine(additive, cluster)


def test_single_word_phrase_passthrough():
    lex = Lexicon.from_embeddings({"a": [1.0, 2.0]})
    assert np.allclose(compose_phrase(lex, ["a"], "additive"), [1.0, 2.0])
    assert np.allclose(compose_phrase(lex, ["a"], "multiplicative"), [1.0, 2.0])


def test_unknown_method_and_word_and_empty_raise():
    lex = Lexicon.from_embeddings({"a": [1.0, 0.0]})
    with pytest.raises(ValueError):
        compose_phrase(lex, ["a"], "bogus")
    with pytest.raises(KeyError):
        compose_phrase(lex, ["a", "missing"], "additive")
    with pytest.raises(ValueError):
        compose_phrase(lex, [], "additive")
