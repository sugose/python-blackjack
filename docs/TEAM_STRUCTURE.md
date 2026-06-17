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

Every PR reviewed by Clead must include all of the following, without being asked:

**1. Threat model statement**
Before the review findings, state what threat model is being applied. Example:
> "Reviewing this as a game engine — primary risks are incorrect payout logic, silent state mutation, and non-deterministic test failures."

**2. TPS compliance check**
Every code PR must be checked against `docs/TECHNICAL_PRODUCT_SPECIFICATION.md`. Explicitly confirm or flag:
- Does the implementation match what the TPS says this component must do?
- Does the public interface (function signatures, return types, error behaviour) match the TPS contract?

**3. Focused second pass on error handling and type validation**
After the general review, always do an explicit second pass covering:
- Every validation function: are edge cases handled correctly?
- Every error path: are exceptions caught at the right level?
- Every external input: is it validated before use?
- Any type coercion that could silently accept unexpected values?

**4. Test quality check**
Coverage percentage and test count are necessary but not sufficient. Every code PR must include a test coverage narrative table in the PR description. Clead must verify:
- Does the table exist? If not, request it before approving.
- For each row in the table: does the named test actually assert what the table claims?
- Are all non-trivial error paths and recovery behaviours represented?
- For every error path in the implementation, is there a test that verifies the correct recovery behaviour (not just that a warning was logged)?

**5. What I did not check**
Every approval must end with an explicit list of what was not verified. Example:
> "Did not check: interaction with other modules not in this diff; behaviour under concurrent access."

These requirements exist because Clead reviews from the diff only (not the full file), which creates structural blind spots. Copi reads full files and catches cross-section inconsistencies — Clead's role is architectural alignment, spec compliance, and test quality. Together they cover different failure modes.

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
