# PATCHi — Findings

> **Status: first measured result (synthetic).** This reports the MVC-3 benchmark
> of Pygmalion's similarity-weighted blending operator. The task is a *controlled
> synthetic denoising* benchmark, **not** real embeddings — scope is stated plainly
> below. Reproduce with `python scripts/run.py` (writes `results/benchmark.json`).

## Question

Pygmalion's distinctive composition primitive is similarity-weighted blending —
a word's representation rebuilt from its similar words, each weighted by
similarity: `blend(w) = ( Σ sim(w,sᵢ)^p · vec(sᵢ) ) / Σ sim(w,sᵢ)^p`. **Does the
similarity weighting actually buy anything over a plain (unweighted) average of
the same neighbours?** That is the operator's whole claim, so it is the thing to
test.

## Method

A controlled synthetic task with a known ground truth. Build `n` clean prototype
vectors; each word is a prototype + Gaussian noise (strength `noise`).
Ground-truth similarity of two words = cosine of their *clean* prototypes (what
the noise hides). Three working representations per word:

- **raw** — the noisy vector (no reconstruction);
- **additive** — unweighted mean of the word's `k` nearest neighbours (the
  control: isolates exactly what the weighting adds);
- **blend** — similarity-weighted mean of the `k` nearest neighbours (power `p`).

Score = Spearman rank correlation between a method's pairwise cosines and the
ground-truth pairwise cosines (higher = recovers the hidden structure better).
Implementation: `src/patchi/{blend,benchmark}.py`; Spearman is numpy-only.

## Results (measured, seed 0)

Headline config (noise 0.6, power 2.0, k 5, 8×6 words, dim 24):

| method   | Spearman vs ground truth |
|----------|--------------------------|
| raw      | 0.7916 |
| additive | 0.9299 |
| **blend**| **0.9334** |

Sweep over noise × weighting sharpness (k = 8), `Δ = blend − additive`:

| noise | power | raw | additive | blend | Δ (blend − additive) |
|------:|------:|----:|---------:|------:|---------------------:|
| 0.4 | 1.0 | 0.892 | 0.829 | 0.924 | **+0.095** |
| 0.4 | 4.0 | 0.892 | 0.829 | 0.972 | **+0.143** |
| 0.8 | 1.0 | 0.689 | 0.751 | 0.811 | +0.060 |
| 0.8 | 4.0 | 0.689 | 0.751 | 0.866 | +0.115 |
| 1.2 | 1.0 | 0.508 | 0.585 | 0.613 | +0.028 |
| 1.2 | 4.0 | 0.508 | 0.585 | 0.625 | +0.040 |
| 1.6 | 1.0 | 0.363 | 0.352 | 0.368 | +0.016 |
| 1.6 | 4.0 | 0.363 | 0.352 | 0.349 | −0.003 |
| 2.0 | 1.0 | 0.257 | 0.211 | 0.215 | +0.004 |
| 2.0 | 4.0 | 0.257 | 0.211 | 0.200 | −0.010 |

## What this shows — and what it doesn't

- **Reconstruction denoises** strongly versus raw vectors whenever the
  neighbourhood carries signal (low–moderate noise): blend beats raw by up to
  +0.14 Spearman.
- **The similarity weighting earns its keep mainly when the neighbourhood is
  trustworthy.** At low noise with sharp weighting (power 4) it adds +0.10 to
  +0.14 over a flat additive average — a real, repeatable margin (locked in by a
  regression test).
- **The advantage decays with noise, and over-sharpening can backfire.** By
  noise 1.6–2.0 the weighting adds almost nothing, and aggressive weighting goes
  slightly *negative* — it over-trusts unreliable similarities. At the highest
  noise, raw vectors even beat both reconstructions.
- **At the middling default (noise 0.6, power 2) the weighting barely beats
  additive (+0.0035).** Stated plainly: the operator's value is *regime-dependent*,
  not universal — it is a trustworthy-neighbourhood denoiser, not a free win.

## Limitations (named, not buried)

- **Synthetic data, not real embeddings.** This tests operator behaviour under
  controlled noise; it is not a claim about WordSim-353/SimLex or real corpora.
- **1-argument operator.** Blending reconstructs *one* word from its
  neighbourhood; it is not a two-word binding/composition, so no tensor/DisCoCat
  baseline is included here (that is a different operation — todo BR-2).
- **Single noise model** (isotropic Gaussian) and one random seed for the
  headline; the sweep uses a fixed seed per noise level.

## Next step

The real-embeddings run: load pretrained vectors (e.g. GloVe), score on a human
word-similarity dataset (WordSim-353 / SimLex-999), repeat raw vs additive vs
blend. Queued; it needs downloads unavailable in the offline CI/loop environment,
so it is named as a blocker rather than faked here.
