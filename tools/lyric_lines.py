"""Find each text line's rectangle on the lyric cards (OPTI/CARD00-16): white font pixels touching the black outline.

usage: lyric_lines.py X_DIR OUT.tsv
Writes card, n, x, y, w, h, one row per line in reading order. Card 13 has two columns, see REGIONS."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import tim

LINE = 13  # the font's line pitch; a run taller than 1.5 lines is lines whose outlines touch
REGIONS = {13: [(0, 304, 3, 87), (0, 150, 87, 127), (150, 304, 90, 205)]}  # x0, x1, y0, y1: long lines, then two columns


def inked(px, x, y):
    r, g, b = px[x, y]
    return min(r, g, b) >= 230 and any(sum(px[x + dx, y + dy]) < 60 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def lines(data, card):
    img = tim.to_image(tim.parse(data), data).convert("RGB")
    px = img.load()
    w, h = img.size
    out = []
    for x0, x1, y0, y1 in REGIONS.get(card, [(0, w, 3, h - 3)]):
        # 3 px in from the card's edge: its white frame also touches black
        rows = {y: [x for x in range(max(x0, 3), min(x1, w - 3)) if inked(px, x, y)] for y in range(y0, y1)}
        y = y0
        while y < y1:
            if len(rows[y]) < 2:
                y += 1
                continue
            top = y
            while y < y1 and len(rows[y]) >= 2:
                y += 1
            n = max(1, round((y - top) / LINE))
            for i in range(n):
                a = top + (y - top) * i // n
                b = top + (y - top) * (i + 1) // n
                xs = [x for r in range(a, b) for x in rows[r]]
                if b - a >= 6:  # a shorter run is art catching the test, never a glyph
                    out.append((min(xs), a, max(xs) + 1 - min(xs), b - a))
    return out


def main():
    x_dir, out = sys.argv[1:3]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("card\tn\tx\ty\tw\th\n")
        for c in range(17):
            data = open(os.path.join(x_dir, "OPTI", f"CARD{c:02d}.BIN"), "rb").read()
            for n, (x, y, w, h) in enumerate(lines(data, c)):
                f.write(f"{c:02d}\t{n}\t{x}\t{y}\t{w}\t{h}\n")


if __name__ == "__main__":
    main()
