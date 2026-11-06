"""Graphics-text edits on TIM pixels: the marker build paints each script/graphics.tsv rect with its row number.

Row number = line of graphics.tsv, counting from 1 under the header; `python tools/gfx.py ids` prints the map. Lyric
lines are marked as card.line. Pixels only ever change inside a row's rect, through tim.with_pixels, so the STP bit
and the CLUT stay untouched."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx_script
import tim

KEEP_FORMS = {"keep"}
# One font and size per label class (form column of graphics.tsv): (file in fonts/, size, 1 px outline)
CLASSES = {
    "menu": ("Bangers-Regular.ttf", 16, True),
    "cells": ("Jersey10-Regular.ttf", 20, False),
    "button": ("Jersey10-Regular.ttf", 20, False),
    "tag": ("Jersey10-Regular.ttf", 10, True),
    "credit": ("Jersey15-Regular.ttf", 15, True),
    "plate": ("Jersey10-Regular.ttf", 20, False),
    "card": ("Bangers-Regular.ttf", 28, True),
    "banner": ("Bangers-Regular.ttf", 34, True),
    "stamp": ("Bangers-Regular.ttf", 40, True),
    "hud": ("Bangers-Regular.ttf", 14, True),
    "sprite": ("Jersey10-Regular.ttf", 10, False),
}
DIGITS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
    ".": ("000", "000", "000", "000", "010"),
}


def ink_indices(t):
    """(dark, bright) CLUT 0 indices, skipping the transparent colour 0 (a black that is non-zero is opaque)."""
    n = 2 ** t.bpp
    pal = list(t.clut[:n]) if t.clut else []
    used = [(i, c) for i, c in enumerate(pal) if c]
    if not used:
        return 1, n - 1
    luma = lambda c: (c & 31) * 2 + ((c >> 5) & 31) * 4 + ((c >> 10) & 31)  # noqa: E731
    return min(used, key=lambda e: luma(e[1]))[0], max(used, key=lambda e: luma(e[1]))[0]


def paint_marker(vals, width, rect, label, dark, bright):
    """Solid dark rect with a bright 1 px frame, filled with the label repeated, so a clipped edge or a stray neighbour
    shows at once in game. Wrapped into lines when the rect is too narrow for one copy."""
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            edge = y in (y0, y0 + h - 1) or x in (x0, x0 + w - 1)
            vals[y * width + x] = bright if edge else dark
    per_line = max(1, (w - 2) // 4)
    text = (label + " ") * (per_line * h // (len(label) + 1) + 2)
    lines = (h - 2) // 6 or 1
    for ln in range(lines):
        row = text[ln * per_line:(ln + 1) * per_line]
        for ci, ch in enumerate(row):
            g = DIGITS.get(ch)
            if not g:
                continue
            for gy, bits in enumerate(g):
                for gx, b in enumerate(bits):
                    px, py = x0 + 1 + ci * 4 + gx, y0 + 1 + ln * 6 + gy
                    if b == "1" and px < x0 + w - 1 and py < y0 + h - 1:
                        vals[py * width + px] = bright


def row_numbers():
    return {r.id: i + 1 for i, r in enumerate(gfx_script.rows())}


def marker_rects():
    """{file: [(rect, label), ...]} for the whole marker build."""
    out = {}
    for i, r in enumerate(gfx_script.rows()):
        if r.form not in KEEP_FORMS:
            out.setdefault(r.file, []).append(((r.x, r.y, r.w, r.h), str(i + 1)))
    for ln in (ROOT / "script" / "lyric_lines.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        card, n, *rect = ln.split("\t")
        out.setdefault(f"OPTI/CARD{card}", []).append((tuple(map(int, rect)), f"{int(card)}.{n}"))
    return out


def pixel_width(t):
    return t.px_wh[0] * (4 if t.bpp == 4 else 2)


def glyphs(text, form):
    """(ink, outline) boolean arrays of the text in its class style, cropped to the ink. "|" breaks a line."""
    name, size, outline = CLASSES[form]
    font = ImageFont.truetype(str(ROOT / "fonts" / name), size)
    lines = text.split("|")
    w = max(int(font.getlength(ln)) for ln in lines) + 8
    pitch = sum(font.getmetrics())
    img = Image.new("1", (w, pitch * len(lines) + 8))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"  # no antialiasing: smoothed small text turns to mush in a 16-colour palette
    for n, ln in enumerate(lines):
        d.text((w // 2, 4 + n * pitch), ln, font=font, fill=1, anchor="ma")
    ink = np.array(img)
    rows, cols = np.flatnonzero(ink.any(axis=1)), np.flatnonzero(ink.any(axis=0))
    ink = ink[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
    if not outline:
        return ink, np.zeros_like(ink)
    ink = np.pad(ink, 1)
    halo = np.zeros_like(ink)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            halo |= np.roll(np.roll(ink, dy, 0), dx, 1)
    return ink, halo & ~ink


def row_width(text, form):
    """The width gate: pixels this text takes in its class. Compare with the row's rect; tests/test_gfx.py asserts it."""
    return glyphs(text, form)[0].shape[1]


def mode(vals):
    v, c = np.unique(vals, return_counts=True)
    return int(v[c.argmax()])


