# Next Session

## Active pins (re-pin at session start)

**Pin A — Table queue (ICE-3 design)**
- Players arriving mid-hand go into table queue (FIFO)
- Before each hand: seating procedure processes queue; full table → PlayerRejected
- Rejected players pushed back to FM hall queue (VIP queue if player.vip = True)
- New events: PlayerQueued, PlayerRejected
- Goodwill credit: FM distributes on rejection

## Process notes
- Copi first invocation: automatic via ruleset ("Copilot review for default branch") on all PRs.
- Copi re-review (src PRs): always manual — Adam clicks "Re-request review" in GitHub UI.
- Copi re-review (non-src PRs): not expected by default; only if Clead explicitly instructs.
- `pr_dump.sh` output is wrapped in a fenced code block.
- Hard stop rule: after posting pr_dump, Crog stops. Wait for Adam to paste Clead's instruction.
- `python -m tools.<script>` is the correct invocation for scripts in `tools/`.
- `HouseRules.multiSeatAllowed` is docs-only — add to `src/table.py` when ICE-3 is next touched.
- No Copi credits: skip `copi_wait.sh`, post pr_dump, state "Copi credits exhausted" in report.

## Backlog (next up)
- ICE-3 — Multiplayer (fully specced TPS Section 10, `src/session.py` and `src/table.py` exist, ready to implement) ← **next**
- T-2 — CI validator for eventType consistency

## PRs merged last session
#77 — TD-1: `_emit_wallet` wallet check `== 0.0` → `<= 0.0`
#78 — tooling: revert Copi review workflow to gh CLI
#79 — PBI-1.6: schemaVersion field on GameEvent
#80 — tooling: add --repo flag and || true to Copi review workflow
#81 — docs: CROG_ONBOARDING Copi flow update
