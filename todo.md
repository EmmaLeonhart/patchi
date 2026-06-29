# Patchi — long-horizon plan (todo)

The **abstract destinations**. Items here are pulled into `queue.md` and
decomposed into concrete steps when work begins. Newest thinking at the bottom.
Grounded in [`literature/REVIEW.md`](literature/REVIEW.md).

## Near-term: the minimum viable core (the real contribution)

- **MVC-1 · WordClass lexicon.** A `WordClass = (vector/region, parameters)` built
  from pretrained embeddings, seeded by dictionary glosses. The atomic object the
  whole stack stands on.
- **MVC-2 · Signed relation graph.** Synonyms (+) / antonyms (−) as TransE-style
  offsets — Pygmalion's stimulator/inhibitor spectrum. Source from WordNet /
  Wiktionary. ✦ *Graph offset/spectrum core landed* (`relations.py`).
  ✦ *Graph-degree structural similarity DONE — the GD thread, the project's first
  positive result* (`structural.py`, `run_structural.py`; `FINDINGS.md` Result 7):
  Pygmalion's "distance = number of shared words" claim, tested over a WordNet
  shared-ancestor graph, **complements** GloVe cosine on SimLex-999 (combined
  0.383 > cosine 0.296). **Remaining reach:** (a) ✦ *learned/weighted combiner DONE*
  (`run_structural_weighted.py`): λ tuned on a train split, scored on held-out
  test — beats cosine on SimLex for all 3 embeddings (+.075/.063/.029) and folds
  the one flat-combine loss (fastText × WordSim) back to break-even.
  ✦ *Significance + 5-fold CV DONE* (`run_structural_significance.py`): the SimLex
  gain is bootstrap-significant on GloVe-50/100 (95% CI [+.057,+.142] / [+.043,
  +.127]) but **not** on fastText-300 (CI [−.008,+.075] crosses 0); 5-fold CV
  confirms the learned combiner is ≥ cosine on every cell.
  ✦ *Baseline contextualisation DONE* (`run_structural_baselines.py`, `FINDINGS.md`
  Result 8): Pygmalion's shared-neighbour count is *beaten* by textbook WordNet
  similarity (path 0.476, Wu-Palmer 0.438 vs his 0.298 on SimLex), but cos+path
  significantly beats cosine on **all three** embeddings incl. fastText (+.168/.151
  /.080, all CIs > 0) — direction right, metric not. (b)
  **remaining:** a denser / genuinely *signed* relation graph (ConceptNet,
  co-occurrence) so the stimulator/inhibitor *polarity* half — which WordNet's
  sparse antonyms left at noise (`signed_overlap` ≈ 0) — can actually be tested
  (needs an external download → scope decision); (c) ✦ *generality DONE* —
  complementarity survives the strongest embedding (fastText-300) on SimLex.
- **MVC-3 · Similarity-weighted blending operator.** Formalize and implement
  `Poly(w)=Σ sim(w,sᵢ)·Poly(sᵢ)`; this is the framework's distinctive composition
  primitive. **Benchmark it head-to-head** against additive and tensor/DisCoCat
  baselines on a concrete task (word/phrase similarity, analogy). This is the
  single most defensible empirical result Patchi can produce.
- **MVC-4 · Infon/situation layer.** `⟨R, args, polarity⟩` records with a graded
  `support(s, σ) ∈ [0,1]`; make "context as base relation" testable by showing
  context-conditioning changes outputs.
- **MVC-5 · Proof(walk) explainability.** Every output carries the trace of words
  / relations / blocks that produced it.
- **MVC-3b · Real-embeddings benchmark.** ✦ *DONE* (`scripts/run_real.py`; see
  `FINDINGS.md`). Ran raw/additive/blend on GloVe-50 × WordSim-353 (all 353 pairs).
  Result: on clean embeddings reconstruction *hurts* (raw 0.50 > blend 0.45) —
  the opposite of the synthetic denoising result. (Correction: this was never
  "blocked in an offline env" — the machine has network; that earlier claim was
  wrong. The download is a one-time ~65 MB, just not run inside CI.)
  ✦ *Residual blending also done* (`run_residual.py`): best α is 0 (raw), no sweet
  spot. ✦ *Generality done* (`run_generality.py`): blend beats raw in **0 of 6**
  over {GloVe-50,GloVe-100,fastText-300}×{WordSim-353,SimLex-999} — holds across
  size, **architecture** (fastText subword), and dataset; penalty shrinks to
  break-even on the strongest embedding+hardest task but never goes positive. The
  empirical generality story is complete (English single-word similarity).

