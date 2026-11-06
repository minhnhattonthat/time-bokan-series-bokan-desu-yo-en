"""build.py: make the playable disc in build/ from rom/. Only Track 01 is rewritten; the audio tracks are hard links.

usage: build.py [OUTDIR] [--marker | --spike]
Every Form 1 file goes through disc.write_file, and every TIM through tim.pixels/with_pixels, so with no edits the
output must equal the dump: tests/test_build.py holds that as the identity test. --marker paints each text rect with its
row number and burns a width test line with its row id into every movie (default OUTDIR build/marker). --spike letters
the rows of script/spike.tsv in English (default OUTDIR build/spike)."""
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


def rebuild(data):
    t = tim.parse(data)
    return tim.with_pixels(t, data, tim.pixels(t, data)) if t else data


def build(out=None, marker=False, spike=False):
    """Returns the path of the new cue."""
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
    if marker or spike:
        import gfx
        rects = gfx.marker_rects() if marker else gfx.spike_rows()
    for e in d.files.values():
        if not d.is_xa(e):
            data = rebuild(d.read(e.path))
            name = e.path.strip("/").removesuffix(".BIN")
            if name in rects:
                data = (gfx.marked if marker else gfx.typeset)(data, rects.pop(name))
            if spike and name == "S10OVER":
                import cells
                data = cells.with_edits(data, ROOT / "script" / "spike_cells.tsv")
            d.write_file(e.path, data)
    d.f.close()
    assert not rects, f"no file for marker rows: {sorted(rects)}"
    if marker:
        import fmv_burn
        for movie, stats in fmv_burn.burn_all(str(out / TRACK1), fmv_burn.marker_text).items():
            print(movie, stats)
    return out / CUE


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a not in ("--marker", "--spike")]
    print(build(args[0] if args else None, "--marker" in sys.argv, "--spike" in sys.argv))
