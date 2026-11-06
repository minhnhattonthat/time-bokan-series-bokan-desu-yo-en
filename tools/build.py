"""build.py: make the playable disc in build/ from rom/. Only Track 01 is rewritten; the audio tracks are hard links.

usage: build.py [OUTDIR] [--no-movies | --identity | --marker | --spike]
Default: the English disc, from script/en/ (--no-movies skips the FMV burn, which takes minutes). Every Form 1 file goes
through disc.write_file, and every TIM through tim.pixels/with_pixels, so with --identity the output must equal the dump:
tests/test_build.py holds that. --marker paints each text rect with its row number and burns a width test line with its
row id into every movie (default OUTDIR build/marker). --spike letters the rows of script/spike.tsv (build/spike)."""
import os
import shutil
import sys
from pathlib import Path

import check_rom
import disc
import tim

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom"
CUE = "Time Bokan Series - Bokan desu yo (Japan).cue"
TRACK1 = "Time Bokan Series - Bokan desu yo (Japan) (Track 01).bin"
ENGLISH = {}


def rebuild(data):
    t = tim.parse(data)
    return tim.with_pixels(t, data, tim.pixels(t, data)) if t else data


def english_edit(name, data):
    """The file's bytes with its English, or data when the file holds none."""
    import credits
    import gfx
    import tl_check
    if name == "S10OVER":
        return credits.edit_overlay(data)
    if name in credits.KEEP:
        return credits.edit_tim(name, data)
    if name == "DATA/GO_S0":
        data = gfx.go_banner(data)
    rows = ENGLISH.get(name)
    if rows:
        data = gfx.typeset(data, rows)
    if name.startswith("OPTI/CARD"):
        card = name[-2:]
        row = next(r for r in tl_check.table(tl_check.EN / "lyric_cards.tsv") if r["card"] == card)
        data = gfx.lyric_card(data, gfx.lyric_rects()[card], row["title"], tl_check.lyric_lines(row["gist"]))
    return data


def english_subs(movie):
    import tl_check
    return tl_check.subs(movie)


def build(out=None, marker=False, spike=False, identity=False, movies=True):
    """Returns the path of the new cue. identity: no edits. movies=False skips the FMV burn, which takes minutes."""
    global ENGLISH
    out = out or ROOT / ("build/marker" if marker else "build/spike" if spike else "build")
    check_rom.check()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for p in ROM.iterdir():
        dst = out / p.name
        if p.name in (CUE, TRACK1):
            shutil.copyfile(p, dst)
        elif not dst.exists():
            try:
                os.link(p, dst)
            except OSError:  # out/ on another volume
                shutil.copyfile(p, dst)
    d = disc.Disc(str(out / TRACK1), write=True)
    rects = {}
    english = not (marker or spike or identity)
    if marker or spike:
        import gfx
        rects = gfx.marker_rects() if marker else gfx.spike_rows()
    if english:
        import gfx
        ENGLISH = gfx.english_rows()
        left = set(ENGLISH)
    for e in d.files.values():
        if not d.is_xa(e):
            data = rebuild(d.read(e.path))
            name = e.path.strip("/").removesuffix(".BIN")
            if name in rects:
                data = (gfx.marked if marker else gfx.typeset)(data, rects.pop(name))
            if spike and name == "S10OVER":
                import cells
                data = cells.with_edits(data, ROOT / "script" / "spike_cells.tsv")
            if english:
                data = english_edit(name, data)
                left.discard(name)
            d.write_file(e.path, data)
    d.f.close()
    assert not rects, f"no file for marker rows: {sorted(rects)}"
    assert not english or not left, f"no file for English rows: {sorted(left)}"
    if marker or (english and movies):
        import fmv_burn
        for movie, stats in fmv_burn.burn_all(str(out / TRACK1), fmv_burn.marker_subs if marker else english_subs).items():
            print(movie, stats)
    return out / CUE


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    print(build(args[0] if args else None, "--marker" in sys.argv, "--spike" in sys.argv, "--identity" in sys.argv,
                "--no-movies" not in sys.argv))
