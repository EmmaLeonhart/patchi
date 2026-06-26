# Patchi — Devlog

**This file is where "done" lives.** `queue.md` is delete-only: when a queue
item is finished, the item is **deleted from `queue.md`** and a dated entry
is **appended here**, in the same commit as the work, then pushed. Never
tick a box in place — a checked box left in `queue.md` is the failure mode
this file exists to prevent.

Also record releases (tag + a one-line note), notable milestones, and
anything else worth a chronological trail. Newest entries at the bottom.

This is the **same convention as the cleanvibe repo's own `devlog.md`** —
every cleanvibe-scaffolded project gets one for the same reason.

See `CLAUDE.md` § "Workflow Rules" and `queue.md`'s preamble.

---

## 2026-06-25 — Project scaffolded

Scaffolded with `cleanvibe new` (cleanvibe v1.13.1). Future entries
land here as queue items get deleted.

## 2026-06-25 — First-pass literature review published (agentic RAG)

- Ran the agentic-RAG literature review across five clusters and wrote `literature/sources.md` (~26 cited sources, verified identifiers only) + `literature/REVIEW.md` (synthesis). Clusters: situation semantics & information (Barwise/Perry, Devlin's infons, Lewis convention); distributional & compositional semantics (Firth/Harris, word2vec, GloVe, **DisCoCat** — closest prior art); vector-symbolic computing & conceptual spaces (Plate HRR, Kanerva, Gayler, Gärdenfors, Smolensky); neuro-symbolic AI, KG embeddings & the control view (Garcez/Lamb, Besold, **TransE**, Vaswani attention, MLN); topos/categorical logic & modal/spatial/temporal logic (Mac Lane–Moerdijk, Goldblatt, Fong & Spivak, Kripke, Handbook of Spatial Logics, Pnueli).
- Key reading: Pygmalion's notebook is a coherent layered stack (infons → WordClasses → neural "VHDL" blocks → spatial/temporal logic → objects/thought/idea → topos), recruiting one established tradition per layer. The layers are known; **the bridges between them are the research** — above all the bijective `WordClass→NeuralBlock` translator and the similarity-weighted polynomial blending operator. Flagged the "NNs are controllers not learners" claim as unsupported (Pygmalion's thesis to argue, not consensus).
- Wrote `todo.md` (MVC core → bridges → higher-risk/speculative layers incl. topos meta-reasoning and the still-underspecified "artificial time") and replaced the bootstrap `queue.md` with the real MVC implementation queue. Published page updated to show the review is live; come-back-in-12-24h message retained.

## 2026-06-25 — Scaffolded the Python package, tests, and CI (queue MVC item 1)

- Added `pyproject.toml` (src layout, numpy dep, pytest config), `src/patchi/__init__.py` (version-only for now), `scripts/run.py` (CI entry point — reports version/stage until an experiment is wired), `tests/test_smoke.py` (import + entry-point run), and `.github/workflows/ci.yml` (pip install -e + pytest). Ran locally: **2 passed in 0.07s**. This gives CI something real to run from the first code commit, before any domain logic. Next: MVC-1 WordClass lexicon.

## 2026-06-25 — MVC-1: WordClass lexicon (queue item)

- Implemented `src/patchi/wordclass.py`: a frozen `WordClass` (word + read-only vector + optional gloss + param bag, with validation), a `cosine` helper (zero-norm guarded), and a `Lexicon` (dimension-checked construction, `from_embeddings`, `nearest`/`nearest_to_vector` by cosine, self-exclusion, k-limit). Vectors come from pretrained embeddings in real use; tests use a small offline 3-D fixture (two clear clusters) so the suite stays network-free. Dictionary-gloss *ingestion* (WordNet/Wiktionary parsing) is deferred — `gloss` is for now just an optional attached string.
- Added `tests/test_wordclass.py` (10 tests: construction/access, dim-mismatch + validation guards, cosine edge cases, in-cluster nearest-neighbour, self-exclusion + k ordering, arbitrary-vector query, unknown-word KeyError). Full suite: **12 passed in 0.08s**.
- Recorded the project name origin in README (Patchi ← Patchouli Knowledge). Next: MVC-2 signed relation graph.

## 2026-06-25 — Barrelled through the held-back "hard" design items (reduced but real)

User directive: don't park the hard/speculative design items — find a way to build them. Built honest, reduced, fully-tested cores for all three, naming plainly what is the reduction vs. the remaining reach (tracked in todo.md):

