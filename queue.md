# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — (empty) — GD thread drained; hand-back point reached again

**The GD (graph-degree structural similarity) thread is complete.** Emma's
re-supplied notebook (`data_lake/proto.txt`) foregrounded Pygmalion's "distance =
number of shared words" claim; it is now tested and written up — the project's
**first positive result** (`FINDINGS.md` Result 7: WordNet shared-ancestor
structure complements GloVe cosine on SimLex-999, combined 0.383 > cosine 0.296).
`structural.py` + 13 tests (suite 129 green), `run_structural.py`, FINDINGS / docs
/ REVIEW / sources updated, `todo.md` MVC-2 reconciled with the remaining reach.

**No item is auto-promoted, by design.** What remains in `todo.md` is large,
open-ended research directions that each need a scope/product decision (full topos
internal logic; learned/adaptive memory gate; the full linguistic pipeline; the GD
reach — a *learned* combiner and a *dense signed* relation graph for the polarity
half). The hard rails forbid fake-decomposing these.

→ **Work-loop: report `nothing actionable` until the user picks a direction.** The
GD reach (learned combiner / signed graph) is the most bounded next candidate if
the user wants the loop to continue.

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
