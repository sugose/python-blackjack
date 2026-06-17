#!/usr/bin/env bash
# Usage: bash tools/dump.sh
# Dumps project context for starting a new Clead session.

set -euo pipefail

echo "=== PROJECT CONTEXT DUMP ==="
echo "Repo: $(gh repo view --json nameWithOwner -q .nameWithOwner)"
echo "Date: $(date)"
echo ""

echo "=== RECENT COMMITS ==="
git log --oneline -10
echo ""

echo "=== OPEN PRS ==="
gh pr list
echo ""

echo "=== PRODUCT BACKLOG ==="
cat docs/PRODUCT_BACKLOG.md
echo ""

echo "=== CHANGELOG ==="
cat CHANGELOG.md
echo ""
