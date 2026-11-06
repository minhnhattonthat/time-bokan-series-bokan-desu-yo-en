"""Find where a file name appears in the EXE or overlays, or list NUL-terminated ASCII strings with RAM addresses.

    python -X utf8 tools/re.py names TAIM_ GO_S     # which file holds each path, at what RAM address
    python -X utf8 tools/re.py read 8005C050 16     # u32 words from RAM image (EXE and overlays do not overlap in name)
"""
import glob
import os
import re
import struct
import sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "x")
OVL_BASE = 0x80159E50
EXE_BASE = 0x80010000 - 0x800


def images():
    yield "TARGET.EXE", EXE_BASE, open(os.path.join(ROOT, "TARGET.EXE"), "rb").read()
    for p in sorted(glob.glob(os.path.join(ROOT, "S*OVER.BIN"))):
        yield os.path.basename(p), OVL_BASE, open(p, "rb").read()


def names(words):
    for name, base, d in images():
        for w in words:
            for m in re.finditer(rb"[\x20-\x7E]*" + re.escape(w.encode()) + rb"[\x20-\x7E]*", d):
                print(f"{name:14} {base + m.start():08X} {m.group().decode()}")


def read(addr, count):
    d = open(os.path.join(ROOT, "TARGET.EXE"), "rb").read()
    print(" ".join(f"{x:08X}" for x in struct.unpack_from(f"<{count}I", d, addr - EXE_BASE)))


if __name__ == "__main__":
    if sys.argv[1] == "names":
        names(sys.argv[2:])
    elif sys.argv[1] == "read":
        read(int(sys.argv[2], 16), int(sys.argv[3]))
    else:
        sys.exit(__doc__)
