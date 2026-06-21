# Changelog

All notable changes to python-blackjack are recorded here.

## [Unreleased]

### Added
- ICE-6: Human player strategy — `src/strategy.py` with `Strategy` type alias, `adapt()` compat shim, and `human_strategy` CLI implementation
- Human session launcher — `src/play.py` invocable as `python -m src.play` with `--name`, `--wallet`, `--bet`, `--decks`, `--hands`, `--seed` flags
- T-2: CI eventType validator — AST-based validator ensuring all eventTypes in src are in the known set
- `tools/copi_wait.sh` timeout increase — detection 120s, completion 360s

### Changed
- Strategy interface extended to `Callable[[Hand, Card], str]` — dealer upcard now passed to all strategies
- `src/session.py` and `src/game.py` updated to pass dealer upcard via `adapt()`
- `CROG_ONBOARDING.md` updated — Copi re-review via `synchronize` trigger documented; manual re-request step removed
