# Changelog

All notable changes to python-blackjack are documented here.

## [Unreleased]

## [0.4.0] - 2026-06-18

### Added — PBI-1.4: Game Session Loop

- `play_session(player, max_hands=10, cut_card=39, seed=None)` — multi-hand session loop
- Cut card policy: reshuffles when `len(deck) <= max(cut_card, 4)` to guarantee deal safety
- Session terminates on wallet = 0 or max hands reached
- New events: `OPEN`, `HAND`, `CUT`, `SHUFFLE`, `LEAVE`, `CLOSE`
- `main.py` now calls `play_session()` instead of a single hand

## [0.3.0] - 2026-06-18

### Added — PBI-1.3: Structured Logger

- `GameEvent` dataclass — `eventType`, `sessionId`, `handId` (optional), `actor` (optional), `eventId` (UUID4 auto-generated), `timestamp` (ISO-8601 UTC auto-generated), `data: dict[str, Any]`
- `emit_event(event, session_file)` — writes JSON object to JSONL file and HRF one-liner to stdout via `logging`
- JSONL output: per-session file at `logs/session-{sessionId[-8:]}.jsonl`; write failures warn and never crash
- HRF format: `[EVENTTYPE] | sess:{8} | hand:{8} | evt:{8} | actor:{name} — {message}`; `hand:` and `actor:` omitted for session-level events
- `play_hand()` refactored: accepts `session_id`, `session_file`, `deck` — seed and deck creation removed
- `play_hand_standalone()` wrapper added for single-hand use
- `TABLE` event retired; `WalletEmpty` fires from `play_hand()` on zero wallet; `LEAVE` fires from `play_session()`
- `PAYOUT` event added at all payout points (blackjack 3:2, win 1:1, push)
- `logs/` added to `.gitignore`

## [0.2.0] - 2026-06-17

### Added — PBI-1.2: Single Hand Engine

- `src/logger.py` — structured event logger; `log_event(tag, message)` emits `[TAG] message` at INFO level via Python `logging`
- `src/player.py` — `Player` dataclass; wallet (100 UoM default), fixed 1 UoM bet (`init=False`), pluggable strategy callable, `place_bet()` / `receive_payout()`
- `src/dealer.py` — `Dealer` with fixed hit-on-16/stand-on-17 strategy and `reveal_hole_card()`
- `src/game.py` — `play_hand()` orchestrating bet → deal → player turn → dealer turn → outcome → wallet update with full structured logging; `_log_wallet()` helper; handles all outcomes: player BJ, dealer BJ, both BJ, player bust, dealer bust, push, player wins, dealer wins
- `src/main.py` — CLI entry point with default strategy mirroring dealer; configures `logging.basicConfig(level=INFO, format="%(message)s")`
- 74 tests across 4 new test files; 93.5% coverage

## [0.1.0] — 2026-06-17

### Added
- Initial project setup
- PBI-1.1: Implement Card, Deck, Hand, and deal_initial (52-card deck, seeded shuffle, O(1) deal, opening hand with dealer hole card, full validation at construction)
