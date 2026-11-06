"""Phase 4: every TIM roundtrips and is accounted for, and the script tables point at real pixels."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import disc
import gfx_script
import lyric_lines
import tim

BIN = build.ROM / build.TRACK1
needs_rom = pytest.mark.skipif(not BIN.exists(), reason="needs the dump in rom/")
LYRICS = ROOT / "work" / "script" / "lyrics_jp.tsv"  # local only: see docs/decisions.md D8


@pytest.fixture(scope="module")
def tims():
    d = disc.Disc(str(BIN))
    out = {}
    for path, e in d.files.items():
        if path.startswith(("/STR/", "/DA/", "/SE/")):
            continue
        data = d.read(path)
        if tim.parse(data):
            out[path.strip("/").removesuffix(".BIN")] = data
    return out


def test_gfx_rows_are_unique_and_complete():
    rows = gfx_script.rows()
    ids = [r.id for r in rows]
    assert len(ids) == len(set(ids))
    assert all(r.jp and r.w > 0 and r.h > 0 for r in rows)


@needs_rom
def test_every_tim_roundtrips(tims):
    assert len(tims) == 249
    for name, data in tims.items():
        t = tim.parse(data)
        assert tim.with_pixels(t, data, tim.pixels(t, data)) == data, name


@needs_rom
def test_every_tim_is_accounted_for_once(tims):
    no_text = {ln for ln in (ROOT / "script" / "no_text.txt").read_text(encoding="utf-8").splitlines() if not ln.startswith("#")}
    text = {r.file for r in gfx_script.rows()}
    assert not no_text & text
    assert no_text | text == set(tims)


@needs_rom
def test_gfx_rects_hold_pixels(tims):
    for r in gfx_script.rows():
        t = tim.parse(tims[r.file])
        img = tim.to_image(t, tims[r.file])
        assert r.x + r.w <= img.width and r.y + r.h <= img.height, r.id
        assert img.crop((r.x, r.y, r.x + r.w, r.y + r.h)).getbbox(), f"{r.id} is blank"


@needs_rom
def test_lyric_rects_stay_current(tims):
    want = [ln.split("\t") for ln in (ROOT / "script" / "lyric_lines.tsv").read_text(encoding="utf-8").splitlines()[1:]]
    got = [[f"{c:02d}", str(n), *map(str, rect)]
           for c in range(17) for n, rect in enumerate(lyric_lines.lines(tims[f"OPTI/CARD{c:02d}"], c))]
    assert got == want


@pytest.mark.skipif(not LYRICS.exists(), reason="the lyric transcript is local only")
def test_every_lyric_line_has_a_rect():
    def count(lines):
        out = {}
        for ln in lines:
            c = ln.split("\t")[0]
            out[c] = out.get(c, 0) + 1
        return out
    jp = count(LYRICS.read_text(encoding="utf-8").splitlines())
    rects = count((ROOT / "script" / "lyric_lines.tsv").read_text(encoding="utf-8").splitlines()[1:])
    assert jp == rects


def test_fmv_scripts_cover_all_16_movies_in_time_order():
    files = sorted((ROOT / "script" / "fmv").glob("MOVIE*.tsv"))
    assert [f.stem for f in files] == [f"MOVIE{n:02d}" for n in range(16)]
    for f in files:
        last = 0.0
        for ln in f.read_text(encoding="utf-8").splitlines()[1:]:
            start, end, form, speaker, jp, *_ = ln.split("\t")
            assert form in ("dlg", "song", "caption"), ln
            assert last <= float(start) < float(end), ln
            if form != "song":  # lyrics stay out of git, D8
                assert jp and not re.search(r"[A-Za-z]{4}", jp), ln
            last = float(start)
