#!/usr/bin/env bash
# Deploys a probe extension (javax or jakarta servlet API) into an upgraded 26.2 repository
# and reports whether the repository starts and loads it.
# Usage: test/extension-check/run.sh <javax|jakarta> [<snapshot>]   (default snapshot: s74)
set -uo pipefail
X="$(cd "$(dirname "$0")" && pwd)"
T="$(dirname "$X")"
variant="$1" snap="${2:-s74}" env=26.2
E="$T/envs/$env"
overlay="$X/build/compose-$variant.yml"
cat > "$overlay" <<YML
services:
    alfresco:
        volumes:
            - $X/build/upgradeprobe-$variant.jar:/usr/local/tomcat/webapps/alfresco/WEB-INF/lib/upgradeprobe.jar
            - $X/config/upgradeprobe-context.xml:/usr/local/tomcat/shared/classes/alfresco/extension/upgradeprobe-context.xml
YML
export COMPOSE_FILE="$E/docker-compose.yml:$E/docker-compose.override.yml:$overlay"
"$T/upgrade.sh" restore "$snap" "$env" || exit 1
READY_TRIES=48 "$T/upgrade.sh" start "$env"; started=$?
log="$T/results/extension-$variant.log"
docker compose -p acs262 --project-directory "$E" logs alfresco > "$log" 2>&1
loaded=$(grep -c "UPGRADE-PROBE loaded: $variant variant" "$log")
error=$(grep -m1 -oE "(NoClassDefFoundError|ClassNotFoundException)[^ ]* [^ ]+" "$log")
"$T/upgrade.sh" stop "$env"
echo "RESULT extension-$variant: started=$([ $started -eq 0 ] && echo yes || echo no) loaded=$([ "$loaded" -gt 0 ] && echo yes || echo no) error=${error:-none}" \
  | tee "$T/results/extension-$variant.txt"
