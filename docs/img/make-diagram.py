"""Writes docs/img/upgrade-paths.svg: upgrade paths to Alfresco Community 26.2.

Usage: python3 -I docs/img/make-diagram.py
"""

from pathlib import Path

W, H = 1240, 740
FONT = "system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
INK, MUTED, LINE = "#1F2933", "#5F6B7A", "#C3CBD5"
BOX, BOX_EDGE = "#FFFFFF", "#9AA5B1"
TARGET, TARGET_EDGE = "#E8F1FD", "#2F6FDE"
SOLR, SOLR_BG = "#C2570C", "#FDEBDD"
OS, OS_BG = "#1F5BC6", "#E3EDFC"

SRC_X, SRC_W, SRC_H = 40, 300, 66
TGT_X, TGT_Y, TGT_W, TGT_H = 880, 200, 330, 250
MID_X, MID_W = 580, 230

# version, runtime line, search line, y, target y (arrow end)
SOURCES = [
    ("26.1.x", "Java 21 / Tomcat 11", "Solr: Search Services 2.0", 96, 250),
    ("25.x", "Java 17 / Tomcat 10.1 (jakarta)", "Solr: Search Services 2.0", 182, 285),
    ("23.x", "Java 17 / Tomcat 10.1 (jakarta)", "Solr: Search Services 2.0", 268, 320),
    ("7.x  (latest patch 7.4.2)", "Java 17 / Tomcat 9 (javax)", "Solr: Search Services 2.0", 354, 355),
    ("6.x", "Java 11 / Tomcat 8.5 (javax)", "Solr: Search Services 1.x", 440, 390),
]
OLD = ("5.2", "Java 8 / Tomcat 7", "Solr 4 or Search Services 1.x", 545)


def text(x, y, s, size=14, weight=400, color=INK, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}">{s}</text>')


def box(x, y, w, h, title, line1, line2, dashed=False):
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{BOX}" stroke="{BOX_EDGE}" stroke-width="1.5"{dash} filter="url(#shadow)"/>',
        text(x + 16, y + 24, title, 17, 700),
        text(x + 16, y + 43, line1, 12.5, 400, MUTED),
        text(x + 16, y + 59, line2, 12.5, 400, MUTED),
    ])


def pill(cx, cy, label, color, bg):
    w = 7.2 * len(label) + 26
    return "\n".join([
        f'<rect x="{cx - w / 2:.1f}" y="{cy - 12}" width="{w:.1f}" height="24" rx="12" fill="{bg}" stroke="{color}" stroke-width="1.2"/>',
        f'<circle cx="{cx - w / 2 + 13:.1f}" cy="{cy}" r="4" fill="{color}"/>',
        text(cx + 6, cy + 4.5, label, 12, 600, color, "middle"),
    ])


def mid(x1, y1, x2, y2):
    """Midpoint (t = 0.5) of the arrow drawn by curve()."""
    x2 -= 8
    mx = (x1 + x2) / 2
    return 0.125 * x1 + 0.75 * mx + 0.125 * x2, (y1 + y2) / 2


def curve(x1, y1, x2, y2, dashed=False, color=LINE):
    dash = ' stroke-dasharray="7 6"' if dashed else ""
    mx = (x1 + x2) / 2
    return (f'<path d="M {x1} {y1} C {mx} {y1}, {mx} {y2}, {x2 - 8} {y2}" fill="none" stroke="{color}" '
            f'stroke-width="2.2"{dash} marker-end="url(#arrow)"/>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    "<defs>",
    '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
    f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{BOX_EDGE}"/></marker>',
    '<filter id="shadow" x="-5%" y="-10%" width="110%" height="130%">'
    '<feDropShadow dx="0" dy="1.5" stdDeviation="2" flood-color="#1F2933" flood-opacity="0.12"/></filter>',
    "</defs>",
    f'<rect width="{W}" height="{H}" fill="#F7F9FB"/>',
    text(40, 50, "Upgrade paths to Alfresco Community 26.2", 24, 700),
    text(40, 74, "Fewest steps from each version. Every path into 26.2 needs an initial search index.", 14, 400, MUTED),
]

