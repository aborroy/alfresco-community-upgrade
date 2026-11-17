"""Writes docs/img/upgrade-paths.svg: the upgrade paths to the current Alfresco Community release.

Usage: python3 -I docs/img/make-diagram.py
To add a release, edit TARGET and SOURCES below and run the script again.
"""

from pathlib import Path

# Data: the target release and one row per source version (newest first).
# "via" is an intermediate stop; "tested" marks rehearsed paths (solid lines); "solr" marks a Solr reindex.
TARGET = {
    "version": "26.2",
    "runtime": "Java 21 / Tomcat 11 (jakarta)",
    "search": ["Alfresco Search Community", "OpenSearch or Elasticsearch", "Solr is no longer supported"],
    "arrival": ["1. Seed the cursor at the first", "    transaction", "2. maxGapAge=0, maxWindow=7d", "3. Compare index count and nodes", "4. Check the dead-letter index"],
}
SOURCES = [
    {"version": "26.1.x", "runtime": "Java 21 / Tomcat 11", "search": "Search Services 2.0", "tested": True},
    {"version": "25.x", "runtime": "Java 17 / Tomcat 10.1 (jakarta)", "search": "Search Services 2.0", "tested": True},
    {"version": "23.x", "runtime": "Java 17 / Tomcat 10.1 (jakarta)", "search": "Search Services 2.0", "tested": True},
    {"version": "7.x  (latest patch 7.4.2)", "runtime": "Java 17 / Tomcat 9 (javax)", "search": "Search Services 2.0", "tested": True},
    {"version": "6.x", "runtime": "Java 11 / Tomcat 8.5 (javax)", "search": "Search Services 1.x", "tested": True},
    {"version": "5.2", "runtime": "Java 8 / Tomcat 7", "search": "Solr 4 or Search Services 1.x", "tested": False,
     "via": {"version": "7.4.2", "runtime": "Java 17 / Tomcat 9", "note": "Start once: schema upgrade", "solr": True}},
]

# Style
FONT = "system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
BG, INK, MUTED = "#F7F9FB", "#1F2933", "#5F6B7A"
BOX, EDGE, ARROW = "#FFFFFF", "#AEB8C4", "#9AA5B1"
BLUE, BLUE_BG, BLUE_SOFT = "#1F5BC6", "#E3EDFC", "#F0F5FE"
ORANGE, ORANGE_BG = "#C2570C", "#FDEBDD"

# Layout
W = 1240
TOP, ROW, BOX_H = 150, 82, 62
SRC_X, SRC_W = 40, 300
VIA_X, VIA_W = 545, 210
RAIL_X = 872
TGT_X, TGT_W = 900, 300
rows_bottom = TOP + ROW * (len(SOURCES) - 1) + BOX_H
LEGEND_Y = rows_bottom + 52
H = LEGEND_Y + 96


def text(x, y, s, size=14, weight=400, color=INK, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}">{s}</text>')


def box(x, y, w, title, line1, line2, dashed=False):
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{BOX_H}" rx="10" fill="{BOX}" stroke="{EDGE}" stroke-width="1.5"{dash} filter="url(#shadow)"/>',
        text(x + 16, y + 23, title, 16.5, 700),
        text(x + 16, y + 41, line1, 12.5, 400, MUTED),
        text(x + 16, y + 56, line2, 12.5, 400, MUTED),
    ])


def pill_w(label):
    return 7.1 * len(label) + 28


def pill(cx, cy, label, color, bg):
    w = pill_w(label)
    return "\n".join([
        f'<rect x="{cx - w / 2:.1f}" y="{cy - 12}" width="{w:.1f}" height="24" rx="12" fill="{bg}" stroke="{color}" stroke-width="1.2"/>',
        f'<circle cx="{cx - w / 2 + 13:.1f}" cy="{cy}" r="4" fill="{color}"/>',
        text(cx + 6, cy + 4.5, label, 12, 600, color, "middle"),
    ])


def arrow(x1, x2, y, dashed=False, label=None):
    dash = ' stroke-dasharray="7 6"' if dashed else ""
    out = [f'<line x1="{x1}" y1="{y}" x2="{x2 - 9}" y2="{y}" stroke="{ARROW}" stroke-width="2.2"{dash} marker-end="url(#arrow)"/>']
    if label:
        out.append(text((x1 + x2) / 2, y - 9, label, 12, 500, MUTED, "middle"))
    return "\n".join(out)


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    "<defs>",
    '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
    f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{ARROW}"/></marker>',
    '<filter id="shadow" x="-5%" y="-10%" width="110%" height="130%">'
    '<feDropShadow dx="0" dy="1.5" stdDeviation="2" flood-color="#1F2933" flood-opacity="0.12"/></filter>',
    "</defs>",
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    text(40, 56, "Upgrade Path", 28, 800),
    text(40, 84, f"To Alfresco Community {TARGET['version']}, with the fewest steps from each version.", 15, 400, MUTED),
]

