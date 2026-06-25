# PATCHi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — minimum viable core (MVC)

Pulled from `todo.md` MVC-1…5. Build under `src/`, entry point `scripts/run.py`,
metrics to `results/`. Write tests as soon as there is logic; wire `ci.yml` once
tests exist. Keep `FINDINGS.md` + `docs/` current as results land.

1. **MVC-2 · Signed relation graph.** Build a synonym(+)/antonym(−) graph with
   relations as offsets; test that offset arithmetic recovers held-out relations
   on a tiny fixture.
2. **MVC-3 · Similarity-weighted blending operator + benchmark.** Implement
   `blend(w) = Σ sim(w,sᵢ)·poly(sᵢ)`. **Benchmark head-to-head** vs additive and
   tensor baselines on a concrete task (word/phrase similarity or analogy) with a
   small public dataset; write metrics to `results/` and the comparison into
   `FINDINGS.md`. This is the headline result — keep the rails: report real
   numbers, never claim "works" without a measured run.
3. **MVC-4 · Infon/situation layer.** `⟨R, args, polarity⟩` + graded
   `support(s, σ) ∈ [0,1]`; test that context-conditioning changes an output.
4. **MVC-5 · Proof(walk) trace.** Thread an explainability trace through blend +
   support so every output records its contributing words/relations.
5. **Publish first findings.** Fill `FINDINGS.md` (question, method, the MVC-3
   numbers, limitations) and update `docs/index.html` findings section + lede so
   the live page shows a real result. Confirm CI + Pages green.

When this drains, refill from `todo.md` (the bridges: BR-1 translator, etc.).

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
- This is a **nested submodule** (`research_library/projects/PATCHi`). When
  pushing here, bump the pointer in `research_library`, then the hub
  `central-command` — innermost first, walk outward.
