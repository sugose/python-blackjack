# Next Session — Pending Items

Items to action at the start of the next session. Clear this file once actioned.

---

## Icebox additions (add to PRODUCT_BACKLOG.md)

| # | Item |
|---|---|
| 1 | **Multi-seat play** — one player occupying multiple seats, playing multiple simultaneous hands |
| 2 | **Back-betting** — non-seated player places a side bet on a seated player's hand; seated player retains hit/stand authority; new events `BackBetPlaced`, `BackBetPaid` |
| 3 | **Blackjack payout rounding** — when minimum bet doesn't divide cleanly into 3:2 payout, define rounding policy (round down, round up, even-money offer, 50-cent chip). Relevant when ICE-7 introduces variable bet sizes and configurable payout ratios |
| 4 | **`HandResolved` on player bust in `play_hand()`** — `play_hand()` in `game.py` does not emit `HandResolved` on player bust; `play_table_session()` does. Inconsistency will break ICE-2 and ICE-4 consumers. Also fix `== 0.0` wallet check in `_emit_wallet()` (TD-1) |
| 5 | **Player identifier** — add `playerId: str` (UUID4) to `Player` dataclass; key internal session state by `playerId` rather than `name` |
| 6 | **Event emission delay** — configurable delay between events for human-readable dashboard playback; `emit_delay_ms: int | None = None` parameter on `play_table_session()` and `play_session()`; disabled by default so tests are unaffected; target range 200–500ms |
| 7 | **Session statistics / KPI tracking** — per-player and house-level running stats updated after each hand: hands played, wins, losses (non-bust), busts, pushes, blackjacks, P&L (cumulative and per-hand). Available during session, not just post-hoc. Feeds ICE-4 and ICE-9 |
| 8 | **`PlayerSession` and `TableSession` entities** — structured session summary entities; `TableSession` holds sessionId, tableId, handsPlayed, startedAt, closedAt, terminationReason, housePnl; `PlayerSession` holds sessionId, playerId, playerName, startingWallet, finalWallet, handsPlayed, stats. Supersedes `finalWallet` in `SessionClosed`. Prerequisite for item 7 |
| 9 | **Dealer tipping** — players can tip the dealer outside normal bet/payout flow; `Dealer` gains `tips: float` field; new `TipGiven` event (actor: player, data: amount, recipient: dealer); tips excluded from house P&L, tracked separately in session stats |
| 10 | **Player and table P&L / KPI tracking** — folded into item 7 |
| 11 | **Voluntary player departure** — player chooses to leave the table between hands with remaining funds; `PlayerLeft` with `reason: "voluntary"`; requires a mechanism to signal intent (likely via FM in ICE-8 or a future strategy interface extension) |
| 12 | **Auto-evict on consecutive sit-outs** — configurable house rule that removes a player after N consecutive `SitOut` events; N configurable per table via `houseRules`; fires `PlayerLeft` with `reason: "sit-out limit reached"` |
| 13 | **`PlayerBooted` behaviour** — FM removes a player from the table or hall (event already reserved in TPS Section 9); spec the trigger conditions, FM authority rules, and whether booted player can re-enter |
| 14 | **`SitOut` behaviour** — player skips a hand without placing a bet (event already reserved in TPS Section 9); spec the flow, wallet impact (none), and interaction with auto-evict rule (item 12) |

---

## Tooling / infra

| # | Item |
|---|---|
| T-1 | **GitHub Actions Node.js version bump** — bump `actions/checkout` and `actions/setup-python` to latest versions targeting Node.js 24; fixes deprecation warning in CI |
| T-2 | **PR process automation** — spec out a CI validator for eventType consistency against TPS reserved table; identify other automation opportunities in the review cycle |

---

## Tech debt

| # | Item |
|---|---|
| TD-1 | **`== 0.0` wallet check in `play_hand()` / `game.py`** — `_emit_wallet()` uses `player.wallet == 0.0`; should be `<= 0.0` to handle float rounding edge cases. Fix when next touching `game.py` |
