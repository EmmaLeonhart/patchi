"""GD-R2 — a *learned* cosine+structural mixing weight.

GD-2/R1 combined cosine and WordNet structural similarity with a **flat**
rank-average (λ = 0.5). That lifts SimLex everywhere but *hurts* the one cell where
cosine already dominates (fastText × WordSim, −0.104): equal-weighting a weak
signal into a strong one drags it down. The fix is obvious — learn the weight:

    combined(λ) = (1 − λ)·rank(cosine) + λ·rank(adamic_adar),  λ ∈ [0, 1]

λ = 0 recovers pure cosine, so a learned λ can never do worse than cosine on the
*training* objective, and on held-out data it should (a) keep most of the SimLex
gain and (b) fold the fastText × WordSim loss back toward break-even by driving λ
small there.

The discipline that makes this a real result, not a fit: **λ is chosen on a train
split and every reported number is on a held-out test split.** Tuning λ on the
test set and reporting that would be the cheat this split exists to forbid. The
split is deterministic (even index = train, odd = test) so the run reproduces.

Run: python scripts/run_structural_weighted.py   (needs nltk WordNet + the cached
embeddings, exactly like run_structural.py).
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # to import run_structural

from patchi.benchmark import spearman  # noqa: E402
from run_structural import (  # noqa: E402
    CACHE, EMBEDDINGS, POOL,
    build_wordnet_graph, load_glove, load_simlex, load_wordsim, cos, ranks,
)
from patchi.structural import adamic_adar  # noqa: E402

LAMBDAS = [round(0.1 * i, 1) for i in range(11)]  # 0.0 .. 1.0


def combined(cos_r, aa_r, lam):
    return (1.0 - lam) * cos_r + lam * aa_r


def eval_split(cosv, aav, human):
    """Return (cosine, flat-0.5, best-lambda, best-lambda-value) Spearman on a split.

    Ranks are computed *within* this split so the rank-average is well defined for
    the split being scored.
    """
    cos_r, aa_r = ranks(cosv), ranks(aav)
    s_cos = spearman(cosv, human)
    s_flat = spearman(combined(cos_r, aa_r, 0.5), human)
    return cos_r, aa_r, s_cos, s_flat


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

            # deterministic interleaved split
            idx = np.arange(len(usable))
            tr, te = idx[idx % 2 == 0], idx[idx % 2 == 1]

            # learn lambda on TRAIN (maximise train Spearman), evaluate on TEST
            cos_r_tr, aa_r_tr = ranks(cosv[tr]), ranks(aav[tr])
            train_scores = {lam: spearman(combined(cos_r_tr, aa_r_tr, lam), human[tr])
                            for lam in LAMBDAS}
            best_lam = max(LAMBDAS, key=lambda L: train_scores[L])

            cos_r_te, aa_r_te = ranks(cosv[te]), ranks(aav[te])
            test_cos = spearman(cosv[te], human[te])
            test_flat = spearman(combined(cos_r_te, aa_r_te, 0.5), human[te])
            test_learned = spearman(combined(cos_r_te, aa_r_te, best_lam), human[te])

            rows.append({
                "embedding": emb_name, "dataset": ds_name,
                "n_total": len(usable), "n_train": len(tr), "n_test": len(te),
                "best_lambda_on_train": best_lam,
                "test_cosine": round(test_cos, 4),
                "test_flat_0.5": round(test_flat, 4),
                "test_learned": round(test_learned, 4),
                "learned_minus_cosine": round(test_learned - test_cos, 4),
                "learned_minus_flat": round(test_learned - test_flat, 4),
            })
        del words, M, gidx

    result = {
        "task": "learned cosine+structural mixing weight; lambda tuned on train, "
                "scored on held-out test",
        "lambda_grid": LAMBDAS, "split": "deterministic interleave (even=train, odd=test)",
        "rows": rows,
        "learned_ge_cosine_everywhere": all(
            r["learned_minus_cosine"] >= -1e-9 for r in rows),
        "learned_ge_flat_everywhere": all(
            r["learned_minus_flat"] >= -1e-9 for r in rows),
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "structural_weighted_benchmark.json").write_text(
        json.dumps(result, indent=2))

    print(f"\n{result['task']}")
    print("embedding     dataset      lam*   cosine  flat.5  learned  L-cos    L-flat")
    for r in rows:
        print(f"{r['embedding']:<13} {r['dataset']:<12} {r['best_lambda_on_train']:>3}  "
              f"{r['test_cosine']:+.3f} {r['test_flat_0.5']:+.3f} {r['test_learned']:+.3f}  "
              f"{r['learned_minus_cosine']:+.4f}  {r['learned_minus_flat']:+.4f}")
    print(f"\nlearned >= cosine everywhere (held-out)? {result['learned_ge_cosine_everywhere']}")
    print(f"learned >= flat-0.5 everywhere (held-out)? {result['learned_ge_flat_everywhere']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
