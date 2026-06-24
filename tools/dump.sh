#!/bin/bash
# Usage: bash tools/dump.sh [start_dir] [--exclude path1,path2,...]
# Dumps full project context for starting a new Clead session.
# Output is written to tools/dumps/<timestamp>.txt
# Aborts if the repo has uncommitted changes or untracked files.

start_dir="."
exclude_paths=()

# Parse arguments — --exclude may appear anywhere
while [[ $# -gt 0 ]]; do
    case "$1" in
        --exclude)
            shift
            IFS=',' read -ra exclude_paths <<< "$1"
            shift
            ;;
        *)
            start_dir="$1"
            shift
            ;;
    esac
done

output_dir="$(dirname "$0")/dumps"

# Guard — repo must be clean
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo "ERROR: repo is not clean. Commit or stash all changes before running dump.sh."
    git status --short
    exit 1
fi

# Warn for any --exclude paths that don't match a tracked file
for excl in "${exclude_paths[@]}"; do
    if ! git ls-files --error-unmatch "$excl" > /dev/null 2>&1; then
        echo "WARNING: --exclude path '$excl' does not match any tracked file" >&2
    fi
done

mkdir -p "$output_dir"
TIMESTAMP=$(date +%s)
output_file="$output_dir/${TIMESTAMP}.txt"

cat << 'EOF' >> "$output_file"
=== CLEAD SESSION START INSTRUCTIONS ===
You are Clead, Tech Owner on the python-blackjack project. Before doing anything else:
1. **Truncation check** — verify that the very last line of this file reads:
   `=== DUMP INTEGRITY: <token> ===`
   where `<token>` matches the token on the `=== DUMP INTEGRITY: ===` line immediately below these instructions.
   If the last line is missing or the token does not match, stop immediately and tell the user the dump file appears truncated — do not proceed with any other work.
2. **Run a document consistency check** across the dumped files below. Check for:
   - TPS vs backlog vs onboarding: are key facts consistent?
   - Decision log entries: recorded in both TPS and backlog?
   - Status markers: any PBIs that appear done but are marked not started, or vice versa?
   - Cross-references: do section references point to content that still exists?
3. **Report any inconsistencies found.** If found, produce a single Crog prompt that fixes all of them in one PR. If none, say so briefly and move on.
4. **Then ask Adam what today's work is.**
=== END SESSION START INSTRUCTIONS ===
EOF

echo "=== DUMP INTEGRITY: ${TIMESTAMP} ===" >> "$output_file"
echo "" >> "$output_file"

git ls-files "$start_dir" | while read file; do
    if file --mime-encoding "$file" | grep -q "binary"; then
        continue
    fi

    git_version=$(git log -1 --format="%H" -- "$file")
    echo "=== FILE: $file | GIT VERSION: $git_version ===" >> "$output_file"

    excluded=false
    for excl in "${exclude_paths[@]}"; do
        if [[ "$file" == "$excl" ]]; then
            excluded=true
            break
        fi
    done

    if $excluded; then
        echo "[File excluded from dump — too large to include]" >> "$output_file"
    else
        cat "$file" >> "$output_file"
    fi
    echo "" >> "$output_file"
done

echo "=== DUMP INTEGRITY: ${TIMESTAMP} ===" >> "$output_file"
echo "Output written to $output_file"
