#!/usr/bin/env bash
# Usage: bash tools/dump.sh
# Dumps full project context for starting a new Clead session.

set -euo pipefail

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
DATE=$(date)

cat << EOF
=== CLEAD SESSION START INSTRUCTIONS ===

You are Clead, Tech Owner on the python-blackjack project. Before doing anything else:

1. **Run a document consistency check** across the context below. Check for:
   - TPS vs backlog vs onboarding: are key facts consistent?
   - Decision log entries: are decisions recorded correctly?
   - Status markers: any PBIs that appear done but are marked not started, or vice versa?
   - Cross-references: do section references point to content that still exists?

2. **Report any inconsistencies found.** If found, produce a single Crog prompt that fixes all of them in one PR. If none, say so briefly and move on.

3. **Then ask Adam what today's work is.**

=== END SESSION START INSTRUCTIONS ===

=== PROJECT CONTEXT DUMP ===
Repo: ${REPO}
Date: ${DATE}

EOF

echo "=== RECENT COMMITS ==="
git log --oneline -10
echo ""

echo "=== OPEN PRS ==="
gh pr list
echo ""

echo "=== ALL TRACKED FILES ==="
git ls-files | while IFS= read -r file; do
    echo ""
    echo "=== FILE: ${file} ==="
    cat "${file}"
    echo ""
done
