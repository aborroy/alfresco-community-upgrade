#!/usr/bin/env bash
# Checks an add-on (JAR or AMP) against a target Alfresco Community version:
#   1. Java: highest class-file version in the add-on vs the Java release of the target.
#   2. Bundled JARs inside the add-on.
#   3. Alfresco Extension Inspector against the Community repository and Share inventories
#      (inventories/repo-<version>.json and inventories/share-<version>.json).
# Usage: scripts/addon-check.sh <inspector.jar> <addon.jar|addon.amp> <target> [repo|share|both]
#   e.g. scripts/addon-check.sh alfresco-extension-inspector-2.8.0.jar my-module.amp 26.2
set -uo pipefail
S="$(cd "$(dirname "$0")" && pwd)"
INV="$S/../inventories"
jar="$1" addon="$2" target="$3" side="${4:-both}"

# Java release of the repository and Share images (read from the images with java -version).
case "$target" in
  6.*) java=11 ;;
  7.*|23.*|25.*) java=17 ;;
  26.*) java=21 ;;
  *) echo "Unknown target $target"; exit 2 ;;
esac

fails=0
echo "== Java (target $target runs Java $java)"
python3 -I "$S/classversion.py" "$addon" "$java" || fails=$((fails + 1))

for s in repo share; do
  [ "$side" = both ] || [ "$side" = "$s" ] || continue
  inv=$(ls "$INV/$s-$target"*.json 2>/dev/null | sort -V | tail -1)
  if [ -z "$inv" ]; then echo "== Inspector ($s): no inventory for $target in $INV"; continue; fi
  echo "== Inspector ($s, $(basename "$inv"))"
  report=$(java -jar "$jar" "$addon" --target-inventory="$inv" 2>&1 | grep -vE ' INFO |Fatal Error')
  echo "$report" | sed -n '/REPORT SUMMARY/,$p'
  echo "$report" | grep -q 'number of conflicts have been found' && fails=$((fails + 1))
done

echo "== RESULT $(basename "$addon") on $target: $([ $fails -eq 0 ] && echo 'no issues found' || echo "$fails check(s) with findings")"
[ $fails -eq 0 ]
