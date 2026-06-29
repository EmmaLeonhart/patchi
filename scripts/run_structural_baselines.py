"""GD-R6 — is the structural measure distinct from textbook WordNet similarity?

Result 7 shows Pygmalion's *shared-ancestor* adamic-adar carries similarity signal
complementary to cosine. The fair challenge: adamic-adar over hypernym-path
ancestors is itself a WordNet-graph similarity, and the field already has standard
ones — **Wu-Palmer** (depth of the lowest common subsumer) and **path** similarity
(inverse shortest path). Does Pygmalion's formulation differ from them, or merely
reproduce one? This script answers it with no new dependency: the measures ship
with the already-downloaded WordNet (`nltk.corpus.wordnet`).

For each pair we take the **max similarity over the two words' synset pairs** (the
usual convention), Spearman-correlate against the human scores on the *same*
head-to-head sets as Result 7, and tabulate Wu-Palmer / path / adamic-adar / cosine
side by side. Then the combine question: does `cosine + wup` (flat rank-average) do
as well as `cosine + adamic_adar` on SimLex?

Run: python scripts/run_structural_baselines.py  (needs nltk WordNet + cached
embeddings, like run_structural.py).
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from patchi.benchmark import spearman  # noqa: E402
from patchi.structural import adamic_adar  # noqa: E402
from run_structural import (  # noqa: E402
    CACHE, EMBEDDINGS, POOL,
    build_wordnet_graph, load_glove, load_simlex, load_wordsim, cos, ranks,
)


def wn_pair_sim(wn, a, b, kind):
    """Max similarity over synset pairs of a,b. kind ∈ {wup, path}. None if undefined."""
    sa, sb = wn.synsets(a), wn.synsets(b)
    best = None
    for x in sa:
        for y in sb:
            s = x.wup_similarity(y) if kind == "wup" else x.path_similarity(y)
            if s is not None and (best is None or s > best):
                best = s
    return best


def combined(cos_r, other_r, lam=0.5):
    return (1.0 - lam) * cos_r + lam * other_r


def bootstrap_delta(cosv, otherv, human, B=2000, seed=0):
    """95% CI + P(>0) for spearman(flat-0.5 combine of cosine+other) − spearman(cosine)."""
    rng = np.random.default_rng(seed)
    n = len(human)
    cos_r, oth_r = ranks(cosv), ranks(otherv)
    observed = spearman(combined(cos_r, oth_r), human) - spearman(cosv, human)
    deltas = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        c, o, h = cosv[idx], otherv[idx], human[idx]
        deltas[i] = spearman(combined(ranks(c), ranks(o)), h) - spearman(c, h)
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return {"observed_delta": round(float(observed), 4),
            "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "p_delta_gt_0": round(float(np.mean(deltas > 0)), 4),
            "significant": bool(lo > 0)}


def main() -> int:
    from nltk.corpus import wordnet as wn

    datasets = [("WordSim-353", load_wordsim(CACHE / "wordsim353.tsv")),
                ("SimLex-999", load_simlex(CACHE / "SimLex-999" / "SimLex-999.txt"))]
    vocab = sorted({w for _, ps in datasets for a, b, _ in ps for w in (a, b)})
    print(f"building WordNet shared-ancestor graph over {len(vocab)} words...")
    adj, signed, covered = build_wordnet_graph(vocab)
    print(f"  {len(covered)}/{len(vocab)} covered")

    rows = []
    for emb_name, emb_path in EMBEDDINGS:
        words, M = load_glove(emb_path, POOL)
        gidx = {w: i for i, w in enumerate(words)}
        for ds_name, pairs in datasets:
            # same head-to-head set as Result 7: both words in WordNet graph + embedding
            usable = [(a, b, s) for a, b, s in pairs
                      if a in adj and b in adj and a in gidx and b in gidx]
            human = np.array([s for _, _, s in usable])
            cosv = np.array([cos(M[gidx[a]], M[gidx[b]]) for a, b, _ in usable])
            aav = np.array([adamic_adar(adj, a, b) for a, b, _ in usable])
            # WordNet textbook measures; missing (None) -> 0.0 (no path found)
            wup = np.array([wn_pair_sim(wn, a, b, "wup") or 0.0 for a, b, _ in usable])
            pth = np.array([wn_pair_sim(wn, a, b, "path") or 0.0 for a, b, _ in usable])

            cos_r = ranks(cosv)
            row = {
                "embedding": emb_name, "dataset": ds_name, "n": len(usable),
                "spearman": {
                    "cosine": round(spearman(cosv, human), 4),
                    "adamic_adar": round(spearman(aav, human), 4),
                    "wu_palmer": round(spearman(wup, human), 4),
                    "path": round(spearman(pth, human), 4),
                },
                "combined_with_cosine": {
                    "cos+adamic": round(spearman(combined(cos_r, ranks(aav)), human), 4),
                    "cos+wup": round(spearman(combined(cos_r, ranks(wup)), human), 4),
                    "cos+path": round(spearman(combined(cos_r, ranks(pth)), human), 4),
                },
            }
            # significance of the best textbook combine (cos+path) vs cosine
            row["bootstrap_cos+path_minus_cos"] = bootstrap_delta(cosv, pth, human)
            rows.append(row)
        del words, M, gidx

    result = {
        "task": "structural (adamic-adar) vs textbook WordNet similarity "
                "(Wu-Palmer, path), alone and combined with cosine",
        "rows": rows,
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "structural_baselines_benchmark.json").write_text(
        json.dumps(result, indent=2))

    print(f"\n{result['task']}")
    print("                              -- alone --              -- combined w/ cosine --")
    print("embedding     dataset      n   cos   adamic  wup   path | c+adamic c+wup  c+path")
    for r in rows:
        s, c = r["spearman"], r["combined_with_cosine"]
        print(f"{r['embedding']:<13} {r['dataset']:<11} {r['n']:>4} "
              f"{s['cosine']:+.3f} {s['adamic_adar']:+.3f} {s['wu_palmer']:+.3f} "
              f"{s['path']:+.3f} | {c['cos+adamic']:+.3f}  {c['cos+wup']:+.3f} "
              f"{c['cos+path']:+.3f}")
    print("\nsignificance of cos+path vs cosine (paired bootstrap, B=2000):")
    for r in rows:
        b = r["bootstrap_cos+path_minus_cos"]
        print(f"  {r['embedding']:<13} {r['dataset']:<11} delta={b['observed_delta']:+.3f} "
              f"CI[{b['ci95'][0]:+.3f},{b['ci95'][1]:+.3f}] "
              f"P(>0)={b['p_delta_gt_0']:.3f} sig={b['significant']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
