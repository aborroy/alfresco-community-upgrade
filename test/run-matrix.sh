#!/usr/bin/env bash
# Runs the full upgrade matrix from a clean state and writes test/results/matrix.txt.
# Each source version is produced by upgrading the 6.1 seed data, so every hop starts
# from a repository that was really created on an older release.
# Usage: [SKIP_SOURCES=1] test/run-matrix.sh
set -uo pipefail
T="$(cd "$(dirname "$0")" && pwd)"
H="$T/upgrade.sh"
OUT="$T/results/matrix.txt"
mkdir -p "$T/results"
hop() { "$T/run-hop.sh" "$@" | tee -a "$T/results/matrix.log" | grep '^RESULT' | tee -a "$OUT"; }

: > "$OUT"; : > "$T/results/matrix.log"
date -u '+Matrix run %Y-%m-%dT%H:%M:%SZ' >> "$OUT"

# SKIP_SOURCES=1 reuses the snapshots s61, s74, s234, s253 and s261 from a previous run.
if [ -z "${SKIP_SOURCES:-}" ]; then
# Baseline: create the test data on a new 6.1.2 repository.
"$H" stop 6.1 >/dev/null 2>&1
rm -rf "$T/envs/6.1/data" "$T/envs/6.1/logs"
"$H" start 6.1 && "$H" seed && "$H" verify 6.1 && "$H" search 6.1 && "$H" snapshot 6.1 s61
r=$?; "$H" stop 6.1
echo "RESULT 6.1 baseline: $([ $r -eq 0 ] && echo PASS || echo FAIL)" | tee -a "$OUT"
[ $r -eq 0 ] || exit 1

# Intermediate versions, created from the 6.1 data.
hop s61 7.4 A-7.4 s74
hop s74 23.4 C-23.4 s234
hop s74 25.3 E-25.3 s253
hop s74 26.1 F-26.1 s261
fi

# Every source version straight to 26.2.
hop s61 26.2 D-6.1-to-26.2
hop s74 26.2 B-7.4-to-26.2
hop s234 26.2 C-23.4-to-26.2
hop s253 26.2 E-25.3-to-26.2
hop s261 26.2 F-26.1-to-26.2

# Old repository: history moved back 2 years. The default maxGapAge (24h) skips it;
# the initial-index procedure (maxGapAge=0) indexes it.
AGE_DAYS=730 GAP=24h SEARCH_TRIES=6 hop s61 26.2 H1-aged-default-gap
AGE_DAYS=730 hop s61 26.2 H2-aged-procedure

cat "$OUT"