- **BR-1 · Bijective translator** (`src/patchi/block.py`). Resolved the "bijection over an open vocabulary" risk by making it a **registry-backed bijection that grows on demand**: unseen words are *registered* (minting a fresh block), so the map is an exact 1:1 over the registered set at all times. `NeuralBlock` is an invertible affine map `y = d⊙x + b` (d = 1+|vector| ⇒ always invertible) with `apply`/`invert`/`compose`/`identity`; `Translator` enforces the 1:1 invariant and rejects conflicting re-registration. Reach left: richer block internals (polynomial/geometric), not just affine.
- **LT-1 · Topos meta-reasoning** (`src/patchi/category.py`). Built the **computable shadow**: a category of blocks (associative `compose`, `identity`) plus property checkers — `preserves_invertibility` (the "preserves bijectivity" claim made decidable), `equivalent`, `round_trips`, `obeys_identity_law`, `is_associative`. Named explicitly as the decidable affine fragment, NOT a full elementary topos.
- **LT-3 · "Artificial time"** (`src/patchi/memory.py`). Gave the notebook's titular-but-undefined term an **operational definition**: artificial time = the discrete recursion index of the memory update (`Memory.time`), decoupled from wall-clock — the TemporalLogic order over states `m_0,m_1,…`. Memory itself is a leaky accumulator `m_{t+1}=decay·m_t+input` (reservoir-style).

Tests: +30 (test_block 11, test_category 9, test_memory 10). **Full suite 42 passed.** Hard rails held — every "preserves invertibility"/"round-trips" claim is a measured assertion, and each reduction is labelled as such (no claim of a full topos or a closed-form infinite bijection). De-parked BR-1/LT-1/LT-3 in todo.md (reduced cores done; full versions are the remaining reach).

## 2026-06-25 — MVC-2: signed relation graph with offset-based recovery (queue item)

