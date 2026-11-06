"""Phase 5 tools: marker paints stay in their rects, and the cell and packet readers decode what the game writes."""
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cells
import credits
import fmv_burn
import gfx
import gfx_script
import prims
import tim
from test_recon import make_tim


def test_marker_changes_only_the_rect():
    data = make_tim()
    t = tim.parse(data)
    new = gfx.marked(data, [((1, 0, 4, 1), "1")])
    a, b = tim.pixels(t, data), tim.pixels(t, new)
    assert new[:t.px_off] == data[:t.px_off]
    assert a[1:5] != b[1:5] or a[1:5] == [gfx.ink_indices(t)[1]] * 4
    assert a[:1] == b[:1] and a[5:] == b[5:]


def test_typeset_stays_in_rect_and_refuses_overflow():
    clut = struct.pack("<I4H", 12 + 32, 0, 480, 16, 1) + struct.pack("<16H", *range(16))
    pixels = struct.pack("<I4H", 12 + 16 * 16 * 2, 320, 0, 16, 16) + bytes(range(256)) * 2
    data = struct.pack("<II", 0x10, 8) + clut + pixels
    t = tim.parse(data)
    rect = (2, 2, 40, 12)
    new = gfx.typeset(data, [(rect, "Ok", "sprite", "c")])
    a, b = [np.array(tim.pixels(t, d)).reshape(16, 64) for d in (data, new)]
    inside = np.zeros((16, 64), bool)
    inside[2:14, 2:42] = True
    assert (a[~inside] == b[~inside]).all() and (a != b).any()
    with pytest.raises(ValueError):
        gfx.typeset(data, [((2, 2, gfx.row_width("Ok", "sprite") - 1, 12), "Ok", "sprite", "c")])
    gfx.typeset(data, [((2, 2, gfx.row_width("Ok", "sprite"), 12), "Ok", "sprite", "c")])  # exactly full fits


def test_inks_come_from_inside_the_strokes():
    clut = [0] * 16
    clut[1], clut[2] = 0x001F, 0x7FFF  # red, white
    thick = np.zeros((9, 9), int)
    thick[1:8, 1:8] = 2  # white outline ...
    thick[2:7, 2:7] = 1  # ... round a red core
    bg, fill, line = gfx.sampled_inks(thick, clut)
    assert (bg == 0).all() and (fill == 1).all() and line == 2
    thin = np.zeros((5, 9), int)
    thin[1, 2:7], thin[2, 2:7] = 1, 2  # strokes too thin for a core: the brighter ink fills
    bg, fill, line = gfx.sampled_inks(thin, clut)
    assert (bg == 0).all() and (fill == 2).all() and line == 1


def test_inks_follow_a_row_gradient():
    clut = list(range(16))
    px = np.zeros((6, 12), int)
    px[:] = np.arange(1, 7)[:, None]  # bar art: one index per row
    px[1:5, 3:9] = np.array([8, 9, 10, 11])[:, None]  # letter: its own gradient
    bg, fill, _ = gfx.sampled_inks(px, clut)
    assert bg.tolist() == list(range(1, 7))
    assert fill[2] == 9 and fill[3] == 10


def test_margin_beats_ink_at_the_rect_ends():
    px = np.full((4, 8), 3)
    px[1] = 5  # a stroke that runs the whole width of a tight rect
    bg, _, _ = gfx.sampled_inks(px, list(range(16)), margin=np.full((4, 6), 3))
    assert (bg == 3).all()


def test_see_through_rect_ignores_neighbours_in_the_margin():
    clut = [0] + [0x7FFF] * 15
    px = np.zeros((4, 8), int)
    px[1:3, 2:6] = 5
    margin = np.array([[1, 2, 3, 4, 5, 6]] * 4)  # a packed strip: other labels' ink beside the rect
    bg, fill, _ = gfx.sampled_inks(px, clut, margin=margin)
    assert (bg == 0).all() and (fill == 5).all()


def test_spike_lines_fit_their_rects():
    for f, rows in gfx.spike_rows().items():
        for (_, _, w, h), text, form, _ in rows:
            ink, _ = gfx.glyphs(text, form)
            assert ink.shape[1] <= w and ink.shape[0] <= h, (f, text, ink.shape, w, h)


def test_every_row_rect_is_inside_its_tim():
    for f, rects in gfx.marker_rects().items():
        data = (ROOT / "work" / "x" / (f + ".BIN")).read_bytes() if (ROOT / "work" / "x").exists() else None
        if data:
            gfx.marked(data, rects)


def test_cell_group_parser_and_write_back():
    part = struct.pack("<BBbbHHHH", 8, 0, -120, -8, 64, 16, 4096, 4096)
    blob = struct.pack("<I", 2) + part * 2 + b"\xff" * 16
    gs = cells.groups(blob, 0)
    assert len(gs) == 1 and len(gs[0].parts) == 2 and gs[0].parts[0].dx == -120
    p = gs[0].parts[1]._replace(u=16)
    assert cells.groups(cells.with_part(blob, p), 0)[0].parts[1].u == 16


def test_sprite_packet_decodes():
    ram = bytearray(prims.RAM)
    words = (0x07000000, 0xE100001B, 0, 0, 0x64808080, (8 << 16) | 16, (0x7E83 << 16) | (32 << 8) | 64, (16 << 16) | 80)
    struct.pack_into("<8I", ram, 0x1000, *words)
    p = next(q for q in prims.scan(bytes(ram)) if q.addr == 0x1000)
    assert (p.x, p.y, p.sw, p.sh, p.u, p.v, p.bpp, p.clut) == (16, 8, 80, 16, 64, 32, 4, 0x7E83)
    assert (p.vx, p.vy) == (704 + 16, 256 + 32)


def test_credit_table_covers_every_group():
    if not (ROOT / "work" / "x" / "S10OVER.BIN").exists():
        return
    rows = (ROOT / "script" / "credits.tsv").read_text(encoding="utf-8").splitlines()[1:]
    assert len(rows) == len(credits.lines())
    assert [r.split("\t")[0] for r in rows] == [str(i) for i in range(1, len(rows) + 1)]


def test_budgets_cover_rows():
    rows = (ROOT / "script" / "budgets.tsv").read_text(encoding="utf-8").splitlines()[1:]
    want = {r.id for r in gfx_script.rows() if r.form != "keep"}
    assert {ln.split("\t")[0] for ln in rows} == want


def test_subtitle_wraps_to_width():
    from PIL import ImageFont
    font = ImageFont.truetype(str(fmv_burn.FONT), fmv_burn.SIZE)
    lines = fmv_burn.wrap(fmv_burn.MARKER, font)
    assert len(lines) >= 2 and all(font.getlength(ln) <= fmv_burn.MAX_W for ln in lines)
    ink, halo = fmv_burn.text_masks(lines[:2], 288, 192)
    assert ink.any() and (halo | ink).sum() == halo.sum()  # the halo covers the ink
