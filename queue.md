# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — GD-R2: learned/weighted cosine+structural combiner

**Context.** GD-1..R1 are done and pushed (suite 129 green, CI green): Pygmalion's
"distance = number of shared words" claim, tested over a WordNet shared-ancestor
graph, gives the project's **first positive result** — structural similarity
*complements* cosine on SimLex-999 across all three embeddings (+0.100 / +0.086 /
+0.034). The one place a **flat equal-weight** rank-average *hurts* is
fastText × WordSim (−0.104, cosine dominates). That negative cell is a property of
the unweighted combiner — the obvious, bounded next step is to learn the weight.

Emma asked to barrel through with the research loop, so this is promoted to active
(not parked). It is bounded, verifiable, and uses only cached data + WordNet.

- **GD-R2 · `scripts/run_structural_weighted.py` (or extend `run_structural.py`).**
  `combined(λ) = (1−λ)·rank(cosine) + λ·rank(adamic_adar)`. For each embedding ×
  dataset, pick λ on a **train split** (maximise Spearman) and report Spearman on a
  held-out **test split** — a proper split so the lift is not overfit (HARD RAIL:
  do not tune on the test set, do not report the train-optimal as if it were the
  result). Sweep λ ∈ {0,0.1,…,1}. Compare test-set: cosine alone vs flat-0.5 vs
  learned-λ. Expect learned-λ ≥ cosine everywhere (λ→0 collapses to cosine, so it
  can fold the fastText × WordSim loss back to ~break-even) and ≥ flat-0.5 on
  SimLex. Write `results/structural_weighted_benchmark.json`; RUN it; record real
  numbers, whichever way they go.
- **GD-R3 · Write up + reconcile.** Fold the learned-combiner numbers into
  `FINDINGS.md` Result 7 (does a tuned weight remove the one negative cell and lift
  the SimLex gains?) and the docs; mark the MVC-2 "learned combiner" reach in
  `todo.md` done/remaining. State numbers flatly.

When GD-R2/R3 drain, the next bounded reach is a **dense/signed relation graph**
(ConceptNet / co-occurrence) to test the stimulator-inhibitor *polarity* half that
WordNet's sparse antonyms left at noise — but that needs an external download
(scope decision), so park it for the user unless explicitly told to fetch it.

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