# Rows: source box, arrows, optional intermediate stop
for i, s in enumerate(SOURCES):
    y = TOP + i * ROW
    cy = y + BOX_H / 2
    dashed = not s["tested"]
    via = s.get("via")
    if via:
        parts.append(arrow(SRC_X + SRC_W, VIA_X, cy, dashed))
        parts.append(arrow(VIA_X + VIA_W, RAIL_X - 8, cy, dashed, "step 2"))
        parts.append(box(VIA_X, y, VIA_W, via["version"], via["runtime"], via["note"], dashed=True))
        if via.get("solr"):
            parts.append(pill((SRC_X + SRC_W + VIA_X) / 2, cy, "Solr reindex", ORANGE, ORANGE_BG))
    else:
        parts.append(arrow(SRC_X + SRC_W, RAIL_X - 8, cy, dashed, "1 step"))
    parts.append(box(SRC_X, y, SRC_W, s["version"], s["runtime"], "Search: " + s["search"], dashed=dashed))

# Blue rail: every path into the target passes the initial index
rail_top, rail_bottom = TOP - 6, rows_bottom + 6
parts += [
    f'<rect x="{RAIL_X - 3}" y="{rail_top}" width="6" height="{rail_bottom - rail_top}" rx="3" fill="{BLUE}"/>',
    pill(RAIL_X - 40, TOP - 30, "OpenSearch initial index, every path", BLUE, BLUE_BG),
]
for i, _ in enumerate(SOURCES):
    parts.append(f'<circle cx="{RAIL_X}" cy="{TOP + i * ROW + BOX_H / 2}" r="6" fill="{BG}" stroke="{BLUE}" stroke-width="2.5"/>')

# Target box
ty, th = TOP - 6, rows_bottom - TOP + 12
tx = TGT_X
parts += [
    f'<rect x="{tx}" y="{ty}" width="{TGT_W}" height="{th}" rx="16" fill="#E8F1FD" stroke="{BLUE}" stroke-width="2" filter="url(#shadow)"/>',
    text(tx + 26, ty + 62, TARGET["version"], 46, 800, BLUE),
    text(tx + 26, ty + 96, TARGET["runtime"], 14.5, 600),
]
yy = ty + 126
for j, line in enumerate(TARGET["search"]):
    parts.append(text(tx + 26, yy, line, 14 if j == 0 else 13, 600 if j == 0 else 400, INK if j == 0 else MUTED))
    yy += 21
yy += 14
box_h = 34 + 21 * len(TARGET["arrival"])
parts += [
    f'<rect x="{tx + 18}" y="{yy}" width="{TGT_W - 36}" height="{box_h}" rx="10" fill="{BLUE_SOFT}" stroke="{BLUE}" stroke-opacity="0.35"/>',
    text(tx + 34, yy + 25, "On arrival: initial search index", 13.5, 700, BLUE),
]
for j, line in enumerate(TARGET["arrival"]):
    parts.append(text(tx + 34, yy + 48 + j * 21, line.replace(' ', '&#160;') if line.startswith(' ') else line, 13, 400, INK))

# Legend
ly = LEGEND_Y
parts += [
    f'<line x1="40" y1="{ly}" x2="90" y2="{ly}" stroke="{ARROW}" stroke-width="2.2"/>',
    text(100, ly + 4.5, "Rehearsed on Docker", 13, 400, MUTED),
    f'<line x1="300" y1="{ly}" x2="350" y2="{ly}" stroke="{ARROW}" stroke-width="2.2" stroke-dasharray="7 6"/>',
    text(360, ly + 4.5, "Documented, not rehearsed", 13, 400, MUTED),
    pill(40 + pill_w("Solr reindex") / 2, ly + 32, "Solr reindex", ORANGE, ORANGE_BG),
    text(40 + pill_w("Solr reindex") + 14, ly + 36.5, "Only if you keep Solr at the 7.4.2 stop (Solr 4 to Search Services).", 13, 400, MUTED),
    f'<rect x="40" y="{ly + 55}" width="6" height="26" rx="3" fill="{BLUE}"/>',
    text(60, ly + 72.5, f"OpenSearch initial index: required on every path into {TARGET['version']}. "
         "The index is built again, and old content is not indexed by default.", 13, 400, MUTED),
]
parts.append("</svg>")

out = Path(__file__).with_name("upgrade-paths.svg")
out.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(f"{out} ({W}x{H})")
