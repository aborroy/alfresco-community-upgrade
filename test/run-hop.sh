#!/usr/bin/env bash
# Runs one upgrade hop end to end: restore a snapshot into an env, start it, verify data,
# rendition and search, and optionally snapshot the result.
# Usage: test/run-hop.sh <from-snapshot> <env> <label> [<new-snapshot>]
# Optional environment:
#   AGE_DAYS=<n>      move all transaction times back n days before the upgrade (old repository)
#   GAP=<duration>    maxGapAge used by the initial index (default 0, as the procedure requires)
#   SEARCH_TRIES=<n>  search attempts, 10 s apart (default 60)
set -uo pipefail
H="$(cd "$(dirname "$0")" && pwd)/upgrade.sh"
from="$1" env="$2" label="$3" snap="${4:-}"
"$H" restore "$from" "$env" || exit 1
[ -n "${AGE_DAYS:-}" ] && "$H" age "$env" "$AGE_DAYS"
"$H" start "$env" || { echo "RESULT $label: START FAILED"; exit 1; }
"$H" verify "$label"; v=$?
r=0
grep -q '^    opensearch:' "$(dirname "$0")/envs/$env/docker-compose.yml" && { "$H" reindex "$env" "${GAP:-0}"; r=$?; }
"$H" search "$label" "$env"; s=$?
[ -n "$snap" ] && "$H" snapshot "$env" "$snap"
"$H" stop "$env"
pf() { [ "$1" -eq 0 ] && echo PASS || echo FAIL; }
echo "RESULT $label: verify=$(pf $v) reindex=$(pf $r) search=$(pf $s)"
