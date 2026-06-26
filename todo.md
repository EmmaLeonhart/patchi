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
  Wiktionary.
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
- **LT-4 · Linguistic pipeline.** Syntax → semantics → pragmatics → world-knowledge
  as staged subset-extraction over the core.
- **LT-5 · The control-system reframing of neural nets.** Either find real support
  or present it explicitly as Patchi's own thesis, argued not asserted.

## Reporting

- Keep `FINDINGS.md` and the themed `docs/` site current as results land; the PDF
  builds from `FINDINGS.md` via CI.
- Maintain the verification debt list in `REVIEW.md` (uncited "CT of cognition"
  ref; a few older editions/DOIs).
