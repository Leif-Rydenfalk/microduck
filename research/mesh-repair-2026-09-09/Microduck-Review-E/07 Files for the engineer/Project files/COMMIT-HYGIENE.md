# Repository history: a warning about over-collecting commits

**Written 2026-09-02 by the session that caused the problem, so it is not
discovered later as a mystery.**

## What happened

This repository is worked by several concurrent Claude sessions, each owning a
lane (drawings, test plan, electronics, sourcing, structural, ...). Several
agents write files at the same moment.

One session committed with `git add -A`. That stages **everything currently in
the working tree**, not the files that session authored. So its commits swept in
whatever the other lanes happened to have half-written at that instant, under a
commit message describing only its own work.

## The commits affected

| commit | message describes | files committed | of which authored by that session |
|---|---|---|---|
| `e63dd4f` | "stress: FEA matrix completed" | 312 | ~7 |
| `77cbd91` | "workflows: stop manufacturing workflow" | 86 | ~4 |
| `9aeb5b9` | "photo-vs-CAD reference-match dossier" | 59 | ~20 |
| `960943a` | "correct the head finding" | 37 | ~5 |
| `1e81af2` | "data-driven reference-match dossier" | 32 | ~12 |

`e63dd4f` is the worst: **305 of its 312 files belong to other lanes** —
`ELECTRONICS-DATASHEET.html`, `MANUFACTURING-PLAYBOOK.html`, `STRUCTURAL.html`,
`TEST-PLAN.html`, `spec/test-plan.json`, `tools/gen_test_plan.py`, and ~290
`ce-parts/*/interfaces.json` and `component.json` files.

## What was and was not damaged

- **No content was lost or reverted.** `git add -A` stages the working tree as
  it is; it does not roll anything back. Lane H's `245746f` (Rev B) landed at
  23:12:41 on top of `e63dd4f` (23:08:29) and was unaffected.
- **History is mislabelled.** Anyone running `git log -- spec/test-plan.json`
  sees an FEA commit in the middle of the test-plan lane's history. That is
  noise, and it is why lane H believed another session was editing its files.
- **Files may have been committed mid-write.** A generator that was part-way
  through writing when `add -A` ran would be committed in a torn state. Any lane
  whose file looks wrong at one of the commits above should regenerate it rather
  than trust that snapshot.

## The rule

**Never `git add -A` (or `git commit -a`, or `git add .`) in this repository.**
Stage explicit paths you authored:

    git add COMPARISON.html tools/gen_comparison.py out/verify/mech_dims.json
    git commit -m "..."

`ce-workshop/ce-designs/microduck/tools/commit-lane.sh` exists for exactly this
and takes a lane name plus explicit paths. Prefer it.

History is deliberately **not** rewritten. Rebasing shared history while other
sessions hold the working tree would be far more destructive than the mislabelled
commits it would tidy.
