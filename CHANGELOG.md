# Changelog

All notable changes to python-blackjack are documented here.

## [Unreleased]

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
