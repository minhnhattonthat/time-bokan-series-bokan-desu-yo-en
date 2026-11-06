"""The credit roll by line: each S10OVER cell group, with the Japanese its parts draw, read through script/graphics.tsv.

usage: credits.py dump [--out script/credits.tsv]
A part's TIM comes from which stretch of the table it sits in (FILES below, checked against the roll's VRAM dumps)."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cells
import gfx_script

FIRST = 0x8015DDA4
# (first group address, file) in table order
FILES = [(0x8015DDA4, "DATA/END_4"), (0x8015E11C, "DATA/END_5"), (0x8015E508, "DATA/END_4"), (0x8015E5AC, "DATA/END_5"),
         (0x8015E5C8, "DATA/END_6")]


def file_of(addr):
    out = None
    for a, f in FILES:
        if addr >= a:
            out = f
    return out


def lines():
    d = (ROOT / "work" / "x" / "S10OVER.BIN").read_bytes()
    return [g for g in cells.groups(d) if g.addr >= FIRST]


def part_text(file, p, rows):
    """Row texts under this part, left to right: a row counts when most of it lies inside the part."""
    hit = []
    for r in rows:
        if r.file != file:
            continue
        ox = min(r.x + r.w, p.u + p.w) - max(r.x, p.u)
        oy = min(r.y + r.h, p.v + p.h) - max(r.y, p.v)
        if ox > 0 and oy > 0 and ox * oy * 2 >= r.w * r.h:
            hit.append((r.y, r.x, r.jp))
    return "".join(h[2] for h in sorted(hit))


def dump(out):
    rows = gfx_script.rows()
    res = ["line\taddr\tfile\trole_jp\tname_jp\tparts"]
    for n, g in enumerate(lines(), 1):
        f = file_of(g.addr)
        role = "".join(part_text(f, p, rows) for p in g.parts if p.dx < 0)
        name = "".join(part_text(f, p, rows) for p in g.parts if p.dx >= 0)
        parts = " ".join(f"{p.u},{p.v},{p.w},{p.h}@{p.dx},{p.dy}" for p in g.parts)
        res.append(f"{n}\t{g.addr:08X}\t{f}\t{role}\t{name}\t{parts}")
    Path(out).write_text("\n".join(res) + "\n", encoding="utf-8")
    print(len(res) - 1, "lines", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["dump"])
    ap.add_argument("--out", default=str(ROOT / "script" / "credits.tsv"))
    a = ap.parse_args()
    dump(a.out)
