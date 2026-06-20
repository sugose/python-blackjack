# Next Session — Pending Items

Items to action at the start of the next session. Clear this file once actioned.

## Pending actions

| # | Item |
|---|---|
| 1 | **Copi review of ICE-2** — ICE-2 merged without full Copi review due to process gap; create a trivial fix PR touching `src/` (e.g. a minor docstring or comment improvement in `src/viewer.py`) to give Copi a proper pass at the implementation |
| 2 | **Template repo sync** — mirror all doc and tooling changes from this session to `sugose/ai-project-template`: `CROG_ONBOARDING.md`, `TEAM_STRUCTURE.md`, `tools/copi_wait.sh`, and enable `review_on_push` ruleset if not already set |

## Pending investigations

| # | Item |
|---|---|
| 1 | **Copi re-review on push not firing reliably** — GitHub ruleset has `review_on_push: true` confirmed enabled. Despite this, Copi does not automatically re-review on subsequent pushes. Root cause unknown. `copi_wait.sh` now handles re-request and polling as the workaround. Investigate via Chrome DevTools: capture the exact request made when manually clicking "Re-request review" to see if a different endpoint is used. |
| 2 | **Fetch caching on multi-iteration PRs** — `web_fetch` returns cached content on repeated fetches of the same URL; workaround is `?i=N` query string cache-busting. Investigate whether there is a more reliable solution. |