- Implemented `src/patchi/relations.py`: `SignedRelationGraph` over a `Lexicon`. Two threads of the framework meet: **relations as vector offsets** (TransE-style `offset(rel) = mean(tail-head)`, with `predict_tail` recovering a held-out edge's tail by arithmetic + nearest-neighbour) and the **signed stimulator/inhibitor spectrum** (synonyms +1, antonyms −1; `polarity_between`, `neighbors(polarity=…)`, `net_effect`).
- Added `tests/test_relations.py` (10 tests): construction/guards, offset = mean difference, **held-out antonym recovery** (train hot/cold + fast/slow → predict up→down), **held-out synonym recovery** (train big→large → predict small→little), signed/symmetric polarity, sign-filtered neighbours, net-effect balance. Full suite: **52 passed**. Next: MVC-3 (the blending-operator benchmark — the headline empirical result).

## 2026-06-25 — MVC-3: similarity-weighted blending operator + measured benchmark (queue item)

- Implemented `src/patchi/blend.py` (the operator `blend(w)=Σ sim(w,sᵢ)^p·vec(sᵢ) / Σ sim^p`, with `weighting="uniform"` collapsing to the additive baseline) and `src/patchi/benchmark.py` (controlled synthetic denoising task + numpy-only Spearman + a noise×power sweep). `scripts/run.py` now runs it and writes `results/benchmark.json`.
- **Measured result (real numbers, not asserted):** headline (noise 0.6, power 2) raw 0.7916 / additive 0.9299 / **blend 0.9334**. The sweep shows the honest structure: similarity weighting helps most when the neighbourhood is trustworthy — at low noise + sharp weighting, blend beats a flat additive average by **+0.10 to +0.14 Spearman**; the margin decays with noise and over-sharpening goes slightly negative under heavy noise. At the middling default it barely beats additive (+0.0035). Conclusion stated plainly in `FINDINGS.md`: the operator is a trustworthy-neighbourhood denoiser, not a universal win.
- Tests: +13 (`test_blend.py` 6, `test_benchmark.py` 7) incl. a **regression guard** that blend beats raw and additive by a clear margin in the favourable regime (deterministic, seed 0). Full suite **66 passed**. Published `FINDINGS.md` + updated the live page's findings section. Named the real-embeddings run (GloVe + WordSim-353) as a blocked next step (offline) in `FINDINGS.md`/`todo.md` — not faked. Next: MVC-4 infon/situation layer.

## 2026-06-25 — MVC-3b: REAL-embeddings benchmark (GloVe-50 × WordSim-353) — and a retraction

- Retraction first: I had called the real-embeddings run "blocked in an offline CI/loop environment." That was wrong — the machine has network (it has been pushing to GitHub all along). Downloaded GloVe-50 (~65 MB, gensim-data release) + WordSim-353 (gensim test tsv) to a gitignored cache and actually ran it.
- `scripts/run_real.py` scores the **same** operator (`patchi.blend.blend_from_neighbors`) on GloVe-50 (top 100k) vs WordSim-353, all 353 pairs. **Measured result:** raw GloVe Spearman **0.5033** (matches the known literature value — harness sanity check); additive ~0.43, blend ~0.43. Across a k×power sweep (k∈{3,5,10,25}, power∈{1,2,6}) **every reconstruction config underperforms raw by 0.06–0.08**; blend beats unweighted additive everywhere but only by +0.001..+0.009.
- **Finding (stated straight):** Pygmalion's blending is a *noise-conditional denoiser*, NOT a free win. It helps on synthetic noisy vectors (blend +0.14 over raw) but HURTS on clean pretrained GloVe (raw 0.50 > best blend 0.45) — the opposite of the synthetic run, which is exactly why running the real one mattered. The similarity weighting's edge over a flat average is real but tiny in both regimes. Updated `FINDINGS.md` + the live page with both results and the corrected conclusion; corrected `todo.md` MVC-3b (done, not "blocked"). `run_real.py` is a local script (needs the download), not CI-covered; the operator + Spearman it uses are unit-tested. Suite still 66 passed.

## 2026-06-25 — MVC-4: infon/situation layer with graded support (queue item)

- Implemented `src/patchi/situation.py`: `Infon` (`⟨relation, args, polarity±1⟩`, with `negate()`) and `Situation`, which turns Devlin's *binary* `s ⊨ σ` into a **graded** `supports(query) ∈ [0,1]`: asserted infon → 1.0, direct contradiction → 0.0, else best cosine of infon-vectors (vector-backed via a `Lexicon`, clamped to [0,1]) with a structural argument-overlap (Jaccard) fallback when no lexicon. Added `contextual_polarity` = support(+) − support(−), a signed context-conditioned output in [−1,1].
- Added `tests/test_situation.py` (9 tests): infon normalisation/negation, exact-support and contradiction, support always in [0,1], graded support higher for more-similar infons (dolphin > car given "swims fish"), structural fallback Jaccard, and the **headline property** — the same infon gets different support across situations (context conditioning changes the output), plus contextual_polarity flipping sign with context. Full suite **75 passed**. Next: MVC-5 Proof(walk) trace.

## 2026-06-25 — MVC-5: Proof(walk) explainability trace — MVC core complete (queue item)

- Implemented `src/patchi/proof.py` (`Contribution`/`Step`/`ProofWalk` with `contributors()`, `to_dict()`, `explain()`) and threaded it through the operators with a **single-source-of-truth** discipline so a trace can never disagree with the computed value:
  - Refactored `blend.py` to extract `blend_weights()` (normalised, used by both the plain and explained paths); added `blend_word_explained()` → `(vector, ProofWalk)` recording each neighbour + its normalised weight. The explained vector is provably identical to `blend_word` (tested).
  - Made `Situation.supports_explained()` the source of truth (records which rule fired: exact/contradiction/vector/structural + the driving infon); `supports()` now returns just its score.
- Added `tests/test_proof.py` (8 tests): ProofWalk structure/serialisation, explained-blend vector == plain blend, normalised weights sum to 1 (and equal under uniform), support score == `supports()`, and each rule (exact/contradiction/structural) recorded. Full suite **83 passed**.
- **MVC-1…5 core is complete** (lexicon, signed relation graph, blending operator + dual-regime benchmark, infon/situation layer, Proof(walk)). Drained the MVC queue and refilled `## Active` from `todo.md` with three bounded next items: residual-blending follow-up (`raw + α·blend`, answers the open MVC-3b question), BR-3 spatial-gated memory, BR-2 regions-with-binding probe. Not executed this tick — queued for the next work-loop ticks.

## 2026-06-25 — Fix the public site + write the actual paper (user-reported failures)

User flagged the live page as broken/useless. Confirmed three real defects and fixed them:
- **Stale, self-contradictory page.** The top still said "just getting started / come back in 12–24h / implementation is next" while the whole MVC core was built and two benchmarks were run — the real results buried at the bottom. Rewrote `docs/index.html` as a current, self-contained report: status badge, what-we-built, both result tables inline, the straight conclusion, limitations.
- **Links went to raw GitHub file trees** instead of readable content. Replaced the three github-tree nav cards with: Download the paper (PDF) · Read the results (on-page) · Code on GitHub (one link).
- **`report.pdf` 404'd (never built).** The pages.yml step used `pandoc -o report.pdf` with no PDF engine (needs LaTeX) and swallowed the failure with `|| echo skipped`. Switched to `--pdf-engine=wkhtmltopdf` (apt-installed), build from `PAPER.md`, removed the error-swallow and added `test -s docs/report.pdf` so a missing PDF fails the build loudly.
- **Wrote the actual paper** (`PAPER.md`): title/abstract/intro/related-work/system/methods/results (both benchmarks)/discussion/limitations/conclusion/references. This is the source for both the PDF and the pending clawRxiv submission. clawRxiv submission (POST /api/posts, Bearer key) is prepared next; it publishes publicly under the user's key, so it needs the key + a go-ahead.

## 2026-06-25 — Paper PUBLISHED to clawRxiv (2606.02822)

- Wrote `PAPER.md` (proper paper: abstract … references) and published it to clawRxiv via the Agent API (`POST /api/posts`, Bearer key from a self-registered "patchi" agent identity, id 486). Authorship `human_names = ["Pygmalion", "Emma Leonhart"]` per the user's call (theory: Pygmalion; formalization/implementation/experiments: Emma + agent). Live at **https://www.clawrxiv.io/abs/2606.02822** (cs.AI, cross-list stat) — abs page verified 200.
- The paper reports the honest, partly-negative result: Pygmalion's blending operator is a noise-conditional denoiser (helps on noisy synthetic vectors, +0.14; hurts on clean GloVe, raw 0.50 > blend 0.45). Added `scripts/submit_clawrxiv.py` (dry-run by default; --register / --confirm gated; key via env). Linked the published paper prominently on the live site.

## 2026-06-25 — Residual blending follow-up: no sweet spot on clean vectors (queue item)

- Added `residual_blend(own, blend, α) = (1-α)·own + α·blend` to `blend.py` (CI-safe unit-tested: α=0→own, α=1→blend, α=0.25→midpoint) and `scripts/run_residual.py` to sweep α on the real GloVe-50 × WordSim-353 benchmark. **Measured curve:** α=0.00→0.5033 (raw, best), 0.05→0.5033 (tie to 4dp), 0.10→0.5026, 0.20→0.4986, 0.50→0.4818, 1.00→0.4347 — monotone decreasing. **Best α is 0.** A little smoothing does NOT beat raw; this closes the rescue hypothesis and strengthens the MVC-3b finding (reconstruction only ever hurts on clean embeddings, neutral at vanishing α). Wrote it into `FINDINGS.md` (new "Result 3") + the live page; updated todo. Full suite **84 passed**. Next: BR-3 spatial-gated memory.

## 2026-06-26 — BR-3: spatial-gated memory (the SpatialLogic half participates) (queue item)

- Wired `block.py` into `memory.py`: `Memory(dim, decay, gate=NeuralBlock)` now runs `m_{t+1} = decay·m_t + gate.apply(input_t)`, so SpatialLogic (block vector-algebra) transforms each input before the temporal recursion — realising Pygmalion's `<TemporalLogic, SpatialLogic>` tuple. Added `spatial_gate` property and `memory_tuple() -> (artificial time, gate)`. Backward-compatible: no gate = plain accumulation (all prior memory tests still pass).
- Added 5 tests: identity-gate matches ungated; a doubling gate transforms input before accumulation; offset gate shifts; gate/dim mismatch raises; `memory_tuple`/`spatial_gate` accessors. Full suite **89 passed**. Next: BR-2 regions-with-binding probe.

## 2026-06-26 — BR-2: regions-vs-binding probe — a negative structural result (queue item)

- Built `src/patchi/regions.py` (`BallRegion` convex region, `bind` = elementwise VSA product, `closed_under_binding`, `fixed_key_commutes_with_convex_combination`) to probe whether Gärdenfors regions and VSA binding cohere on the same objects (the open §3.3 question). **Measured result (negative):** a region is NOT closed under binding in general — `a=[1.2,1.0]` ∈ ball([1,1],0.3) but `a⊙a=[1.44,1.0]` escapes. It DOES cohere in restricted cases: fixed-key binding is linear so preserves convexity; an origin-centred unit ball is closed (products shrink inward). Closure depends on the region's position relative to the binding algebra's fixed points (0, ±1), which semantics doesn't respect — so the unification doesn't hold for free.
- Added `tests/test_regions.py` (6 tests, all measured facts incl. the off-origin counterexample and the origin-ball closure). Full suite **95 passed**. Wrote `FINDINGS.md` Result 4. Active queue drained (BR-2 was last); refilled from todo with: generality run (SimLex-999/word2vec) and LT-2 "twirking" blocks. Next: generality of the negative result.

## 2026-06-26 — Generality: the negative result holds across embeddings + datasets (queue item)

- Downloaded SimLex-999 (similarity, not relatedness — a harder test) + GloVe-100, and ran `scripts/run_generality.py`: the same operator across {GloVe-50, GloVe-100} × {WordSim-353, SimLex-999}. **Blend beats raw in 0 of 4 cells** (blend−raw: −0.069, −0.026, −0.081, −0.015) — reconstruction is negative everywhere; blend still edges additive by a hair everywhere but neither catches raw. The penalty is *smaller* on SimLex (the harder similarity task) than WordSim, but stays negative. So "reconstruction hurts on clean embeddings" generalises across embedding *size* and *dataset*. **Caveat named:** both embeddings are GloVe-family (different dims, same architecture); a different *architecture* (word2vec/fastText) is the only generality axis still untested (large downloads). Wrote FINDINGS Result 5 + updated the page limitation. Reused `blend_from_neighbors` (operator unchanged); local script, not CI. Suite 95 passed. Next: LT-2 twirking.

## 2026-06-26 — LT-2: "twirking" — constraint-checked block reconfiguration (queue item)

- Built `src/patchi/twirk.py`: `twirk_block` (re-implement a block's scale/offset, **rejected with `TwirkRejected` if it breaks invertibility**) and `rewire` (propose a new composition, gated by `category.preserves_invertibility`), plus non-raising `is_valid_twirk`/`is_valid_rewire`. This puts the LT-1 topos-shadow checker to work *gating* reconfiguration — the meta-reasoning role the notebook wants ("does this twirk maintain bijectivity?"). Named plainly what's NOT modelled: cycle detection + interface retyping across a wiring graph (the current linear/affine block model has no connection graph, so "no cycle introduced" is N/A until blocks live in a real graph).
- Added `tests/test_twirk.py` (8 tests): param twirk stays invertible / defaults the untouched field / round-trips; a twirk that zeros the scale is rejected; rewire of invertible blocks composes; rewire with a degenerate block is rejected; empty rewire invalid. Full suite **103 passed**. LT-2 was the last Active item → refilled the queue from todo: (1) end-to-end integration demo + test, (2) richer WordClass-carrying blocks (BR-1 reach). Next: the integration demo.

## 2026-06-26 — End-to-end integration demo + test (queue item)

- Built `src/patchi/demo.py`: one deterministic semantic world flows through the whole vertical slice — lexicon → signed relation graph → similarity-weighted blend (+ Proof(walk)) → bijective translator to a NeuralBlock (applied + round-tripped) → spatial-gated Memory tick → infon/situation graded support (+ Proof(walk)). Surfaced via `python scripts/run.py --demo` (prints the traced pipeline). Confirms the modules **compose**, not just pass in isolation.
- Added `tests/test_demo.py` (2 integration tests): the slice composes end-to-end (relation net-effect, 3 blend neighbours with dolphin excluded, translator round-trip, memory tick, graded support in [0,1] via the vector rule > 0.5) and every output carries a Proof(walk). Updated the live page's "What we built" to note the runnable end-to-end demo. Full suite **105 passed**. Next: richer WordClass-carrying blocks.

## 2026-06-26 — BR-1 reach: blocks carry the WordClass payload (queue item)

- `NeuralBlock` now has an optional `payload` mapping carrying the originating WordClass's structured attributes (word, gloss, params, source vector); `from_wordclass` populates it, `twirk_block` preserves it (re-implementing a word's circuit keeps its identity). Crucially the payload is **semantics, not the morphism**: `apply`/`invert`/`compose` and the category/twirk invariants depend only on (scale, offset), and `category.equivalent` ignores payload — so a block can carry a word's meaning while still being reasoned about purely as an affine map. Named the honest limit: the affine map is still *vector-derived*; *using* the polynomial/region payload in the computation is future work.
- Added 4 tests (payload carried from WordClass; bare/composite blocks have empty payload; payload not part of the morphism — same map + different payload → `equivalent`; twirk preserves payload). Full suite **109 passed**. Drained the Active queue; refilled from todo with: (1) architecture-generality (word2vec/fastText — the one untested axis), (2) LT-5 control-system reframing (argue, don't assert). Next: architecture generality.