def sampled_inks(px, clut, margin=None, stone=False):
    """(background per row, fill per row, outline) indices of a rect of the original; per row because labels sit on
    palette gradients. Background: the commonest of the row's margin (columns beside the rect, as a tight rect's own ends
    can hold ink), or of its end columns. Fill: the commonest inside the strokes; per row only when no one index
    dominates, which is a gradient. Thin strokes take the brightest ink. Outline: the commonest other ink.
    stone: engraved on a noisy texture, so one background and the darkest ink.
    shortcut: stone flattens the plate's texture inside the rect; inpaint it if the flat patch reads badly in QA."""
    ends = np.concatenate([px[:, :2], px[:, -2:]], axis=1)
    side = ends if margin is None or not margin.size else margin
    if clut[0] == 0 and (px == 0).mean() >= 0.1:  # see-through: in a packed atlas the margin holds neighbours' ink
        bg = np.zeros(len(px), int)
    elif stone or (side == mode(side)).mean() >= 0.6:
        bg = np.full(len(px), mode(side))
    else:
        bg = np.array([mode(row) for row in side])
    ink = px != bg[:, None]
    if not ink.any():
        return bg, bg, int(bg[0])
    luma = lambda i: (clut[i] & 31) * 2 + ((clut[i] >> 5) & 31) * 4 + ((clut[i] >> 10) & 31)  # noqa: E731
    if stone:
        return bg, np.full(len(px), min(np.unique(px[ink]).tolist(), key=luma)), int(bg[0])
    core = np.zeros_like(ink)
    core[1:-1, 1:-1] = ink[1:-1, 1:-1] & ink[:-2, 1:-1] & ink[2:, 1:-1] & ink[1:-1, :-2] & ink[1:-1, 2:]
    if not core.any():
        fill = np.full(len(px), max(np.unique(px[ink]).tolist(), key=luma))
    elif (px[core] == mode(px[core])).mean() >= 0.6:
        fill = np.full(len(px), mode(px[core]))
    else:
        have = np.flatnonzero(core.any(axis=1))
        fill = np.array([mode(px[y][core[y]]) for y in have[np.abs(have[:, None] - np.arange(len(px))).argmin(axis=0)]])
    rest = px[ink & ~np.isin(px, fill)]
    return bg, fill, mode(rest) if rest.size else int(fill[0])


def typeset(data, rows):
    """data (a TIM file) with each (rect, text, form, align) rect cleared and lettered. Raises ValueError on overflow:
    English is never clipped silently."""
    t = tim.parse(data)
    assert t and t.bpp in (4, 8), "not a CLUT TIM"
    width = pixel_width(t)
    px = np.array(tim.pixels(t, data), dtype=np.int32).reshape(t.px_wh[1], width)
    for (x, y, w, h), text, form, align in rows:
        assert x + w <= width and y + h <= t.px_wh[1], f"rect {x, y, w, h} outside {width}x{t.px_wh[1]}"
        ink, halo = glyphs(text, form)
        gh, gw = ink.shape
        if gw > w or gh > h:
            raise ValueError(f"{text!r} is {gw}x{gh} in class {form}, rect is {w}x{h}")
        margin = np.concatenate([px[y:y + h, max(x - 3, 0):x], px[y:y + h, x + w:x + w + 3]], axis=1)
        bg, fill, line = sampled_inks(px[y:y + h, x:x + w], t.clut, margin, form == "plate")
        cell = px[y:y + h, x:x + w]
        cell[:] = bg[:, None]
        oy, ox = (h - gh) // 2, 0 if align == "l" else (w - gw) // 2
        box = cell[oy:oy + gh, ox:ox + gw]
        box[halo] = line
        box[ink] = np.broadcast_to(fill[oy:oy + gh, None], ink.shape)[ink]
    return tim.with_pixels(t, data, px.reshape(-1).tolist())


def spike_rows(path=ROOT / "script" / "spike.tsv"):
    """{file: [(rect, text, form, align), ...]} of the font spike's test lines. Columns id, en, class (empty = the
    row's), rect (empty = the row's; x,y,w,h for a credit cell the spike rewrites)."""
    by_id = {r.id: r for r in gfx_script.rows()}
    out = {}
    for ln in path.read_text(encoding="utf-8").splitlines()[1:]:
        rid, en, form, rect = ln.split("\t")
        r = by_id[rid]
        align = "l" if rid.startswith(("extra.", "end.")) else "c"
        box = tuple(map(int, rect.split(","))) if rect else (r.x, r.y, r.w, r.h)
        out.setdefault(r.file, []).append((box, en, form or r.form, align))
    return out


def marked(data, rects):
    """data (a TIM file) with every rect painted."""
    t = tim.parse(data)
    assert t, "not a TIM"
    vals = tim.pixels(t, data)
    width = pixel_width(t)
    dark, bright = ink_indices(t)
    for rect, label in rects:
        x, y, w, h = rect
        assert x + w <= width and y + h <= t.px_wh[1], f"rect {rect} outside {width}x{t.px_wh[1]}"
        paint_marker(vals, width, rect, label, dark, bright)
    return tim.with_pixels(t, data, vals)


if __name__ == "__main__":
    for i, r in enumerate(gfx_script.rows()):
        print(i + 1, r.id, r.jp, sep="\t")
