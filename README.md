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

*"The loop that keeps running after you close the laptop."* The entry-point primitive here is the
**`loop-dispatch.yml`** workflow: assigning the issue fires it, and it hands the work to the
Copilot coding agent, which then runs the same skill + instructions the CLI track uses.

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

| Stage | What you see | **Primitive at work** | Your move |
|---|---|---|---|
| **P0** Trigger | `loop-dispatch` adds `loop-started` + a kickoff comment | **`loop-dispatch.yml`** reacts to `issues: assigned`; `feature-loop.yml` shaped the issue input | — |
| **P1** Normalize | Agent posts goals, constraints, assumptions, open questions | **`copilot-instructions.md`** — auto-loaded by the coding agent, it's the policy source for this track (the cloud agent does *not* auto-load skills) | — |
| **P2** Plan | Agent opens a **draft PR** with the plan, then waits | **`copilot-instructions.md`** P2 rule: "stop and wait for `plan approved`" | 🚦 comment **`plan approved`** |
| **P3** Implement | Commits stream onto the PR branch | **`copilot-instructions.md`** P3: bounded, intent-named slices | — |
| **P4** Verify | `loop-verify` runs on each push | **`loop-verify.yml`** — lint/unit/integration/contract + fixture test | — |
| **P5** Auto-recover | Red check → agent fixes itself (or nudge `@copilot fix the failing check`) | **`.vscode/mcp.json`** (least-privilege GitHub MCP) lets it read CI logs + write the thread | — |
| **P6/P7** Guardrails + memory | Push-to-main blocked; thread carries every decision | **`pre-pr.json`** hook (P6 bounds); the issue/PR thread is the memory (P7) | — |
| **P8** Done-condition | Gate stays red until all boxes checked + CI green | **`loop-verify.yml`** `done-condition` job counts `- [ ]` vs `- [x]` | 🚦 click **Merge** |

Watch the run: `gh run watch $(gh run list --workflow loop-dispatch.yml -L1 --json databaseId -q '.[0].databaseId')`

---

## Track B — CLI `/loop` (drive it live in the terminal)

*"The loop you steer on stage."* Run `copilot` in this repo, then:

```text
/loop 15m advance the delivery loop for issue #<ISSUE#> by one stage using @.github/prompts/deliver-feature.loop.md
```

**The only primitive that changes between the two tracks is the entry point.** Track A's entry
point is the **`loop-dispatch.yml`** workflow (cloud); Track B's is **`deliver-feature.loop.md`**
scheduled by `/loop` (local). From P1 onward the *behaviour* is identical because both tracks run
against the same P0–P8 policy and the same issue/PR thread. The one nuance: the cloud agent reads
its policy from **`copilot-instructions.md`** (it doesn't auto-load skills), while the CLI track
reads it from **`deliver-feature/SKILL.md`** — the two are kept in lock-step on purpose. Everything
downstream (`loop-verify.yml`, `pre-pr.json`, `.vscode/mcp.json`) is shared. That shared thread is
why either track can start the work and the other can finish it.

`/loop` schedules that prompt to re-run **for this session**; each tick advances the loop by
**one** stage and stops, so the human gates are always respected. Close the terminal and it stops
— that's the difference from Track A. Narrate as it moves:

1. **P0/P1** — **`deliver-feature.loop.md`** loads **`SKILL.md`** + **`copilot-instructions.md`**, reads the issue via the **`.vscode/mcp.json`** connector, and posts understanding (no code yet).
2. **P2** — following the **`copilot-instructions.md`** plan-gate rule, it posts the plan and **pauses**. Reply **`plan approved`** (in chat or on the issue).
3. **P3–P5** — per **`SKILL.md`**, it builds `feature/<#>-…` in slices; **`loop-verify.yml`** runs on each push; on a red check it self-heals through the MCP connector. The **`pre-pr.json`** hook keeps it off `main`.
4. **P8** — **`loop-verify.yml`**'s `done-condition` job blocks it until every box is checked; then it announces "ready for merge" and stops. You **merge** on GitHub.

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
