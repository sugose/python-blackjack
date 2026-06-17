#!/usr/bin/env bash
# pr_dump.sh — bundle a Pull Request into a single text file for Clead's review.
#
# Sibling of dump.sh: where dump.sh gives Clead the whole repo for session
# catch-up, pr_dump.sh gives Clead one PR for code review. Upload the output
# file to the Clead chat session.
#
# Usage (from project root, Git Bash):
#   bash tools/pr_dump.sh <PR-number>
#
# Output: reviews/pr_<N>_review.txt  (reviews/ is gitignored working space)
#
# Requirements: gh CLI installed and authenticated (gh auth status).

set -euo pipefail

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: bash tools/pr_dump.sh <PR-number> [--no-src]" >&2
    exit 1
fi

NO_SRC=false
for arg in "$@"; do
  if [ "$arg" = "--no-src" ]; then
    NO_SRC=true
  fi
done

PR="$1"
mkdir -p reviews
OUT="reviews/pr_${PR}_review.txt"

{
    echo "=== PR #${PR} — METADATA ==="
    # Title, author, branches, state, CI status, description
    gh pr view "${PR}" --json title,author,headRefName,baseRefName,state,statusCheckRollup,body \
        --template '{{.title}}
Author: {{.author.login}}
Branch: {{.headRefName}} -> {{.baseRefName}}
State:  {{.state}}
CI:     {{range .statusCheckRollup}}{{.name}}={{.conclusion}} {{end}}

--- Description ---
{{.body}}
'

    echo ""
    echo "=== PR #${PR} — EXISTING REVIEW COMMENTS ==="
    gh pr view "${PR}" --comments || echo "(none or unavailable)"

    echo ""
    echo "=== PR #${PR} — CHANGED FILES ==="
    gh pr diff "${PR}" --name-only

    echo ""
    echo "=== PR #${PR} — FULL DIFF ==="
    gh pr diff "${PR}"

    if [ "$NO_SRC" = false ]; then
      echo ""
      echo "=== FULL SOURCE CONTEXT ==="
      echo ""
      git ls-files src/ | while read file; do
        git_version=$(git log -1 --format="%H" -- "$file")
        echo "=== FILE: $file | GIT VERSION: $git_version ==="
        cat "$file"
        echo ""
      done
    fi
} > "${OUT}"

echo "Wrote ${OUT} — upload this file to the Clead session for review."
