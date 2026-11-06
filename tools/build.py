"""build.py: make the playable disc in build/ from rom/. Only Track 01 is rewritten; the audio tracks are hard links.

usage: build.py [OUTDIR]
Every Form 1 file goes through disc.write_file, and every TIM through tim.pixels/with_pixels, so with no edits the
output must equal the dump: tests/test_build.py holds that as the identity test."""
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


def build(out=ROOT / "build"):
    """Returns the path of the new cue."""
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
    for e in d.files.values():
        if not d.is_xa(e):
            d.write_file(e.path, rebuild(d.read(e.path)))
    d.f.close()
    return out / CUE


if __name__ == "__main__":
    print(build(*sys.argv[1:2]))
