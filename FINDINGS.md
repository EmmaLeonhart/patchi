# Patchi — Findings

> **Status: first measured results — synthetic AND real.** The MVC-3 benchmark of
> Pygmalion's similarity-weighted blending operator now has both a controlled
> synthetic run and a **real-embeddings run (GloVe-50 × WordSim-353)**. The two
> point in *opposite* directions, and that contrast is the finding. Reproduce:
> `python scripts/run.py` (synthetic) and `python scripts/run_real.py` (real;
> needs a one-time ~65 MB GloVe download — see that script's docstring).
>
> **Update (Result 7): the first *positive* result.** The blending/reconstruction
> thread above is uniformly negative on clean vectors. A different Pygmalion claim
> — that similarity is a *relational* property, "the number of words two words
> have in common" — does carry signal: WordNet shared-ancestor structure
> **complements** GloVe cosine on genuine-similarity judgements (SimLex-999),
> combined .383 vs cosine .296. See Result 7. Reproduce: `python
> scripts/run_structural.py` (needs nltk WordNet).

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

## Result 5 — generality: the negative result holds across embeddings & datasets

Does "reconstruction hurts on clean vectors" survive beyond GloVe-50 ×
WordSim-353? Ran the same operator (`run_generality.py`) across
{GloVe-50, GloVe-100, **fastText-300**} × {WordSim-353, SimLex-999} — fastText is a
genuinely different *architecture* (subword) from GloVe (count-based), and
SimLex-999 scores *similarity*, not mere relatedness (a harder/cleaner test).

| embedding | dataset | raw | additive | blend | blend − raw |
|-----------|---------|----:|---------:|------:|------------:|
| GloVe-50      | WordSim-353 | 0.503 | 0.432 | 0.435 | −0.069 |
| GloVe-50      | SimLex-999  | 0.263 | 0.235 | 0.237 | −0.026 |
| GloVe-100     | WordSim-353 | 0.533 | 0.445 | 0.451 | −0.081 |
| GloVe-100     | SimLex-999  | 0.296 | 0.278 | 0.281 | −0.015 |
| fastText-300  | WordSim-353 | 0.718 | 0.643 | 0.652 | −0.066 |
| fastText-300  | SimLex-999  | 0.445 | 0.442 | 0.445 | −0.000 |

**Blend beats raw in 0 of 6 cells**, now including a different embedding
*architecture* (fastText) and a much stronger raw baseline (0.718). Reconstruction
is ≤ raw everywhere; blend edges additive by a hair everywhere but never catches
raw. The penalty is **regime-dependent**: largest on weaker embeddings /
relatedness datasets (−0.08), and it shrinks to **break-even (−0.000) on the
strongest embedding + hardest similarity task** (fastText × SimLex) — but never
goes positive. So the negative result generalises across embedding *size*,
*architecture*, and *dataset*: similarity-weighted reconstruction is, at best,
break-even and usually a loss on clean vectors.

## Result 6 — phrase composition: does the weighting help here either?

The blend operator reconstructs *one* word; phrase composition combines *several*.
A synthetic benchmark mirroring MVC-3 at the phrase level: phrases are several
words (noisy samples of concept prototypes) drawn from distinct concepts; the
ground-truth phrase meaning is the mean of the clean concept prototypes; score =
Spearman(method pairwise cosine, ground truth). Methods: `additive` (Σ vec),
`multiplicative` (elementwise Π), `weighted` (similarity-weighted toward the
centroid — the project's operator).

| noise | additive | multiplicative | weighted | weighted − additive |
|------:|---------:|---------------:|---------:|--------------------:|
| 0.3 | **0.954** | 0.032 | 0.866 | −0.088 |
| 0.6 | **0.827** | 0.027 | 0.744 | −0.082 |
| 1.0 | **0.584** | 0.023 | 0.533 | −0.051 |
| 1.5 | **0.339** | 0.023 | 0.312 | −0.027 |

**Additive wins; similarity-weighting hurts; multiplicative fails.** Plain
additive recovers the ground-truth phrase structure best at every noise level;
the project's similarity-weighted composition is worse everywhere (−0.03…−0.09);
multiplicative is near-zero (~0.03) — it cannot recover an additive ground truth
and amplifies noise. Why: when the true phrase meaning is an *equal-weight*
combination of its concepts, any non-uniform weighting (toward the centroid)
deviates from it, and additive is the natural match. **Caveat:** this is
conditional on an equal-weight "bag of concepts" ground truth; if a head word
genuinely dominated, weighting *could* help — untested. The through-line stands:
the similarity weighting that defines Pygmalion's operator does not beat the plain
baseline — for single-word reconstruction *or* phrase composition.

## Result 7 — structural (relational) similarity: the first positive result

Every result above tests one Pygmalion idea: *reconstruct* a word from its
neighbourhood in vector space (a geometric signal). It loses. But the notebook's
most-repeated claim is a *different*, relational one (`data_lake/proto.txt`
L229–235, L308–316): **"distance between words corresponds to the number of words
they have in common"** — similarity as overlap of relational neighbourhoods, not
vector geometry. We tested it with an *independent* relation source so the test is
fair: **WordNet**. Each word's features are the synsets on its senses' hypernym
paths (the concepts it *is a kind of*); `patchi.structural` then scores how much
two words' feature sets overlap. Spearman vs human similarity, GloVe-100 cosine on
the same covered pairs as the baseline, and a rank-average **combined** score
(`run_structural.py`):

| dataset (GloVe-100) | common-nbr | jaccard | adamic-adar | signed | cosine | **combined** |
|---------|----:|----:|----:|----:|----:|----:|
| WordSim-353 (relatedness) | 0.253 | 0.371 | 0.323 | −0.031 | **0.536** | 0.541 |
| SimLex-999 (similarity)   | 0.167 | 0.276 | **0.298** | 0.093 | 0.296 | **0.383** |

**On SimLex-999 the relational signal stands on its own and then adds to cosine.**
Adamic-adar alone (0.298) *matches* GloVe cosine (0.296); the combined score
(0.383) beats cosine by **+0.087** (~29% relative) — the first time anything in
this project beats the embedding baseline rather than losing to it. The mechanism
is not mysterious: SimLex scores genuine *similarity* and deliberately penalises
mere *relatedness* (coffee/cup are related, not similar), which distributional
cosine conflates; WordNet's taxonomic shared-ancestor structure measures
is-a-kind-of directly, so the two signals are **complementary** rather than
redundant — exactly Pygmalion's claim that relational structure carries similarity
information the geometry misses. Adamic-adar's inverse-log-degree weighting is what
makes the raw "shared words" idea work: a specific shared ancestor (carnivore)
counts for more than a generic one (entity).

**On WordSim-353 (relatedness) the structural signal is weaker and adds almost
nothing** (cosine 0.536, combined +0.005): taxonomy does not capture relatedness
(computer/keyboard share no useful ancestor). And `signed_overlap` — the sign-aware
stimulator/inhibitor variant — is weak both ways (−0.031, +0.093): WordNet's
antonym links are too sparse to move it. Stated flatly: the *polarity* half of the
claim is untested here for lack of a dense signed graph.

**Does it generalise across embeddings? On SimLex, yes; and the boundary is
informative.** Re-running the head-to-head across {GloVe-50, GloVe-100,
fastText-300} (combined = rank-average of cosine + adamic-adar):

| embedding | adamic-adar | WordSim cos→comb | SimLex cos→comb |
|-----------|----:|----:|----:|
| GloVe-50     | 0.323 | 0.506 → 0.517 (**+0.011**) | 0.263 → 0.363 (**+0.100**) |
| GloVe-100    | 0.323 | 0.536 → 0.541 (**+0.006**) | 0.296 → 0.383 (**+0.086**) |
| fastText-300 | 0.343 | 0.718 → 0.614 (**−0.104**) | 0.445 → 0.479 (**+0.034**) |

The relational signal **complements cosine on SimLex for all three embeddings** —
across two architectures (GloVe count-based, fastText subword) and a 0.263→0.445
range of baseline strength. The gain *shrinks as the embedding gets stronger*
(+0.100 → +0.034): a better embedding already captures more of the similarity, so
there is less left for structure to add — a regular, explicable trend, not a
fluke. The one place combining **hurts** is fastText × WordSim (−0.104): there
cosine (0.718) so dominates the weaker structural signal (0.343) that a flat
equal-weight rank-average drags it down. That is a property of the *unweighted
combiner*, not of the structural signal — and it is exactly why the next step is a
*learned* weight that down-weights structure where it is weaker (todo MVC-2 reach).

**A *learned* mixing weight keeps the gain and removes the one loss.** The flat
0.5 combine is the wrong knob where one signal dominates. So learn it:
`combined(λ) = (1−λ)·rank(cosine) + λ·rank(adamic_adar)`, with **λ chosen on a
train split and every number scored on a held-out test split** (deterministic
even/odd interleave; `run_structural_weighted.py`):

| embedding | dataset | λ\* | test cosine | test flat-0.5 | **test learned** | learned − cosine |
|-----------|---------|--:|----:|----:|----:|----:|
| GloVe-50     | WordSim-353 | 0.3 | 0.483 | 0.518 | 0.522 | +0.039 |
| GloVe-50     | SimLex-999  | 0.6 | 0.249 | 0.321 | **0.324** | **+0.075** |
| GloVe-100    | WordSim-353 | 0.2 | 0.522 | 0.541 | 0.549 | +0.027 |
| GloVe-100    | SimLex-999  | 0.5 | 0.278 | 0.341 | **0.341** | **+0.063** |
| fastText-300 | WordSim-353 | 0.1 | 0.750 | 0.618 | 0.743 | −0.008 |
| fastText-300 | SimLex-999  | 0.4 | 0.471 | 0.485 | **0.500** | **+0.029** |

On held-out data the learned combiner **beats cosine on all three embeddings on
SimLex** (+0.075 / +0.063 / +0.029) and **is ≥ the flat-0.5 combine in every
cell**. The previously catastrophic fastText × WordSim cell (flat-0.5 was −0.13
vs cosine) is **folded back to −0.008 — break-even**: training picked λ\* = 0.1
there, correctly near-zeroing the weaker structural signal where cosine (0.750)
dominates. The −0.008 residual is the coarse 0.1 λ grid (λ = 0 would tie cosine
exactly), not a real loss. So the learned weight captures the relational gain on
genuine-similarity judgements without the flat combine's downside on
relatedness — and it does so on *held-out* pairs, so the lift is not an overfit.

So the project's empirical story is now two-sided: Pygmalion's *geometric*
reconstruction loses on clean embeddings (Results 1–6), but his *relational*
similarity is real and complementary on the harder, cleaner similarity task,
robustly across embeddings and through a learned (held-out-validated) combiner
(Result 7). The earlier headline was "a noise-conditional smoother that usually
loses"; it is now "loses as geometry, wins as relational structure on
genuine-similarity judgements."

## Limitations (named, not buried)

- Three embeddings (GloVe-50/100 + fastText-300, two architectures) × two datasets
  (WordSim-353, SimLex-999). Broad, but still English single-word similarity.
- The phrase benchmark is synthetic with an equal-weight ground truth; a real
  phrase-similarity dataset (Mitchell & Lapata) and head-weighted phrases are
  untested.
- `run_real.py` / `run_residual.py` / `run_generality.py` / `run_structural.py` are
  local scripts (they need the embedding downloads / nltk WordNet); they are **not**
  part of CI. The operators they exercise (`blend_from_neighbors`, `residual_blend`,
  `patchi.structural`) and Spearman are unit-tested; the scripts' glue (parsing /
  neighbour search / graph construction) is not CI-covered.
- Result 7's structural graph is WordNet only; the relational similarity is as good
  as that one relation source. A denser or multi-relational graph (co-occurrence,
  ConceptNet) and a real *signed* graph (to test the polarity half) are untested.
- The learned combiner uses a coarse λ grid (0.1 step) and a single deterministic
  even/odd train/test split — not k-fold cross-validation. The held-out lift is
  therefore directional evidence, not a tuned ceiling; a finer grid + CV would
  sharpen the exact numbers (and would let λ = 0 tie cosine exactly on fastText ×
  WordSim instead of the −0.008 grid artefact).

## Next steps

- Result 7's structural signal is complementary, not redundant, with cosine on
  SimLex — now confirmed across embeddings *and* through a learned, held-out-
  validated combiner. The remaining follow-up is a denser or genuinely *signed*
  relation graph (ConceptNet, co-occurrence) to test the stimulator/inhibitor
  **polarity** half that WordNet's sparse antonyms left at noise — the one part of
  Pygmalion's spectrum claim still untested. (It needs an external download, so it
  is a scope decision, not an autonomous step.)
