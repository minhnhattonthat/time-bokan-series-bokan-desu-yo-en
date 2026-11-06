"""Burn subtitles into STR movies on a built disc, in place: only macroblocks under the text are repainted, each frame
keeps its sectors, and audio sectors stay untouched (see tools/mdec.py). A frame that no longer fits its sectors is
re-quantised whole, up to +4 steps: most subtitled frames in the final build (7,347 of 8,584).

Library: burn_all(track_path, text_of) where text_of(movie, n, row) gives a subtitle string or None."""
import concurrent.futures as cf
import os
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import disc
import mdec

FONT = ROOT / "fonts" / "Jersey10-Regular.ttf"
SIZE = 20          # 10 px design size, doubled: the cleanest size of this pixel font that reads on a TV
LINE = 16
MAX_W = 272        # picture is 288 wide, keep 8 px each side
MAX_LINES = 3      # at LINE px each, the most the marker build showed clear of the picture's top half
BOTTOM = 188       # last text row inside the 192-line picture
SECTORS_PER_SEC = 150
WORDS_MAX = 12544  # largest MDEC size in the original movies (MOVIE06), so the one player's buffer is known to hold it
MARKER = "The quick brown fox jumps over the lazy dog, again and again and again"


def wrap(text, font, width=MAX_W):
    """Greedy word wrap by pixel width."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur] if cur else lines


def text_masks(lines, w, h):
    """(ink, halo) boolean masks of the subtitle, drawn without antialiasing, centred, sitting on BOTTOM."""
    font = ImageFont.truetype(str(FONT), SIZE)
    ink, halo = Image.new("1", (w, h)), Image.new("1", (w, h))
    di, dh = ImageDraw.Draw(ink), ImageDraw.Draw(halo)
    di.fontmode = dh.fontmode = "1"
    top = BOTTOM - LINE * len(lines)
    for n, ln in enumerate(lines):
        x = (w - int(font.getlength(ln))) // 2
        y = top + n * LINE - 4  # the font's ascent space
        dh.text((x, y), ln, font=font, fill=1, stroke_width=1, stroke_fill=1)
        di.text((x, y), ln, font=font, fill=1)
    return np.array(ink), np.array(halo)


def burn_frame(p, ink, halo):
    """Paint on Picture p: white ink, black halo, grey chroma under both."""
    rows = np.flatnonzero(halo.any(axis=1))
    if not len(rows):
        return
    for r in range(rows[0] // 16, rows[-1] // 16 + 1):
        for c in range(p.cols):
            h = halo[r * 16:r * 16 + 16, c * 16:c * 16 + 16]
            if not h.any():
                continue
            i = ink[r * 16:r * 16 + 16, c * 16:c * 16 + 16]
            y, cb, cr = p.get_mb(c, r)
            y[h] = -112.0
            y[i] = 107.0
            mask = h.reshape(8, 2, 8, 2).any(axis=(1, 3))
            cb[mask] = 0.0
            cr[mask] = 0.0
            p.set_mb(c, r, y, cb, cr)


def burn_movie(track, entry, movie, subs):
    """New raw sectors {lba: bytes} for one movie. subs = [(start, end, text)]; times in seconds."""
    d = disc.Disc(track)
    n = -(-entry.size // 2048)
    raw = {i: d.raw(entry.lba + i) for i in range(n)}
    font = ImageFont.truetype(str(FONT), SIZE)
    frames = mdec.frames(raw.items())
    masks = {}
    out = {}
    stats = dict(frames=0, requant=0, max_q_step=0, frames_total=len(frames))
    for f in frames:
        t = f.sectors[0] / SECTORS_PER_SEC
        sub = next((s for s in subs if s[0] <= t < s[1]), None)
        if not sub:
            continue
        if sub[2] not in masks:
            lines = wrap(sub[2], font)
            assert len(lines) <= MAX_LINES, f"{movie}: subtitle over {MAX_LINES} lines: {sub[2]!r}"
            masks[sub[2]] = text_masks(lines, f.w, f.h)
        bs = mdec.frame_bytes(f, raw.__getitem__)
        p = mdec.Picture(bs, f.w, f.h)
        burn_frame(p, *masks[sub[2]])
        cap = f.chunks * mdec.CHUNK
        new = p.tobytes()
        q = p.q
        while len(new) > cap or struct.unpack_from("<H", new)[0] > WORDS_MAX:
            q += 1
            assert q <= mdec.MAX_Q, f"{movie} frame {f.no}: no qscale fits {cap} bytes, {WORDS_MAX} words"
            new = p.tobytes_at(q)
        stats["requant"] += q != p.q
        stats["max_q_step"] = max(stats["max_q_step"], q - p.q)
        for idx, i in enumerate(f.sectors):
            sec = bytearray(raw[i])
            struct.pack_into("<I", sec, 36, len(new))
            sec[44:52] = new[:8]
            sec[56:56 + mdec.CHUNK] = new[idx * mdec.CHUNK:(idx + 1) * mdec.CHUNK].ljust(mdec.CHUNK, b"\0")
            disc.form1_seal(sec)
            out[entry.lba + i] = bytes(sec)
        stats["frames"] += 1
    return movie, out, stats


def read_rows(movie):
    path = ROOT / "script" / "fmv" / f"{movie}.tsv"
    rows = []
    for ln in path.read_text(encoding="utf-8").splitlines()[1:]:
        c = ln.split("\t")
        rows.append((float(c[0]), float(c[1]), c[2], c[3], c[4]))
    return rows


def burn_all(track, subs_of, jobs=None):
    """Writes every movie's new sectors into track. subs_of(movie) -> [(start, end, text)]. Returns stats by movie."""
    d = disc.Disc(track)
    entries = {os.path.basename(p).split(".")[0]: e for p, e in d.files.items() if p.startswith("/STR/")}
    d.f.close()
    jobs_list = [(track, e, movie, subs_of(movie)) for movie, e in sorted(entries.items())]
    report = {}
    with cf.ProcessPoolExecutor(jobs or min(8, os.cpu_count())) as ex:
        results = list(ex.map(burn_movie, *zip(*jobs_list)))
    with open(track, "r+b") as f:
        for movie, out, stats in results:
            for lba, sec in out.items():
                f.seek(lba * disc.SECTOR)
                f.write(sec)
            report[movie] = stats
    return report


def marker_subs(movie):
    """Marker build: the row's id on every spoken or captioned row, then a line that fills the width."""
    return [(row[0], row[1], f"{movie[5:]}.{n} {MARKER}") for n, row in enumerate(read_rows(movie), 1)
            if row[2] in ("dlg", "caption", "form")]
