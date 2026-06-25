"""MVC-2 tests — signed relation graph + offset-based held-out recovery."""

import numpy as np
import pytest

from patchi.relations import ANTONYM, SYNONYM, SignedRelationGraph
from patchi.wordclass import Lexicon

# Antonym pairs share a constant offset [0, 2]; synonym pairs share ~[0, 0.05].
FIXTURE = {
    # antonym relation, offset [0, 2]
    "hot": [1.0, 0.0], "cold": [1.0, 2.0],
    "fast": [3.0, 0.0], "slow": [3.0, 2.0],
    "up": [5.0, 0.0], "down": [5.0, 2.0],
    # synonym relation, offset ~[0, 0.05]
    "big": [7.0, 0.0], "large": [7.0, 0.05],
    "small": [9.0, 0.0], "little": [9.0, 0.05],
}


def make_graph() -> SignedRelationGraph:
    return SignedRelationGraph(Lexicon.from_embeddings(FIXTURE))


# -- construction & guards ---------------------------------------------------

def test_add_and_count_edges():
    g = make_graph()
    g.add_antonym("hot", "cold")
    g.add_synonym("big", "large")
    assert len(g) == 2
    assert set(g.relation_types()) == {ANTONYM, SYNONYM}


def test_add_relation_unknown_word_raises():
    g = make_graph()
    with pytest.raises(KeyError):
        g.add_synonym("big", "ginormous")  # not in lexicon


def test_bad_polarity_raises():
    g = make_graph()
    with pytest.raises(ValueError):
        g.add_relation("hot", "cold", ANTONYM, 0)


# -- relations as offsets ----------------------------------------------------

def test_offset_is_mean_difference():
    g = make_graph()
    g.add_antonym("hot", "cold")
    g.add_antonym("fast", "slow")
    assert np.allclose(g.offset(ANTONYM), [0.0, 2.0])


def test_offset_unknown_type_raises():
    g = make_graph()
    with pytest.raises(KeyError):
        g.offset("hypernym")


def test_predict_recovers_heldout_antonym():
    g = make_graph()
    # train on two antonym pairs, hold out (up, down)
    g.add_antonym("hot", "cold")
    g.add_antonym("fast", "slow")
    pred = g.predict_tail("up", ANTONYM, k=1)
    assert pred[0][0] == "down"


def test_predict_recovers_heldout_synonym():
    g = make_graph()
    g.add_synonym("big", "large")          # train
    pred = g.predict_tail("small", SYNONYM, k=1)  # hold out small->little
    assert pred[0][0] == "little"


# -- the signed spectrum -----------------------------------------------------

def test_polarity_between_is_signed_and_symmetric():
    g = make_graph()
    g.add_synonym("big", "large")
    g.add_antonym("hot", "cold")
    assert g.polarity_between("big", "large") == 1
    assert g.polarity_between("large", "big") == 1   # symmetric lookup
    assert g.polarity_between("hot", "cold") == -1
    assert g.polarity_between("big", "hot") == 0      # unrelated


def test_neighbors_filtered_by_sign():
    g = make_graph()
    g.add_synonym("big", "large")
    g.add_antonym("big", "small")
    assert set(g.neighbors("big")) == {"large", "small"}
    assert g.neighbors("big", polarity=1) == ["large"]
    assert g.neighbors("big", polarity=-1) == ["small"]


def test_net_effect_balances_stimulators_and_inhibitors():
    g = make_graph()
    g.add_synonym("big", "large")   # +1 incident to big
    g.add_synonym("big", "large")   # +1 again (parallel edge)
    g.add_antonym("big", "small")   # -1 incident to big
    assert g.net_effect("big") == 1
