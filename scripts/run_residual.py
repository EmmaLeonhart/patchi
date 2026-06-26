"""MVC-3b follow-up — residual blending sweep on GloVe × WordSim-353.

Tests whether a *little* smoothing beats raw on clean embeddings. For each word,
form `(1-α)·own + α·blend` and score Spearman vs the human WordSim-353 judgements
across α ∈ {0.0 … 1.0}. α=0 is the raw baseline; if any α>0 beats it, "a little
smoothing helps"; if the curve is monotone decreasing, reconstruction only ever
hurts on clean vectors. Uses the cached GloVe (see run_real.py docstring).

Run: python scripts/run_residual.py
"""

import gzip
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from patchi.blend import blend_from_neighbors, residual_blend  # noqa: E402
from patchi.benchmark import spearman  # noqa: E402

CACHE = ROOT / "results" / "_cache"
POOL, K, POWER = 100_000, 10, 2.0
ALPHAS = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0]


def load_glove(path, limit):
    words, vecs = [], []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        first = f.readline().split()
        if len(first) != 2:
            words.append(first[0]); vecs.append([float(x) for x in first[1:]])
        for line in f:
            if len(words) >= limit:
                break
            p = line.rstrip().split(" ")
            words.append(p[0]); vecs.append([float(x) for x in p[1:]])
    return words, np.asarray(vecs, dtype=float)


def main() -> int:
    words, M = load_glove(CACHE / "glove50.gz", POOL)
    idx = {w: i for i, w in enumerate(words)}
    norm = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    pairs = []
    for line in (CACHE / "wordsim353.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        a, b, s = line.split("\t")[:3]
        pairs.append((a.lower(), b.lower(), float(s)))
    usable = [(a, b, s) for a, b, s in pairs if a in idx and b in idx]
    human = np.array([s for _, _, s in usable])

    qwords = sorted({w for a, b, _ in usable for w in (a, b)})
    qrows = np.array([idx[w] for w in qwords])
    S = norm[qrows] @ norm.T
    own, blend = {}, {}
    for r, w in enumerate(qwords):
        s = S[r].copy(); s[idx[w]] = -np.inf
        nn = np.argpartition(s, -K)[-K:]
        own[w] = M[idx[w]]
        blend[w] = blend_from_neighbors(M[nn], s[nn], weighting="similarity", power=POWER)

    def cos(u, v):
        return float(u @ v / ((np.linalg.norm(u) * np.linalg.norm(v)) + 1e-12))

    curve = []
    for a in ALPHAS:
        rep = {w: residual_blend(own[w], blend[w], a) for w in qwords}
        sc = spearman(np.array([cos(rep[x], rep[y]) for x, y, _ in usable]), human)
        curve.append({"alpha": a, "spearman": round(sc, 4)})

    raw = curve[0]["spearman"]
    best = max(curve, key=lambda c: c["spearman"])
    result = {"task": "residual (1-a)*own + a*blend on GloVe-50 x WordSim-353",
              "k": K, "power": POWER, "curve": curve,
              "raw_alpha0": raw, "best": best,
              "a_little_smoothing_helps": best["alpha"] > 0.0 and best["spearman"] > raw}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "residual_benchmark.json").write_text(json.dumps(result, indent=2))

    print(result["task"])
    for c in curve:
        mark = "  <- best" if c is best else ""
        print(f"  alpha={c['alpha']:.2f} : {c['spearman']:.4f}{mark}")
    print(f"a little smoothing beats raw? {result['a_little_smoothing_helps']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
