#!/usr/bin/env bash
# copi_wait.sh — Re-request Copi review and wait for it to complete.
# Usage: bash tools/copi_wait.sh <PR-number>

set -euo pipefail

PR="${1:?Usage: bash tools/copi_wait.sh <PR-number>}"
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# Count existing Copi reviews before re-request
BEFORE=$(gh pr view "$PR" --json reviews \
  --jq '[.reviews[] | select(.author.login | test("copilot"; "i"))] | length')

echo "Re-requesting Copi review on PR #$PR (existing Copi reviews: $BEFORE)..."
if ! gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "repos/$REPO/pulls/$PR/requested_reviewers" \
  -f 'reviewers[]=copilot' > /dev/null 2>&1; then
  echo "Warning: Copi re-request may have failed (already requested or network error)."
fi

# Poll for new Copi review (count increase means new review started)
echo "Polling for Copi review detection..."
DETECTED=false
for i in $(seq 1 6); do
  sleep 10
  AFTER=$(gh pr view "$PR" --json reviews \
    --jq '[.reviews[] | select(.author.login | test("copilot"; "i"))] | length')
  if [ "$AFTER" -gt "$BEFORE" ]; then
    DETECTED=true
    BEFORE=$AFTER
    echo "Copi review detected. Polling until complete..."
    break
  fi
done

if [ "$DETECTED" = false ]; then
  echo "No Copi review detected after 60s — please re-request manually via GitHub UI."
  echo "Continuing to poll..."
fi

# Poll until no Copi review is PENDING
# Only exit if we know a review exists (BEFORE > 0 or DETECTED=true)
while true; do
  sleep 10
  TOTAL=$(gh pr view "$PR" --json reviews \
    --jq '[.reviews[] | select(.author.login | test("copilot"; "i"))] | length')
  PENDING=$(gh pr view "$PR" --json reviews \
    --jq '[.reviews[] | select(.author.login | test("copilot"; "i")) | select(.state == "PENDING")] | length')
  if [ "$TOTAL" -gt 0 ] && [ "$PENDING" -eq 0 ]; then
    echo "Copi review complete."
    break
  fi
done
