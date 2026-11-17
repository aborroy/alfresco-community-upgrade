#!/usr/bin/env bash
# Smoke test for Share and the Content App on a running, upgraded environment.
# Starts share, content-app and proxy, then checks login, the test site and a document thumbnail.
# Usage: test/smoke-ui.sh <env> <label>   (run after test/upgrade.sh start <env> and verify)
set -uo pipefail
T="$(cd "$(dirname "$0")" && pwd)"
env="$1" label="$2"
P="http://localhost:8080"
out="$T/results/$label-ui.txt" jar="$(mktemp)"
trap 'rm -f "$jar"' EXIT
dc() { docker compose -p "acs$(echo "$env" | tr -d '.')" --project-directory "$T/envs/$env" "$@"; }
dc up -d --build share content-app proxy >/dev/null 2>&1
for _ in $(seq 1 60); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' "$P/share/page/")" = "200" ] && break
  sleep 5
done
: > "$out"; fails=0
check() { if [ "$2" = "$3" ]; then echo "PASS $1" >> "$out"; else echo "FAIL $1 (expected '$3', got '$2')" >> "$out"; fails=$((fails + 1)); fi; }

check "content app home" "$(curl -s -o /dev/null -w '%{http_code}' "$P/")" 200
login=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' -c "$jar" -b "$jar" -X POST "$P/share/page/dologin" \
  -d 'username=admin&password=admin&success=/share/page/&failure=/share/page/?error=true')
check "share login" "$(echo "$login" | grep -c 'error=true')" 0
check "share site dashboard" "$(curl -s -o /dev/null -w '%{http_code}' -b "$jar" "$P/share/page/site/upgrade-test/dashboard")" 200
node=$(curl -s -u admin:admin "$P/alfresco/api/-default-/public/alfresco/versions/1/nodes/-root-?relativePath=Sites/upgrade-test/documentLibrary/Upgrade%20folder/doc1.txt" \
  | python3 -I -c "import json,sys; print(json.load(sys.stdin)['entry']['id'])")
thumb=""
for _ in $(seq 1 24); do
  thumb=$(curl -s -o /dev/null -w '%{http_code} %{content_type}' -b "$jar" \
    "$P/share/proxy/alfresco/api/node/workspace/SpacesStore/$node/content/thumbnails/doclib?c=force")
  case "$thumb" in 200\ image/*) break ;; esac
  sleep 5
done
check "share document thumbnail" "${thumb%% *}" 200
check "share document library" "$(curl -s -o /dev/null -w '%{http_code}' -b "$jar" "$P/share/page/site/upgrade-test/documentlibrary")" 200
cat "$out"
[ "$fails" -eq 0 ]