## Mid-term: the bridges

- **BR-1 · The bijective translator `WordClass → NeuralBlock`.** ✦ *Reduced
  version landed* (`block.py`): a registry-backed bijection over the lexicon that
  grows on demand. ✦ *Richer blocks landed*: `NeuralBlock` now carries a `payload`
  (the WordClass's gloss/params/source-vector), preserved by the translator and
  through twirks, while the affine map stays the morphism (category/twirk
  untouched). **Remaining stretch:** actually *use* the polynomial/region payload
  *in* the computation (not just carry it) — the affine map is still vector-derived.
- **BR-2 · Classes-as-regions with binding.** ✦ *DONE (probe)* — `regions.py`:
  VSA binding does **not** keep convex regions closed in general (off-origin ball
  counterexample); fixed-key binding preserves convexity, origin unit ball is
  closed. Negative structural result in `FINDINGS.md` Result 4. **Reach:** a
  binding variant or region redefinition that restores closure.
- **BR-3 · Memory `<TemporalLogic, SpatialLogic>`.** ✦ *DONE* — temporal half
  (recursion + artificial time) and now the spatial half: a `NeuralBlock` gates
  each input (`m_{t+1} = decay·m_t + gate(input_t)`), with `memory_tuple()`
  exposing `(time, gate)`. **Reach:** a learned/adaptive gate rather than a fixed block.

## Stretch: the deeper layers (reduced cores built; full versions are the reach)

These are no longer "parked." Each now has a buildable core; the item is the
*full* version beyond the honest reduction already shipped.

- **LT-1 · Topos meta-reasoning over blocks.** ✦ *Computable shadow landed*
  (`category.py`: block category + property checkers for invertibility /
  equivalence / associativity / identity). **Remaining reach:** a genuine
  internal-logic / subobject-classifier treatment and "full-image coverage"
  proofs, beyond the decidable affine fragment.
- **LT-3 · "Artificial time."** ✦ *Operational definition landed* — the discrete
  recursion index (`Memory.time`), decoupled from wall-clock, as the TemporalLogic
  order over states. **Remaining reach:** time as an active modal dimension (R in
  `⟨W,R,V⟩`) the reasoner quantifies over, not just a counter.
- **LT-2 · "VHDL twirking" reconfigurable circuits.** ✦ *DONE* — `twirk.py`:
  `twirk_block` (re-implement params, rejected if it breaks invertibility) +
  `rewire` (re-compose, gated by `category.preserves_invertibility`); the
  topos-shadow checker now *gates* reconfiguration. **Reach:** cycle detection +
  interface retyping once blocks live in a real wiring graph (the current
  linear/affine model has no connection graph, so "no cycle introduced" is N/A).
- **LT-4 · Linguistic pipeline.** ✦ *First slice landed* (`compose.py`): phrase
  composition (additive / multiplicative / similarity-weighted) — the
  syntax→semantics composition step, with the Mitchell & Lapata / DisCoCat
  baselines. **Remaining (large):** the staged syntax → semantics → pragmatics →
  world-knowledge extraction pipeline over real text.
- **LT-5 · The control-system reframing of neural nets.** ✦ *DONE (argued)* —
  `literature/control-reframing.md`: the flow-control *lens* is grounded
  (attention/gating/routing — Vaswani, LSTM/GRU, MoE, Highway), but "controllers
  *not* learners" is a false dichotomy (the controllers are themselves learned),
  so it's a framing to argue in specific mechanisms, not assert. Cross-ref REVIEW §3.

## Reporting

- Keep `FINDINGS.md` and the themed `docs/` site current as results land; the PDF
  builds from `FINDINGS.md` via CI.
- Maintain the verification debt list in `REVIEW.md` (uncited "CT of cognition"
  ref; a few older editions/DOIs).
