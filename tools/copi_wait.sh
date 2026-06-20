#!/usr/bin/env bash
# smoke-test commit 1
# smoke-test commit 2
# copi_wait.sh — Re-request Copi review and wait for it to complete.
# Usage: bash tools/copi_wait.sh <PR-number>

set -euo pipefail

PR="${1:?Usage: bash tools/copi_wait.sh <PR-number>}"
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# Count existing Copi reviews before re-request
BEFORE=$(gh pr view "$PR" --json reviews \
  --jq '[.reviews[] | select(.author.login | test("copilot"; "i"))] | length')

echo "Re-requesting Copi review on PR #$PR (existing Copi reviews: $BEFORE)..."

# Dismiss the latest Copi review so GitHub will accept a fresh re-request.
# GitHub silently no-ops /requested_reviewers when the reviewer has already submitted
# a review — dismissing first resets reviewer state.
REVIEW_ID=$(gh api "repos/$REPO/pulls/$PR/reviews" \
  --jq '[.[] | select(.user.login == "copilot-pull-request-reviewer[bot]" or (.user.type == "Bot" and (.user.login | contains("copilot"))))] | last | .id')

if [ -n "$REVIEW_ID" ] && [ "$REVIEW_ID" != "null" ]; then
  gh api "repos/$REPO/pulls/$PR/reviews/$REVIEW_ID/dismissals" \
    -X PUT \
    -f message="Dismissing prior review to enable re-request after push" \
    --silent
  echo "Dismissed review ${REVIEW_ID}"
else
  echo "No existing Copi review to dismiss"
fi

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

# Poll until no Copi review is PENDING (with timeout)
WAIT_COUNT=0
MAX_WAIT=18
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
  echo "Copi review did not complete within 3 minutes — check GitHub UI."
  exit 1
fi
