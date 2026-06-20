# Next Session — Pending Items

Items to action at the start of the next session. Clear this file once actioned.

## Pending actions

| # | Item |
|---|---|
| 1 | **ICE-2 viewer test gaps** — follow-up PR to close 4 missing test paths identified in Crog's post-merge review: (a) `eventId` UUID suffix match, (b) `~=` on absent field returns False, (c) `actor!=player` and `actor!=dealer` abstract semantics, (d) non-dict JSON line warning path (e.g. `[1,2,3]`) |
| 2 | **CHANGELOG** — update with: ICE-2 post-merge Copi findings fix (PR #53), copi_wait.sh fixes (PR #55) |
| 3 | **`copi_wait.sh` sync to ai-project-template** — PR #55 fixed the completion loop logic in python-blackjack; same fix needs porting to `sugose/ai-project-template` (currently still has `TOTAL > 0` condition) |
| 4 | **Document post-merge review process** — established this session: when a PR is merged without sufficient Copi iterations, correct remedy is VS Code Copilot full-file review of all changed files, findings fed back to Clead, fix PR opened for any material findings. Add to `docs/TEAM_STRUCTURE.md` under Clead Review Standard. |

## Pending investigations

| # | Item |
|---|---|
| 1 | **Copi re-review on push not firing reliably** — `review_on_push: true` confirmed enabled. Despite correct config, Copi does not automatically re-review on subsequent pushes. `copi_wait.sh` is the workaround. Investigate via Chrome DevTools: capture the exact request made when manually clicking "Re-request review". |
| 2 | **Fetch caching on multi-iteration PRs** — `web_fetch` returns cached content on repeated fetches of the same URL; workaround is `?i=N` query string cache-busting. |
| 3 | **`~=` on absent field semantics** — currently returns False (field absent = no match). Not documented in TPS Section 11. Clarify and document before PBI-1.6. |
