"""Phase 6 gate over script/en/: ids complete, plain ASCII, within the measured widths, glossary spellings.

usage: tl_check.py        prints errors and warnings, exit 1 on any error. tests/test_translation.py runs it.
Library: subs(movie) gives the timed subtitles the build burns; lyric_lines(gist) wraps a lyric card."""
import csv
import re
import sys
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import fmv_burn
import gfx
import gfx_script

EN = ROOT / "script" / "en"
SKIP_FORMS = {"keep", "scribble", "credit"}
ROLE_W, ROW_W = 112, 304  # cells.md: role at dx -120, name at dx 0, anchored at screen x 160; screen keeps 8 px each side
CREDIT_ROOM = 12700  # END_4-6 packed at 14 px rows (11,160 px at 16 px rows in cells.md); glyphs are at most 14 tall
LYRIC_W = 270
MIN_SHOW = 1.2  # s: a short row stays up this long, unless the next row starts first
SONG_SHOW = 5.0
MAX_CPS, WARN_CPS = 30, 22


def table(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE, restval=""))


def budgets():
    """{id: (w, h)} the smallest sampled box; rect when nothing was measured."""
    out = {}
    for b in table(ROOT / "script" / "budgets.tsv"):
        boxes = [list(map(int, u.split(","))) for u in b["uv"].split(";")] if b["uv"] else []
        if not boxes:
            boxes = [list(map(int, b["rect"].split(",")))]
        out[b["id"]] = (min(u[2] for u in boxes), min(u[3] for u in boxes))
    out["go.game"] = (128, 64)  # two 64 px quads drawn side by side, lettered as one strip (cells.md)
    return out


def fmv_rows(movie):
    return fmv_burn.read_rows(movie)


def span(n):
    a, _, b = n.partition("-")
    return list(range(int(a), int(b or a) + 1))


def en_rows(movie, rows=None):
    return [r for r in (rows or table(EN / "fmv.tsv")) if r["movie"] == movie]


def subs(movie, rows=None):
    """[(start, end, text)] for one movie: rows without English are skipped, and short ones stretch to MIN_SHOW."""
    src, out = fmv_rows(movie), []
    for r in en_rows(movie, rows):
        ns = span(r["n"])
        if not r["en"]:
            continue
        first, last = src[ns[0] - 1], src[ns[-1] - 1]
        start, end = first[0], last[1]
        if first[2] == "song":
            end = start + SONG_SHOW
        later = [s[0] for s in src[ns[-1]:] if s[0] > start]
        limit = min(later) if later else end + MIN_SHOW
        end = max(end, min(start + MIN_SHOW, limit))
        out.append((start, end, r["en"]))
    return out


def lyric_lines(text, width=LYRIC_W):
    font = ImageFont.truetype(str(ROOT / "fonts" / gfx.CLASSES["credit"][0]), gfx.CLASSES["credit"][1])
    return fmv_burn.wrap(text, font, width)


def glossary():
    """(jp terms, en, avoid) of every glossary table row."""
    out = []
    for ln in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if not ln.startswith("|") or len(c) != 5 or c[0] in ("JP", "---"):
            continue
        out.append(([t.strip() for t in c[0].split("/")], c[1], [t.strip() for t in c[4].split(",") if t.strip()]))
    return out


def check_text(where, text, terms, errors):
    if not text.isascii() or "\t" in text or "\\u" in text:
        errors.append(f"{where}: not plain ASCII: {text!r}")
    for _, _, avoid in terms:
        for a in avoid:
            if re.search(rf"\b{re.escape(a)}\b", text):
                errors.append(f"{where}: avoided spelling {a!r}: {text!r}")


def check_term(where, jp, text, terms, errors):
    for jps, en, _ in terms:
        if any(j in jp for j in jps) and en.lower() not in text.lower():
            errors.append(f"{where}: {jp!r} needs {en!r}: {text!r}")


def check_graphics(terms, errors):
    rows = {r.id: r for r in gfx_script.rows()}
    want = {i for i, r in rows.items() if r.form not in SKIP_FORMS}
    en = table(EN / "graphics.tsv")
    ids = [r["id"] for r in en]
    if len(ids) != len(set(ids)) or set(ids) != want:
        errors.append(f"graphics ids: missing {sorted(want - set(ids))}, extra {sorted(set(ids) - want)}")
    sizes = budgets()
    for r in en:
        rid = r["id"]
        if rid not in rows:
            continue
        check_text(rid, r["en"], terms, errors)
        check_term(rid, rows[rid].jp, r["en"], terms, errors)
        ink = gfx.glyphs(r["en"], r["class"] or rows[rid].form)[0]
        w, h = sizes[rid]
        if ink.shape[1] > w or ink.shape[0] > h:
            errors.append(f"{rid}: {r['en']!r} is {ink.shape[1]}x{ink.shape[0]}, budget {w}x{h}")


