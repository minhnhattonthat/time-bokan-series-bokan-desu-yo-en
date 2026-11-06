"""The credit roll: line = index into S10OVER's group table. Its data is all in S10OVER.BIN (docs/re/cells.md).

usage: credits.py dump [--out FILE]    every line, its TIM, palette and the Japanese its parts draw
       credits.py pack                 where the English strips land, by TIM
Library: edit_tim(file, data) and edit_overlay(data) give the build its bytes."""
import argparse
import struct
import sys
from collections import namedtuple
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cells
import disc
import gfx
import gfx_script
import tim

TRACK1 = "Time Bokan Series - Bokan desu yo (Japan) (Track 01).bin"
BASE = cells.OVL_BASE
TABLE = 0x8015EA4C   # u32 group pointer per line
ART = 0x8015EF4C     # per line: u32 slot (TIM END_<slot>, texture page 0x15 + slot), u32 palette (CLUT row 0x1F0 + n)
SCRIPT = 0x8015EC0C  # u16 words: -2/-3/-4 + arg are scene commands, -1 ends, else duration, n, n x (line, x, y, end)
LINES = 82           # the group table's length; ART stops at 80: lines 80 and 81 are never drawn
HEADS = {0: ((35, 224, 81, 24), "head"), 18: ((35, 224, 177, 24), "head"),
         44: ((146, 224, 68, 24), "menu"), 50: ((145, 200, 102, 24), "menu")}
COPYRIGHT = 77       # keeps its (C) cell, which line 78 draws too; lines 77-78 are placed by code, not by SCRIPT
COPY_RECT = (24, 208, 96, 16)
# TIM areas that stay: heading art, and in END_6 the kept English of line 78. Lines 80-81 are never drawn: their art goes.
KEEP = {
    "DATA/END_4": [(8, 224, 206, 24)],
    "DATA/END_5": [(120, 200, 128, 24), (8, 224, 240, 32)],
    "DATA/END_6": [(8, 208, 112, 16), (120, 208, 112, 16), (168, 192, 40, 16), (232, 208, 24, 16)],
}
FILL, ROLE_LINE, NAME_LINE = 15, 3, 2  # the original strips' inks: the line's colour, outlined pale for roles, white for names
BLOCK = 2            # shelf 0 starts here: (0, 0) stays transparent so spare parts can sample it
LINE_H = 16         # least pitch of one-row lines
TOP = 38            # first screen row clear of the roll's curtain
Placed = namedtuple("Placed", "u v w")


def overlay():
    """S10OVER from the original disc."""
    d = disc.Disc(str(ROOT / "rom" / TRACK1))
    data = d.read("/S10OVER.BIN")
    d.f.close()
    return data


def lines(d=None):
    """[Group] by line."""
    d = d or overlay()
    out = []
    for addr in struct.unpack_from(f"<{LINES}I", d, TABLE - BASE):
        off = addr - BASE
        n = struct.unpack_from("<I", d, off)[0]
        out.append(cells.Group(off, addr, [cells.part_at(d, off + 4 + i * 12) for i in range(n)]))
    return out


def art(d=None):
    """[(slot, palette)] by line, for the 80 lines the game can draw."""
    d = d or overlay()
    return [struct.unpack_from("<II", d, ART - BASE + i * 8) for i in range(80)]


def pages(d=None):
    """[[(offset of y, line, y), ...]] the roll's pages in order."""
    d = d or overlay()
    o = SCRIPT - BASE
    out = []
    while True:
        h = struct.unpack_from("<H", d, o)[0]
        if h == 0xFFFF:
            return out
        if h >= 0xFFFC:
            o += 4
            continue
        n = struct.unpack_from("<H", d, o + 2)[0]
        o += 4
        page = []
        for _ in range(n):
            line, _x, y, _end = struct.unpack_from("<4H", d, o)
            page.append((o + 4, line, y))
            o += 8
        out.append(page)


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
    d = overlay()
    table = art(d)
    res = ["line\taddr\tfile\tpalette\trole_jp\tname_jp\tparts"]
    for n, g in enumerate(lines(d)):
        slot, pal = table[n] if n < len(table) else (6, "")
        f = f"DATA/END_{slot}"
        role = "".join(part_text(f, p, rows) for p in g.parts if p.dx < 0)
        name = "".join(part_text(f, p, rows) for p in g.parts if p.dx >= 0)
        parts = " ".join(f"{p.u},{p.v},{p.w},{p.h}@{p.dx},{p.dy}" for p in g.parts)
        res.append(f"{n}\t{g.addr:08X}\t{f}\t{pal}\t{role}\t{name}\t{parts}")
    Path(out).write_text("\n".join(res) + "\n", encoding="utf-8")
    print(len(res) - 1, "lines", out)


