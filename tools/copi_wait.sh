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
for i in $(seq 1 12); do
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
  echo "No Copi review detected after 120s — please re-request manually via GitHub UI."
  echo "Continuing to poll..."
fi

# Poll until no Copi review is PENDING (with timeout)
WAIT_COUNT=0
MAX_WAIT=36
COMPLETED=false
while [ "$WAIT_COUNT" -lt "$MAX_WAIT" ]; do
  sleep 10
  WAIT_COUNT=$((WAIT_COUNT + 1))
  TOTAL=$(gh pr view "$PR" --json reviews \
    --jq '[.reviews[] | select(.author.login | test("copilot"; "i"))] | length')
  PENDING=$(gh pr view "$PR" --json reviews \
    --jq '[.reviews[] | select(.author.login | test("copilot"; "i")) | select(.state == "PENDING")] | length')
  # If detection succeeded, BEFORE was updated to AFTER — just check PENDING.
  # If detection failed, require TOTAL > BEFORE to avoid exiting on stale reviews.
  if [ "$DETECTED" = true ] && [ "$PENDING" -eq 0 ]; then
    echo "Copi review complete."
    COMPLETED=true
    break
  elif [ "$DETECTED" = false ] && [ "$TOTAL" -gt "$BEFORE" ] && [ "$PENDING" -eq 0 ]; then
    echo "Copi review complete."
    COMPLETED=true
    break
  fi
done
if [ "$COMPLETED" = false ]; then
  echo "Copi re-review timed out — please click 'Re-request review' in the GitHub UI, then run: bash tools/copi_wait.sh $PR"
  exit 1
fi
