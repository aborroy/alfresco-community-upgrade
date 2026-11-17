import json, sys, urllib.request, re
base = "https://docs.hyland.com/api/khub/maps/"
mid, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
d = json.load(urllib.request.urlopen(base + mid + "/topics"))
def walk(nodes, path):
    for n in nodes:
        p = path + [n["title"]]
        if pat.search(n["title"]):
            print(n.get("contentId"), "|", " > ".join(p))
        walk(n.get("children", []), p)
walk(d, [])
