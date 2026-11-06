"""Pixel budgets for script/graphics.tsv rows: what the game actually samples and where it draws it.

usage: budgets.py [--prims work/recon/prims_rows.tsv] [--out script/budgets.tsv]
Sources, best first: quad = seen in a GPU dump (tools/prims.py); cell = a part of the file's overlay cell table hugs the
rect (tools/cells.py), not seen in a dump; none = neither, so the row's own rect is only a guess. Parts overlapping under
half of a row are not counted, and a row split over several parts lists each. The `uv` column is what English must fit."""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cells
import gfx_script

EXE_BASE = 0x8000F800


def owner(file):
    """Which code image holds the cells for this TIM."""
    if file.startswith(("SUBDATA/TITLE", "SUBDATA/CONFIG", "SUBDATA/OPTI", "OPTI/")):
        return "S8OVER"
    if file.startswith("DATA/END"):
        return "S10OVER"
    if file.startswith("STAGE"):
        return f"S{file[5]}OVER"
    return "TARGET"


def load_cells():
    out = {}
    for name in ["TARGET", "S10OVER", "S8OVER"] + [f"S{n}OVER" for n in range(1, 8)]:
        path = ROOT / "work" / "x" / (name + ".EXE" if name == "TARGET" else name + ".BIN")
        base = EXE_BASE if name == "TARGET" else cells.OVL_BASE
        out[name] = {(p.u, p.v, p.w, p.h) for g in cells.groups(path.read_bytes(), base) for p in g.parts}
    return out


def overlap(r, u, v, w, h):
    ox = min(r.x + r.w, u + w) - max(r.x, u)
    oy = min(r.y + r.h, v + h) - max(r.y, v)
    return max(ox, 0) * max(oy, 0)


def read_quads(path):
    q = defaultdict(set)
    for ln in Path(path).read_text(encoding="utf-8").splitlines()[1:]:
        c = ln.split("\t")
        if c[3] == "NOT DRAWN":
            continue
        q[c[0]].add((tuple(map(int, c[3].split(","))), tuple(map(int, c[4].split(",")))))
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prims", default=str(ROOT / "work" / "recon" / "prims_rows.tsv"))
    ap.add_argument("--out", default=str(ROOT / "script" / "budgets.tsv"))
    a = ap.parse_args()
    quads = read_quads(a.prims)
    tables = load_cells()
    lines = ["id\tfile\trect\tsource\tuv\tscreen"]
    count = defaultdict(int)
    for r in gfx_script.rows():
        area = r.w * r.h
        rect = f"{r.x},{r.y},{r.w},{r.h}"
        if r.form == "keep":
            continue
        seen = [(uv, sc) for uv, sc in quads.get(r.id, ()) if overlap(r, *uv) * 2 >= min(area, uv[2] * uv[3])]
        if seen:
            uvs = sorted({uv for uv, _ in seen})
            screens = sorted({sc[:2] for uv, sc in seen})[:4]
            source = "quad"
        else:
            # shortcut: cell tables don't say which TIM they sample, so only a part hugging the rect counts as evidence
            uvs = sorted(c for c in tables[owner(r.file)] if overlap(r, *c) == area and c[2] * c[3] <= area * 3)
            screens, source = [], "cell" if uvs else "none"
        count[source] += 1
        lines.append("\t".join([r.id, r.file, rect, source, ";".join(",".join(map(str, u)) for u in uvs),
                                ";".join(f"{x},{y}" for x, y in screens)]))
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(dict(count), a.out)


if __name__ == "__main__":
    main()
