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
- Port to `ai-project-template`: PR flow hard stop rule, copi_wait.sh known limitation, console summary rule, Epic 2 backlog structure
- Check `fomo-f` for consistency
- Depends on main being clean ✅

## Process notes
- Copi re-review known limitation: no public API can re-trigger Copi after first review. After pushing a fix, run `bash tools/copi_wait.sh <PR-number>`. If timeout: click "Re-request review" in GitHub UI, then run again.
- Console summary rule: Crog posts 3–5 line summary as separate PR comment when scripts run, non-zero exit, or diagnostic task.
- Hard stop rule: after posting pr_dump, Crog stops. Wait for Adam to paste Clead's instruction before acting on any Copi finding.
- `python -m tools.<script>` is the correct invocation for scripts in `tools/` (direct `python tools/...` fails without PYTHONPATH).
- `HouseRules.multiSeatAllowed` is docs-only (PR #58) — add to `src/table.py` when ICE-3 is next touched.

## PRs merged this session
#58–#69 (process fixes, Copi investigation, TPS Section 12, multiplayer log analysis)
