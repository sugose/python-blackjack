# Next Session

## Active pins (re-pin at session start)

**Pin A — Table queue & intoxication model (ICE-3 design)**
- Players arriving mid-hand go into table queue (FIFO)
- Before each hand: seating procedure processes queue; full table → PlayerRejected
- Rejected players pushed back to FM hall queue (VIP queue if player.vip = True)
- New events: PlayerQueued, PlayerRejected
- Goodwill credit: FM distributes on rejection; amount/threshold lowers as FM intoxication rises
- Three-axis intoxication model per actor:
  - Player: erratic decisions (DecisionPoint.PLAY error rate), tips more/larger/biased toward drinks
  - FM: mutates HouseRules/ChaosRules, goodwill credit threshold/amount lowers
  - Dealer: mutates HouseRules/ChaosRules
- Feedback loop: FM drinks → more goodwill drinks to players → players tip FM drinks → FM more intoxicated → rules change + more generous → repeat
- `player.levelOfIntoxication` → strategy error rate
- `fm.levelOfIntoxication` / `dealer.levelOfIntoxication` → HouseRules/ChaosRules mutation + generosity axis

**Pin B — ICE-21: Chaos Mode (icebox — low priority)**
- `ChaosRules` dataclass on `Table`
- `bustThreshold: int = 26` — FM raises bust limit
- `dual_value_cards: dict[str, tuple[int, int]]` — FM-designated arbitrary dual values (e.g. `{"5": (5, -5)}`, `{"7H": (7, 17)}`). Values are arbitrary per FM proclamation, NOT derived from ace formula. Negative values allowed.
- New events: `FMDeclaredRule`, `DealerImprovisedRule`, `FMTookOverTable`, `RulesViolation`, `CasinoShutdown`
- Implementation: two primitives — card value override lookup + bust threshold check
- ICE-21 v1: table-level `ChaosRules` only
- ICE-21 v2: player-level override with inheritance from table (same pattern as HouseRules)
- FM/player intoxication cascade feeds into Chaos Mode

**Pin C — Cross-repo sync (ai-project-template + fomo-f)**
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
