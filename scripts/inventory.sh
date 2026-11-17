#!/usr/bin/env bash
# Builds an Extension Inspector inventory for a webapp shipped in an Alfresco Docker image.
# The images contain the unpacked webapp, so it is copied out and zipped into a WAR first.
# Usage: scripts/inventory.sh <inspector.jar> <image> <webapp> <out.json>
#   e.g. scripts/inventory.sh alfresco-extension-inspector-2.8.0.jar \
#          alfresco/alfresco-content-repository-community:26.2.0 alfresco inventories/repo-26.2.0.json
set -euo pipefail
jar="$1" image="$2" webapp="$3" out="$4"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
docker pull -q "$image" >/dev/null
# Old images (6.x) have webapp folders without the execute bit, so copy them as root with tar
# and make the local copy readable.
docker run --rm --entrypoint tar "$image" -C /usr/local/tomcat/webapps -cf - "$webapp" | tar -xf - -C "$work"
chmod -R u+rwX "$work/$webapp"
# Tomcat provides the servlet, JSP, EL and WebSocket APIs, so they are not in the WAR. The Inspector then
# guesses javax or jakarta from the mail library, which fails for Share. Add the APIs the image really runs.
docker run --rm --entrypoint sh "$image" -c 'cd /usr/local/tomcat/lib && tar -cf - *-api.jar' | tar -xf - -C "$work/$webapp/WEB-INF/lib"
(cd "$work/$webapp" && zip -q -r "../$webapp.war" .)
mkdir -p "$(dirname "$out")"
java -jar "$jar" --inventory "$work/$webapp.war" --o="$(cd "$(dirname "$out")" && pwd)/$(basename "$out")" >/dev/null
echo "$out: $(python3 -I -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['alfrescoVersion'], {k: len(v) for k, v in d['resources'].items()})" "$out")"
