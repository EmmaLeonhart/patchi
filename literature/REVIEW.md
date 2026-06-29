# Patchi — Literature Review

**What this is.** A survey grounding Pygmalion's relation/agreement-based theory
of cognition in the established literature: for each major construct, the prior
work it descends from, and the gap Patchi must actually close. Full source notes
(with verified identifiers) are in [`sources.md`](sources.md). Pygmalion's
original framework is in [`../data_lake/artificialtime2.txt`](../data_lake/artificialtime2.txt)
— with a later, seven-phase reorganization of the same notebook in
[`../data_lake/proto.txt`](../data_lake/proto.txt) (same constructs, sorted into
his own pipeline order; see the *Primary sources* note in `sources.md`) — and is
his intellectual work; this review is analysis built on top of it.

> **Research question.** Can Pygmalion's framework — *words as agreements on
> labels; context as the base relation; infons & situations; meaning as relations
> between word-sets realized geometrically; memory as a `<TemporalLogic,
> SpatialLogic>` recursion; reconfigurable "VHDL-style" neural blocks bound
> bijectively to words; topos-level meta-reasoning* — be given a precise
> formalization and a working reference implementation, and where does it extend
> vs. re-derive what is already known?

## 1. The framework as a layered stack

Read charitably, Pygmalion's notebook is not a grab-bag — it is a single
**semantic-cognitive stack** that happens to recruit five established traditions,
one per layer. The notebook's own closing hierarchy makes this explicit:

```
infons / infon-classes      → situation theory (Devlin)
   ↓
WordClasses (poly+geom+axiom) → conceptual spaces + VSA (Gärdenfors, Plate/Kanerva)
   ↓
neural "VHDL" blocks         → distributional/compositional semantics (word2vec, DisCoCat)
   ↓
spatial / temporal logic     → modal/spatial/temporal logic (Kripke, Aiello, Pnueli)
   ↓
objects → thought → idea      → emergent, the project's own contribution
   ↓
collectives / topos          → categorical logic (Mac Lane–Moerdijk, Goldblatt)
```

Each arrow is a place where Pygmalion asserts a bridge ("spatial logic is the
gateway to vector algebra"; "topos as VHDL category reasoning"; the bijective
"translator: WordClass → NeuralCircuitBlock"). **The bridges are the research.**
The layers themselves are well-trodden; what is unproven is that they compose.

## 2. What is already known (so Patchi should not re-derive it)

- **Meaning from relations / distribution.** That a word's meaning is fixed by
  the company it keeps (Firth, Harris) and is representable as geometry where
  *relations are consistent vector offsets* (word2vec, GloVe, TransE) is settled.
  Pygmalion's "meaning as relations between sets of words" and "king−man+woman"
  are this tradition; Patchi should *use* it, not reinvent it.
- **Information as infons-in-situations.** The `⟨relation, args, polarity⟩` infon
  and the `s ⊨ σ` support relation are Devlin's situation theory verbatim. The
  symbolic account is complete; what is missing is a *graded/learned* one.
- **Compositional vectors, including categorically.** DisCoCat already fuses
  grammar + category theory + distributional vectors to compose sentence meaning.
  This is the **single most important prior art**: it is the closest existing
  realization of Pygmalion's vision and the natural baseline/skeleton.
