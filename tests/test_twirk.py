"""LT-2 tests — twirking gated by the category's invertibility invariant."""

import numpy as np
import pytest

from patchi.block import NeuralBlock
from patchi.category import round_trips
from patchi.twirk import (
    TwirkRejected,
    is_valid_rewire,
    is_valid_twirk,
    rewire,
    twirk_block,
)


def inv(label, scale, offset):
    return NeuralBlock(label, scale, offset)


# -- twirk_block (re-implement parameters) -----------------------------------

def test_twirk_changes_parameters_and_stays_invertible():
    b = inv("b", [2.0, 3.0], [1.0, 0.0])
    t = twirk_block(b, scale=[4.0, 1.0])
    assert np.allclose(t.scale, [4.0, 1.0])
    assert np.allclose(t.offset, [1.0, 0.0])   # offset defaulted from b
    assert t.is_invertible
    assert "twirk" in t.label


def test_twirk_only_offset_defaults_scale():
    b = inv("b", [2.0], [0.0])
    t = twirk_block(b, offset=[5.0])
    assert np.allclose(t.scale, [2.0]) and np.allclose(t.offset, [5.0])


def test_twirk_breaking_invertibility_is_rejected():
    b = inv("b", [2.0, 3.0], [0.0, 0.0])
    with pytest.raises(TwirkRejected):
        twirk_block(b, scale=[2.0, 0.0])   # zero in scale -> non-invertible


def test_is_valid_twirk_true_false():
    b = inv("b", [2.0, 2.0], [0.0, 0.0])
    assert is_valid_twirk(b, scale=[1.0, 5.0]) is True
    assert is_valid_twirk(b, scale=[1.0, 0.0]) is False


def test_twirked_block_still_round_trips():
    b = inv("b", [2.0, 3.0], [1.0, -1.0])
    t = twirk_block(b, scale=[5.0, 0.5], offset=[2.0, 2.0])
    assert round_trips(t, [4.0, 4.0])


# -- rewire (re-compose) -----------------------------------------------------

def test_rewire_of_invertible_blocks_returns_composite():
    blocks = [inv("a", [2.0], [1.0]), inv("b", [3.0], [0.0])]
    composed = rewire(blocks)
    assert composed.is_invertible
    # a∘b applied to x: b(2)=6, a(6)=13
    assert np.allclose(composed.apply([2.0]), [13.0])


def test_rewire_with_degenerate_block_is_rejected():
    good = inv("a", [2.0, 1.0], [0.0, 0.0])
    bad = inv("z", [1.0, 0.0], [0.0, 0.0])   # not invertible
    with pytest.raises(TwirkRejected):
        rewire([good, bad])
    assert is_valid_rewire([good, bad]) is False
    assert is_valid_rewire([good]) is True


def test_rewire_empty_is_rejected():
    assert is_valid_rewire([]) is False