# Arrows first, so boxes and badges sit on top.
for _, _, _, y, ty in SOURCES:
    parts.append(curve(SRC_X + SRC_W, y + SRC_H / 2, TGT_X, ty))
old_y = OLD[3]
parts.append(curve(SRC_X + SRC_W, old_y + SRC_H / 2, MID_X, old_y + SRC_H / 2, dashed=True))
parts.append(curve(MID_X + MID_W, old_y + SRC_H / 2, TGT_X, 425, dashed=True))

for title, l1, l2, y, _ in SOURCES:
    parts.append(box(SRC_X, y, SRC_W, SRC_H, title, l1, l2))
parts.append(box(SRC_X, old_y, SRC_W, SRC_H, OLD[0], OLD[1], OLD[2], dashed=True))
parts.append(box(MID_X, old_y, MID_W, SRC_H, "7.4.2", "Java 17 / Tomcat 9", "Start once: schema upgrade", dashed=True))

# Target box
parts += [
    f'<rect x="{TGT_X}" y="{TGT_Y}" width="{TGT_W}" height="{TGT_H}" rx="14" fill="{TARGET}" stroke="{TARGET_EDGE}" stroke-width="2" filter="url(#shadow)"/>',
    text(TGT_X + 24, TGT_Y + 44, "26.2", 34, 800, TARGET_EDGE),
    text(TGT_X + 24, TGT_Y + 72, "Java 21 / Tomcat 11 (jakarta)", 14, 500),
    text(TGT_X + 24, TGT_Y + 94, "Alfresco Search Community", 14, 500),
    text(TGT_X + 24, TGT_Y + 113, "OpenSearch or Elasticsearch", 13, 400, MUTED),
    text(TGT_X + 24, TGT_Y + 132, "Solr is no longer supported", 13, 400, MUTED),
    f'<line x1="{TGT_X + 24}" y1="{TGT_Y + 152}" x2="{TGT_X + TGT_W - 24}" y2="{TGT_Y + 152}" stroke="{TARGET_EDGE}" stroke-opacity="0.25"/>',
    text(TGT_X + 24, TGT_Y + 176, "On arrival:", 13, 700, OS),
    text(TGT_X + 24, TGT_Y + 196, "seed the indexer cursor at the first", 13, 400, INK),
    text(TGT_X + 24, TGT_Y + 214, "transaction, maxGapAge=0, maxWindow=7d", 13, 400, INK),
]

# Badges on the arrows
for _, _, _, y, ty in SOURCES:
    parts.append(pill(*mid(SRC_X + SRC_W, y + SRC_H / 2, TGT_X, ty), "1 step, OpenSearch initial index", OS, OS_BG))
parts.append(pill(*mid(SRC_X + SRC_W, old_y + SRC_H / 2, MID_X, old_y + SRC_H / 2), "Solr reindex", SOLR, SOLR_BG))
parts.append(pill(*mid(MID_X + MID_W, old_y + SRC_H / 2, TGT_X, 425), "OpenSearch initial index", OS, OS_BG))

# Legend
def pill_left(x, cy, label, color, bg):
    return pill(x + (7.2 * len(label) + 26) / 2, cy, label, color, bg)


ly = 650
parts += [
    f'<line x1="40" y1="{ly}" x2="90" y2="{ly}" stroke="{BOX_EDGE}" stroke-width="2.2"/>',
    text(100, ly + 4.5, "Rehearsed on Docker", 13, 400, MUTED),
    f'<line x1="300" y1="{ly}" x2="350" y2="{ly}" stroke="{BOX_EDGE}" stroke-width="2.2" stroke-dasharray="7 6"/>',
    text(360, ly + 4.5, "Documented, not rehearsed", 13, 400, MUTED),
    pill_left(40, ly + 32, "Solr reindex", SOLR, SOLR_BG),
    text(166, ly + 36.5, "Only if you keep Solr at the 7.4.2 stop (Solr 4 to Search Services).", 13, 400, MUTED),
    pill_left(40, ly + 64, "OpenSearch initial index", OS, OS_BG),
    text(253, ly + 68.5, "Required for every path into 26.2. Old content is not indexed by default.", 13, 400, MUTED),
]
parts.append("</svg>")

out = Path(__file__).with_name("upgrade-paths.svg")
out.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(out)
