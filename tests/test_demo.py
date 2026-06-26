"""Integration test — the whole vertical slice composes and yields a Proof(walk).

This is the consolidation test: it doesn't re-check each module's internals (the
unit tests do that), it checks they actually fit together end to end.
"""

from patchi.demo import WORLD, demo


def test_demo_composes_end_to_end():
    r = demo()

    # lexicon
    assert r["lexicon_size"] == len(WORLD)

    # signed relation graph: fish has +1 (whale) and −1 (car) -> net 0
    assert r["relations"]["net_effect_fish"] == 0
    assert r["relations"]["polarity_fish_whale"] == 1

    # blend reconstructed dolphin from 3 neighbours, itself excluded, all real words
    nb = r["blend"]["neighbours"]
    assert len(nb) == 3
    assert "dolphin" not in nb
    assert set(nb) <= set(WORLD)

    # bijective translator round-trips WordClass <-> block
    assert r["translate"]["block"] == "dolphin"
    assert r["translate"]["round_trip_ok"] is True

    # spatial-gated memory advanced one tick of artificial time
    assert r["memory"]["artificial_time"] == 1
    assert r["memory"]["gated"] is True

    # situation gives graded support in [0,1], via the vector rule, and it's high
    assert 0.0 <= r["situation"]["support"] <= 1.0
    assert r["situation"]["support"] > 0.5      # dolphin swims, given fish/whale swim
    assert r["situation"]["rule"] == "vector"


def test_demo_produces_proof_walks():
    r = demo()
    # the framework's promise: every output carries a Proof(walk)
    assert "blend:" in r["blend"]["proof"]
    assert "support:" in r["situation"]["proof"]
    # the blend proof lists its contributing neighbours by name
    assert any(w in r["blend"]["proof"] for w in WORLD)