def english():
    import tl_check
    return {int(r["line"]): r for r in tl_check.table(ROOT / "script" / "en" / "credits.tsv")}


def strips_of(row):
    """[(text, outline index)] the line's parts draw, roles first."""
    role = [(p, ROLE_LINE) for p in row["role"].split("|") if p]
    return role + ([(row["name"], NAME_LINE)] if row["name"] else [])


def drawn_lines(en):
    """Lines lettered as strips: headings and the copyright card are drawn in place; 78, 80, 81 keep their parts."""
    return [n for n in en if n < 80 and n not in HEADS and n not in (COPYRIGHT, 78)]


def strip_rows(en):
    """(top, bottom) of the raster holding every strip's ink, so all strips share a baseline."""
    top, bottom = 10 ** 6, 0
    for n in drawn_lines(en):
        for text, _ in strips_of(en[n]):
            rows = np.flatnonzero(gfx.raster(text, "credit").any(axis=1))
            top, bottom = min(top, rows[0]), max(bottom, rows[-1] + 1)
    return int(top), int(bottom)


def pack(en=None, d=None):
    """{file: {(text, outline): Placed}} and the strip height. First-fit decreasing on shelves. ValueError on overflow."""
    en = en or english()
    table = art(d)
    span = strip_rows(en)
    height = span[1] - span[0] + 2
    wanted = {}
    for n in drawn_lines(en):
        f = f"DATA/END_{table[n][0]}"
        wanted.setdefault(f, set()).update(strips_of(en[n]))
    out = {}
    for f, strips in wanted.items():
        shelves = free_runs(f, height)
        placed = {}
        sized = sorted(strips, key=lambda s: (-gfx.glyphs(s[0], "credit", span)[0].shape[1], s))
        for s in sized:
            w = gfx.glyphs(s[0], "credit", span)[0].shape[1]
            run = next((r for r in shelves if r[1] + w <= r[2]), None)
            if run is None:
                raise ValueError(f"{f}: no room for {s[0]!r}: {len(shelves)} runs of {height} px")
            placed[s] = Placed(run[1], run[0], w)
            run[1] += w + 1
        out[f] = placed
    return out, height


def free_runs(file, height):
    """[[v, u, end]] the free stretches of each shelf, clear of KEEP; (0, 0) stays transparent for spare parts."""
    runs = []
    for v in range(0, 256 - height + 1, height):
        hits = sorted((x, x + w) for x, y, w, h in KEEP[file] if y < v + height and v < y + h)
        u = BLOCK if v == 0 else 0
        for a, b in hits + [(256, 256)]:
            if a > u:
                runs.append([v, u, a])
            u = max(u, b)
    return runs


