"""BR-2 (probe) tests — where VSA binding and Gärdenfors regions cohere, and
where they break. These assertions are measured facts (see the FINDINGS write-up),
not a claim that the unification succeeds.
"""

import numpy as np
import pytest

from patchi.regions import (
    BallRegion,
    bind,
    closed_under_binding,
    fixed_key_commutes_with_convex_combination,
)


def test_ball_region_membership():
    R = BallRegion([0.0, 0.0], 1.0)
    assert R.contains([0.5, 0.5])
    assert not R.contains([1.0, 1.0])  # dist sqrt(2) > 1
    with pytest.raises(ValueError):
        BallRegion([0.0], -0.1)


def test_bind_is_elementwise_product():
    assert np.allclose(bind([1.0, 2.0, 3.0], [4.0, 0.0, 2.0]), [4.0, 0.0, 6.0])


# -- where it COHERES --------------------------------------------------------

def test_fixed_key_binding_preserves_convexity():
    # binding by a fixed key is linear -> commutes with convex combination
    assert fixed_key_commutes_with_convex_combination([0.2, 0.9], [0.8, 0.1], [2.0, 3.0])


def test_origin_unit_ball_is_closed_under_binding():
    # at the origin, elementwise products shrink toward 0, so the unit ball is closed
    R = BallRegion([0.0, 0.0], 1.0)
    rng = np.random.default_rng(0)
    members = []
    while len(members) < 8:
        p = rng.uniform(-1, 1, 2)
        if R.contains(p):
            members.append(p)
    closed, fail = closed_under_binding(R, members)
    assert closed and fail is None


def test_binding_with_unit_vector_is_identity_so_membership_preserved():
    R = BallRegion([1.0, 1.0], 0.3)
    a = [1.1, 0.95]
    assert R.contains(a)
    assert R.contains(bind(a, [1.0, 1.0]))  # a ⊙ 1 == a


# -- where it BREAKS ---------------------------------------------------------

def test_off_origin_ball_is_NOT_closed_under_binding():
    # the headline negative: a region placed away from the origin is not closed.
    R = BallRegion([1.0, 1.0], 0.3)
    a = np.array([1.2, 1.0])
    assert R.contains(a)                      # a is a member
    bound = bind(a, a)                         # [1.44, 1.0]
    assert np.allclose(bound, [1.44, 1.0])
    assert not R.contains(bound)               # ...but a ⊙ a escapes the region

    closed, fail = closed_under_binding(R, [a, [1.0, 1.2], [1.0, 1.0]])
    assert closed is False and fail is not None
