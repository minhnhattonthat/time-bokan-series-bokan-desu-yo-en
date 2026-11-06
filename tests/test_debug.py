"""The warp scene list covers what phase 8 must reach, and its script indexes agree with the game's tables."""
import importlib.util
import re
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("warp_all", ROOT / "tools" / "debug" / "warp_all.py")
warp_all = importlib.util.module_from_spec(spec)
spec.loader.exec_module(warp_all)
SRC = (ROOT / "tools" / "debug" / "scenes.lua").read_text(encoding="utf-8")
EXE = ROOT / "work" / "x" / "TARGET.EXE"


def test_scene_list_covers_every_screen_class():
    names = set(warp_all.scene_names())
    must = {"logo", "title", "menu", "options", "buttons", "sound", "extras", "viewer", "ending", "fin", "continue",
            "gameover0", "gameover1", "clear", "danger"}
    must |= {f"card_{c}" for c in "st1 st2 st3 st4 st5 sts stf".split()}
    must |= {f"movie{n:02d}" for n in range(16)}
    assert must <= names, must - names


def script(data, addr):
    return struct.unpack_from("<20i", data, addr - 0x80010000 + 0x800)


@pytest.mark.skipif(not EXE.exists(), reason="needs tools/disc.py x output in work/x")
def test_scene_indexes_match_story_script():
    data = EXE.read_bytes()
    tables = [script(data, 0x8005C050), script(data, 0x8005C0A8)]
    card_st = {"st1": 0, "st2": 1, "st3": 2, "st4": 3, "st5": 4, "sts": 5, "stf": 6}
    cards = re.search(r"local CARDS = \{(.*?)\n", SRC).group(1)
    found = re.findall(r"(\w+) = \{ (\d), (\d+) \}", cards)
    assert {f[0] for f in found} == set(card_st)
    for name, game, ind in found:
        assert tables[int(game)][int(ind)] == card_st[name], name
    movies = re.search(r"local MOVIES = \{(.*?)\n\s*\n?-- Movie 0|local MOVIES = \{(.*?)\}\n", SRC, re.S)
    found = re.findall(r"\[(\d+)\] = \{ (\d), (\d+) \}", movies.group(0))
    assert sorted(int(f[0]) for f in found) == list(range(1, 16))
    for n, game, ind in found:
        assert tables[int(game)][int(ind)] == 0x10 + int(n), n
