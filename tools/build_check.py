"""Phase 7 gate: compare a built Track 01 with the dump, so an edit can't land outside where it is meant to go.

usage: build_check.py [BUILD_DIR]     default build/; exit 1 on any finding
Fails on a changed sector outside the allowed files, a changed TIM header or CLUT, a TIM pixel changed outside its rows'
rects, or an S10OVER byte changed outside the credit parts and page script. The last goes through romdiff.check."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import credits
import disc
import gfx
import romdiff
import tim

TRACK1 = credits.TRACK1
GO_BOXES = [(160, 0, 64, 96), (160, 96, 64, 64), (0, 222, 64, 33)]
PARTS = (0x8015DD88 - credits.BASE, 0x8015EA34 - credits.BASE)   # credit groups
PAGES = (credits.SCRIPT - credits.BASE, 0x8015EF48 - credits.BASE)


def allowed_rects():
    """{TIM file: [rect, ...]}; credit TIMs are all cleared and relaid, so have no list."""
    out = {f: [r[0] for r in rows] for f, rows in gfx.english_rows().items()}
    out.setdefault("DATA/GO_S0", []).extend(GO_BOXES)
    for card, rects in gfx.lyric_rects().items():
        x0, y0 = min(r[0] for r in rects), min(r[1] for r in rects)
        y1 = max(r[1] + r[3] for r in rects)
        # to x 300: English may run past the Japanese, and CARD16's Japanese reaches 299. The white frame starts at 302.
        out[f"OPTI/CARD{card}"] = [(x0 - 1, y0 - 1, 301 - x0, y1 - y0 + 2)]
    return out


def check(build_dir):
    """(findings, one-line summary)."""
    a, b = disc.Disc(str(ROOT / "rom" / TRACK1)), disc.Disc(str(Path(build_dir) / TRACK1))
    errs = []
    rects = allowed_rects()
    allowed = set(rects) | set(credits.KEEP) | {"S10OVER"}
    x = np.memmap(str(ROOT / "rom" / TRACK1), dtype=np.uint8, mode="r")
    y = np.memmap(str(Path(build_dir) / TRACK1), dtype=np.uint8, mode="r")
    if len(x) != len(y):
        errs.append(f"track size {len(x)} became {len(y)}")
        return errs, ""
    n = len(x) // disc.SECTOR
    moved = np.flatnonzero((x[:n * disc.SECTOR].reshape(n, -1) != y[:n * disc.SECTOR].reshape(n, -1)).any(axis=1))
    owner = {}
    for path, e in a.files.items():
        for i in range(-(-e.size // 2048)):
            owner[e.lba + i] = path
    touched = {}
    for lba in moved.tolist():
        path = owner.get(lba)
        name = path.strip("/").removesuffix(".BIN") if path else None
        if path is None or not (name in allowed or path.startswith("/STR/")):
            errs.append(f"LBA {lba} changed, in {path or 'no file'}")
        else:
            touched[path] = touched.get(path, 0) + 1
    files = 0
    for path in touched:
        name = path.strip("/").removesuffix(".BIN")
        if path.startswith("/STR/"):
            continue
        old, new = a.read(path), b.read(path)
        files += 1
        if name == "S10OVER":
            ok = set(range(*PARTS)) | set(range(*PAGES))
            errs += [f"S10OVER: {e}" for e in romdiff.check(old, new, ok, [])[0]]
            continue
        t = tim.parse(old)
        if old[:t.px_off] != new[:t.px_off]:
            errs.append(f"{path}: TIM header or CLUT changed")
        if name in credits.KEEP:
            continue
        p, q = gfx.tim_px(t, old), gfx.tim_px(t, new)
        mask = p != q
        for rx, ry, rw, rh in rects[name]:
            mask[ry:ry + rh, rx:rx + rw] = False
        if mask.any():
            ys, xs = np.nonzero(mask)
            errs.append(f"{path}: {len(ys)} pixels outside rects, first at {xs[0]},{ys[0]}")
    return errs, f"{len(moved)} sectors changed in {files} files and {sum(p.startswith('/STR/') for p in touched)} movies"


if __name__ == "__main__":
    findings, summary = check(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build")
    for f in findings:
        print(f)
    print(f"{len(findings)} findings; {summary}")
    sys.exit(1 if findings else 0)