def role_parts(row, height, widths):
    """[(index into strips_of(row), dx, dy)]: role at -120, name at 0, a long name sliding left over a short role."""
    strips = strips_of(row)
    if not row["name"] and len(strips) == 1:  # a centred title
        return [(0, -widths[0] // 2, -height // 2)]
    name_dx = 0
    out = []
    if row["name"]:
        name_dx = min(0, 152 - widths[-1])
        out.append((len(strips) - 1, name_dx, -height // 2))
    roles = strips[:-1] if row["name"] else strips
    for i in range(len(roles)):
        dx = min(-120, name_dx - 8 - widths[i]) if row["name"] else -120
        if dx < -128:
            raise ValueError(f"{row!r}: role at dx {dx}")
        dy = -height // 2 if len(roles) == 1 else -height + i * height
        out.append((i, dx, dy))
    return out


def page_ys(page, height, en):
    """New y per line of one page, or the old ones when nothing collides: a page holding a two-row line opens up, around
    its original middle."""
    tall = lambda line: (24 if line in HEADS else 2 * height + 2 if "|" in en[line]["role"] else LINE_H)  # noqa: E731
    ys = [p[2] for p in page]
    need = [(tall(a[1]) + tall(b[1])) // 2 for a, b in zip(page, page[1:])]
    if all(y2 - y1 >= g for y1, y2, g in zip(ys, ys[1:], need)):
        return ys
    new = [0]
    for g in need:
        new.append(new[-1] + g)
    shift = (ys[0] + ys[-1] - new[-1]) // 2
    shift = max(shift, TOP + tall(page[0][1]) // 2)  # the curtain hides anything above TOP
    new = [y + shift for y in new]
    if new[-1] + tall(page[-1][1]) // 2 > 170:
        raise ValueError(f"page of lines {[p[1] for p in page]} doesn't fit: {new}")
    return new


def edit_overlay(d, en=None):
    """S10OVER with every drawn line's parts pointing at its strips, spare parts at a transparent pixel, pages re-spaced."""
    en = en or english()
    d = bytes(d)
    placed, height = pack(en, d)
    span = strip_rows(en)
    table = art(d)
    groups = lines(d)
    for n in drawn_lines(en):
        f = f"DATA/END_{table[n][0]}"
        strips = strips_of(en[n])
        widths = [gfx.glyphs(s[0], "credit", span)[0].shape[1] for s in strips]
        parts = role_parts(en[n], height, widths)
        g = groups[n]
        if len(parts) > len(g.parts):
            raise ValueError(f"line {n}: {len(parts)} strips for {len(g.parts)} parts")
        for i, old in enumerate(g.parts):
            if i < len(parts):
                s, dx, dy = parts[i]
                pl = placed[f][strips[s]]
                d = cells.with_part(d, old._replace(u=pl.u, v=pl.v, w=pl.w, h=height, dx=dx, dy=dy, sx=4096, sy=4096))
            else:
                d = cells.with_part(d, old._replace(u=0, v=0, w=1, h=1, dx=0, dy=0, sx=4096, sy=4096))
    theme = groups[44].parts  # the word part grows to its wider English, and the flipped pig moves out with it
    d = cells.with_part(cells.with_part(d, theme[0]._replace(w=94, dx=-59)), theme[1]._replace(dx=35))
    out = bytearray(d)
    for page in pages(d):
        for (off, _, _), y in zip(page, page_ys(page, height, en)):
            struct.pack_into("<H", out, off, y)
    return bytes(out)


def edit_tim(file, data, en=None):
    """A credit TIM with everything but KEEP cleared to transparent, its heading re-lettered, and the strips laid in."""
    en = en or english()
    d = overlay()
    t = tim.parse(data)
    placed, _ = pack(en, d)
    span = strip_rows(en)
    table = art(d)
    rows = [(rect, en[n]["role"], form, "c") for n, (rect, form) in HEADS.items() if f"DATA/END_{table[n][0]}" == file]
    if rows:
        data = gfx.typeset(data, rows)
    px = gfx.tim_px(t, data)
    keep = np.zeros(px.shape, bool)
    for x, y, w, h in KEEP[file]:
        keep[y:y + h, x:x + w] = True
    px[~keep] = 0
    if file == "DATA/END_6":
        x, y, w, h = COPY_RECT
        ink, halo = gfx.glyphs(en[COPYRIGHT]["role"].removeprefix("(C) "), "hud")
        if ink.shape[1] > w or ink.shape[0] > h:
            raise ValueError(f"line {COPYRIGHT} is {ink.shape[1]}x{ink.shape[0]}, rect {w}x{h}")
        px[y:y + h, x:x + w] = 0
        cell = px[y + (h - ink.shape[0]) // 2:y + (h - ink.shape[0]) // 2 + ink.shape[0], x:x + ink.shape[1]]
        cell[halo] = 15
        cell[ink] = 2
    for (text, line), p in placed[file].items():
        ink, halo = gfx.glyphs(text, "credit", span)
        cell = px[p.v:p.v + ink.shape[0], p.u:p.u + p.w]
        cell[halo] = line
        cell[ink] = FILL
    return tim.with_pixels(t, data, px.reshape(-1).tolist())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["dump", "pack"])
    ap.add_argument("--out", default=str(ROOT / "work" / "credits_parts.tsv"))
    a = ap.parse_args()
    if a.cmd == "dump":
        dump(a.out)
    else:
        result, h = pack()
        for name, strips in sorted(result.items()):
            print(name, len(strips), "strips, lowest shelf", max(p.v for p in strips.values()), "of", h, "px rows")
