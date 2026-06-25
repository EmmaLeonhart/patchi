# PATCHi — Devlog

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
- Recorded the project name origin in README (PATCHi ← Patchouli Knowledge). Next: MVC-2 signed relation graph.

## 2026-06-25 — Barrelled through the held-back "hard" design items (reduced but real)

User directive: don't park the hard/speculative design items — find a way to build them. Built honest, reduced, fully-tested cores for all three, naming plainly what is the reduction vs. the remaining reach (tracked in todo.md):

- **BR-1 · Bijective translator** (`src/patchi/block.py`). Resolved the "bijection over an open vocabulary" risk by making it a **registry-backed bijection that grows on demand**: unseen words are *registered* (minting a fresh block), so the map is an exact 1:1 over the registered set at all times. `NeuralBlock` is an invertible affine map `y = d⊙x + b` (d = 1+|vector| ⇒ always invertible) with `apply`/`invert`/`compose`/`identity`; `Translator` enforces the 1:1 invariant and rejects conflicting re-registration. Reach left: richer block internals (polynomial/geometric), not just affine.
- **LT-1 · Topos meta-reasoning** (`src/patchi/category.py`). Built the **computable shadow**: a category of blocks (associative `compose`, `identity`) plus property checkers — `preserves_invertibility` (the "preserves bijectivity" claim made decidable), `equivalent`, `round_trips`, `obeys_identity_law`, `is_associative`. Named explicitly as the decidable affine fragment, NOT a full elementary topos.
- **LT-3 · "Artificial time"** (`src/patchi/memory.py`). Gave the notebook's titular-but-undefined term an **operational definition**: artificial time = the discrete recursion index of the memory update (`Memory.time`), decoupled from wall-clock — the TemporalLogic order over states `m_0,m_1,…`. Memory itself is a leaky accumulator `m_{t+1}=decay·m_t+input` (reservoir-style).

Tests: +30 (test_block 11, test_category 9, test_memory 10). **Full suite 42 passed.** Hard rails held — every "preserves invertibility"/"round-trips" claim is a measured assertion, and each reduction is labelled as such (no claim of a full topos or a closed-form infinite bijection). De-parked BR-1/LT-1/LT-3 in todo.md (reduced cores done; full versions are the remaining reach).

## 2026-06-25 — MVC-2: signed relation graph with offset-based recovery (queue item)

- Implemented `src/patchi/relations.py`: `SignedRelationGraph` over a `Lexicon`. Two threads of the framework meet: **relations as vector offsets** (TransE-style `offset(rel) = mean(tail-head)`, with `predict_tail` recovering a held-out edge's tail by arithmetic + nearest-neighbour) and the **signed stimulator/inhibitor spectrum** (synonyms +1, antonyms −1; `polarity_between`, `neighbors(polarity=…)`, `net_effect`).
- Added `tests/test_relations.py` (10 tests): construction/guards, offset = mean difference, **held-out antonym recovery** (train hot/cold + fast/slow → predict up→down), **held-out synonym recovery** (train big→large → predict small→little), signed/symmetric polarity, sign-filtered neighbours, net-effect balance. Full suite: **52 passed**. Next: MVC-3 (the blending-operator benchmark — the headline empirical result).
