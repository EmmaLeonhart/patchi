"""LT-3 tests — memory recursion and artificial time."""

import numpy as np
import pytest

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
