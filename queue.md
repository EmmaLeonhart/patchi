# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — GD-R4: is the structural gain statistically real? (significance + k-fold)

**Why.** The whole positive result (Result 7) rests on small Spearman gains
(+0.03…+0.10) measured once. Two named limitations make it attackable: no
significance test (is +0.087 just noise?) and a single deterministic train/test
split (not k-fold). Both are fixable with **only cached data + the already-
downloaded WordNet** — no external dependency, no scope decision. This is the
unblocked, bounded "keep persisting" task.

- **GD-R4 · `scripts/run_structural_significance.py`.**
  1. **Paired bootstrap CI** on the headline deltas. For each embedding × dataset,
     resample the usable pairs with replacement (B = 2000, seeded RNG for
     reproducibility); on each resample recompute `spearman(combined_flat0.5)` and
     `spearman(cosine)` and their difference. Report the observed delta, the 95%
     percentile CI, and `P(delta > 0)`. Headline question: on SimLex, is
     `combined − cosine` CI strictly above 0 for the GloVe embeddings?
  2. **5-fold cross-validation** of the learned λ (finer grid, 0.05 step) replacing
     the single even/odd split: per fold, learn λ on the other 4, score the
     held-out fold; report mean test Spearman (cosine vs learned) ± std across
     folds. This removes the "single split / coarse grid" limitation and should let
     λ→0 tie cosine exactly on fastText × WordSim (killing the −0.008 artefact).
  Write `results/structural_significance_benchmark.json`. RUN it; record the real
  numbers. HARD RAIL: if a gain's CI includes 0, say so plainly — a non-significant
  gain is reported as non-significant, not spun.
- **GD-R5 · Write up + reconcile.** Fold the CIs and CV numbers into `FINDINGS.md`
  Result 7 (and update the two limitations they resolve); update the docs if the
  significance claim changes the headline; mark the limitation closed in `todo.md`.

**After GD-R4/R5,** the only remaining reach is the ConceptNet signed-graph
*polarity* test, which needs an external download → still a scope decision for the
user, not auto-promoted.

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
