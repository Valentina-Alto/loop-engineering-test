# Loop Engineering — Test Repo

A runnable companion to **Chapter 7: Loop Engineering** of *Agentic Development in Practice*.
It ships the full delivery loop (P0–P8) as real GitHub primitives so you can **watch a feature
go from a filed issue to a governed merge** — driven either from the cloud (the Copilot coding
agent) or from your terminal (`/loop` in GitHub Copilot CLI).

> **The one idea:** you don't prompt the agent — you *engineer the loop that prompts it*. Here it
> is as versioned, reviewable infrastructure. You show up at exactly two gates: **approve the
> plan**, **authorize the merge**.

---

## What's in the box

| Primitive | File | Loop stage |
|---|---|---|
| Always-on rulebook | `.github/copilot-instructions.md` | P1 / P6 |
| Delivery-loop skill | `.github/skills/deliver-feature/SKILL.md` | P1 ("how we ship") |
| CLI entry-point prompt | `.github/prompts/deliver-feature.loop.md` | P0 (`/loop`) |
| Loop-ready issue form | `.github/ISSUE_TEMPLATE/feature-loop.yml` | P1 (trigger input) |
| Trigger workflow | `.github/workflows/loop-dispatch.yml` | P0 (cron + `issues: assigned`) |
| Verify + done-condition | `.github/workflows/loop-verify.yml` | P4 + P8 |
| Guardrail hook | `.github/hooks/pre-pr.json` + `scripts/pre_pr_check.py` | P6 / bounds |
| Least-privilege MCP | `.vscode/mcp.json` | P5 / P7 |

**None of these artifacts mention the feature being built** — they are issue-agnostic. You build
the loop once; every future issue rides the same rails.

---

## One-time setup

1. **Make the repo public** (or have Actions minutes available). GitHub-hosted Actions are free
   on public repos; a personal-account billing lock blocks runs on private repos.
   `Settings → General → Danger Zone → Change visibility → Public`
2. **Create the two loop labels** (once):
   ```bash
   gh label create loop --description "Ride the delivery loop" --color 1f6feb
   gh label create loop-started --description "Loop already dispatched (idempotency)" --color 8250df
   ```
3. **For the cloud track:** enable the Copilot coding agent — `Settings → Copilot → Coding agent`.
4. **For the CLI track:** install GitHub Copilot CLI, run `copilot` inside this repo, `/login` if
   prompted.

---

## The demo in 60 seconds

File one ordinary issue, then choose how to drive it. The loop marks it started, posts its
understanding, plans **and waits for your approval**, implements in slices, verifies on every
push, auto-recovers from red checks, and **refuses to merge until every acceptance box is checked
with evidence and CI is green.** You approve the plan; you click merge. That's it.

---

## Track A — Triggered (cloud coding agent)

*"The loop that keeps running after you close the laptop."*

```bash
# P0 — file a loop-ready issue (or use the 🔁 Feature Loop template in the UI)
gh issue create --title "[loop] Book launch landing page" --label loop --body-file - <<'EOF'
## Goal
A simple, self-contained HTML landing page for the book launch.
## Acceptance criteria (machine-checkable)
- [ ] index.html renders title, subtitle, author, blurb, cover, CTA
- [ ] Responsive: no horizontal overflow at 375px and 1280px
- [ ] Accessibility checks pass (single h1, landmarks, alt text, contrast)
- [ ] CI green
EOF

# P0 — start the loop by handing the issue to the coding agent
gh issue edit <ISSUE#> --add-assignee "@copilot"
```

Then **watch it on GitHub**:

| Stage | What you see | Your move |
|---|---|---|
| **P0** Trigger | `loop-dispatch` adds `loop-started` + a kickoff comment | — |
| **P1** Normalize | Agent posts goals, constraints, assumptions, open questions | — |
| **P2** Plan | Agent opens a **draft PR** with the plan, then waits | 🚦 comment **`plan approved`** |
| **P3** Implement | Commits stream onto the PR branch | — |
| **P4** Verify | `loop-verify` runs on each push | — |
| **P5** Auto-recover | Red check → agent fixes itself (or nudge `@copilot fix the failing check`) | — |
| **P6/P7** Guardrails + memory | Push-to-main blocked; thread carries every decision | — |
| **P8** Done-condition | Gate stays red until all boxes checked + CI green | 🚦 click **Merge** |

Watch the run: `gh run watch $(gh run list --workflow loop-dispatch.yml -L1 --json databaseId -q '.[0].databaseId')`

---

## Track B — CLI `/loop` (drive it live in the terminal)

*"The loop you steer on stage."* Run `copilot` in this repo, then:

```text
/loop 15m advance the delivery loop for issue #<ISSUE#> by one stage using @.github/prompts/deliver-feature.loop.md
```

`/loop` schedules that prompt to re-run **for this session**; each tick advances the loop by
**one** stage and stops, so the human gates are always respected. Close the terminal and it stops
— that's the difference from Track A. Narrate as it moves:

1. **P1** — it posts understanding (no code yet).
2. **P2** — it posts the plan and **pauses**. Reply **`plan approved`** (in chat or on the issue).
3. **P3–P5** — it builds `feature/<#>-…`, `loop-verify` runs, it self-heals a red check.
4. **P8** — it announces "ready for merge" and stops. You **merge** on GitHub.

> Tip: for a snappier live demo use a short interval (`/loop 5m …`); to narrow it to just fixing
> CI on an open PR: `/loop 5m check the open PR for issue #<#>, read failing loop-verify checks,
> patch, push, repeat until green — do not merge`.

---

## The money moment — prove "PR opened" ≠ "done" (P8)

This is the single most important thing to show. On any open PR:

```bash
# 1) With unchecked boxes in the PR body → the gate BLOCKS merge
gh pr checks <PR#>          # → "P8 — done-condition (hard gate)  fail"

# 2) Check every acceptance box (edit the PR body), re-run:
gh pr checks <PR#>          # → "P8 — done-condition (hard gate)  pass"
```

The `done-condition` job counts `- [ ]` vs `- [x]` in the PR body and **fails while any box is
unchecked** — so the loop physically cannot declare itself finished early.

---

## Try the guardrail hook (P6) — no CI needed

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | python .github/hooks/scripts/pre_pr_check.py
# → pre-pr guard: BLOCKED — Direct push to `main` is not allowed. (exit 2)

echo '{"tool_input":{"command":"git push origin feature/4-launch-page"}}' | python .github/hooks/scripts/pre_pr_check.py
# → allowed (exit 0)
```

---

## Reset between demos

```bash
gh pr close <PR#> --delete-branch                    # drop the demo PR + branch
gh issue edit <ISSUE#> --remove-label loop-started   # let the loop re-fire
# or just open a fresh issue with the `loop` label for a clean P0→P8 run
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Workflow shows **"Startup failure"** / *"account locked due to a billing issue"* | Personal-account Actions billing lock | Make the repo **public**, or clear billing at `github.com/settings/billing` |
| `loop-dispatch` never fires | Issue has no assignee, or already has `loop-started` | Assign it; remove `loop-started` to re-fire |
| No **Copilot** assignee option | Coding agent not enabled | `Settings → Copilot → Coding agent` |
| `@.github/prompts/...` won't resolve in CLI | `copilot` not started from repo root | `cd` to repo root, relaunch; or inline the instruction |
| Two runs start for one issue | Cron + event both fired | Expected — `loop-started` makes dispatch idempotent, so no double-start |

See `.github/copilot-instructions.md` for the always-on rulebook the loop follows.
