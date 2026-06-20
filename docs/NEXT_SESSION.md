# Next Session — Pending Items

Items to action at the start of the next session. Clear this file once actioned.

## Pending actions

| # | Item |
|---|---|
| 1 | **ICE-2 viewer test gaps** — follow-up PR to close 4 missing test paths identified in Crog's post-merge review: (a) `eventId` UUID suffix match, (b) `~=` on absent field returns False, (c) `actor!=player` and `actor!=dealer` abstract semantics, (d) non-dict JSON line warning path (e.g. `[1,2,3]`) |
| 2 | **CHANGELOG** — update with ICE-2 post-merge Copi findings fix (PR #53) |
| 3 | **Template repo sync** — mirror PR #53 viewer fixes to `sugose/ai-project-template` if applicable (likely not — viewer is project-specific) |

## Pending investigations

| # | Item |
|---|---|
| 1 | **Copi re-review on push not firing reliably** — `review_on_push: true` confirmed enabled. Despite correct config, Copi does not automatically re-review on subsequent pushes. `copi_wait.sh` is the workaround. Investigate via Chrome DevTools: capture the exact request made when manually clicking "Re-request review". |
| 2 | **Fetch caching on multi-iteration PRs** — `web_fetch` returns cached content on repeated fetches of the same URL; workaround is `?i=N` query string cache-busting. |
| 3 | **`~=` on absent field semantics** — currently returns False (field absent = no match). Not documented in TPS Section 11. Clarify and document before PBI-1.6. |
