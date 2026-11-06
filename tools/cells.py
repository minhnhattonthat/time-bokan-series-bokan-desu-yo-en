"""The game's sprite cell groups: a u32 part count, then 12-byte parts u8 u, v; s8 dx, dy; u16 w, h; u16 sx, sy (4096 = 1:1).

usage: cells.py scan FILE [--base 0x80159E50]     every group found, with RAM address
       cells.py rows FILE ID_PREFIX               groups whose parts sample a graphics.tsv row (rows of that prefix)
Library: groups(data, base) -> [Group]. Reading only; build code writes parts back through with_part()."""
import argparse
import struct
import sys
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

Part = namedtuple("Part", "off u v dx dy w h sx sy")
Group = namedtuple("Group", "off addr parts")
OVL_BASE = 0x80159E50


def part_at(d, o):
    u, v, dx, dy, w, h, sx, sy = struct.unpack_from("<BBbbHHHH", d, o)
    return Part(o, u, v, dx, dy, w, h, sx, sy)


def valid(p):
    return 0 < p.w <= 256 and 0 < p.h <= 256 and p.sx == 4096 and p.sy == 4096 and p.u + p.w <= 256 and p.v + p.h <= 256


def groups(d, base=OVL_BASE):
    """Greedy walk: a group is a count 1..64 followed by that many valid parts; a found group is skipped whole."""
    out = []
    o = 0
    while o + 16 <= len(d):
        n = struct.unpack_from("<I", d, o)[0]
        if 1 <= n <= 64 and o + 4 + n * 12 <= len(d):
            ps = [part_at(d, o + 4 + i * 12) for i in range(n)]
            if all(valid(p) for p in ps):
                out.append(Group(o, base + o, ps))
                o += 4 + n * 12
                continue
        o += 4
    return out


def with_part(d, p):
    """Bytes d with part p written back at p.off."""
    return d[:p.off] + struct.pack("<BBbbHHHH", p.u, p.v, p.dx, p.dy, p.w, p.h, p.sx, p.sy) + d[p.off + 12:]


def with_edits(d, path, base=OVL_BASE):
    """d with the parts of a tsv (addr part u v dx dy w h sx sy note) rewritten. The group's part count stays."""
    for ln in Path(path).read_text(encoding="utf-8").splitlines()[1:]:
        c = ln.split("\t")
        off = int(c[0], 16) - base
        assert 0 <= int(c[1]) < struct.unpack_from("<I", d, off)[0], f"no part {c[1]} in group {c[0]}"
        d = with_part(d, Part(off + 4 + int(c[1]) * 12, *map(int, c[2:10])))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["scan"])
    ap.add_argument("file")
    ap.add_argument("--base", type=lambda s: int(s, 16), default=OVL_BASE)
    a = ap.parse_args()
    d = open(a.file, "rb").read()
    gs = groups(d, a.base)
    print(f"{len(gs)} groups, {sum(len(g.parts) for g in gs)} parts")
    for g in gs:
        print(f"{g.addr:08X} " + " | ".join(f"{p.u},{p.v} {p.w}x{p.h} at {p.dx:+},{p.dy:+}" for p in g.parts))


if __name__ == "__main__":
    main()
