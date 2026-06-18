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
| ICE-3 | Multiplayer — table ID, seat numbers, PlayerSeated/PlayerJoined events, multiple concurrent players |
