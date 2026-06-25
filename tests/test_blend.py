"""MVC-3 tests — the similarity-weighted blending operator."""

import numpy as np
import pytest

from patchi.blend import blend_from_neighbors, blend_word
from patchi.wordclass import Lexicon

CLUSTERS = {
    "cat": [1.0, 0.0, 0.0], "dog": [0.95, 0.05, 0.0], "pup": [0.9, 0.1, 0.0],
    "car": [0.0, 1.0, 0.0], "van": [0.0, 0.95, 0.05], "bus": [0.0, 0.9, 0.1],
}


def test_uniform_weighting_is_plain_mean():
    vecs = [np.array([0.0, 0.0]), np.array([2.0, 4.0])]
    out = blend_from_neighbors(vecs, [0.1, 0.9], weighting="uniform")
    assert np.allclose(out, [1.0, 2.0])


def test_similarity_weighting_leans_toward_similar_neighbour():
    vecs = [np.array([0.0, 0.0]), np.array([10.0, 0.0])]
    out = blend_from_neighbors(vecs, [0.0, 1.0], weighting="similarity")
    # all weight on the second neighbour
    assert np.allclose(out, [10.0, 0.0])


def test_power_sharpens_weighting():
    vecs = [np.array([0.0]), np.array([1.0])]
    soft = blend_from_neighbors(vecs, [0.5, 1.0], weighting="similarity", power=1.0)
    sharp = blend_from_neighbors(vecs, [0.5, 1.0], weighting="similarity", power=8.0)
    # sharper weighting pulls closer to the higher-similarity neighbour (1.0)
    assert sharp[0] > soft[0]


def test_nonpositive_similarities_fall_back_to_mean():
    vecs = [np.array([0.0, 0.0]), np.array([2.0, 2.0])]
    out = blend_from_neighbors(vecs, [-0.5, 0.0], weighting="similarity")
    assert np.allclose(out, [1.0, 1.0])


def test_empty_and_unknown_weighting_raise():
    with pytest.raises(ValueError):
        blend_from_neighbors([], [])
    with pytest.raises(ValueError):
        blend_from_neighbors([np.array([1.0])], [1.0], weighting="bogus")


def test_blend_word_reconstructs_within_cluster():
    lex = Lexicon.from_embeddings(CLUSTERS)
    # reconstruct "cat" from its neighbours (cat excluded): should land near the
    # animal cluster, closer to it than to the vehicle cluster.
    recon = blend_word(lex, "cat", k=3, weighting="similarity", power=2.0)
    from patchi.wordclass import cosine
    assert cosine(recon, lex["dog"].vector) > cosine(recon, lex["car"].vector)
