# Changelog

All notable changes to python-blackjack are documented here.

## [Unreleased]

### Added — Backlog housekeeping

- ICE-10–ICE-20 added to icebox: multi-seat play, back-betting, blackjack payout rounding, player identifier, event emission delay, session statistics and summary entities, dealer tipping, voluntary player departure, auto-evict on consecutive sit-outs, PlayerBooted behaviour, SitOut behaviour
- Tooling table added (T-1: Node.js version bump, T-2: PR process automation spec)
- `NEXT_SESSION.md` cleared

### Added — PR process automation

- Auto-Copilot review workflow (`.github/workflows/request-copilot-review.yml`) — fires on PR open, ready-for-review, and push; requests Copilot review via REST API (`POST /requested_reviewers`) instead of `gh` CLI (which fails via GraphQL)
- `synchronize` trigger added — Copilot re-review requested automatically on every push to an open PR
- New PR flow: Crog posts pr_dump as PR comment; Adam drops PR URL to Clead; Clead fetches directly from GitHub; Clead produces verdict + merge prompt in one step
- `CROG_ONBOARDING.md` and `TEAM_STRUCTURE.md` updated in both repos to reflect new flow

### Changed — Tooling

- `actions/checkout` bumped to v7.0.0 (Node.js 24, closes T-1)
- `actions/setup-python` bumped to v6.2.0 (Node.js 24, closes T-1)

## [0.5.0] - 2026-06-19

### Changed — PBI-1.5: Event Model Refactor

- All `eventType` literals migrated to PascalCase: `BetPlaced`, `CardDealt`, `CardDrawn`, `StandDeclared`, `HandBust`, `HoleCardRevealed`, `HandResolved`, `PayoutMade`, `WalletUpdated`, `PlayerLeft`, `SessionOpened`, `SessionClosed`, `HandStarted`, `ShoeShuffled`, `CutCardReached` — `WalletEmpty` unchanged
- JSONL filename format updated to session-bound with timestamp: `logs/blackjack-{YYYYmmddTHHMMSS}-{sessionId[-8:]}.jsonl`
- HRF tag alignment falls out automatically from PascalCase eventType rename
- All test assertions updated to PascalCase; new test added for JSONL filename pattern (`test_play_hand_standalone_session_file_matches_naming_pattern`)
- Pure refactor — no new behaviour, no new events, no changes to `GameEvent` dataclass or `emit_event()` signature

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