def check_credits(terms, errors):
    src = table(ROOT / "script" / "credits.tsv")
    en = table(EN / "credits.tsv")
    if [r["line"] for r in en] != [r["line"] for r in src]:
        errors.append("credits: line numbers differ from script/credits.tsv")
    strips = set()
    for r, s in zip(en, src):
        where = f"credits {r['line']}"
        role, name = r["role"], r["name"]
        check_text(where, role + name, terms, errors)
        check_term(where, s["role_jp"] + s["name_jp"], role + " " + name, terms, errors)
        rw = max((gfx.row_width(p, "credit") for p in role.split("|") if p), default=0)
        nw = gfx.row_width(name, "credit") if name else 0
        if name and rw > ROLE_W:
            errors.append(f"{where}: role {role!r} is {rw} px, room {ROLE_W}")
        if rw + nw + 8 > ROW_W:  # a long name slides left into a short or empty role's column; parts can be re-anchored
            errors.append(f"{where}: {role!r} {name!r} is {rw + nw + 8} px, room {ROW_W}")
        strips.update(p for p in role.split("|") + [name] if p)
    return sum(gfx.row_width(t, "credit") + 2 for t in strips)


def check_fmv(terms, errors, warnings):
    en = table(EN / "fmv.tsv")
    font = ImageFont.truetype(str(fmv_burn.FONT), fmv_burn.SIZE)
    movies = sorted(p.stem for p in (ROOT / "script" / "fmv").glob("*.tsv"))
    for movie in movies:
        src = fmv_rows(movie)
        seen = []
        for r in en_rows(movie, en):
            where = f"{movie}.{r['n']}"
            ns = span(r["n"])
            seen += ns
            check_text(where, r["en"], terms, errors)
            if not r["en"]:
                if "dropped" not in r["note"]:
                    errors.append(f"{where}: no English and no reason")
                elif not any("?" in src[n - 1][4] + notes(movie, n) for n in ns):
                    errors.append(f"{where}: dropped, but the source row isn't marked uncertain")
                continue
            check_term(where, "".join(src[n - 1][4] for n in ns), r["en"], terms, errors)
            lines = fmv_burn.wrap(r["en"], font)
            if max(font.getlength(ln) for ln in lines) > fmv_burn.MAX_W or len(lines) > fmv_burn.MAX_LINES:
                errors.append(f"{where}: {len(lines)} lines or over {fmv_burn.MAX_W} px: {r['en']!r}")
            elif len(lines) > 2:
                warnings.append(f"{where}: {len(lines)} lines")
        need = [i for i, s in enumerate(src, 1) if s[2] != "song"]
        if sorted(n for n in seen if src[n - 1][2] != "song") != need:
            errors.append(f"{movie}: rows covered {sorted(seen)}, need {need}")
        timed = subs(movie, en)
        for (s, e, t) in timed:
            cps = len(t) / (e - s)
            if cps > MAX_CPS:
                errors.append(f"{movie}: {cps:.0f} chars/s: {t!r}")
            elif cps > WARN_CPS:
                warnings.append(f"{movie}: {cps:.0f} chars/s: {t!r}")


def notes(movie, n):
    ln = (ROOT / "script" / "fmv" / f"{movie}.tsv").read_text(encoding="utf-8").splitlines()[n]
    c = ln.split("\t")
    return c[5] if len(c) > 5 else ""


def check_lyrics(terms, errors):
    counts = {}
    for r in table(ROOT / "script" / "lyric_lines.tsv"):
        counts[r["card"]] = counts.get(r["card"], 0) + 1
    en = table(EN / "lyric_cards.tsv")
    if {r["card"] for r in en} != set(counts):
        errors.append("lyric cards: card set differs from script/lyric_lines.tsv")
    for r in en:
        where = f"lyric {r['card']}"
        check_text(where, r["title"] + r["gist"], terms, errors)
        lines = [r["title"]] + lyric_lines(r["gist"])
        if gfx.row_width(r["title"], "credit") > LYRIC_W:
            errors.append(f"{where}: title over {LYRIC_W} px")
        if len(lines) > counts[r["card"]]:
            errors.append(f"{where}: {len(lines)} lines, card has {counts[r['card']]}")


def run():
    errors, warnings = [], []
    terms = glossary()
    check_graphics(terms, errors)
    px = check_credits(terms, errors)
    check_fmv(terms, errors, warnings)
    check_lyrics(terms, errors)
    if px > CREDIT_ROOM:
        errors.append(f"credits: {px} px of strips, room {CREDIT_ROOM}")
    return errors, warnings, px


if __name__ == "__main__":
    errs, warns, width = run()
    for w in warns:
        print("warn:", w)
    for e in errs:
        print("ERROR:", e)
    print(f"{len(errs)} errors, {len(warns)} warnings; credit strips {width}/{CREDIT_ROOM} px")
    sys.exit(1 if errs else 0)
