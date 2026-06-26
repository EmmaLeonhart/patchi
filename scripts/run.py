"""Patchi entry point — runs the current headline experiment.

Right now that is the MVC-3 benchmark: similarity-weighted blending vs an
additive baseline vs raw vectors on a controlled synthetic denoising task. It
writes the measured scores to ``results/benchmark.json`` and prints a summary.
The task is synthetic (not real embeddings) — see ``FINDINGS.md`` for scope.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import patchi  # noqa: E402
from patchi.benchmark import run_benchmark, run_sweep  # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"


def main() -> int:
    print(f"Patchi v{patchi.__version__}")

    if "--demo" in sys.argv:
        from patchi.demo import demo
        r = demo()
        print("end-to-end demo (lexicon -> relations -> blend -> block -> memory -> situation):")
        print(f"  relations: net_effect(fish)={r['relations']['net_effect_fish']}")
        print(f"  blend('dolphin') neighbours: {r['blend']['neighbours']}")
        print(f"  translate -> block '{r['translate']['block']}', round-trip {r['translate']['round_trip_ok']}")
        print(f"  memory: artificial_time={r['memory']['artificial_time']}, gated={r['memory']['gated']}")
        print(f"  situation: support(swims|dolphin)={r['situation']['support']} (rule={r['situation']['rule']})")
        print("  -- blend Proof(walk) --")
        print(r["blend"]["proof"])
        print("  -- support Proof(walk) --")
        print(r["situation"]["proof"])
        return 0

    headline = run_benchmark()
    sweep = run_sweep()
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "benchmark.json").write_text(
        json.dumps({"headline": headline, "sweep": sweep}, indent=2)
    )

    s = headline["scores"]
    print(f"task: {headline['task']}")
    print(f"metric: {headline['metric']}")
    print(f"headline (noise={headline['params']['noise']}, power={headline['params']['power']}):")
    print(f"  raw {s['raw']:.4f} | additive {s['additive']:.4f} | blend {s['blend']:.4f}"
          f" | blend-additive {headline['delta_blend_minus_additive']:+.4f}")
    print("sweep (noise | power | raw | additive | blend | blend-additive):")
    for r in sweep:
        print(f"  {r['noise']:.1f} | {r['power']:.1f} | {r['raw']:.3f} | {r['additive']:.4f}"
              f" | {r['blend']:.4f} | {r['blend_minus_additive']:+.4f}")
    print("wrote results/benchmark.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
