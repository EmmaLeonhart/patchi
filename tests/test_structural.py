"""Tests for graph-degree structural similarity (patchi.structural).

Hand-built toy graphs with hand-computable overlaps, plus the edge cases the
docstrings promise (isolated nodes, identical neighbourhoods, sign agreement).
"""

import math

import pytest

from patchi.structural import (
    adamic_adar,
    common_neighbors,
    jaccard,
    neighbours,
    signed_overlap,
)


# A small undirected co-membership graph:
#   cat   -- {pet, animal, fur}
#   dog   -- {pet, animal, fur}
#   car   -- {vehicle, metal}
# cat and dog share all three neighbours; cat and car share none.
TOY = {
    "cat": {"pet", "animal", "fur"},
    "dog": {"pet", "animal", "fur"},
    "car": {"vehicle", "metal"},
    # neighbour degrees (for adamic-adar): pet/animal/fur shared by cat & dog
    "pet": {"cat", "dog"},
    "animal": {"cat", "dog"},
    "fur": {"cat", "dog"},
    "vehicle": {"car"},
    "metal": {"car"},
}


def test_neighbours_absent_word_is_empty():
    assert neighbours(TOY, "unknown") == set()


def test_common_neighbors_counts_shared():
    assert common_neighbors(TOY, "cat", "dog") == 3
    assert common_neighbors(TOY, "cat", "car") == 0


def test_jaccard_full_overlap_is_one():
    assert jaccard(TOY, "cat", "dog") == pytest.approx(1.0)


def test_jaccard_disjoint_is_zero():
    assert jaccard(TOY, "cat", "car") == 0.0


def test_jaccard_partial_overlap():
    # x shares 1 of 3 union neighbours with y: N(x)={a,b}, N(y)={b,c} -> 1/3
    g = {"x": {"a", "b"}, "y": {"b", "c"}}
    assert jaccard(g, "x", "y") == pytest.approx(1 / 3)


def test_jaccard_both_isolated_is_zero_not_nan():
    g = {}
    assert jaccard(g, "x", "y") == 0.0


def test_adamic_adar_weights_by_inverse_log_degree():
    # cat & dog share pet, animal, fur — each of degree 2 -> 3 * 1/log(2)
    expected = 3.0 / math.log(2)
    assert adamic_adar(TOY, "cat", "dog") == pytest.approx(expected)


def test_adamic_adar_degree_one_neighbour_contributes_nothing():
    # shared neighbour 'c' has degree 1 (only x lists it... give both x,y the link
    # but c itself points to a single node) -> log(1)=0 is skipped.
    g = {"x": {"c"}, "y": {"c"}, "c": {"x"}}
    assert adamic_adar(g, "x", "y") == 0.0


def test_adamic_adar_no_shared_is_zero():
    assert adamic_adar(TOY, "cat", "car") == 0.0


# Signed graph: cat & dog both *stimulate* (+) pet and animal -> concordant.
# happy & sad both link 'mood' but with opposite signs -> discordant.
SIGNED = {
    "cat": {"pet": 1, "animal": 1},
    "dog": {"pet": 1, "animal": 1},
    "happy": {"mood": 1, "smile": 1},
    "sad": {"mood": -1, "smile": -1},
}


def test_signed_overlap_concordant_is_positive_one():
    assert signed_overlap(SIGNED, "cat", "dog") == pytest.approx(1.0)


def test_signed_overlap_discordant_is_negative_one():
    assert signed_overlap(SIGNED, "happy", "sad") == pytest.approx(-1.0)


def test_signed_overlap_no_shared_is_zero():
    assert signed_overlap(SIGNED, "cat", "happy") == 0.0


def test_signed_overlap_mixed():
    # share two neighbours: one concordant (+), one discordant (-) -> net 0/2 = 0
    g = {"a": {"x": 1, "y": 1}, "b": {"x": 1, "y": -1}}
    assert signed_overlap(g, "a", "b") == pytest.approx(0.0)
