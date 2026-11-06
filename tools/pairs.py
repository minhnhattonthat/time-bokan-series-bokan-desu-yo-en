"""Review files from script/en/: one per chapter in story order, `>> id | speaker | JP` then the English.

usage: pairs.py [OUT_DIR]   default work/qa/story/chapters; the same files feed the phase 6 review and qa_gate.py.
Story order is the script tables in docs/re/state.md. Lyric cards list the title and summary only (D8, D10)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx_script
import tl_check

CARDS = {"ST1": "card.st1", "ST2": "card.st2", "ST3": "card.st3", "ST4": "card.st4", "ST5": "card.st5", "STF": "card.stf", "STS": "card.sts"}
NORMAL = "MOVIE00 MOVIE01 ST1 MOVIE02 ST2 MOVIE03 ST3 MOVIE04 ST4 MOVIE05 ST5 MOVIE06 MOVIE07".split()
SPECIAL = "MOVIE08 ST1 MOVIE09 ST2 MOVIE10 STS MOVIE11 ST3 MOVIE12 ST4 MOVIE05 ST5 MOVIE13 STF MOVIE14 MOVIE07 MOVIE15".split()


def fmv_lines(movie, en_rows):
    src = tl_check.fmv_rows(movie)
    out = [f"## {movie}"]
    for r in tl_check.en_rows(movie, en_rows):
        ns = tl_check.span(r["n"])
        jp = " / ".join(src[n - 1][4] for n in ns)
        out += [f">> {movie}.{r['n']} | {src[ns[0] - 1][3]} | {jp}", r["en"] or f"({r['note']})", ""]
    return out


def route(steps, gfx, en_rows):
    out = []
    for s in steps:
        if s in CARDS:
            g = gfx[CARDS[s]]
            out += [f"## {s}", f">> {g[0].id} | card | {g[0].jp}", g[1].replace("|", " / "), ""]
        else:
            out += fmv_lines(s, en_rows)
    return out


def main(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = {r.id: r for r in gfx_script.rows()}
    gfx = {r["id"]: (rows[r["id"]], r["en"]) for r in tl_check.table(tl_check.EN / "graphics.tsv")}
    en_rows = tl_check.table(tl_check.EN / "fmv.tsv")
    files = {"normal": route(NORMAL, gfx, en_rows), "special": route(SPECIAL, gfx, en_rows)}
    files["labels"] = [ln for g, en in gfx.values() if g.form != "card" for ln in (f">> {g.id} | {g.form} | {g.jp}", en.replace("|", " / "), "")]
    src = tl_check.table(ROOT / "script" / "credits.tsv")
    files["credits"] = [ln for s, r in zip(src, tl_check.table(tl_check.EN / "credits.tsv"))
                        for ln in (f">> {s['line']} | | {s['role_jp']} | {s['name_jp']}", f"{r['role'].replace('|', ' / ')} | {r['name']}", "")]
    files["lyric_cards"] = [ln for r in tl_check.table(tl_check.EN / "lyric_cards.tsv") for ln in (f">> card {r['card']} | {r['title']}", r["gist"], "")]
    for name, lines in files.items():
        (out_dir / f"{name}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(len(files), "chapters in", out_dir)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "work" / "qa" / "story" / "chapters")
