# Product Backlog — python-blackjack

## How to Use This Backlog

- PBIs are numbered sequentially: PBI-1.1, PBI-1.2, PBI-2.1, etc.
- The first number is the epic; the second is the item within the epic.
- Adam picks the next PBI and hands it to Crog via a task prompt.
- Completed PBIs are marked ✅ and recorded in CHANGELOG.md.

---

## Epic 1 — Core Game Engine

| ID | Description | Status |
|---|---|---|
| PBI-1.1 | Implement Card, Deck, Hand, and deal_initial — 52-card deck, seeded shuffle, O(1) deal, opening hand with dealer hole card, full validation at construction | ✅ Done |
| PBI-1.2 | Play out a single hand end-to-end — player and dealer turns, betting, payout, wallet, logging | ✅ Done |
| PBI-1.3 | Structured logger — `GameEvent` dataclass, `emit_event()` JSONL + HRF output, refactor `play_hand()` to carry session/hand context | ✅ Done (PR #12) |
| PBI-1.4 | Game session loop — multi-hand session with shared deck, cut-card reshuffle policy, session open/close logging, wallet termination | ✅ Done (PR #12) |
| PBI-1.5 | Event model refactor — PascalCase eventTypes, session-bound JSONL filename, HRF tag alignment | 🔲 Not started |

---

## Icebox

| ID | Description |
|---|---|
| ICE-1 | Card counting strategy — pluggable card behaviour (hit/stand based on running count) and pluggable bet behaviour (bet size based on running count). Requires extending the strategy interface to take deck state as input. |
| ICE-2 | JSONL viewer — reads session files, replays event stream hand by hand; requires PBI-1.5 stable event format |
| ICE-3 | Multiplayer — introduces a `Table` entity with attributes: `tableId` (UUID), `maxSeats` (capacity, e.g. 7), `minBet` / `maxBet` (betting limits), `numDecks` (shoe size — 1/2/4/6/8), `players` (seated players, length ≤ maxSeats), `dealer`, and `houseRules` (blackjack payout ratio, soft 17 rule). Requires new events: `TableOpened`, `TableClosed`, `PlayerSeated`, `PlayerJoined`. Multiple concurrent players share a single shoe. |
| ICE-4 | Casino operations dashboard — real-time JSONL event aggregator that watches `logs/`, tails all active session files, and displays live casino-level statistics: active sessions, total hands played, house P&L, player win/loss/push rates, bust rates (player vs dealer), blackjack frequency, wallet trajectories per active session, and a live feed of recent hand outcomes. Requires PBI-1.5 stable event format. Builds on but is independent from ICE-2 (single-session replay). |
| ICE-5 | ML player strategy — train a classifier on simulated session JSONL data (hand state → action → outcome), wrap inference in the `strategy: Callable[[Hand], str]` interface, and plug into `Player` as a drop-in replacement for the deterministic strategy. Natural sequence: data generation → training → strategy plug-in → evaluation against deterministic baseline. Requires PBI-1.5 stable event format for training data collection. |
| ICE-6 | Human player strategy — interactive CLI strategy that blocks on `input()` for hit/stand decisions, surfacing the player's hand value and dealer upcard to the human before each decision. Requires extending the strategy interface from `Callable[[Hand], str]` to `Callable[[Hand, Card], str]` to pass the dealer upcard into the strategy function. Plug-in point is the existing `Player.strategy` callable — no changes to `play_hand()` or `play_session()` beyond the signature extension. |
| ICE-7 | Extended table rules — implements the remaining standard blackjack rule set as a bundle: (1) **Double down** — player doubles bet after initial deal, receives exactly one more card then stands; (2) **Split** — if first two cards share identical value, split into two independent hands each with their own bet; (3) **Insurance** — side bet of up to half the original bet when dealer shows Ace, pays 2:1 if dealer has blackjack; (4) **Surrender** — player folds before playing, recovers half the bet (late surrender — after dealer checks for blackjack); (5) **Soft 17 rule** — configurable dealer behaviour on soft 17 (hit or stand), added to `houseRules`; (6) **Blackjack payout ratio** — configurable 3:2 or 6:5, added to `houseRules`. Requires new events: `DoubleDown`, `SplitTaken`, `InsuranceTaken`, `InsurancePaid`, `SurrenderTaken`. All rules configurable via `houseRules` so they can be toggled per table. |
