# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — bridges & follow-ups (MVC-1…5 core complete)

The minimum viable core is done (WordClass lexicon, signed relation graph,
blending operator + benchmark, infon/situation layer, Proof(walk) trace). These
next items are pulled from `todo.md`; same rails — tests as logic lands, real
measured numbers, `FINDINGS.md`/`docs/` kept current.

1. **BR-3 · spatial-gated memory.** Let a `NeuralBlock` (spatial logic) gate the
   `Memory` recurrence — `m_{t+1} = decay·m_t + block.apply(input_t)` — so the
   SpatialLogic half actually participates, not just accumulation. Test it.
2. **BR-2 · regions-with-binding probe.** Test whether VSA-style binding
   (elementwise/convolution) stays consistent with Gärdenfors-style region
   membership on a small fixture; report plainly where it breaks (this is a
   *probe*, an expected-to-be-partial result, not a guaranteed success).

(Findings publishing is continuous — each item updates `FINDINGS.md` + `docs/`.)

When this drains, refill from `todo.md` (SimLex-999 / word2vec generality of the
"reconstruction hurts on clean vectors" result; then the LT reaches).

---

## Always last — keep the three crons running and summarize

**Pinned to the tail at all times.**

A. **Ensure the three crons are running** — work-loop (`3 * * * *`), auto-flush
   (`15 * * * *`), status-report (`42 * * * *`); restart if a planning burst /
   queue re-fill killed them.
B. **Run the status-report action once more, independently** — an end-of-session
   summary of everything that happened this session.

---

## Pointers
- Long-horizon backlog: `todo.md`. Literature base: `literature/REVIEW.md`.
- Completed work (chronological): `devlog.md`. Narrative: `git log`.
- This is a **nested submodule** (`research_library/projects/Patchi`). When
  pushing here, bump the pointer in `research_library`, then the hub
  `central-command` — innermost first, walk outward.
