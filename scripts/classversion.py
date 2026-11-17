"""Reports the Java class-file versions used in a JAR or AMP, including nested JARs.

Usage: python3 -I scripts/classversion.py <addon.jar|addon.amp> [<target java release>]
Exits with status 1 if a class needs a newer Java than the target release.
"""

import io
import sys
import zipfile
from collections import Counter

# Class-file major version = Java release + 44 (Java 8 = 52, 11 = 55, 17 = 61, 21 = 65).
OFFSET = 44


def scan(zf, path, versions, nested):
    for name in zf.namelist():
        if name.endswith(".class"):
            head = zf.open(name).read(8)
            if head[:4] == b"\xca\xfe\xba\xbe":
                versions[int.from_bytes(head[6:8], "big") - OFFSET] += 1
        elif name.endswith(".jar"):
            nested.append(f"{path}!/{name}")
            with zipfile.ZipFile(io.BytesIO(zf.read(name))) as inner:
                scan(inner, f"{path}!/{name}", versions, nested)


def main():
    addon = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else None
    versions, nested = Counter(), []
    with zipfile.ZipFile(addon) as zf:
        scan(zf, addon, versions, nested)
    print("Class files by Java release: " + ", ".join(f"Java {v}: {n}" for v, n in sorted(versions.items())))
    print(f"Bundled JARs: {len(nested)}")
    for n in nested:
        print(f"  {n.split('!/')[-1]}")
    if not versions:
        print("No class files found.")
        return 0
    needed = max(versions)
    if target is not None and needed > target:
        print(f"FAIL needs Java {needed}, target runs Java {target}")
        return 1
    print(f"OK needs Java {needed}" + (f", target runs Java {target}" if target else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
