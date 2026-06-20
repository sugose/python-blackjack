# Next Session — Pending Items

Items to action at the start of the next session. Clear this file once actioned.

## Pending investigations

| # | Item |
|---|---|
| 1 | **Copilot review automation** — investigate GitHub ruleset approach ("Create ruleset for default branch" in repo Settings → Copilot Code Review) as a replacement for the manual "Request" click. Current `request-copilot-review.yml` workflow does not trigger the actual Copi review — it only no-ops against an already-present reviewer. Ruleset may be the correct native mechanism. If rulesets work, `request-copilot-review.yml` can be removed from both repos. |
