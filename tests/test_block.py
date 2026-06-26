"""BR-1 tests — NeuralBlock affine algebra and the bijective Translator."""

import numpy as np
import pytest

from patchi.block import NeuralBlock, Translator
from patchi.wordclass import WordClass


# -- NeuralBlock -------------------------------------------------------------

def test_apply_and_invert_round_trip():
    blk = NeuralBlock("b", scale=[2.0, 3.0], offset=[1.0, -1.0])
    x = np.array([5.0, 4.0])
    y = blk.apply(x)
    assert np.allclose(y, [11.0, 11.0])
    assert np.allclose(blk.invert(y), x)


def test_non_invertible_block_rejected_on_invert():
    blk = NeuralBlock("z", scale=[1.0, 0.0], offset=[0.0, 0.0])
    assert blk.is_invertible is False
    with pytest.raises(ValueError):
        blk.invert([1.0, 2.0])


def test_compose_is_function_composition():
    f = NeuralBlock("f", scale=[2.0], offset=[1.0])
    g = NeuralBlock("g", scale=[3.0], offset=[-2.0])
    fg = f.compose(g)  # apply g then f
    x = np.array([4.0])
    assert np.allclose(fg.apply(x), f.apply(g.apply(x)))
    # explicit: g(4)=10, f(10)=21
    assert np.allclose(fg.apply(x), [21.0])


def test_identity_block_is_neutral():
    idb = NeuralBlock.identity(3)
    x = np.array([1.0, 2.0, 3.0])
    assert np.allclose(idb.apply(x), x)
    assert idb.is_invertible


def test_from_wordclass_is_deterministic_and_invertible():
    wc = WordClass("cat", [1.0, -2.0, 0.0])
    b1 = NeuralBlock.from_wordclass(wc)
    b2 = NeuralBlock.from_wordclass(wc)
    assert np.allclose(b1.scale, [2.0, 3.0, 1.0])  # 1 + |v|
    assert np.allclose(b1.offset, [1.0, -2.0, 0.0])
    assert b1.is_invertible
    assert np.allclose(b1.scale, b2.scale) and np.allclose(b1.offset, b2.offset)


def test_compose_dim_mismatch_raises():
    f = NeuralBlock("f", scale=[1.0, 1.0], offset=[0.0, 0.0])
    g = NeuralBlock("g", scale=[1.0], offset=[0.0])
    with pytest.raises(ValueError):
        f.compose(g)


# -- BR-1 reach: blocks carry the WordClass payload --------------------------

def test_from_wordclass_carries_structured_payload():
    wc = WordClass("cat", [1.0, -2.0, 0.0], gloss="a feline",
                   params={"freq": 0.7})
    b = NeuralBlock.from_wordclass(wc)
    assert b.payload["word"] == "cat"
    assert b.payload["gloss"] == "a feline"
    assert b.payload["params"] == {"freq": 0.7}
    assert np.allclose(b.payload["source_vector"], [1.0, -2.0, 0.0])


def test_bare_block_has_empty_payload_and_composite_is_not_lexical():
    bare = NeuralBlock("b", [2.0], [1.0])
    assert bare.payload == {}
    a = NeuralBlock.from_wordclass(WordClass("a", [1.0]))
    composite = a.compose(NeuralBlock("id", [1.0], [0.0]))
    assert composite.payload == {}        # a composite is not a single word


def test_payload_is_not_part_of_the_morphism():
    # same affine map, different payloads -> equivalent as morphisms
    from patchi.category import equivalent
    p = NeuralBlock("p", [2.0, 3.0], [1.0, 0.0], payload={"word": "p"})
    q = NeuralBlock("q", [2.0, 3.0], [1.0, 0.0], payload={"word": "q"})
    assert equivalent(p, q)
    # and apply ignores payload
    assert np.allclose(p.apply([1.0, 1.0]), q.apply([1.0, 1.0]))


# -- Translator (bijective, on-demand) ---------------------------------------

def test_register_mints_block_and_is_idempotent():
    tr = Translator()
    wc = WordClass("dog", [0.5, 0.5])
    b1 = tr.register(wc)
    b2 = tr.register(wc)  # same word + vector -> same block, no error
    assert b1.label == "dog"
    assert np.allclose(b1.scale, b2.scale)
    assert len(tr) == 1


def test_to_block_grows_on_demand_open_vocabulary():
    tr = Translator()
    assert "new" not in tr
    blk = tr.to_block(WordClass("new", [1.0, 0.0]))
    assert "new" in tr and blk.label == "new"
    assert len(tr) == 1


def test_translate_back_recovers_wordclass():
    tr = Translator()
    wc = WordClass("king", [1.0, 2.0])
    blk = tr.register(wc)
    assert tr.to_wordclass(blk) is wc


def test_translate_back_unknown_block_raises():
    tr = Translator()
    stray = NeuralBlock("ghost", scale=[1.0], offset=[0.0])
    with pytest.raises(KeyError):
        tr.to_wordclass(stray)


def test_conflicting_reregistration_breaks_bijection_and_is_rejected():
    tr = Translator()
    tr.register(WordClass("bank", [1.0, 0.0]))
    with pytest.raises(ValueError):
        tr.register(WordClass("bank", [0.0, 1.0]))  # different vector, same word


def test_is_bijective_holds_across_many_registrations():
    tr = Translator()
    for i, w in enumerate(["a", "b", "c", "d"]):
        tr.register(WordClass(w, [float(i), 1.0]))
    assert tr.is_bijective()
    assert set(tr.words()) == {"a", "b", "c", "d"}
