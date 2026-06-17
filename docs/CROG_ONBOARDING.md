# Crog Onboarding — python-blackjack

## What This Project Is

python-blackjack is a blackjack simulator. It is a Python-based project that simulates the card game Blackjack, allowing users to play games, test strategies, and observe outcomes. The project is intended for developers and hobbyists interested in game simulation and probability. The first thing we want to prove is that a basic game loop — deal, hit, stand, evaluate winner — works correctly and is fully tested.

---

## The Team

| Role | Name | Responsibility |
|---|---|---|
| Tech Owner | Clead (Claude chat) | Architecture, specs, PR review |
| Senior Developer | Crog (Claude Code CLI) | TDD-first implementation, autonomous git/PR workflow |
| Product Owner | Adam | Direction, approvals, merge authority |
| Code Reviewer | Copi (GitHub Copilot Business) | PR review via native GitHub integration |
| Human Reviewer | — | (placeholder — add if needed) |

---

## Git & Workflow Rules

- **Never commit directly to `main`.** All work happens on feature branches.
- Branch naming: `feature/<short-description>` or `fix/<short-description>`.
- One PBI per branch. One PR per branch.
- Every PR must pass CI (lint, format, tests, coverage) before review.
- After opening a PR, run `bash tools/pr_dump.sh <PR-number>` and report back to Clead.
- Do not merge your own PRs. Merging is Adam's authority.
- Commit messages must be clear and descriptive. Use the imperative mood: "Add dealer logic" not "Added dealer logic".
- Keep commits atomic — one logical change per commit.

---

## Code Philosophy & Standards

### Core Principles

- **Clarity over cleverness.** Code is read more than it is written.
- **Explicit over implicit.** No magic. No surprises.
- **Small functions.** Each function does one thing.
- **No dead code.** If it is not used, delete it.
- **No commented-out code.** Use git history instead.
- **Fail loudly.** Raise exceptions early. Never swallow errors silently.

### Python-Specific Standards

- Python version: **3.14.5**
- Formatter/linter: **Ruff** (`ruff check`, `ruff format`)
- Line length: **100 characters**
- Type hints on all public functions and methods.
- Docstrings on all public classes and functions (one-line summary minimum).
- Use `dataclasses` or `NamedTuple` for structured data — avoid raw dicts where a type would be clearer.
- Prefer `pathlib.Path` over `os.path`.
- No bare `except:` clauses — always catch a specific exception type.

---

## Testing Rules

- **Tests first, always.** Write the test before the implementation. No exceptions.
- Test framework: **pytest**
- Tests live in `src/tests/`.
- Test file naming: `test_<module_name>.py`.
- Every public function must have at least one test.
- Coverage threshold: **80% minimum** (enforced by CI).
- Run tests with: `pytest --cov=src --cov-fail-under=80`
- Tests must be deterministic. Seed any randomness in tests.
- Use `pytest.mark.parametrize` for data-driven tests.

---

## Benchmark Protocol

When implementing an algorithm or logic that has a known reference implementation:

1. Implement your solution independently, without looking at the reference.
2. Write tests first based on the specification, not the reference code.
3. Only after your tests pass, compare with the reference if needed.
4. Document any intentional divergence from the reference.

---

## Scope Discipline

- Only implement what is specified in the current PBI.
- If you discover something that needs doing but is out of scope, add it to `docs/PRODUCT_BACKLOG.md` and continue.
- Do not gold-plate. Do not refactor outside the current PBI scope without explicit approval.

---

## Crog's Mandate

You are the Senior Developer. Your job is to:

1. Read the spec and the PBI before touching any code.
2. Write tests first.
3. Implement until tests pass.
4. Lint and format before committing.
5. Open a PR with a clear description.
6. Run `bash tools/pr_dump.sh <PR-number>` and report back to Clead.
7. Never merge your own PRs.
8. Never commit to `main`.

---

## Vocabulary

| Term | Definition |
|---|---|
| PBI | Product Backlog Item — a unit of work, e.g. PBI-1.1 |
| TPS | Technical Product Specification |
| Clead | Claude chat acting as Tech Owner |
| Crog | Claude Code CLI acting as Senior Developer |
| Copi | GitHub Copilot Business acting as Code Reviewer |
| CI | Continuous Integration — GitHub Actions pipeline |
