#!/usr/bin/env bash
# Usage: bash tools/pr_dump.sh <PR-number>
# Dumps PR metadata, review comments (including inline), changed files, full diff, and full source context.

set -euo pipefail

PR="${1:?Usage: bash tools/pr_dump.sh <PR-number>}"
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

echo "=== PR #${PR} — METADATA ==="
gh pr view "$PR" --json title,author,headRefName,baseRefName,state --template \
  '{{.title}}{{"\n"}}Author: {{.author.login}}{{"\n"}}Branch: {{.headRefName}} -> {{.baseRefName}}{{"\n"}}State:  {{.state}}{{"\n"}}'

echo "CI:     $(gh pr checks "$PR" 2>/dev/null | awk '{print $1"="$2}' | tr '\n' ' ')"
echo ""
echo "--- Description ---"
gh pr view "$PR" --json body -q .body
echo ""

echo "=== PR #${PR} — REVIEW COMMENTS (top-level) ==="
gh api "repos/${REPO}/pulls/${PR}/reviews" --paginate \
  --jq '.[] | "author:\t\(.user.login)\nstatus:\t\(.state | ascii_downcase)\n--\n\(.body)\n--"'
echo ""

echo "=== PR #${PR} — INLINE COMMENTS ==="
gh api "repos/${REPO}/pulls/${PR}/comments" --paginate \
  --jq '.[] | "author:\t\(.user.login)\nfile:\t\(.path)\nline:\t\(.line // .original_line)\n--\n\(.body)\n--"'
echo ""

echo "=== PR #${PR} — CHANGED FILES ==="
gh pr diff "$PR" --name-only
echo ""

echo "=== PR #${PR} — FULL DIFF ==="
gh pr diff "$PR"
echo ""

echo "=== FULL SOURCE CONTEXT ==="
while IFS= read -r file; do
  [[ "$file" == *.py || "$file" == *.ts || "$file" == *.js ]] || continue
  HASH=$(gh api "repos/${REPO}/pulls/${PR}" -q .head.sha 2>/dev/null || echo "unknown")
  echo ""
  echo "=== FILE: ${file} | GIT VERSION: ${HASH} ==="
  gh api "repos/${REPO}/contents/${file}?ref=${HASH}" -q '.content' 2>/dev/null \
    | base64 --decode 2>/dev/null || echo "(could not fetch file)"
done < <(gh pr diff "$PR" --name-only)
