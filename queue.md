# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — GD-R6: contextualize the structural measure vs textbook WordNet similarity

**Why (the skeptic's question).** Result 7 says Pygmalion's *shared-ancestor*
adamic-adar carries similarity signal complementary to cosine. The obvious
challenge: "that is just a WordNet similarity, and Wu-Palmer / path similarity are
the standard ones — does your formulation actually differ, or does it merely
reproduce a textbook measure?" Answering it is fully unblocked: nltk's
`wup_similarity` / `path_similarity` ship with the **already-downloaded** WordNet,
no external dependency. Bounded, verifiable (Spearman vs human), and it sharpens
the contribution either way (distinct → a real formulation; same → "Pygmalion's
shared-neighbour idea reconstructs known WordNet similarity, itself complementary
to distributional cosine" — a clearer, still-valid story).

- **GD-R6 · `scripts/run_structural_baselines.py`.** For each WordSim-353 /
  SimLex-999 pair compute the standard WordNet measures (max over synset pairs, the
  usual convention): **Wu-Palmer**, **path**, and (same-POS) **Leacock-Chodorow**.
  Spearman vs human on the *same* head-to-head sets as Result 7; tabulate alongside
  adamic-adar (the project's structural measure) and GloVe cosine. Then ask the
  combine question: does `cosine + wup` do as well as / better than
  `cosine + adamic_adar` (flat rank-average) on SimLex? Write
  `results/structural_baselines_benchmark.json`. RUN it; record the real numbers.
  HARD RAIL: if a textbook measure matches or beats adamic-adar, say so plainly —
  that reframes the contribution, it does not get buried.
- **GD-R7 · Write up + reconcile.** Fold the comparison into `FINDINGS.md` Result 7
  (is the structural signal distinct from textbook WordNet similarity?), update the
  docs framing if it changes, cross-ref `REVIEW.md`, note the measures in
  `sources.md`, reconcile `todo.md`. State numbers flatly.

**After GD-R6/R7,** the only remaining reach is the ConceptNet signed-graph
*polarity* test (external download → scope decision, not auto-promoted).

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
