# PATCHi — long-horizon plan (todo)

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
  single most defensible empirical result PATCHi can produce.
- **MVC-4 · Infon/situation layer.** `⟨R, args, polarity⟩` records with a graded
  `support(s, σ) ∈ [0,1]`; make "context as base relation" testable by showing
  context-conditioning changes outputs.
- **MVC-5 · Proof(walk) explainability.** Every output carries the trace of words
  / relations / blocks that produced it.

## Mid-term: the bridges

- **BR-1 · The bijective translator `WordClass → NeuralBlock`.** The keystone.
  Decide honestly whether a true bijection is tenable over an open vocabulary, or
  whether it must weaken to an injection / typed family. Document the call.
- **BR-2 · Classes-as-regions with binding.** Test whether VSA binding stays
  closed under Gärdenfors-style region membership; report where it breaks.
- **BR-3 · Memory as `<TemporalLogic, SpatialLogic>` recursion.** A recurrent
  state where spatial logic gates vector ops and temporal logic orders them.

## Long-term / higher-risk (named as hard, partly speculative)

- **LT-1 · Topos meta-reasoning over blocks.** Instantiate an internal-logic check
  that a block composition "preserves bijectivity / full-image coverage." The most
  demanding, least de-risked layer — may end as a formal sketch, not running code.
- **LT-2 · "VHDL twirking" reconfigurable circuits.** Blocks that rewire/retype
  under constraint-checking (the Prolog `valid_twirk` rules).
- **LT-3 · "Artificial time."** Pin down what the notebook's titular concept
  actually denotes operationally before building it — currently underspecified.
- **LT-4 · Linguistic pipeline.** Syntax → semantics → pragmatics → world-knowledge
  as staged subset-extraction over the core.
- **LT-5 · The control-system reframing of neural nets.** Either find real support
  or present it explicitly as PATCHi's own thesis, argued not asserted.

## Reporting

- Keep `FINDINGS.md` and the themed `docs/` site current as results land; the PDF
  builds from `FINDINGS.md` via CI.
- Maintain the verification debt list in `REVIEW.md` (uncited "CT of cognition"
  ref; a few older editions/DOIs).
