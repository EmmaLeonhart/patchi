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

1. **LT-5 · the control-system reframing — argue, don't assert.** Write a short,
   grounded position (FINDINGS section or `docs/`) on Pygmalion's "neural nets are
   information-flow controllers, not learners" claim: present attention-as-gain
   (Vaswani) as the nearest *real* mechanism and state plainly where the claim is
   the notebook's thesis vs. established. No code; verifiable = written + cited.

(Findings publishing is continuous — each item updates `FINDINGS.md` + `docs/`.)

When this drains, refill from `todo.md` (the hardest reaches: full topos internal
logic, a learned/adaptive memory gate, the linguistic pipeline).

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
