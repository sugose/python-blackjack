#!/usr/bin/env bash
# copi_wait.sh — Re-request Copi review and wait for it to complete.
# Usage: bash tools/copi_wait.sh <PR-number>

set -euo pipefail

PR="${1:?Usage: bash tools/copi_wait.sh <PR-number>}"
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Re-requesting Copi review on PR #$PR..."
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "repos/$REPO/pulls/$PR/requested_reviewers" \
  -f 'reviewers[]=copilot' 2>/dev/null || true  # ignore 422 if already requested

echo "Polling for Copi review detection..."
DETECTED=false
for i in $(seq 1 6); do
  sleep 10
  REVIEWS=$(gh pr view "$PR" --json reviews \
    --jq "[.reviews[] | select(.author.login | test(\"copilot\"; \"i\")) | select(.submittedAt > \"$START_TIME\")]")
  if [ "$(echo "$REVIEWS" | jq 'length')" -gt 0 ]; then
    DETECTED=true
    echo "Copi review detected. Polling until complete..."
    break
  fi
done

if [ "$DETECTED" = false ]; then
  echo "No Copi review detected after 60s — please re-request manually via GitHub UI."
  echo "Continuing to poll..."
fi

# Poll until Copi review is no longer PENDING
while true; do
  sleep 10
  PENDING=$(gh pr view "$PR" --json reviews \
    --jq "[.reviews[] | select(.author.login | test(\"copilot\"; \"i\")) | select(.state == \"PENDING\")] | length")
  if [ "$PENDING" -eq 0 ]; then
    echo "Copi review complete."
    break
  fi
done
