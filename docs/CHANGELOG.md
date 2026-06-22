# Changelog

All notable changes to python-blackjack are recorded here.

## [Unreleased]

### Added
- `docs/COPILOT_LIMITATIONS.md` — operational guide to GitHub Copilot code review limitations, mitigations, and label-based review control model (v3)
- `docs/COPILOT_REVIEW_MS_VARIANT.md` — Microsoft-only stack variant of the review model (human tech lead + Copilot Chat replacing AI tech lead)
- `docs/CLEAD_ONBOARDING.md` — Clead session startup checklist and dynamic review depth policy

### Added — T-4: Mixed-player table launcher

- `src/play.py` replaced with multi-player launcher — `--players name:strategy:wallet` flag accepts one or more player specs
- Built-in strategies: `human` (interactive CLI), `mirror` (hit ≤16/stand 17+), `hit` (always hit), `stand` (always stand)
- Validation: missing/malformed specs, unknown strategy, wallet ≤ 0, duplicate names, invalid `--decks`, `--hands < 1` — all exit 1 with stderr message
- `src/tests/test_play.py` updated: 12 tests covering all new behaviours

### Changed — CROG_ONBOARDING.md: removed stale copi_wait.sh polling instructions

- "Copi review flow" section replaced with correct label-based description: Crog does not interact with Copi at all
- Code PRs review steps updated: pr_dump posted immediately after opening PR, no polling step
- Crog's Mandate steps 6 and 7 updated to reference label-based flow

### Changed
- TPS Section 12: added Human Session Launcher subsection documenting `src/play.py` flags, validation, and behaviour
- `docs/HOW_WE_WORK.md` — added Copi evolution note (always-on → label-based) and hard stop rule enforcement sentence
- `.github/workflows/copilot-review.yml` — upgraded to v3: concurrency block, `if: always()` label cleanup, label auto-removed after every run
- Copilot review trigger changed from ruleset-driven to label-driven (`ai-review` label)
- `tools/copi_wait.sh` removed — no longer needed under label-based flow
- `src/play.py` — human session launcher added (see PR #91)

---

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
