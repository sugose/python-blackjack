#!/bin/bash

start_dir="${1:-.}"
output_dir="$(dirname "$0")/dumps"
mkdir -p "$output_dir"
output_file="$output_dir/$(date +%s).txt"

cat << 'EOF' >> "$output_file"
=== CLEAD SESSION START INSTRUCTIONS ===

You are Clead, Tech Owner on the [PROJECT NAME] project. Before doing anything else:

1. **Run a document consistency check** across the dumped files below. Check for:
   - TPS vs backlog vs onboarding: are key facts consistent?
   - Decision log entries: recorded in both TPS and backlog?
   - Status markers: any [NEXT] items that appear done, or [DONE] items referencing superseded approaches?
   - Cross-references: do section references point to content that still exists?

2. **Report any inconsistencies found.** If found, produce a single Crog prompt that fixes all of them in one PR. If none, say so briefly and move on.

3. **Then ask [PO NAME] what today's work is.**

=== END SESSION START INSTRUCTIONS ===

EOF

git ls-files "$start_dir" | while read file; do
  git_version=$(git log -1 --format="%H" -- "$file")
  echo "=== FILE: $file | GIT VERSION: $git_version ===" >> "$output_file"
  cat "$file" >> "$output_file"
  echo "" >> "$output_file"
done

echo "Output written to $output_file"
