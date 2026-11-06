"""Run scenes of tools/debug/scenes.lua from cold boot, each in work/qa/warp/<scene>; exit 1 if any fails.

    python -X utf8 tools/debug/warp_all.py [--rom CUE] [--jobs 3] [--out DIR] [--god] [--states] [scene ...]

--states also saves work/states/<scene>.sstate. A shot is judged by a flat-colour test on final.png (emu.py --smoke);
the state checks inside each scene fail the run on their own (exit 2 from emu.py).
"""
import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from skill import SKILL  # noqa: E402

DEFAULT_ROM = os.path.join(ROOT, "rom", "Time Bokan Series - Bokan desu yo (Japan).cue")
SCENES = os.path.join(ROOT, "tools", "debug", "scenes.lua")
WARP = os.path.join(ROOT, "tools", "debug", "warp.lua")
LONG = {"ending": 60000, "sprite_itadaki": 40000}
NO_SMOKE = {"ending"}  # the roll ends on a black screen by design; its state checks prove the scene


def scene_names():
    """Names of the scene list, expanded from scenes.lua's literal tables (kept in step by test_debug)."""
    src = open(SCENES, encoding="utf-8").read()
    names = re.findall(r"^S\.(\w+) = ", src, re.M)
    cards = re.search(r"local CARDS = \{(.*?)\n", src).group(1)
    for c in re.findall(r"(\w+) = \{", cards):
        names += [f"card_{c}", f"play_{c}", f"tour_{c}"]
    names += [f"movie{n:02d}" for n in range(1, 16)]
    names += [f"ship{g}_{n}" for g in (0, 1) for n in range(9)]
    return names


def run(scene, rom, out, god, states, prims=False):
    d = os.path.join(out, scene)
    frames = LONG.get(scene, 20000)
    cmd = [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "emu.py"), rom, "--out", d, "--frames", str(frames),
           "--timeout", "1200", "--script", WARP, "--script", SCENES, "--var", f"SCENE='{scene}'"]
    if prims:
        cmd += ["--script", os.path.join(ROOT, "tools", "debug", "primdump.lua")]
    if scene not in NO_SMOKE:
        cmd.append("--smoke")
    if god:
        cmd += ["--var", "GOD=1"]
    if states:
        cmd += ["--state-out", os.path.join(ROOT, "work", "states", scene + ".sstate")]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")
    log = os.path.join(d, "log.txt")
    last = ""
    if os.path.exists(log):
        lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
        last = lines[-1] if lines else ""
    return scene, r.returncode, last, r.stdout.strip().splitlines()[-1:] if r.returncode else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default=DEFAULT_ROM)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "qa", "warp"))
    ap.add_argument("--god", action="store_true")
    ap.add_argument("--states", action="store_true")
    ap.add_argument("--prims", action="store_true", help="dump RAM and VRAM at every shot, for tools/prims.py")
    ap.add_argument("scenes", nargs="*")
    a = ap.parse_args()
    names = a.scenes or scene_names()
    bad = 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for scene, rc, last, err in ex.map(lambda s: run(s, a.rom, a.out, a.god, a.states, a.prims), names):
            print(f"{'ok  ' if rc == 0 else 'FAIL'} {scene:16} rc={rc} {last} {err}")
            bad += rc != 0
    print(f"{len(names) - bad}/{len(names)} scenes ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
