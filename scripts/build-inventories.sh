#!/usr/bin/env bash
# Builds Extension Inspector inventories for the Community repository and Share images used in the tests.
# Usage: scripts/build-inventories.sh <inspector.jar> [<out-dir>]
set -uo pipefail
S="$(cd "$(dirname "$0")" && pwd)"
jar="$1" out="${2:-$S/../inventories}"
while read -r image webapp name; do
  [ -f "$out/$name.json" ] && { echo "$out/$name.json: exists"; continue; }
  "$S/inventory.sh" "$jar" "alfresco/$image" "$webapp" "$out/$name.json" 2>&1 | grep -v 'Fatal Error'
done <<'EOF'
alfresco-content-repository-community:6.1.2-ga alfresco repo-6.1.2
alfresco-content-repository-community:7.4.2 alfresco repo-7.4.2
alfresco-content-repository-community:23.4.1 alfresco repo-23.4.1
alfresco-content-repository-community:25.3.0 alfresco repo-25.3.0
alfresco-content-repository-community:26.1.0 alfresco repo-26.1.0
alfresco-content-repository-community:26.2.0 alfresco repo-26.2.0
alfresco-share:6.1.0 share share-6.1.0
alfresco-share:7.4.2 share share-7.4.2
alfresco-share:23.4.0 share share-23.4.0
alfresco-share:25.3.0 share share-25.3.0
alfresco-share:26.1.0 share share-26.1.0
alfresco-share:26.2.1 share share-26.2.1
EOF
