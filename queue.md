# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — GD-R8: bring the published paper (PAPER.md) current with Results 5–8

**Why.** `PAPER.md` (the standalone clawRxiv paper, distinct from `FINDINGS.md`
which builds the report PDF) **predates the entire GD arc**. Its abstract,
results, discussion, and conclusion present only the all-negative blending story
("on real data, negative… a noise-conditional smoother") and omit the generality
result (Result 5), phrase composition (6), and the whole **positive
relational-similarity finding** (Results 7–8) that is now the project's actual
headline. That is a correctness gap in a published artifact — the paper currently
states the *opposite* of the project's main conclusion. Bounded, unblocked (prose
only, verified against the measured numbers already in `FINDINGS.md`), no new
dependency.

- **GD-R8 · Update `PAPER.md` to the two-sided story.** Revise the **abstract**
  (geometric reconstruction loses *but* relational/taxonomic structure
  significantly complements cosine on genuine similarity); add a **results**
  subsection condensing Results 5–8 (generality 0/6; phrase additive>weighted;
  structural first-positive; the Wu-Palmer/path baseline that beats Pygmalion's
  count while the phenomenon is real, bigger, and significant on all 3 embeddings);
  update **Methods** (3 embeddings × 2 datasets, bootstrap + 5-fold CV, WordNet
  structural measures); rewrite **Discussion/Conclusion** to "loses as geometry,
  wins (significantly, with path similarity) as relational structure on
  genuine-similarity judgements"; refresh **Limitations** (resolve the
  one-embedding/one-dataset caveat; keep the ConceptNet polarity gap). Add
  references (Miller 1995 WordNet; Wu & Palmer 1994; Leacock-Chodorow 1998). Every
  number must match `FINDINGS.md` — cross-check, do not invent. HARD RAIL: keep the
  Result-8 demotion of Pygmalion's specific metric in the paper, stated plainly.
  **Do NOT re-publish to clawRxiv** — that needs an API key + `--confirm`, a user
  action; note that in `devlog.md`.

**After GD-R8,** the only remaining reach is the ConceptNet signed-graph *polarity*
test (external download → scope decision, not auto-promoted).

**No item is auto-promoted after that — the remaining work needs a scope decision.** The one
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
