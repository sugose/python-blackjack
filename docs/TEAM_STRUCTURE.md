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

**A — Feature/Fix PR (code)**
1. Crog opens PR from `feature/<name>` or `fix/<name>` to `main`
2. Crog posts pr_dump as PR comment: `gh pr comment <PR-number> --body "$(bash tools/pr_dump.sh <PR-number>)"` and reports PR URL to Adam with `?i=1` (increment `i` by 1 on each re-report of the same PR)
3. Adam drops URL into Clead's chat
4. Clead fetches PR directly, reads diff + Copi comments + pr_dump
5. If changes needed: Clead produces fix prompt → Adam pastes → Crog implements only what the prompt specifies → pushes → posts pr_dump → reports `?i=1` to Adam (increment `i` by 1 on each re-report of the same PR) → **stops and waits**. Go back to step 3.
6. If approved: Clead produces verdict + merge prompt → Adam pastes → Crog posts comment and merges

**B — Docs/Tooling PR** (Copi is not involved — go straight to Clead)
1. Crog opens PR from `docs/<name>` or `tooling/<name>` to `main`
2. Crog posts pr_dump as PR comment: `gh pr comment <PR-number> --body "$(bash tools/pr_dump.sh <PR-number> --no-src)"` and reports PR URL to Adam with `?i=1` (increment `i` by 1 on each re-report of the same PR)
3. Adam drops URL into Clead's chat
4. Clead fetches PR directly, reads diff + pr_dump
5. If Clead requests changes: Clead produces fix prompt → Adam pastes → Crog implements only what the prompt specifies → pushes → posts pr_dump → reports `?i=1` to Adam (increment `i` by 1 on each re-report of the same PR) → **stops and waits**. Go back to step 3.
6. If approved: Clead produces verdict + merge prompt → Adam pastes → Crog posts comment and merges

**Hard stop rule:** After posting the pr_dump and reporting back to Adam, Crog stops completely — for both PR types. For code PRs, this follows Copi's review; for docs/tooling PRs, Copi is not involved and the stop applies immediately after posting pr_dump. In both cases: Crog does not read or act on Copi's comments, does not push any fix based on Copi's findings, and waits for Adam to paste Clead's instruction. Clead is the mandatory gate on every iteration. No exceptions except Crog's own unambiguous mechanical mistakes before the first Clead review.

---

## Copi suspended mode

When Adam announces "Copi suspended", all PR reviews run without Copi until Adam announces resumption.

**Crog behaviour:**
- Skip Copi review entirely (Copi is triggered via the `ai-review` label on Clead's instruction — not by Crog).
- After opening PR and posting pr_dump, report PR URL and changed file URLs to Adam (file URL reporting applies to all PR reports — see `docs/CROG_ONBOARDING.md`).
- Clead reviews with full file context as sole reviewer.
- Fix loop continues as normal (Clead ↔ Crog) until Clead approves.

**Clead behaviour:**
- Reviews full file content (not diff-only) for each changed file.
- Flags if additional files outside the PR are needed for cross-module review.
- Issues verdict and merge prompt as normal.

On resumption, standard Copi flow resumes immediately.

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

**6. Verdict prompt discipline**
Clead's verdict is delivered as a single Crog prompt with no preamble or chat commentary. The review summary goes into the PR comment via Crog — not into the chat. The prompt block must be the only content in Clead's post so Adam can copy-paste it directly.

**7. Copi review gate**
Clead's verdict prompt includes a merge instruction if and only if Copi has completed its review and has no open comments requiring resolution. If Copi has not yet reviewed, or has open comments, the verdict prompt must not include a merge instruction — the merge prompt is issued separately once Copi is satisfied. This gate applies to code PRs only. Docs/tooling PRs do not require Copi review and may be merged on Clead's approval alone.

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
3. Crog implements, opens a PR, posts pr_dump as PR comment, and reports back to Adam with `?i=1`.
4. Adam drops the PR URL into Clead's chat. Clead fetches and reviews directly from GitHub.
5. Adam pastes Clead's verdict prompt. Crog posts verdict comment and merges.
6. Adam updates `CHANGELOG.md` and moves to the next PBI.

**Parallel PRs:** When two or more PRs have no dependencies between them, Crog may work on them in parallel — opening PR B while Copi is reviewing PR A. Adam handles multiple PRs by dropping URLs to Clead in sequence as they arrive. Clead reviews each independently and produces separate verdict prompts.
