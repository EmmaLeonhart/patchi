# Patchi — Findings

> **Status: first measured results — synthetic AND real.** The MVC-3 benchmark of
> Pygmalion's similarity-weighted blending operator now has both a controlled
> synthetic run and a **real-embeddings run (GloVe-50 × WordSim-353)**. The two
> point in *opposite* directions, and that contrast is the finding. Reproduce:
> `python scripts/run.py` (synthetic) and `python scripts/run_real.py` (real;
> needs a one-time ~65 MB GloVe download — see that script's docstring).

## Question

Pygmalion's distinctive composition primitive is similarity-weighted blending — a
word's representation rebuilt from its similar words, each weighted by similarity:
`blend(w) = ( Σ sim(w,sᵢ)^p · vec(sᵢ) ) / Σ sim(w,sᵢ)^p`. **Does the similarity
weighting buy anything over a plain (unweighted) average of the same neighbours,
and does reconstructing a word from its neighbourhood help at all?**

## Method

Two benchmarks, same operator code (`patchi.blend.blend_from_neighbors`), three
representations per word: **raw** (the vector itself), **additive** (unweighted
mean of the `k` nearest neighbours, the control), **blend** (similarity-weighted
mean, power `p`).

- **Synthetic** (`benchmark.py`): clustered prototype vectors + Gaussian noise;
  ground truth = cosine of the *clean* prototypes. Score = Spearman(method
  pairwise cosine, ground-truth cosine).
- **Real** (`run_real.py`): GloVe-50 (top 100k words) vs the **WordSim-353** human
  similarity judgements; all 353 pairs covered. Score = Spearman(method pair
  similarity, human score).

## Result 1 — real embeddings (the one that matters most)

GloVe-50 × WordSim-353, 353/353 pairs. Raw GloVe Spearman **0.5033** (matches the
known literature value for GloVe-50 — a sanity check that the harness is right).

| k | power | additive | blend | blend − raw |
|--:|------:|---------:|------:|------------:|
| 3 | 1 | 0.4420 | 0.4440 | −0.0594 |
| 3 | 6 | 0.4420 | 0.4470 | −0.0564 |
| 5 | 2 | 0.4309 | 0.4336 | −0.0697 |
| 10 | 2 | 0.4318 | 0.4347 | −0.0686 |
| 10 | 6 | 0.4318 | 0.4391 | −0.0642 |
| 25 | 2 | 0.4228 | 0.4256 | −0.0777 |

**On clean pretrained embeddings, reconstructing a word from its neighbourhood
*hurts*** — every additive and blend configuration lands 0.06–0.08 Spearman
*below* raw GloVe (best blend 0.447 vs raw 0.503). The similarity weighting does
reliably beat the unweighted additive average, but by a hair (+0.001 to +0.009),
nowhere near enough to recover what reconstruction throws away. Fewer neighbours
(k=3) and sharper weighting help only by reconstructing *less*, i.e. by staying
closer to raw.

## Result 2 — synthetic (controlled noise)

Headline (noise 0.6, power 2, k 5): raw 0.7916 · additive 0.9299 · **blend
0.9334**. Sweep over noise × sharpness, `Δ = blend − additive`:

| noise | power | raw | additive | blend | Δ |
|------:|------:|----:|---------:|------:|---:|
| 0.4 | 4.0 | 0.892 | 0.829 | **0.972** | +0.143 |
| 0.8 | 4.0 | 0.689 | 0.751 | 0.866 | +0.115 |
| 1.2 | 4.0 | 0.508 | 0.585 | 0.625 | +0.040 |
| 1.6 | 4.0 | 0.363 | 0.352 | 0.349 | −0.003 |
| 2.0 | 4.0 | 0.257 | 0.211 | 0.200 | −0.010 |

Here, when vectors are **noisy**, reconstruction *denoises*: blend beats raw by up
to +0.14, and the weighting beats additive by +0.10–0.14 — until noise gets so
high the neighbourhood itself is unreliable and the gain vanishes / goes negative.

## What this shows — the regime, stated straight

- **The blending operator's value is entirely conditional on input noise.** It is
  a *denoiser*: it helps exactly when the base vectors are noisy enough that
  averaging over trustworthy neighbours recovers signal (synthetic, low–moderate
  noise). On already-clean, well-tuned vectors (GloVe), the same operation
  destroys discriminative information and **loses to doing nothing**.
- **The similarity weighting — the operator's distinctive ingredient — is real but
  small.** It beats a flat additive average consistently, in both regimes, but
  only by +0.001 to +0.14 depending on how much signal there is to concentrate on.
  It is never the difference between winning and losing; the *decision to
  reconstruct at all* dominates.
- **Net:** Pygmalion's blending is not a free improvement over standard
  embeddings. It is a noise-conditional smoother. That is a genuine, narrow result
  — and the opposite of what the synthetic run alone would have suggested, which
  is exactly why the real run was worth running rather than declaring "blocked".

## Result 3 — residual blending (does a *little* smoothing help?)

The natural rescue for the negative real result: maybe full reconstruction is too
aggressive, and a residual nudge `(1-α)·own + α·blend` keeps raw's signal while
denoising a little. We swept α on GloVe-50 × WordSim-353 (`run_residual.py`):

| α | 0.00 | 0.05 | 0.10 | 0.20 | 0.30 | 0.50 | 0.75 | 1.00 |
|--:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| Spearman | **0.5033** | 0.5033 | 0.5026 | 0.4986 | 0.4943 | 0.4818 | 0.4623 | 0.4347 |

**The best α is 0** (raw). A vanishing nudge (α=0.05) merely ties raw to four
decimals; any meaningful smoothing is monotonically worse. So there is no
"sweet spot" — on clean embeddings, smoothing toward the neighbourhood only ever
hurts (or, in the limit, does nothing). This closes the rescue hypothesis: the
negative real result is not an artifact of over-aggressive reconstruction.

## Result 4 — regions vs. binding (BR-2 probe): they don't cohere for free

Pygmalion's framework wants Gärdenfors **convex regions** and VSA **binding**
(elementwise product) on the same objects. We probed whether a region stays
**closed under binding** (if `a, b ∈ R`, is `a ⊙ b ∈ R`?). Measured facts
(`regions.py`, tested):

- **Binding by a fixed key preserves convexity** — it is a linear (diagonal) map,
  so it commutes with convex combination and sends a convex region to a convex
  region. ✓
- **An origin-centred unit ball is closed under binding** — there, elementwise
  products shrink toward 0, so they stay inside. ✓
- **A region placed away from the origin is NOT closed.** Concretely, `a = [1.2,
  1.0]` is in the ball centred at `[1,1]` with radius `0.3`, but `a ⊙ a = [1.44,
  1.0]` escapes it. ✗

**Conclusion:** the unification does *not* hold for free. Closure under binding
depends on where the region sits relative to the binding algebra's fixed points
(coordinates 0 and ±1) — but Gärdenfors regions are placed by *semantics*, not by
that algebra, so a generic semantic region is not closed under binding. A faithful
implementation must either restrict binding (e.g. to fixed-key/linear bindings,
which do preserve convexity) or recompute the region after binding. This is a
negative structural result, exactly what the probe was for.

## Limitations (named, not buried)

- One embedding model (GloVe-50) and one dataset (WordSim-353). SimLex-999, larger
  GloVe dims, and word2vec/fastText would strengthen or qualify this.
- `run_real.py` / `run_residual.py` are local scripts (they need the GloVe
  download); they are **not** part of CI. The operators they exercise
  (`blend_from_neighbors`, `residual_blend`) and Spearman are unit-tested; the
  scripts' glue (parsing / neighbour search) is not CI-covered.

## Next steps

- A second dataset (SimLex-999) and a second embedding (word2vec) to test whether
  the "reconstruction hurts on clean vectors" result generalises beyond GloVe-50.
