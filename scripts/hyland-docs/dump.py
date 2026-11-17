import json, sys, urllib.request, re, html
B = "https://docs.hyland.com"
mid, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
mode = sys.argv[3] if len(sys.argv) > 3 else "list"
d = json.load(urllib.request.urlopen(B + "/api/khub/maps/" + mid + "/topics"))
def text(h):
    h = re.sub(r"(?s)<(script|style).*?</\1>", "", h)
    h = re.sub(r"</(p|tr|li|h\d|div|table|pre)>", "\n", h)
    h = re.sub(r"</t[dh]>", " | ", h)
    h = re.sub(r"<[^>]+>", "", h)
    return re.sub(r"\n\s*\n+", "\n", html.unescape(h)).strip()
for t in d:
    bc = " > ".join(t.get("breadcrumb", []))
    if pat.search(t["title"]) or pat.search(bc):
        print("##", bc, "|", B + t["readerUrl"])
        if mode == "dump":
            print(text(urllib.request.urlopen(B + t["contentApiEndpoint"]).read().decode()))
            print()
