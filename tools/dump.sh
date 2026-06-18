#!/bin/bash
# Usage: bash tools/dump.sh
# Dumps full project context for starting a new Clead session.
# Output is written to tools/dumps/<timestamp>.txt
# Aborts if the repo has uncommitted changes or untracked files.

start_dir="${1:-.}"
output_dir="$(dirname "$0")/dumps"

# Guard — repo must be clean
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo "ERROR: repo is not clean. Commit or stash all changes before running dump.sh."
    git status --short
    exit 1
fi

mkdir -p "$output_dir"
output_file="$output_dir/$(date +%s).txt"

cat << 'EOF' >> "$output_file"
=== CLEAD SESSION START INSTRUCTIONS ===
You are Clead, Tech Owner on the python-blackjack project. Before doing anything else:
1. **Run a document consistency check** across the dumped files below. Check for:
   - TPS vs backlog vs onboarding: are key facts consistent?
   - Decision log entries: recorded in both TPS and backlog?
   - Status markers: any PBIs that appear done but are marked not started, or vice versa?
   - Cross-references: do section references point to content that still exists?
2. **Report any inconsistencies found.** If found, produce a single Crog prompt that fixes all of them in one PR. If none, say so briefly and move on.
3. **Then ask Adam what today's work is.**
=== END SESSION START INSTRUCTIONS ===
EOF

git ls-files "$start_dir" | while read file; do
  git_version=$(git log -1 --format="%H" -- "$file")
  echo "=== FILE: $file | GIT VERSION: $git_version ===" >> "$output_file"
  cat "$file" >> "$output_file"
  echo "" >> "$output_file"
done

echo "Output written to $output_file"
