"""Graphics-text edits on TIM pixels: the marker build paints each script/graphics.tsv rect with its row number.

Row number = line of graphics.tsv, counting from 1 under the header; `python tools/gfx.py ids` prints the map. Lyric
lines are marked as card.line. Pixels only ever change inside a row's rect, through tim.with_pixels, so the STP bit
and the CLUT stay untouched."""
import sys
from collections import namedtuple
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
    "gameover": ("Bangers-Regular.ttf", 56, True),
    "head": ("Bangers-Regular.ttf", 18, True),
    "hud": ("Bangers-Regular.ttf", 14, True),
    "hudplain": ("Bangers-Regular.ttf", 12, False),
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


def raster(text, form):
    """Boolean ink of the text on a frame that is the same for every one-line text of a class."""
    name, size, _ = CLASSES[form]
    font = ImageFont.truetype(str(ROOT / "fonts" / name), size)
    lines = text.split("|")
    w = max(int(font.getlength(ln)) for ln in lines) + 8
    pitch = sum(font.getmetrics())
    img = Image.new("1", (w, pitch * len(lines) + 8))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"  # no antialiasing: smoothed small text turns to mush in a 16-colour palette
    for n, ln in enumerate(lines):
        d.text((w // 2, 4 + n * pitch), ln, font=font, fill=1, anchor="ma")
    return np.array(img)


def glyphs(text, form, rows=None):
    """(ink, outline) boolean arrays of the text in its class style, cropped to the ink. "|" breaks a line. rows = (top,
    bottom) of the raster keeps that span instead of the text's own, so strips of one class share a baseline."""
    outline = CLASSES[form][2]
    ink = raster(text, form)
    own, cols = np.flatnonzero(ink.any(axis=1)), np.flatnonzero(ink.any(axis=0))
    top, bottom = rows or (own[0], own[-1] + 1)
    ink = ink[top:bottom, cols[0]:cols[-1] + 1]
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


def sampled_inks(px, clut, margin=None, stone=False, flat=False):
    """(background per row, fill per row, outline) indices of a rect of the original; per row because labels sit on
    palette gradients. Background: the commonest of the row's margin (columns beside the rect, as a tight rect's own ends
    can hold ink), or of its end columns. Fill: the commonest inside the strokes; per row only when no one index
    dominates, which is a gradient. Thin strokes take the brightest ink. Outline: the commonest other ink.
    stone: engraved on a noisy texture, so one background and the darkest ink. flat: a solid box whose margin holds other
    art (a button's mark), so one background.
    shortcut: stone flattens the plate's texture inside the rect; inpaint it if the flat patch reads badly in QA."""
    ends = np.concatenate([px[:, :2], px[:, -2:]], axis=1)
    side = ends if margin is None or not margin.size else margin
    if clut[0] == 0 and (px == 0).mean() >= 0.1:  # see-through: in a packed atlas the margin holds neighbours' ink
        bg = np.zeros(len(px), int)
    elif flat:
        bg = np.full(len(px), mode(px))
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


Inks = namedtuple("Inks", "fill line clear bg", defaults=(True, None))
# Rows whose sampled inks fail. hud.gameover: the fill alternates 10 and 15 by row, which stripes the letters.
# sel.repair: lettered on the X that stamp_x redrew, so nothing is cleared. Thin one-ink kana and kanji (hints, tags,
# names, the sign) give no strokes to sample, and a packed strip's or speckled sign's margin no background.
ROW_INKS = {"hud.gameover": Inks(15, 10), "sel.repair": Inks(15, 1, False),
            "title.hint_select": Inks(15, 2, bg=2), "title.hint_ok": Inks(15, 2, bg=2),
            "title.hint_back1": Inks(15, 2, bg=2), "title.hint_back2": Inks(15, 2, bg=2),
            "opt.player1": Inks(15, 7), "opt.pad": Inks(15, 2),
            "sprite.itadaki1": Inks(12, 11), "sprite.itadaki2": Inks(12, 11), "sprite.itadaki3": Inks(12, 11),
            "sprite.sign1": Inks(3, 14, bg=14), "sprite.sign2": Inks(11, 14, bg=14)}
TAG_INKS = Inks(15, 1)  # ship name tags: white on a dark outline in every file


def stamp_x(data):
    """SELMAIN with 整備中 gone and the X it lay on redrawn. Each arm steps 1 px a row and the art mirrors about y 131.5,
    so clean row 121 gives every row the kanji covered. Only the row's own rect changes."""
    t = tim.parse(data)
    px = tim_px(t, data)
    x, y, w, h = next((r.x, r.y, r.w, r.h) for r in gfx_script.rows() if r.id == "sel.repair")
    top = 121
    drawn = np.zeros((y + h, px.shape[1]), dtype=px.dtype)
    for row in range(y, 132):
        k = row - top
        drawn[row, 119:122] = px[top, 119:122]
        drawn[row, 157:160] = px[top, 157:160]
        drawn[row, 124 + k:134 + k] = px[top, 124:134]
        drawn[row, 145 - k:155 - k] = px[top, 145:155]
        drawn[263 - row] = drawn[row]
    px[y:y + h, x:x + w] = drawn[y:y + h, x:x + w]
    return tim.with_pixels(t, data, px.reshape(-1).tolist())


def typeset(data, rows):
    """data (a TIM file) with each (rect, text, form, align) rect cleared and lettered. Raises ValueError on overflow:
    English is never clipped silently. A fifth item forces the inks: a clean rect of the original to sample, or Inks."""
    t = tim.parse(data)
    assert t and t.bpp in (4, 8), "not a CLUT TIM"
    width = pixel_width(t)
    px = np.array(tim.pixels(t, data), dtype=np.int32).reshape(t.px_wh[1], width)
    orig = px.copy()
    for (x, y, w, h), text, form, align, *sample in rows:
        assert x + w <= width and y + h <= t.px_wh[1], f"rect {x, y, w, h} outside {width}x{t.px_wh[1]}"
        ink, halo = glyphs(text, form)
        gh, gw = ink.shape
        if gw > w or gh > h:
            raise ValueError(f"{text!r} is {gw}x{gh} in class {form}, rect is {w}x{h}")
        margin = np.concatenate([px[y:y + h, max(x - 3, 0):x], px[y:y + h, x + w:x + w + 3]], axis=1)
        bg, fill, line = sampled_inks(px[y:y + h, x:x + w], t.clut, margin, form == "plate", form == "button")
        clear = True
        if sample and isinstance(sample[0], Inks):
            fill, line, clear = np.full(h, sample[0].fill), sample[0].line, sample[0].clear
            if sample[0].bg is not None:
                bg = np.full(h, sample[0].bg)
        elif sample:  # a list whose rows must match: take the inks of one clean row of the original
            sx, sy, sw, sh = sample[0]
            _, f2, line = sampled_inks(orig[sy:sy + sh, sx:sx + sw], t.clut)
            fill = np.full(h, f2[len(f2) // 2])
        cell = px[y:y + h, x:x + w]
        if clear:
            cell[:] = bg[:, None]
        oy, ox = (h - gh) // 2, 0 if align == "l" else (w - gw) // 2
        box = cell[oy:oy + gh, ox:ox + gw]
        box[halo] = line
        box[ink] = np.broadcast_to(fill[oy:oy + gh, None], ink.shape)[ink]
    return tim.with_pixels(t, data, px.reshape(-1).tolist())


def uv_box(budget, rect):
    """The row's smallest drawn box that holds its rect, or the rect when nothing was measured."""
    x, y, w, h = rect
    boxes = [tuple(map(int, u.split(","))) for u in budget["uv"].split(";")] if budget["uv"] else []
    held = [b for b in boxes if b[0] <= x and b[1] <= y and x + w <= b[0] + b[2] and y + h <= b[1] + b[3]]
    return min(held, key=lambda b: b[2] * b[3]) if held else rect


def widened(rect, need_w, need_h, box, others):
    """rect grown around its centre to need_w x need_h, inside box and clear of the other rows' rects. ValueError if it
    can't: an overflow must stop the build."""
    x, y, w, h = rect
    if need_w > w:
        x, w = max(box[0], min(x - (need_w - w) // 2, box[0] + box[2] - need_w)), need_w
    if need_h > h:
        y, h = max(box[1], min(y - (need_h - h) // 2, box[1] + box[3] - need_h)), need_h
    if x + w > box[0] + box[2] or y + h > box[1] + box[3]:
        raise ValueError(f"rect {rect} can't reach {need_w}x{need_h} inside {box}")
    for o in others:
        if x < o[0] + o[2] and o[0] < x + w and y < o[1] + o[3] and o[1] < y + h:
            raise ValueError(f"rect {rect} grown to {x, y, w, h} hits {o}")
    return x, y, w, h


def english_rows():
    """{file: [(rect, text, form, align), ...]} of script/en/graphics.tsv, each rect widened to its text if needed.
    The GAME OVER banner is left to go_banner()."""
    out = {}
    for _, file, row in english_items():
        out.setdefault(file, []).append(row)
    return out


def english_items():
    """(row id, file, typeset row) of each row english_rows() lists."""
    import tl_check
    budgets = {b["id"]: b for b in tl_check.table(ROOT / "script" / "budgets.tsv")}
    by_id = {r.id: r for r in gfx_script.rows()}
    en = [e for e in tl_check.table(ROOT / "script" / "en" / "graphics.tsv") if e["id"] not in GO_ROWS]
    forms = {e["id"]: e["class"] or by_id[e["id"]].form for e in en}
    for e in en:
        r = by_id[e["id"]]
        rect = (r.x, r.y, r.w, r.h)
        gh, gw = glyphs(e["en"], forms[e["id"]])[0].shape
        others = [(o.x, o.y, o.w, o.h) for o in by_id.values() if o.file == r.file and o.id != r.id and o.form != "keep"]
        if gw > r.w or gh > r.h:
            rect = widened(rect, max(gw, r.w), max(gh, r.h), uv_box(budgets[r.id], rect), others)
        row = (rect, e["en"], forms[e["id"]], "c")
        if r.id.startswith("extra."):
            row = (rect, e["en"], forms[e["id"]], "l", EXTRAS_INKS)
        inks = ROW_INKS.get(r.id, TAG_INKS if r.id.startswith("tag.") else None)
        if inks:
            row = (rect, e["en"], forms[e["id"]], "c", inks)
        yield r.id, r.file, row


GO_ROWS = ("go.game", "go.over_o", "go.over")
EXTRAS_INKS = (0, 0, 96, 16)  # extra.m00, whose inks every row of the list takes


def tim_px(t, data):
    return np.array(tim.pixels(t, data), dtype=np.int32).reshape(t.px_wh[1], pixel_width(t))


def go_banner(data):
    """GO_S0: GAME over two quads drawn side by side, OVER below it over one quad's foot and a third quad. Colours are
    sampled off the Japanese. pieces = (TIM x, y, w, h) with the canvas column and row they show."""
    t = tim.parse(data)
    px = tim_px(t, data)
    x, y, w, h = 160, 0, 64, 60  # ゲ: both words take its inks, as オ's thin strokes sample in bands
    inks = sampled_inks(px[y:y + h, x:x + w], t.clut)
    import tl_check
    en = {e["id"]: e["en"] for e in tl_check.table(ROOT / "script" / "en" / "graphics.tsv")}
    rows = ((en["go.game"], ((160, 0, 64, 60, 0, 0), (160, 96, 64, 60, 64, 0))),
            (en["go.over_o"] + en["go.over"], ((160, 62, 64, 30, 0, 2), (0, 224, 64, 28, 64, 4))))  # screen y 166 and 168: canvas rows 2 and 4
    for (u, v, w, h) in ((160, 0, 64, 96), (160, 96, 64, 64), (0, 222, 64, 33)):
        px[v:v + h, u:u + w] = 0
    _, fill, line = inks
    for text, pieces in rows:
        height = max(p[3] + p[5] for p in pieces)
        form = "gameover" if text == rows[0][0] else "banner"
        ink, halo = glyphs(text, form)
        if ink.shape[1] > 128 or ink.shape[0] > height:
            raise ValueError(f"{text!r} is {ink.shape[1]}x{ink.shape[0]}, canvas 128x{height}")
        cell = np.zeros((height, 128), dtype=np.int32)
        oy, ox = (height - ink.shape[0]) // 2, (128 - ink.shape[1]) // 2
        box = cell[oy:oy + ink.shape[0], ox:ox + ink.shape[1]]
        box[halo] = line
        ramp = fill[(np.arange(ink.shape[0]) * len(fill) // ink.shape[0]), None]
        box[ink] = np.broadcast_to(ramp, ink.shape)[ink]
        for u, v, w, h, cx, cy in pieces:
            px[v:v + h, u:u + w] = cell[cy:cy + h, cx:cx + w]
    return tim.with_pixels(t, data, px.reshape(-1).tolist())


def commonest(area, clut, test):
    """The index used most in area among those whose r + g + b (0-93) passes test: a lyric card's ink is white on near
    black, each at one index, and which index differs per card."""
    v, n = np.unique(area, return_counts=True)
    hits = [(int(c), int(i)) for i, c in zip(v, n) if test((clut[i] & 31) + ((clut[i] >> 5) & 31) + ((clut[i] >> 10) & 31))]
    return max(hits)[1]


def inpainted(px, mask, clut, skip):
    """px with masked pixels filled from their neighbours in colour, then matched back to the palette."""
    c = np.array(clut)
    rgb = np.stack([c & 31, (c >> 5) & 31, (c >> 10) & 31], axis=-1).astype(float)[px]
    todo = mask.copy()
    while todo.any():
        known = ~todo
        total, n = np.zeros_like(rgb), np.zeros(px.shape)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            k = np.roll(np.roll(known, dy, 0), dx, 1)
            total += np.roll(np.roll(rgb, dy, 0), dx, 1) * k[..., None]
            n += k
        ready = todo & (n > 0)
        if not ready.any():
            raise ValueError("no pixel to inpaint from")
        rgb[ready] = total[ready] / n[ready][..., None]
        todo &= ~ready
    pal = np.stack([c & 31, (c >> 5) & 31, (c >> 10) & 31], axis=1).astype(int)
    usable = np.array([i for i in range(len(clut)) if i not in skip and clut[i] & 0x7FFF])
    out = px.copy()
    ys, xs = np.nonzero(mask)
    out[ys, xs] = usable[np.abs(pal[usable][None] - rgb[ys, xs][:, None]).sum(axis=2).argmin(axis=1)]
    return out


LYRIC_PITCH, LYRIC_GAP = 14, 15  # summary line pitch; title to first summary line


LYRIC_GROW = {"03": (2, 2, 2, 8), "06": (4, 2, 2, 2)}  # strokes past the line rects: dashes under CARD03, a stroke left of CARD06


def lyric_area(card, rects):
    """(x, y, w, h) a lyric card clears: its line rects, plus a margin for the glyphs' edges."""
    x0, y0 = min(r[0] for r in rects), min(r[1] for r in rects)
    x1, y1 = max(r[0] + r[2] for r in rects), max(r[1] + r[3] for r in rects)
    left, top, right, bottom = LYRIC_GROW.get(card, (2, 2, 2, 2))
    return x0 - left, y0 - top, x1 - x0 + left + right, y1 - y0 + top + bottom


def lyric_card(data, card, rects, title, lines):
    """A lyric card with the Japanese lines painted out and the English title and summary lettered on their rows.
    rects = the card's rows of script/lyric_lines.tsv. White text with a dark halo, as the original."""
    t = tim.parse(data)
    px = tim_px(t, data)
    x0, y0 = min(r[0] for r in rects), min(r[1] for r in rects)
    x1, y1 = max(r[0] + r[2] for r in rects), max(r[1] + r[3] for r in rects)
    ax, ay, aw, ah = lyric_area(card, rects)
    area = px[ay:ay + ah, ax:ax + aw]
    white, dark = commonest(area, t.clut, lambda s: s >= 85), commonest(area, t.clut, lambda s: s <= 9)
    ink = np.isin(area, (white, dark))
    mask = ink.copy()  # one px wider: the glyphs' soft edges are other indices, and stayed as specks
    mask[1:] |= ink[:-1]
    mask[:-1] |= ink[1:]
    mask[:, 1:] |= ink[:, :-1]
    mask[:, :-1] |= ink[:, 1:]
    area[:] = inpainted(area, mask, t.clut, (white, dark))
    rows = [title] + lines
    if len(rows) > len(rects):
        raise ValueError(f"{len(rows)} lines for {len(rects)} rows")
    for n, text in enumerate(rows):  # an even pitch from the title: the Japanese rows have stanza gaps, a summary doesn't
        ink, halo = glyphs(text, "credit")
        gh, gw = ink.shape
        if x0 + gw > px.shape[1] - 4:
            raise ValueError(f"{text!r} is {gw} px from x {x0}")
        oy = y0 + (0 if n == 0 else LYRIC_GAP + (n - 1) * LYRIC_PITCH) + (LYRIC_PITCH - gh) // 2
        if oy + gh > y1:
            raise ValueError(f"{text!r} ends at y {oy + gh}, card text ends at {y1}")
        cell = px[oy:oy + gh, x0:x0 + gw]
        cell[halo] = dark
        cell[ink] = white
    return tim.with_pixels(t, data, px.reshape(-1).tolist())


def lyric_rects():
    out = {}
    for ln in (ROOT / "script" / "lyric_lines.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        card, _, *rect = ln.split("\t")
        out.setdefault(card, []).append(tuple(map(int, rect)))
    return out


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
