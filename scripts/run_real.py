"""MVC-3b — the REAL-embeddings benchmark (GloVe + WordSim-353).

Not run in CI (it needs a ~65MB embedding download), but absolutely runnable on
any machine with a network — which is the point. It scores the *same* blending
operator (`patchi.blend.blend_from_neighbors`) used in the synthetic benchmark,
now on pretrained GloVe vectors against the human WordSim-353 similarity
judgements. Raw vs additive (unweighted neighbour mean) vs blend (similarity-
weighted), Spearman against the human scores.

Download once (gitignored cache):
  curl -sL -o results/_cache/glove50.gz \
    https://github.com/RaRe-Technologies/gensim-data/releases/download/glove-wiki-gigaword-50/glove-wiki-gigaword-50.gz
  curl -sL -o results/_cache/wordsim353.tsv \
    https://raw.githubusercontent.com/RaRe-Technologies/gensim/develop/gensim/test/test_data/wordsim353.tsv

Then: python scripts/run_real.py
"""

import gzip
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from patchi.blend import blend_from_neighbors  # noqa: E402
from patchi.benchmark import spearman  # noqa: E402

CACHE = ROOT / "results" / "_cache"
GLOVE = CACHE / "glove50.gz"
WORDSIM = CACHE / "wordsim353.tsv"

POOL = 100_000   # neighbour-search vocabulary (GloVe is frequency-ordered)
K = 10
POWER = 2.0


def load_glove(path: Path, limit: int):
    words, vecs = [], []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        first = f.readline().split()
        # word2vec-style header "<vocab> <dim>"? if so it's already consumed.
        if len(first) != 2:
            words.append(first[0]); vecs.append([float(x) for x in first[1:]])
        for i, line in enumerate(f):
            if len(words) >= limit:
                break
            parts = line.rstrip().split(" ")
            words.append(parts[0]); vecs.append([float(x) for x in parts[1:]])
    M = np.asarray(vecs, dtype=float)
    return words, M


def load_wordsim(path: Path):
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        a, b, score = line.split("\t")[:3]
        pairs.append((a.lower(), b.lower(), float(score)))
    return pairs


def main() -> int:
    if not GLOVE.exists() or not WORDSIM.exists():
        print("missing cache files; see this script's docstring for the curl commands")
        return 1

    words, M = load_glove(GLOVE, POOL)
    idx = {w: i for i, w in enumerate(words)}
    norm = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    pairs = load_wordsim(WORDSIM)

    usable = [(a, b, s) for a, b, s in pairs if a in idx and b in idx]
    coverage = f"{len(usable)}/{len(pairs)} pairs (both words in top-{POOL})"

    # reconstruct every unique wordsim word from its top-K neighbours in the pool
    qwords = sorted({w for a, b, _ in usable for w in (a, b)})
    qrows = np.array([idx[w] for w in qwords])
    sims_all = norm[qrows] @ norm.T               # (Q, POOL) cosine
    recon_add, recon_blend = {}, {}
    for r, w in enumerate(qwords):
        s = sims_all[r].copy()
        s[idx[w]] = -np.inf                       # exclude self
        nn = np.argpartition(s, -K)[-K:]
        nvecs, nsims = M[nn], s[nn]
        recon_add[w] = blend_from_neighbors(nvecs, nsims, weighting="uniform")
        recon_blend[w] = blend_from_neighbors(nvecs, nsims, weighting="similarity", power=POWER)

    def cos(u, v):
        return float(u @ v / ((np.linalg.norm(u) * np.linalg.norm(v)) + 1e-12))

    human = np.array([s for _, _, s in usable])
    raw = np.array([cos(M[idx[a]], M[idx[b]]) for a, b, _ in usable])
    add = np.array([cos(recon_add[a], recon_add[b]) for a, b, _ in usable])
    bln = np.array([cos(recon_blend[a], recon_blend[b]) for a, b, _ in usable])

    scores = {"raw": spearman(raw, human),
              "additive": spearman(add, human),
              "blend": spearman(bln, human)}
    result = {
        "task": "REAL embeddings: GloVe-50 (top %d) vs WordSim-353" % POOL,
        "coverage": coverage, "k": K, "power": POWER,
        "metric": "spearman(method pair-similarity, human judgement)",
        "scores": scores,
        "delta_blend_minus_additive": scores["blend"] - scores["additive"],
        "delta_blend_minus_raw": scores["blend"] - scores["raw"],
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "real_benchmark.json").write_text(json.dumps(result, indent=2))

    print(result["task"]); print(coverage)
    print(f"  raw      : {scores['raw']:.4f}")
    print(f"  additive : {scores['additive']:.4f}")
    print(f"  blend    : {scores['blend']:.4f}")
    print(f"  blend - additive : {result['delta_blend_minus_additive']:+.4f}")
    print(f"  blend - raw      : {result['delta_blend_minus_raw']:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
