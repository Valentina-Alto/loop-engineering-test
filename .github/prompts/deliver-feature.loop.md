---
name: deliver-feature-loop
description: >
  The schedulable prompt that drives the delivery loop from GitHub Copilot CLI.
  Pair it with `/loop` to run the same P0–P8 protocol locally that the Copilot
  coding agent runs in the cloud. Each tick advances the loop by exactly one
  stage and then stops, so the human gates are always respected.
argument-hint: "The loop issue number, e.g. 1"
---

# Recurring prompt: advance the delivery loop by one stage

This is the **CLI entry point** for the delivery loop. It is the local twin of the
`loop-dispatch.yml` workflow: where the workflow reacts to an assigned issue in the
cloud, this prompt is re-run on an interval by `/loop` on your machine.

Run it with:

```text
/loop 15m advance the delivery loop for issue #1 by one stage using @.github/prompts/deliver-feature.loop.md
```

`/loop` schedules this prompt to re-run for the session; each tick performs **one**
loop step, so closing the terminal stops the loop (this is the personal, session-scoped
altitude — promote it to `loop-dispatch.yml` when you want it to survive you).

## What to do on each tick

1. **Load policy.** Read `.github/copilot-instructions.md` and run the
   `deliver-feature` skill — that skill is the source of truth for the P0–P8 protocol.
2. **Acquire context (P0).** Identify the target loop issue (the number passed to this
   prompt, or the open issue labeled `loop`). Read the issue **and** any open PR that
   references it via the GitHub MCP connector. The issue/PR thread is the loop's memory
   (P7) — reconstruct current state from it, do not assume.
3. **Determine the current stage** from the thread:
   - No understanding comment yet → do **P1** (post goals, constraints, assumptions,
     open questions).
   - Understanding posted, no plan yet → do **P2** (post the reviewable plan), then
     **stop and wait** — do not implement until a human replies `plan approved`.
   - Plan not yet approved → **stop**. Re-check next tick. (Human gate 1.)
   - Plan approved, work remaining → do the next **P3** slice + ensure **P4** verify runs;
     on a red check or review comment, **P5** auto-recover.
   - All acceptance boxes checked + CI green → announce the loop is ready for the
     **merge gate** and **stop** — do not merge. (Human gate 2, P8.)
4. **Advance exactly one stage, then stop.** Post everything you did back to the thread
   so the next tick — or the cloud agent — can pick up where you left off.

## Non-negotiable bounds

- Never push directly to `main`; never bypass required checks (the `pre-pr` hook enforces
  this).
- Never cross a human gate autonomously: stop before implementing without `plan approved`,
  and stop before merging.
- Sensitive areas (auth, payments, PII, production) add a hard gate regardless of CI — halt
  and ask.
- This prompt is idempotent per tick: if the current stage is already satisfied, do nothing
  and wait for the next tick.
