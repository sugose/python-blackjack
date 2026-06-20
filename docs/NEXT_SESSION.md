# Next Session — Pending Items

Items to action at the start of the next session. Clear this file once actioned.

## Pending actions

| # | Item |
|---|---|
| 1 | **Copi review of ICE-2** — ICE-2 merged without full Copi review due to process gap; create a trivial fix PR touching `src/` (e.g. a minor docstring or comment improvement in `src/viewer.py`) to give Copi a proper pass at the implementation |
| 2 | **Update CROG_ONBOARDING** — one PR covering: (a) when reporting PR URL to Adam, append `?i=N` query string starting at 1, incrementing on each re-report of the same PR; (b) Crog waits for Copi review to complete before posting PR URL; (c) after each push on an existing PR, Crog explicitly re-requests Copi review via REST API before polling; (d) Crog outputs status message when Copi review is detected (or timeout message after 60s if not) |

## Pending investigations

| # | Item |
|---|---|
| 1 | **Copi re-review on push not firing reliably** — GitHub ruleset has `review_on_push: true` confirmed enabled (Settings → Rules → Rulesets → "Review new pushes" ✅). Despite this, Copi does not automatically re-review on subsequent pushes to open PRs. Root cause unknown — could be quota/rate limiting, a GitHub bug, or push-source restrictions. Manual re-request via GitHub UI works every time. Investigate why the correctly-configured ruleset is not firing reliably. |
| 2 | **Fetch caching on multi-iteration PRs** — `web_fetch` returns cached content on repeated fetches of the same URL; workaround is `?i=N` query string cache-busting. Investigate whether there is a more reliable solution. |
