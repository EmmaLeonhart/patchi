"""End-to-end demo — the Patchi vertical slice wired into one path.

Proves the modules compose, not just pass in isolation. One small semantic world
flows through: **lexicon → signed relation graph → similarity-weighted blend
(with Proof(walk)) → bijective translator to a neural block → spatial-gated memory
tick → infon/situation graded support (with Proof(walk))**. Returns a structured,
inspectable result; ``scripts/run.py --demo`` prints it.

Deterministic (a fixed offline fixture), so the integration test can assert on it.
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .blend import blend_word_explained
from .block import Translator
from .memory import Memory
from .relations import SignedRelationGraph
from .situation import Infon, Situation
from .wordclass import Lexicon

# A tiny world: sea animals + vehicles + two verbs, in clear clusters.
WORLD = {
    "fish": [1.0, 0.0, 0.0],
    "whale": [0.95, 0.05, 0.0],
    "dolphin": [0.9, 0.1, 0.0],
    "car": [0.0, 1.0, 0.0],
    "truck": [0.0, 0.95, 0.05],
    "swims": [0.8, 0.1, 0.0],
    "drives": [0.1, 0.9, 0.0],
}


def demo() -> Dict[str, Any]:
    lex = Lexicon.from_embeddings(WORLD)

    # 1. Signed relation graph — fish is reinforced by "whale" (+) and opposed by "car" (−)
    g = SignedRelationGraph(lex)
    g.add_synonym("fish", "whale")
    g.add_antonym("fish", "car")

    # 2. Reconstruct "dolphin" from its neighbourhood, with a Proof(walk)
    blended, blend_proof = blend_word_explained(lex, "dolphin", k=3,
                                                weighting="similarity", power=2.0)

    # 3. Bijective translator: dolphin's WordClass -> NeuralBlock, apply, and recover
    tr = Translator()
    block = tr.to_block(lex["dolphin"])
    routed = block.apply(blended)                      # the "circuit" step
    recovered = tr.to_wordclass(block)                 # inverse direction
    round_trip_ok = recovered.word == "dolphin"

    # 4. Spatial-gated memory: feed the blended vector through the block gate, one tick
    mem = Memory(dim=lex.dim, decay=0.5, gate=block)
    mem.step(blended)

    # 5. Situation: does context support "dolphin swims"? graded, with a Proof(walk)
    sit = Situation("sea", lexicon=lex)
    sit.assert_infon(Infon("swims", ("fish",), 1))
    sit.assert_infon(Infon("swims", ("whale",), 1))
    support, support_proof = sit.supports_explained(Infon("swims", ("dolphin",), 1))

    return {
        "lexicon_size": len(lex),
        "relations": {
            "net_effect_fish": g.net_effect("fish"),       # +1 and −1 -> 0
            "polarity_fish_whale": g.polarity_between("fish", "whale"),
        },
        "blend": {
            "word": "dolphin",
            "neighbours": blend_proof.contributors(),
            "routed_norm": round(float(np.linalg.norm(routed)), 4),
            "proof": blend_proof.explain(),
        },
        "translate": {"block": block.label, "round_trip_ok": round_trip_ok},
        "memory": {"artificial_time": mem.time, "gated": mem.spatial_gate is not None},
        "situation": {
            "query": "swims(dolphin)[+]",
            "support": round(float(support), 4),
            "rule": support_proof.steps[0].detail.get("rule"),
            "proof": support_proof.explain(),
        },
    }
