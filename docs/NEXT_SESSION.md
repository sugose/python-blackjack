# Next Session

## Active pins (re-pin at session start)

**Pin A — Table queue (ICE-3 design)**
- Players arriving mid-hand go into table queue (FIFO)
- Before each hand: seating procedure processes queue; full table → PlayerRejected
- Rejected players pushed back to FM hall queue (VIP queue if player.vip = True)
- New events: PlayerQueued, PlayerRejected
- Goodwill credit: FM distributes on rejection

## Process notes
- Copi review applies to code PRs (`src/`) only. Docs/tooling PRs skip Copi and go straight to Clead.
- `request-copilot-review.yml` scoped to `src/**` — Copi will not auto-invoke on docs/tooling PRs.
- GitHub ruleset "Copilot review for default branch" disabled on all three repos (python-blackjack, ai-project-template, fomo-f) — workflow is sole Copi trigger.
- `pr_dump.sh` output is wrapped in a fenced code block — inline comment bodies render correctly when Clead fetches a PR.
- Copi re-review known limitation: no public API can re-trigger Copi after first review. After pushing a fix, run `bash tools/copi_wait.sh <PR-number>`. If timeout: click "Re-request review" in GitHub UI, then run again.
- Console summary rule: Crog posts 3–5 line summary as separate PR comment when scripts run, non-zero exit, or diagnostic task.
- Hard stop rule: after posting pr_dump, Crog stops. Wait for Adam to paste Clead's instruction before acting on any Copi finding.
- `python -m tools.<script>` is the correct invocation for scripts in `tools/` (direct `python tools/...` fails without PYTHONPATH).
- `HouseRules.multiSeatAllowed` is docs-only — add to `src/table.py` when ICE-3 is next touched.

## Backlog (next up)
- PBI-1.6 — `schemaVersion` field on `GameEvent`
- ICE-3 — Multiplayer (fully specced, `session.py` and `table.py` exist, ready to implement)
- T-2 — CI validator for eventType consistency
- TD-1 — `play_hand()` wallet check `== 0.0` should be `<= 0.0`

## PRs merged last session
#71 — Copi gate rule formalised (docs/tooling PRs skip Copi)
#72 — request-copilot-review.yml scoped to src/** only
#73 — pr_dump.sh output wrapped in fenced code block
#74 — NEXT_SESSION.md updated (session close)
#75 — NEXT_SESSION.md trimmed (Chaos Mode/intoxication deferred)
