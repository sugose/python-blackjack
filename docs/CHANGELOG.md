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
- Copi review trigger changed from ruleset-driven (`review_on_push: true`) to label-driven via `.github/workflows/copilot-review.yml`. Adding the `ai-review` label triggers a single Copi review. Conserves credits and gives explicit control over when Copi engages.
- Removed `tools/copi_wait.sh` — no longer needed under label-based flow.
- Shelved dummy.txt re-review pattern investigation — irrelevant under label-based flow.
