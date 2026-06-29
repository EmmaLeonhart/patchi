# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — GD: graph-degree structural similarity (Pygmalion's "shared-neighbor distance")

**Why now.** Emma re-supplied Pygmalion's full notebook (`data_lake/proto.txt`).
Its most-repeated *untested* empirical claim is **"distance between words = the
number of words they have in common"** / "similarity by graph degree"
(proto.txt L229–235, L308–316). Every empirical result so far is about *vector
reconstruction* (blend ≤ raw, 0 of 6) — a geometric signal. Structural /
relational similarity from an **independent** relation source (WordNet) is a
genuinely different signal the negative results never touched. Falsifiable
question in two parts: (1) does neighbourhood-overlap similarity correlate with
human similarity at all? (2) does combining it with cosine beat cosine alone —
i.e. does Pygmalion's relational signal add what reconstruction could not?

- **GD-4 · Reconcile `todo.md`.** Mark the graph-degree similarity thread's status
  (done / remaining reach, e.g. learned edge weights or a real multi-relational
  graph beyond WordNet). Keep `todo.md` items abstract.

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
