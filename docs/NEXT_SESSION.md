# Next Session — Pending Items

Items to action at the start of the next session. Clear this file once actioned.

## Pending actions

| # | Item |
|---|---|
| 1 | **Copi review of ICE-2 (#42)** — ICE-2 merged without full Copi review due to process gap; create a trivial fix PR on `src/viewer.py` (fix `~~=` docstring typo in `test_match_event_contains_operator`) to give Copi a proper pass at the implementation |
| 2 | **CHANGELOG** — add entries for ICE-2 (PR #42) and Copi review gate / process docs (PR #44) |
| 3 | **Update CROG_ONBOARDING** — when reporting PR URL to Adam, append `?i=N` query string (starting at 1, incrementing on each re-report of the same PR) so Clead can cache-bust GitHub's page cache on repeated fetches |

## Pending investigations

| # | Item |
|---|---|
| 1 | **Copilot review automation** — investigate GitHub ruleset approach ("Create ruleset for default branch" in repo Settings → Copilot Code Review) as a replacement for the manual "Request" click. Current `request-copilot-review.yml` workflow does not trigger the actual Copi review — it only no-ops against an already-present reviewer. Ruleset may be the correct native mechanism. If rulesets work, `request-copilot-review.yml` can be removed from both repos. |
| 2 | **Fetch caching on multi-iteration PRs** — `web_fetch` returns cached content on repeated fetches of the same URL; workaround is `?i=N` query string cache-busting (see pending action 4). Investigate whether there is a more reliable solution. |
