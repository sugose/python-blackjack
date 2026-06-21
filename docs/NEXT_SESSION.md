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
- No Copi credits: skip `copi_wait.sh`, post pr_dump, state "Copi credits exhausted" in report.
- Changed file URLs: use `blob/<branch>/` (not `blob/main/`) with `?pr=<N>&i=<iteration>` on every re-report. See `docs/CROG_ONBOARDING.md` for format.
- Copi suspended mode: documented in `docs/CROG_ONBOARDING.md` — skip `copi_wait.sh`, report PR URL + changed file URLs, Clead reviews full file context as sole reviewer.

## Backlog (next up)
- No active python-blackjack PBI next — icebox review or new PBI to be decided next session
- ICE-3 multiplayer housekeeping complete (`multiSeatAllowed` added, soft-17 tests added) — full ICE-3 implementation still in icebox

## PRs merged this session
#82 — docs: housekeeping — backlog and NEXT_SESSION refresh
#83 — ICE-3 housekeeping: add multiSeatAllowed to HouseRules and soft-17 tests
#84 — docs: add Copi suspended mode to CROG_ONBOARDING and TEAM_STRUCTURE
#85 — docs: fix changed file URLs to use head branch instead of main
#86 — T-2: add eventType CI validator test
#87 — docs: add HOW_WE_WORK.md — collaboration model documentation
