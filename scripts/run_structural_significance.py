"""GD-R4 — is the structural gain statistically real, or is it noise?

Result 7's headline rests on small Spearman gains (+0.03…+0.10) measured once. Two
weaknesses make it attackable, and this script closes both with cached data only
(no external dependency beyond the already-downloaded WordNet):

1. **Paired bootstrap CI.** Resample the usable pairs with replacement (B = 2000,
   seeded), recompute `spearman(combined_flat0.5) − spearman(cosine)` on each
   resample, and report the observed delta, its 95% percentile CI, and
   `P(delta > 0)`. A gain whose CI excludes 0 is significant; one whose CI straddles
   0 is reported as non-significant — flatly, not spun.

2. **5-fold cross-validation of the learned λ** (finer 0.05 grid) replacing the
   single even/odd split: per fold, learn λ on the other four folds and score the
   held-out fold; report mean ± std test Spearman (cosine vs learned). This removes
   the "single split / coarse grid" limitation.

Run: python scripts/run_structural_significance.py  (needs nltk WordNet + cached
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

B = 2000          # bootstrap resamples
K = 5             # CV folds
LAMBDAS = [round(0.05 * i, 2) for i in range(21)]  # 0.00 .. 1.00 by 0.05
SEED = 0


def combined(cos_r, aa_r, lam):
    return (1.0 - lam) * cos_r + lam * aa_r


def bootstrap_delta(cosv, aav, human, rng):
    """95% CI + P(>0) for spearman(flat-0.5 combine) − spearman(cosine), paired."""
    n = len(human)
    cos_r, aa_r = ranks(cosv), ranks(aav)
    observed = spearman(combined(cos_r, aa_r, 0.5), human) - spearman(cosv, human)
    deltas = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        c, a, h = cosv[idx], aav[idx], human[idx]
        cr, ar = ranks(c), ranks(a)
        deltas[i] = spearman(combined(cr, ar, 0.5), h) - spearman(c, h)
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return {
        "observed_delta": round(float(observed), 4),
        "ci95": [round(float(lo), 4), round(float(hi), 4)],
        "p_delta_gt_0": round(float(np.mean(deltas > 0)), 4),
        "significant": bool(lo > 0),
    }


def kfold_learned(cosv, aav, human, rng):
    """5-fold CV: learn λ on 4 folds, score held-out fold. Mean±std test Spearman."""
    n = len(human)
    perm = rng.permutation(n)
    folds = np.array_split(perm, K)
    cos_scores, learned_scores, lams = [], [], []
    for f in range(K):
        te = folds[f]
        tr = np.concatenate([folds[j] for j in range(K) if j != f])
        cr_tr, ar_tr = ranks(cosv[tr]), ranks(aav[tr])
        best = max(LAMBDAS, key=lambda L: spearman(combined(cr_tr, ar_tr, L), human[tr]))
        cr_te, ar_te = ranks(cosv[te]), ranks(aav[te])
        cos_scores.append(spearman(cosv[te], human[te]))
        learned_scores.append(spearman(combined(cr_te, ar_te, best), human[te]))
        lams.append(best)
    cs, ls = np.array(cos_scores), np.array(learned_scores)
    return {
        "cv_cosine_mean": round(float(cs.mean()), 4),
        "cv_cosine_std": round(float(cs.std()), 4),
        "cv_learned_mean": round(float(ls.mean()), 4),
        "cv_learned_std": round(float(ls.std()), 4),
        "cv_learned_minus_cosine": round(float((ls - cs).mean()), 4),
        "lambdas_per_fold": [round(x, 2) for x in lams],
    }


def main() -> int:
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
            usable = [(a, b, s) for a, b, s in pairs
                      if a in adj and b in adj and a in gidx and b in gidx]
            cosv = np.array([cos(M[gidx[a]], M[gidx[b]]) for a, b, _ in usable])
            aav = np.array([adamic_adar(adj, a, b) for a, b, _ in usable])
            human = np.array([s for _, _, s in usable])
            rng = np.random.default_rng(SEED)  # same seed per cell for reproducibility
            boot = bootstrap_delta(cosv, aav, human, rng)
            cv = kfold_learned(cosv, aav, human, rng)
            rows.append({"embedding": emb_name, "dataset": ds_name, "n": len(usable),
                         "bootstrap": boot, "cv": cv})
        del words, M, gidx

    result = {
        "task": "significance (paired bootstrap CI) + 5-fold CV of the structural gain",
        "B": B, "K": K, "lambda_grid_step": 0.05, "seed": SEED,
        "rows": rows,
        "simlex_gain_significant_all": all(
            r["bootstrap"]["significant"] for r in rows if r["dataset"] == "SimLex-999"),
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "structural_significance_benchmark.json").write_text(
        json.dumps(result, indent=2))

    print(f"\n{result['task']}  (B={B}, K={K})")
    print("embedding     dataset      n    flat_d  95%CI            P(>0)  sig | "
          "cv_cos  cv_learn  cv_d")
    for r in rows:
        b, c = r["bootstrap"], r["cv"]
        print(f"{r['embedding']:<13} {r['dataset']:<11} {r['n']:>4}  "
              f"{b['observed_delta']:+.3f}  [{b['ci95'][0]:+.3f},{b['ci95'][1]:+.3f}]  "
              f"{b['p_delta_gt_0']:.3f}  {str(b['significant']):<5}| "
              f"{c['cv_cosine_mean']:+.3f}  {c['cv_learned_mean']:+.3f}   "
              f"{c['cv_learned_minus_cosine']:+.3f}")
    print(f"\nSimLex gain significant (CI>0) on all embeddings? "
          f"{result['simlex_gain_significant_all']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
