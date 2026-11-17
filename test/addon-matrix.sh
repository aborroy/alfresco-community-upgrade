#!/usr/bin/env bash
# Checks a folder of add-ons against several Community versions with scripts/addon-check.sh.
# Writes the full output to test/results/addons.log and a table to test/results/addons.md.
# Repository add-ons go in <dir>/repo, Share add-ons in <dir>/share.
# Usage: test/addon-matrix.sh <inspector.jar> <addons-dir> [versions...]   (default: 7.4 23.4 25.3 26.1 26.2)
set -uo pipefail
T="$(cd "$(dirname "$0")" && pwd)"
jar="$1" dir="$2"; shift 2
versions=("$@")
[ ${#versions[@]} -eq 0 ] && versions=(7.4 23.4 25.3 26.1 26.2)
log="$T/results/addons.log"
mkdir -p "$T/results"; : > "$log"
for side in repo share; do
  for f in "$dir/$side"/*; do
    [ -f "$f" ] || continue
    for v in "${versions[@]}"; do
      { echo "### $(basename "$f") on $v"; "$T/../scripts/addon-check.sh" "$jar" "$f" "$v" "$side" 2>&1; } >> "$log"
    done
  done
done
python3 -I "$T/../scripts/summarize-addons.py" "$log" > "$T/results/addons.md"
cat "$T/results/addons.md"
