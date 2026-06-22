# Next Session

## Status — ON HOLD until July 1 (Copi credits resume)

All `src/` PRs are frozen until Copi is back. No code merges until then.

PR #107 (PBI-2.1 — AI provider infrastructure) is open and approved by Clead
but not merged. Merge this first when Copi resumes and has reviewed it.

## July 1 startup sequence

1. Merge PR #107 after Copi reviews it — add `ai-review` label, wait for
   Copi review comment, then paste Clead verdict and merge.
2. PBI-2.2 — AI player strategy (wraps AIProvider in strategy callable).
3. Wire `ai` strategy into `src/play.py` launcher (T-5).

## Pending refinements (spec before July 1 if time allows)

- Table display layer — live per-player view during session: chip stacks,
  cards, hit/stand actions, hand outcome per player. Triggered by human
  play session experience. Needs design before implementation.
- `src/play.py` missing `logging.basicConfig` — HRF output not visible
  when entering via `python -m src.play`. One-liner fix, holds until July 1.
- Bot player display names with strategy in parentheses — already possible
  via naming convention at CLI, no code change needed.

## Backlog reminders

- ICE-2 test gaps (four specific paths)
- Chaos Mode icebox spec completion

## Copi resume checklist (July 1)

- [ ] Validate label-based flow: add `ai-review` to PR #107, confirm Copi
      runs once, confirm no token drain
- [ ] Update community discussion:
      https://github.com/orgs/community/discussions/186152
- [ ] Merge PR #107 once Copi review is clean
- [ ] Resume PBI-2.2
