"""Builds the add-on compatibility table (Markdown) from the log written by test/addon-matrix.sh.

Usage: python3 -I scripts/summarize-addons.py test/results/addons.log > test/results/addons.md
"""

import re
import sys

SIDE = {}
cells = {}
versions = []
addons = []

text = open(sys.argv[1], encoding="utf-8").read()
for block in re.split(r"^### ", text, flags=re.M)[1:]:
    head, body = block.split("\n", 1)
    addon, version = head.rsplit(" on ", 1)
    side = re.search(r"== Inspector \((repo|share),", body)
    SIDE[addon] = side.group(1) if side else "?"
    if version not in versions:
        versions.append(version)
    if addon not in addons:
        addons.append(addon)
    found = [(k, n) for k, n in re.findall(r"\|([A-Z_]+)\s*\|(\d+)\s*\|", body) if k != "Type"]
    java = re.search(r"FAIL needs Java (\d+)", body)
    parts = ([f"Java {java.group(1)}"] if java else []) + [f"{k.replace('_CONFLICT', '').lower()} {n}" for k, n in found]
    cells[(addon, version)] = ", ".join(parts) if parts else "OK"

print("| Add-on | Side | " + " | ".join(versions) + " |")
print("| --- | --- | " + " | ".join("---" for _ in versions) + " |")
for a in addons:
    print(f"| {a} | {SIDE[a]} | " + " | ".join(cells.get((a, v), "") for v in versions) + " |")
