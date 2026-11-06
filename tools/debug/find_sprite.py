"""Find a TIM region in emulator shots, to learn which frame of a stage tour shows a given sprite.

    python -X utf8 tools/debug/find_sprite.py work/x/STAGE3/DATA/ST3_S5D.BIN 160,18,82,20 work/qa/warp/tour_st3 [--clut N]

Compares opaque non-black template pixels by colour and prints the best position per shot, best shots first. A score
near 1.0 means the sprite is on screen unscaled. Sprites drawn with another CLUT need --clut.
"""
import argparse
import glob
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import tim  # noqa: E402


def template(path, rect, clut):
    data = open(path, "rb").read()
    img = tim.to_image(tim.parse(data), data, clut).crop((rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]))
    a = np.asarray(img.convert("RGBA"), dtype=np.int16)
    mask = (a[..., 3] > 0) & (a[..., :3].sum(axis=2) > 60)
    ys, xs = np.nonzero(mask)
    return ys, xs, a[ys, xs, :3], a.shape[:2]


def best(shot, ys, xs, cols, size, tol=24):
    a = np.asarray(Image.open(shot).convert("RGB"), dtype=np.int16)
    h, w = size
    top = (0.0, 0, 0)
    if a.shape[0] < h or a.shape[1] < w:
        return top
    # coarse: a sample of pixels, then full score on the few best positions
    step = max(1, len(ys) // 40)
    sy, sx, sc = ys[::step], xs[::step], cols[::step]
    hits = np.zeros((a.shape[0] - h + 1, a.shape[1] - w + 1), dtype=np.int32)
    for y, x, c in zip(sy, sx, sc):
        m = (np.abs(a[y:y + hits.shape[0], x:x + hits.shape[1]] - c).sum(axis=2) < tol)
        hits += m
    for i in np.argsort(hits, axis=None)[-5:]:
        oy, ox = np.unravel_index(i, hits.shape)
        s = (np.abs(a[oy + ys, ox + xs] - cols).sum(axis=1) < tol).mean()
        if s > top[0]:
            top = (float(s), int(ox), int(oy))
    return top


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tim")
    ap.add_argument("rect")
    ap.add_argument("dir")
    ap.add_argument("--clut", type=int, default=0)
    ap.add_argument("--top", type=int, default=6)
    a = ap.parse_args()
    rect = tuple(int(v) for v in a.rect.split(","))
    t = template(a.tim, rect, a.clut)
    if not len(t[0]):
        sys.exit(f"CLUT {a.clut} leaves no visible pixels in {a.rect}")
    out = []
    for p in sorted(glob.glob(os.path.join(a.dir, "t*.png"))):
        out.append((*best(p, *t), os.path.basename(p)))
    out.sort(reverse=True)
    for s, x, y, name in out[:a.top]:
        print(f"{s:.2f} {name} at {x},{y}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
