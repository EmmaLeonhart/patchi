"""MVC-3 tests — Spearman, synthetic data, and the benchmark harness.

Includes a real regression guard: in the operator's favourable regime (low noise,
sharp weighting) similarity-weighted blending must beat both raw and additive by
a clear, deterministic margin. If a future change erodes that, the test fails —
which is the point.
"""

import numpy as np
import pytest

from patchi.benchmark import (
    evaluate,
    make_synthetic,
    run_benchmark,
    run_sweep,
    spearman,
    _rankdata,
)


# -- spearman ----------------------------------------------------------------

def test_spearman_perfect_monotonic():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    assert spearman(x, 2 * x + 1) == pytest.approx(1.0)
    assert spearman(x, -x) == pytest.approx(-1.0)


def test_spearman_constant_is_zero():
    assert spearman(np.array([1.0, 1.0, 1.0]), np.array([1.0, 2.0, 3.0])) == 0.0


def test_spearman_handles_ties_via_average_rank():
    assert np.allclose(_rankdata(np.array([5.0, 5.0, 1.0])), [2.5, 2.5, 1.0])


# -- synthetic data ----------------------------------------------------------

def test_make_synthetic_is_deterministic():
    a = make_synthetic(seed=3)
    b = make_synthetic(seed=3)
    w = a.lexicon.words()[0]
    assert np.allclose(a.lexicon[w].vector, b.lexicon[w].vector)
    assert len(a.lexicon) == 8 * 6


# -- evaluate / harness ------------------------------------------------------

def test_evaluate_returns_three_methods_in_range():
    data = make_synthetic(seed=0)
    scores = evaluate(data, k=5, power=2.0)
    assert set(scores) == {"raw", "additive", "blend"}
    for v in scores.values():
        assert -1.0 <= v <= 1.0


def test_run_benchmark_structure_and_determinism():
    r1 = run_benchmark()
    r2 = run_benchmark()
    assert r1["scores"] == r2["scores"]
    assert "metric" in r1 and "params" in r1


def test_run_sweep_rows_have_expected_fields():
    rows = run_sweep(noises=(0.4, 0.8), powers=(1.0,), k=8)
    assert len(rows) == 2
    assert set(rows[0]) >= {"noise", "power", "raw", "additive", "blend",
                            "blend_minus_additive"}


def test_blending_helps_in_favourable_regime():
    # low noise + sharp weighting: measured deterministically at seed 0.
    data = make_synthetic(noise=0.4, seed=0)
    scores = evaluate(data, k=8, power=4.0)
    assert scores["blend"] > scores["raw"]
    assert scores["blend"] - scores["additive"] > 0.10
