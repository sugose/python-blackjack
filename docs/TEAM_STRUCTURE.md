# Team Structure — python-blackjack

## Team

| Role | Name | Tool | Responsibility |
|---|---|---|---|
| Product Owner | Adam | claude.ai (browser) | Direction, approvals, merge authority |
| Tech Owner | Clead | claude.ai (browser) | Architecture, specs, PR review |
| Senior Developer | Crog | Claude Code CLI | TDD-first implementation, autonomous git/PR workflow |
| Code Reviewer | Copi | GitHub Copilot Business | PR review via native GitHub integration |

---

## PR Workflow

### PR Directions

**A — Feature PR (Crog → main)**
1. Crog opens PR from `feature/<name>` to `main`.
2. Crog requests Copi review: `gh pr edit <PR-number> --add-reviewer copilot`
3. Crog waits for Copi review to complete.
4. Crog runs `bash tools/pr_dump.sh <PR-number>` and reports to Clead with the full output.
5. Clead reviews in Claude chat.
6. Adam merges once CI is green and Clead approves.

**B — Fix PR (Crog → main)**
1. Crog opens PR from `fix/<name>` to `main`.
2. Crog requests Copi review: `gh pr edit <PR-number> --add-reviewer copilot`
3. Crog waits for Copi review to complete.
4. Crog runs `bash tools/pr_dump.sh <PR-number>` and reports to Clead with the full output.
5. Clead reviews in Claude chat.
6. Adam merges once CI is green and Clead approves.

**C — Spec/Docs PR (Clead → main)**
1. Clead produces updated doc content.
2. Crog writes the file to disk, commits, and opens a PR.
3. Skip Copi — docs-only PR.
4. Crog runs `bash tools/pr_dump.sh <PR-number>` immediately and reports to Clead.
5. Adam reviews and merges directly.

---

## Clead Review Standard

Every PR review from Clead covers all five of these points:

1. **Correctness** — Does the implementation match the TPS and PBI spec?
2. **Test quality** — Are tests meaningful? Do they cover edge cases? Are they deterministic?
3. **Code clarity** — Is the code readable? Are names clear? Are functions small and focused?
4. **Error handling** — Are errors raised explicitly? No silent failures?
5. **Scope discipline** — Does the PR contain only what the PBI asked for?

---

## Branch Protection

| Rule | Setting |
|---|---|
| Restrict deletions | ✅ Enabled |
| Require pull request | ✅ Required (0 approvals — Clead is the quality gate) |
| Required status check | ✅ `build` (CI must pass) |
| Require branch up to date | ✅ Enabled |
| Block force pushes | ✅ Enabled |

---

## Day-to-Day Workflow

1. Adam picks the next PBI from `docs/PRODUCT_BACKLOG.md`.
2. Adam pastes the Crog task prompt into Claude Code.
3. Crog implements, opens a PR, requests Copi review (code PRs only), waits for Copi to complete, runs `pr_dump.sh`, and reports back.
4. Clead reviews in Claude chat.
5. Adam merges on Clead's approval.
6. Adam updates `CHANGELOG.md` and moves to the next PBI.
