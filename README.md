# Loop Engineering — Test Repo

A runnable companion to **Chapter 7: Loop Engineering** of *Agentic Development in Practice*.
It ships a delivery loop as real, versioned GitHub primitives so you can **watch a feature go
from a filed issue to a governed merge** — driven from your terminal with the `/loop` command in
GitHub Copilot CLI.

> **The one idea:** you don't prompt the agent — you *engineer the loop that prompts it*. Here it
> is as reviewable infrastructure. You show up at exactly two gates: **approve the plan**,
> **authorize the merge**.

---

## Five capabilities, not eight phases

Every iteration of the loop passes through five recurring capabilities. That is the whole model:

1. **Discover** — read the issue, load repo conventions, turn an informal request into an
   executable objective. Ambiguity disappears; nothing is built yet.
2. **Plan** — produce a delivery plan (files, strategy, tests, assumptions), then **pause**.
   *(Human gate 1 — you review thinking, not typing.)*
3. **Execute** — once approved, the loop autonomously works in small, committed slices.
4. **Verify & Recover** — every iteration self-validates; a red check just becomes the next
   iteration's input. Recovery is part of the loop.
5. **Complete** — when every acceptance box is checked and CI is green, the loop prepares the PR
   and stops. *(Human gate 2 — you merge.)*

---

## The primitives that steer the loop

Six primitives, each with one job. Together they are everything the loop needs — and **none of
them mention the feature being built**, so you build the loop once and every issue rides it.

| # | Primitive | File | What it steers |
|---|---|---|---|
| 1 | **The engine** | `.github/prompts/deliver-feature.loop.md` | What `/loop` runs. One tick = advance **one** capability, then stop at the gates. |
| 2 | **The protocol** | `.github/skills/deliver-feature/SKILL.md` | The single source of truth for the five capabilities + the two gates. The engine invokes it every tick. |
| 3 | **The conventions** | `.github/copilot-instructions.md` | Always-on law (cadence, gates, guardrails), **auto-loaded every turn** — the loop's policy during **Discover**. |
| 4 | **The contract** | `.github/ISSUE_TEMPLATE/feature-loop.yml` | Forces a machine-checkable acceptance checklist — the objective **Discover** reads and the done-condition **Complete** closes on. |
| 5 | **The verifier** | `.github/workflows/verify.yml` | Runs on every push (**Verify & Recover**) *and* gates **Complete**: refuses to pass while any acceptance box is unchecked. |
| 6 | **The guardrails** | `.github/hooks/pre-pr.json` + `.vscode/mcp.json` | Keep **Execute** off `main`; give **Verify & Recover** least-privilege read-CI / write-thread access. |

---

## One-time setup

1. **Make the repo public** (or have Actions minutes available). GitHub-hosted Actions are free
   on public repos; a personal-account billing lock blocks runs on private repos.
   `Settings → General → Danger Zone → Change visibility → Public`
2. **Create the two loop labels** (once):
   ```bash
   gh label create loop --description "Ride the delivery loop" --color 1f6feb
   gh label create loop-started --description "Loop already started" --color 8250df
   ```
3. **Install GitHub Copilot CLI**, run `copilot` inside this repo, `/login` if prompted.

---

## Run the loop

### Step 1 — File a loop-ready issue (the contract)

Use the **🔁 Feature Loop** template in the UI, or:

```bash
gh issue create --title "[loop] Book launch landing page" --label loop --body-file - <<'EOF'
## Goal
A simple, self-contained HTML landing page for the book launch.
## Acceptance criteria (machine-checkable)
- [ ] index.html renders title, subtitle, author, blurb, cover, CTA
- [ ] Responsive: no horizontal overflow at 375px and 1280px
- [ ] Accessibility checks pass (single h1, landmarks, alt text, contrast)
- [ ] CI green
EOF
```

### Step 2 — Start the loop with `/loop`

Run `copilot` in this repo, then:

```text
/loop 15m advance the delivery loop for issue #<ISSUE#> by one capability using @.github/prompts/deliver-feature.loop.md
```

`/loop` schedules that prompt to re-run **for this session**; each tick advances the loop by
**one** capability and stops, so the gates are always respected. Close the terminal and it stops.

### Step 3 — Watch it move, and steer at the two gates

| Capability | What you see on the issue/PR thread | Primitive at work | Your move |
|---|---|---|---|
| **1. Discover** | Loop posts goals, constraints, assumptions, open questions — no code | **engine** reads the issue; **instructions** (`copilot-instructions.md`) + **protocol** (`SKILL.md`) shape the restatement; **contract** supplied the acceptance criteria | — |
| **2. Plan** | Loop posts a file map + test mapping + rollback, then **stops** | **protocol** — "produce a reviewable plan, then wait for `plan approved`" | 🚦 reply **`plan approved`** |
| **3. Execute** | Commits stream onto `feature/<#>-…` in small, intent-named slices | **engine** (one slice/tick) + **guardrail** `pre-pr.json` keeps it off `main` | — |
| **4. Verify & Recover** | `verify` runs on each push; a red check self-heals next tick | **verifier** `verify.yml`; **guardrail** `.vscode/mcp.json` lets it read CI + write the thread | — |
| **5. Complete** | Gate stays red until all boxes checked + CI green, then loop announces "ready" and stops | **verifier** `done-condition` job counts `- [ ]` vs `- [x]` | 🚦 click **Merge** |

> Tip: for a snappier live demo use a short interval (`/loop 5m …`). To narrow a run to just
> fixing CI on an open PR: `/loop 5m check the open PR for issue #<#>, read failing verify checks,
> patch, push, repeat until green — do not merge`.

---

## The money moment — prove "PR opened" ≠ "done" (Complete)

The single most important thing to show. On any open PR:

```bash
# 1) With unchecked boxes in the PR body → the gate BLOCKS merge
gh pr checks <PR#>          # → "Complete — done-condition (hard gate)  fail"

# 2) Check every acceptance box (edit the PR body), re-run:
gh pr checks <PR#>          # → "Complete — done-condition (hard gate)  pass"
```

The `done-condition` job counts `- [ ]` vs `- [x]` in the PR body and **fails while any box is
unchecked** — so the loop physically cannot declare itself finished early.

---

## Try the guardrail hook — no CI needed

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
# or just open a fresh issue with the `loop` label for a clean Discover→Complete run
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Workflow shows **"Startup failure"** / *"account locked due to a billing issue"* | Personal-account Actions billing lock | Make the repo **public**, or clear billing at `github.com/settings/billing` |
| `@.github/prompts/...` won't resolve in CLI | `copilot` not started from repo root | `cd` to repo root, relaunch; or inline the instruction |
| The loop implements before you approve | Plan gate skipped | It must **stop** after Plan — reply `plan approved` only when you mean it; see the skill's decision flow |
| Done-condition never passes | An acceptance box is still `- [ ]` | Edit the PR body, check every box with a link to evidence |

See `.github/copilot-instructions.md` for the always-on rules and `.github/skills/deliver-feature/SKILL.md` for the
full protocol the loop follows.
