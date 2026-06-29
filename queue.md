# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — (empty) — GD arc complete through significance testing

**GD-1..R5 done and pushed.** Pygmalion's "distance = number of shared words"
claim, tested over a WordNet shared-ancestor graph, is the project's **first
positive result**, now statistically scoped: structural similarity complements
cosine on SimLex, **bootstrap-significant on GloVe-50/100** (95% CI [+.057,+.142] /
[+.043,+.127]) but **not significant on fastText-300** (CI [−.008,+.075] crosses 0
— reported as non-significant, not spun). A 5-fold-CV learned combiner is ≥ cosine
on every cell and removes the flat-combine's fastText × WordSim loss. Suite 129
green, CI + pages green. Written up in `FINDINGS.md` Result 7 (+ two limitations
resolved), the docs, `REVIEW.md`, `sources.md`, `todo.md`.

**No item is auto-promoted — the remaining work needs a scope decision.** The one
untested part of Pygmalion's spectrum claim is the stimulator/inhibitor *polarity*
half, which WordNet's sparse antonyms left at noise (`signed_overlap` ≈ 0). Testing
it needs a **dense/signed relation graph** (ConceptNet or a co-occurrence graph) —
an external download, i.e. a scope decision, not an unblocked autonomous step. The
other `todo.md` directions (full topos internal logic; learned/adaptive memory
gate; full linguistic pipeline) are large and open-ended.

→ **Work-loop: report `nothing actionable` until the user picks a direction.** The
most bounded next candidate is the signed-graph polarity test (ConceptNet), but it
should not be started autonomously because it pulls an external dependency.

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
