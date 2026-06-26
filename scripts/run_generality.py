"""MVC-3b generality — does "reconstruction hurts on clean vectors" hold beyond
GloVe-50 x WordSim-353?

Runs the SAME operator (patchi.blend.blend_from_neighbors) across the product of
two embeddings {GloVe-50, GloVe-100} and two human-similarity datasets
{WordSim-353, SimLex-999}. SimLex-999 is a meaningfully harder test than
WordSim-353: it scores *similarity* (not mere relatedness). Local-only (needs the
cached embeddings/datasets in results/_cache/; see run_real.py docstring).

Run: python scripts/run_generality.py
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
POOL, K, POWER = 100_000, 10, 2.0

EMBEDDINGS = [("GloVe-50", CACHE / "glove50.gz"),
              ("GloVe-100", CACHE / "glove100.gz"),
              ("fastText-300", CACHE / "fasttext300.gz")]  # different architecture (subword)


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


def load_wordsim(path):
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        a, b, s = line.split("\t")[:3]
        pairs.append((a.lower(), b.lower(), float(s)))
    return pairs


def load_simlex(path):
    pairs, lines = [], path.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:  # skip header
        c = line.split("\t")
        pairs.append((c[0].lower(), c[1].lower(), float(c[3])))  # SimLex999 col
    return pairs


def evaluate(M, norm, idx, pairs, k, power):
    usable = [(a, b, s) for a, b, s in pairs if a in idx and b in idx]
    human = np.array([s for _, _, s in usable])
    qwords = sorted({w for a, b, _ in usable for w in (a, b)})
    qrows = np.array([idx[w] for w in qwords])
    S = norm[qrows] @ norm.T
    add, bl = {}, {}
    for r, w in enumerate(qwords):
        s = S[r].copy(); s[idx[w]] = -np.inf
        nn = np.argpartition(s, -k)[-k:]
        add[w] = blend_from_neighbors(M[nn], s[nn], weighting="uniform")
        bl[w] = blend_from_neighbors(M[nn], s[nn], weighting="similarity", power=power)

    def cos(u, v):
        return float(u @ v / ((np.linalg.norm(u) * np.linalg.norm(v)) + 1e-12))

    raw = np.array([cos(M[idx[a]], M[idx[b]]) for a, b, _ in usable])
    av = np.array([cos(add[a], add[b]) for a, b, _ in usable])
    bv = np.array([cos(bl[a], bl[b]) for a, b, _ in usable])
    return {
        "coverage": f"{len(usable)}/{len(pairs)}",
        "raw": round(spearman(raw, human), 4),
        "additive": round(spearman(av, human), 4),
        "blend": round(spearman(bv, human), 4),
        "blend_minus_raw": round(spearman(bv, human) - spearman(raw, human), 4),
    }


def main() -> int:
    datasets = [("WordSim-353", load_wordsim(CACHE / "wordsim353.tsv")),
                ("SimLex-999", load_simlex(CACHE / "SimLex-999" / "SimLex-999.txt"))]
    rows = []
    for emb_name, emb_path in EMBEDDINGS:
        words, M = load_glove(emb_path, POOL)
        idx = {w: i for i, w in enumerate(words)}
        norm = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
        for ds_name, pairs in datasets:
            res = evaluate(M, norm, idx, pairs, K, POWER)
            res.update({"embedding": emb_name, "dataset": ds_name})
            rows.append(res)

    result = {"task": "generality: {GloVe-50,GloVe-100} x {WordSim-353,SimLex-999}",
              "k": K, "power": POWER, "rows": rows,
              "blend_beats_raw_anywhere": any(r["blend_minus_raw"] > 0 for r in rows)}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "generality_benchmark.json").write_text(json.dumps(result, indent=2))

    print(result["task"])
    print("embedding   dataset       cover    raw     add    blend   blend-raw")
    for r in rows:
        print(f"{r['embedding']:<11} {r['dataset']:<12} {r['coverage']:>8}  "
              f"{r['raw']:.3f}  {r['additive']:.3f}  {r['blend']:.3f}  {r['blend_minus_raw']:+.4f}")
    print(f"blend beats raw anywhere? {result['blend_beats_raw_anywhere']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
