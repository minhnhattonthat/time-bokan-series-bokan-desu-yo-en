"""Phase 6: the English in script/en/ passes its gate, and the gate catches what it claims to."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tl_check


def test_script_en_is_clean():
    errors, _, _ = tl_check.run()
    assert not errors, "\n".join(errors)


def test_avoided_spelling_and_non_ascii_are_caught():
    terms = [(["トンズラー"], "Tonzra", ["Tonzura"])]
    errors = []
    tl_check.check_text("x", "Tonzura car", terms, errors)
    tl_check.check_text("y", "café", terms, errors)
    tl_check.check_term("z", "トンズラー", "Someone else", terms, errors)
    assert len(errors) == 3


def test_subs_stretch_short_rows_but_never_past_the_next():
    rows = [dict(movie="MOVIE03", n="1-3", en="No way! Really? So cute!", note=""), dict(movie="MOVIE03", n="7", en="Ara", note="")]
    subs = tl_check.subs("MOVIE03", rows)
    assert subs[0] == (0.68, 3.02, "No way! Really? So cute!")
    assert subs[1][1] - subs[1][0] >= tl_check.MIN_SHOW