- **Binding structured meaning into fixed-width vectors.** VSA/HDC (Plate,
  Kanerva, Gayler; Smolensky's tensor products) gives binding/bundling/permutation
  — the operations Pygmalion calls "blending."
- **Concepts as regions.** Gärdenfors' convex regions over quality dimensions are
  Pygmalion's "classes as perimeters delimited by parameters" almost exactly.
- **Worlds, space, time, topoi.** Kripke's `⟨W,R,V⟩`, the *Handbook of Spatial
  Logics*, Pnueli's temporal logic, and topos internal logic each exist in mature
  form. Pygmalion adopts their notation directly.

## 3. The gaps — where Patchi's actual contribution lives

Across every cluster the same shape of gap recurs: **the components are known in
isolation; the bridges between them are not standard, and in several cases not
known to be consistent.** Concretely:

1. **The bijective `WordClass → NeuralBlock` translator.** No standard model
   makes word→computational-unit a *bijection* whose two sides (a region/concept
   and a reconfigurable circuit) update in lockstep. This is the framework's
   keystone and its biggest risk: bijectivity over an open, growing vocabulary is
   a strong claim.
2. **Similarity-weighted polynomial blending.** Pygmalion's composition operator
   — `Poly(w) = Σ Similarity(w, sᵢ)·Poly(sᵢ)` — is *not* the bilinear/tensor
   composition of DisCoCat/Smolensky. It is a similarity-gated interpolation over
   the lexicon. Formalizing it and comparing it to known operators is a crisp,
   testable contribution. *(Tested — `FINDINGS.md` Results 1–6: on clean
   embeddings this geometric reconstruction loses to raw vectors in 0 of 6
   cells.)*
   2b. **Similarity as *relational* overlap.** A distinct Pygmalion claim
   (`../data_lake/proto.txt` L229–235, L308–316): "distance between words = the
   number of words they have in common" — structural neighbourhood overlap, not
   vector geometry. *(Tested — `FINDINGS.md` Result 7, the project's first
   positive result: WordNet shared-ancestor structure **complements** GloVe
   cosine on genuine-similarity judgements, combined 0.383 vs cosine 0.296 on
   SimLex-999. This is graph-degree similarity, the structural-equivalence line
   from network science, applied to Pygmalion's signed relation graph.
   **Result 8 contextualises it:** Pygmalion's specific shared-neighbour count is
   *beaten* by the textbook WordNet measures (path 0.476, Wu-Palmer 0.438 vs his
   0.298 on SimLex) — but the stronger measure complements cosine *more*: cos+path
   significantly beats cosine on all three embeddings incl. fastText. Direction
   right, metric not — the established Wu-Palmer/path similarities capture the
   phenomenon better than the raw shared-word count.)*
3. **Classes-as-regions *with* a binding algebra.** Conceptual Spaces gives
   regions but no composition; VSA gives composition but no region boundary.
   Unifying them — set theory over class perimeters *and* binding on the same
   objects — is open (does binding stay closed under region membership?).
4. **Graded `s ⊨ σ` and context as a learned signal.** Turning Devlin's binary
   support into a continuous, learnable conditioning score is unbuilt.
5. **Topos meta-reasoning over actual blocks.** Using a topos's internal logic to
   *prove* "this block composition preserves bijectivity / full-image coverage"
   is asserted but not instantiated anywhere. This is the most mathematically
   demanding and least de-risked bridge.
6. **The control reframing of neural nets.** "NNs are information-flow controllers,
   not learners" has *no* verified support; attention-as-gain (Vaswani) is the
   nearest real mechanism. This is Pygmalion's framing to argue, not a citation.
   **Argued in full in [`control-reframing.md`](control-reframing.md):** the
   flow-control *lens* is grounded (attention, gating, routing), but "controllers
   *not* learners" is a false dichotomy because the controllers are themselves
   learned.

## 4. What a defensible first implementation looks like

The review points to an implementable **minimum viable core** that exercises the
real contribution without requiring the whole tower:

- A lexicon of **WordClasses** = (embedding/region + a small parameter set), built
  from pretrained vectors (words-as-coordinates) seeded by dictionary glosses
  (Pygmalion's "definitions from encyclopedias/dictionaries").
- A **signed relation graph** (synonyms = +, antonyms = −) with relations as
  offsets (TransE-style), giving the stimulator/inhibitor spectrum.
- The **similarity-weighted blending** operator (#2) as the composition primitive,
  evaluated against a plain additive and a tensor/DisCoCat baseline on a concrete
  task (e.g. word-pair similarity / analogy / short-phrase similarity).
- A thin **infon/situation layer**: `⟨R, args, polarity⟩` records with a graded
  `support(s, σ)` score, so "context as base relation" is testable.
- A **`Proof(walk)`** trace (Pygmalion's term) recording which words/relations
  produced an output — the explainability the framework promises.

Topos meta-reasoning, the full VHDL "twirking" circuit story, and "artificial
time" are deferred to `todo.md` as later, higher-risk layers — named plainly as
hard and partly speculative rather than papered over.

## 5. Relation to the wider research library

Patchi sits squarely next to existing topics in this library: **hyperdimensional
computing / VSA**, **neural architectures**, **reservoir computing**, and
**neuromorphic hardware**. The VSA/HDC and conceptual-spaces cluster in
particular overlaps the library's HDC work; the "neural blocks as control over
information flow" reading rhymes with the reservoir-computing / control-systems
framing already collected there. Cross-pollination both ways is expected.

---

*Status: first-pass review (2026-06-25), five clusters, ~26 sources with verified
identifiers in `sources.md`. Open verification debt: a credible "category theory
of cognition" reference (flagged, uncited); exact editions/DOIs for a few older
volumes (Kripke 1963, Goldblatt 1979, RCC 1992).*
