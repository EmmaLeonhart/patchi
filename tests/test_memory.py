"""LT-3 tests — memory recursion and artificial time."""

import numpy as np
import pytest

from patchi.block import NeuralBlock
from patchi.memory import Memory


def test_initial_state_and_artificial_time():
    m = Memory(dim=3)
    assert m.time == 0
    assert np.allclose(m.state, [0.0, 0.0, 0.0])


def test_step_advances_artificial_time():
    m = Memory(dim=2, decay=0.5)
    m.step([1.0, 0.0])
    assert m.time == 1
    m.step([0.0, 1.0])
    assert m.time == 2


def test_leaky_accumulation_with_decay():
    m = Memory(dim=1, decay=0.5)
    assert np.allclose(m.step([1.0]), [1.0])      # 0.5*0 + 1
    assert np.allclose(m.step([1.0]), [1.5])      # 0.5*1 + 1
    assert np.allclose(m.step([0.0]), [0.75])     # 0.5*1.5 + 0


def test_decay_one_is_pure_accumulation():
    m = Memory(dim=1, decay=1.0)
    m.run([[1.0], [2.0], [3.0]])
    assert np.allclose(m.state, [6.0])


def test_decay_zero_is_memoryless():
    m = Memory(dim=1, decay=0.0)
    m.step([5.0])
    assert np.allclose(m.step([2.0]), [2.0])  # only the latest input survives


def test_run_returns_state_per_step():
    m = Memory(dim=1, decay=1.0)
    outs = m.run([[1.0], [1.0]])
    assert [float(o[0]) for o in outs] == [1.0, 2.0]
    assert m.time == 2


def test_reset_clears_state_and_time():
    m = Memory(dim=2, decay=0.5)
    m.run([[1.0, 2.0], [3.0, 4.0]])
    m.reset()
    assert m.time == 0 and np.allclose(m.state, [0.0, 0.0])


def test_wrong_input_shape_raises():
    m = Memory(dim=2)
    with pytest.raises(ValueError):
        m.step([1.0])


def test_construction_guards():
    with pytest.raises(ValueError):
        Memory(dim=0)
    with pytest.raises(ValueError):
        Memory(dim=2, decay=1.5)


def test_before_is_strict_time_order():
    assert Memory.before(1, 2) is True
    assert Memory.before(2, 2) is False


# -- BR-3: spatial-gated recurrence ------------------------------------------

def test_identity_gate_matches_ungated():
    plain = Memory(dim=2, decay=0.5)
    gated = Memory(dim=2, decay=0.5, gate=NeuralBlock.identity(2))
    seq = [[1.0, 2.0], [3.0, 4.0]]
    assert np.allclose(plain.run(seq), gated.run(seq))


def test_spatial_gate_transforms_input_before_accumulation():
    # gate doubles each input (scale 2, offset 0)
    gate = NeuralBlock("double", scale=[2.0, 2.0], offset=[0.0, 0.0])
    m = Memory(dim=2, decay=0.0, gate=gate)  # decay 0 -> state == gated input
    assert np.allclose(m.step([1.0, 3.0]), [2.0, 6.0])


def test_gate_with_offset_shifts_input():
    gate = NeuralBlock("shift", scale=[1.0], offset=[5.0])
    m = Memory(dim=1, decay=0.0, gate=gate)
    assert np.allclose(m.step([1.0]), [6.0])


def test_gate_dim_mismatch_raises():
    with pytest.raises(ValueError):
        Memory(dim=2, gate=NeuralBlock.identity(3))


def test_memory_tuple_and_spatial_gate_accessor():
    gate = NeuralBlock.identity(2)
    m = Memory(dim=2, gate=gate)
    m.step([1.0, 1.0])
    t, g = m.memory_tuple()
    assert t == 1 and g is gate
    assert m.spatial_gate is gate
