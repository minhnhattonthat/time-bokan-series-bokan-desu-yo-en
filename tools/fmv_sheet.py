"""Contact sheets of movie frames decoded from a disc image, on the clock the subtitle burn uses (sector / 150).

usage: fmv_sheet.py BIN MOVIE OUT.png --from S --to S --step S    frames in a time range
       fmv_sheet.py BIN MOVIE OUT_PREFIX --subs                   the middle of every subtitle, paged 24 frames a sheet
Each frame is labelled with its time and, with --subs, its subtitle's number. Needs no emulator, so it shows every line."""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import disc
import fmv_burn
import mdec
import tl_check

PER_SHEET = 24
COLS = 4


def movie_frames(d, movie):
    e = next(e for p, e in d.files.items() if p.startswith("/STR/") and movie in p)
    n = -(-e.size // 2048)
    raw = {i: d.raw(e.lba + i) for i in range(n)}
    return raw, mdec.frames(raw.items())


def decode(raw, frames, t):
    """(frame's own time, RGB array) of the last frame starting at or before t."""
    f = next((f for f in reversed(frames) if f.sectors[0] / fmv_burn.SECTORS_PER_SEC <= t), frames[0])
    return f.sectors[0] / fmv_burn.SECTORS_PER_SEC, mdec.Picture(mdec.frame_bytes(f, raw.__getitem__), f.w, f.h).rgb()


def sheet(tiles, path):
    w, h = tiles[0][1].shape[1], tiles[0][1].shape[0]
    rows = -(-len(tiles) // COLS)
    out = Image.new("RGB", (COLS * (w + 2), rows * (h + 14)), (30, 30, 30))
    draw = ImageDraw.Draw(out)
    for i, (label, px) in enumerate(tiles):
        x, y = (i % COLS) * (w + 2), (i // COLS) * (h + 14)
        draw.text((x + 2, y + 1), label, fill=(255, 255, 0))
        out.paste(Image.fromarray(px), (x, y + 14))
    out.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin")
    ap.add_argument("movie")
    ap.add_argument("out")
    ap.add_argument("--from", dest="start", type=float)
    ap.add_argument("--to", type=float)
    ap.add_argument("--step", type=float, default=0.5)
    ap.add_argument("--subs", action="store_true")
    a = ap.parse_args()
    d = disc.Disc(a.bin)
    raw, frames = movie_frames(d, a.movie)
    if a.subs:
        subs = tl_check.subs(a.movie)
        for page in range(0, len(subs), PER_SHEET):
            tiles = []
            for n, (s, e, _) in enumerate(subs[page:page + PER_SHEET], page + 1):
                t, px = decode(raw, frames, (s + e) / 2)
                tiles.append((f"{a.movie[5:]} #{n} {t:.2f}", px))
            sheet(tiles, f"{a.out}_{page // PER_SHEET:02d}.png")
    else:
        tiles, t = [], a.start
        while t <= a.to:
            ft, px = decode(raw, frames, t)
            tiles.append((f"{ft:.2f}", px))
            t += a.step
        sheet(tiles, a.out)


if __name__ == "__main__":
    main()
