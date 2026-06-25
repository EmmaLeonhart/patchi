"""LT-1 (reduced) tests — the block category and its property checkers."""

import numpy as np
import pytest

from patchi.block import NeuralBlock
from patchi import category as cat


def inv(label, scale, offset):
    return NeuralBlock(label, scale, offset)


def test_compose_all_matches_manual_composition():
    f = inv("f", [2.0], [1.0])
    g = inv("g", [3.0], [0.0])
    h = inv("h", [1.0], [-1.0])
    composed = cat.compose_all([f, g, h])
    x = np.array([2.0])
    assert np.allclose(composed.apply(x), f.apply(g.apply(h.apply(x))))


def test_compose_all_empty_raises():
    with pytest.raises(ValueError):
        cat.compose_all([])


def test_preserves_invertibility_true_for_invertible_chain():
    blocks = [inv("a", [2.0, 1.0], [0.0, 0.0]), inv("b", [1.0, 3.0], [1.0, 1.0])]
    assert cat.preserves_invertibility(blocks) is True


def test_preserves_invertibility_false_if_any_block_degenerate():
    good = inv("a", [2.0, 1.0], [0.0, 0.0])
    bad = inv("b", [1.0, 0.0], [0.0, 0.0])  # zero scale -> not invertible
    assert cat.preserves_invertibility([good, bad]) is False


def test_equivalent_detects_equal_and_unequal_maps():
    a = inv("a", [2.0, 3.0], [1.0, 0.0])
    a_copy = inv("relabeled", [2.0, 3.0], [1.0, 0.0])
    different = inv("c", [2.0, 3.0], [1.0, 0.1])
    assert cat.equivalent(a, a_copy) is True  # equivalence ignores the label
    assert cat.equivalent(a, different) is False


def test_round_trips_witness():
    b = inv("b", [2.0, 5.0], [1.0, -3.0])
    assert cat.round_trips(b, [4.0, 2.0]) is True
    degenerate = inv("z", [0.0], [0.0])
    assert cat.round_trips(degenerate, [1.0]) is False


def test_identity_law_holds():
    b = inv("b", [2.0, 3.0], [1.0, -1.0])
    assert cat.obeys_identity_law(b) is True


def test_composition_is_associative():
    a = inv("a", [2.0], [1.0])
    b = inv("b", [3.0], [-2.0])
    c = inv("c", [0.5], [4.0])
    assert cat.is_associative(a, b, c) is True
