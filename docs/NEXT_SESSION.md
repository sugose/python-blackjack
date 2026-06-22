# Next Session

## Priority

1. Formalise dummy.txt pattern — create `docs/dummy.txt` (gitignored), document in CROG_ONBOARDING.md that Crog appends a line per iteration before posting pr_dump. Update ai-project-template to match.
   - Posted findings on Copi re-review behaviour to https://github.com/orgs/community/discussions/186152 — check for responses and incorporate into investigation when Copi resumes.
   - Target flow when Copi resumes:
     - i=1: src push → Copi auto-invokes → Crog detects and hands back
     - i>1: docs push (append line to dummy.txt) immediately followed by src push, in the same iteration → observe whether Copi auto-invokes on src push → Crog detects and hands back
     - This folds the docs touch into every fix iteration as an invisible implementation detail. Tests whether the pattern holds beyond i=3 naturally over real PRs.
2. Human session launcher TPS update — add `src/play.py` to Section 12 of TECHNICAL_PRODUCT_SPECIFICATION.md.

## Backlog reminders

- PBI-1.6 — schemaVersion field
- TD-1 — wallet check operator fix
- ICE-2 test gaps (four specific paths)
- Chaos Mode icebox spec completion
