# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — (empty) — GD arc complete; paper brought current

**GD-1..R8 done and pushed.** The relational-similarity thread is the project's
first positive result, fully scoped (Result 7 + the Result 8 baseline comparison),
and the standalone clawRxiv paper (`PAPER.md`) is now consistent with it: the
abstract, methods, results, discussion, limitations, and conclusion all carry the
two-sided story (loses as geometry, wins as relational structure; cos+path
significant on all 3 embeddings; Pygmalion's specific metric demoted). Numbers
cross-checked against `FINDINGS.md`. **Not re-published** — clawRxiv re-submit needs
an API key + `--confirm` (a user action). Suite 129 green, CI + pages green.

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
