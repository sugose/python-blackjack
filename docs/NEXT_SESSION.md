# Next Session

## Active pins (re-pin at session start)

**Pin A — Table queue (ICE-3 design)**
- Players arriving mid-hand go into table queue (FIFO)
- Before each hand: seating procedure processes queue; full table → PlayerRejected
- Rejected players pushed back to FM hall queue (VIP queue if player.vip = True)
- New events: PlayerQueued, PlayerRejected
- Goodwill credit: FM distributes on rejection

**Pin B — Cross-repo sync (ai-project-template + fomo-f)**
- Port to `ai-project-template`: process changes from PRs #71, #72, #73 (Copi gate rule, src/-only workflow trigger, pr_dump fenced code block), plus any earlier items not yet synced (PR flow hard stop rule, copi_wait.sh known limitation, console summary rule, Epic 2 backlog structure)
- Check `fomo-f` for consistency
- Depends on main being clean ✅

## Process notes
- Copi review applies to code PRs (`src/`) only. Docs/tooling PRs skip Copi and go straight to Clead.
- `request-copilot-review.yml` now scoped to `src/**` — Copi will not auto-invoke on docs/tooling PRs.
- `pr_dump.sh` output is wrapped in a fenced code block — inline comment bodies now render correctly when Clead fetches a PR.
- Copi re-review known limitation: no public API can re-trigger Copi after first review. After pushing a fix, run `bash tools/copi_wait.sh <PR-number>`. If timeout: click "Re-request review" in GitHub UI, then run again.
- Console summary rule: Crog posts 3–5 line summary as separate PR comment when scripts run, non-zero exit, or diagnostic task.
- Hard stop rule: after posting pr_dump, Crog stops. Wait for Adam to paste Clead's instruction before acting on any Copi finding.
- `python -m tools.<script>` is the correct invocation for scripts in `tools/` (direct `python tools/...` fails without PYTHONPATH).
- `HouseRules.multiSeatAllowed` is docs-only — add to `src/table.py` when ICE-3 is next touched.

## PRs merged this session
#71 — Copi gate rule formalised (docs/tooling PRs skip Copi)
#72 — request-copilot-review.yml scoped to src/** only
#73 — pr_dump.sh output wrapped in fenced code block
