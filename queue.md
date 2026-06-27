# Patchi — Work Queue (research)

**Concrete, executable steps — not a state snapshot.** Finished work is deleted
from here and appended to `devlog.md` in the same commit, then pushed. No
checkmarks left in place. Long-horizon/abstract goals live in `todo.md`; the
literature review that grounds all of this is `literature/REVIEW.md`.

**Three-cron playbook is running this session** (work-loop :03, auto-flush :15,
status-report :42). The `## Always last` tail keeps them alive.

---

## Active — (empty) — hand-back point reached

**The bounded work is drained.** The MVC core, every bridge, every reduced-core
reach, the full empirical story (blend ≤ raw across 2 architectures × 2 datasets;
residual no-sweet-spot; phrase additive > weighted > multiplicative), the
end-to-end demo, the published paper, and the argued positions are all done. Suite
green, CI/Pages green, site + paper live.

**No item is auto-promoted, by design.** The only things left in `todo.md` are
large, open-ended *research directions*, each needing a scope/product decision —
not bounded hourly-tick work, and the hard rails forbid fake-decomposing them:

- **Full topos internal logic** (genuine subobject-classifier / full-image proofs)
  — hard mathematics, not a tick.
- **Learned / adaptive memory gate & "use the polynomial/region payload in the
  computation"** — needs a training setup + a product decision on scope.
- **The full linguistic pipeline** (syntax → semantics → pragmatics →
  world-knowledge over real text) — a large multi-stage build.
- **A real phrase-similarity dataset** (Mitchell & Lapata) — a download-dependent
  empirical extension, optional.

→ **Work-loop: report `nothing actionable` until the user picks a direction.** The
auto-flush + status crons keep running; they will not invent work.

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
