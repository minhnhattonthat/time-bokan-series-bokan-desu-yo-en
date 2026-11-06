# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4. Extract next (phase 3 identity build finished 2026-11-06).
- **Done:**
  - Step 0: dump pinned, hooks, check, emulator smoke on the original. Guard blocks `sed -i`; a failing test blocks a commit. Scripted Start press changes the screen. Not tested: GUI keyboard input (headless run, no person at the keyboard).
  - Phase 1: `docs/re/` holds disc layout, the no-text-encoding finding, and the graphics survey. All 249 TIMs were read. FMVs were sampled every 5 s only. Fixed an ECC offset bug in `tools/disc.py` (any write would have crashed).
  - Phase 2: `tools/debug/warp_all.py` reaches all 73 scenes from a cold boot on the original disc, each with shots in `work/qa/warp/`: logo, title, menus, options, button config, sound test with all 17 lyric cards, Extras list and viewer, ship select and name tags, 7 cards, 7 stages, 7 god-mode tours, 16 movies, continue, 3 game overs, stage clear, ending and credits. 72 ran in one pass, then `sprite_itadaki` was added and passed alone. Scenes assert game state; a wrong warp exits 2. `docs/re/state.md` has the variables and the story script. Shots were read by the implementer on contact sheets, not by a separate reviewer.
  - Phase 3: `tools/build.py` rewrites all 310 Form 1 files (8,027 sectors, 249 TIMs through `tim.pixels`/`with_pixels`) with fresh EDC/ECC. `tests/test_build.py` requires Track 01's SHA-1 to equal the dump; breaking the seal or the TIM step made the hash differ (one-off check, not a kept test). `disc.write_file` no longer skips unchanged sectors, because that skip made the identity vacuous. Built disc passes `emu.py --smoke` with the boot route. Not covered: FMV (STR) rewrite, which has no tool yet.
- **Next:** phase 4. The "script" is Japanese read from images and captions, plus FMV dialogue. FMV speech needs a transcript: try faster-whisper with VAD off (not installed yet; platform-ps1.md), and check it by ear-free means, e.g. against lyric cards.
- **Later phases, what differs here:** no script bytes exist.
  - Phase 5: redraw tiles with a font; check UV rectangles for labels that must grow. Edit CLUT indices through `tim.with_pixels`, since `to_image` drops the STP bit.
  - FMV subtitles: jPSXdec `-replaceframes` is the documented route (not installed; Java is). ffmpeg decodes STR for sampling.
- **Open bugs:** none. Two graphics rows not yet seen in game: 怒 (`ST3_S2F`) and はらわた (`ST3_S5D`), see `docs/re/graphics.md`. PCSX-Redux once exited 0xC0000374 (heap corruption) as a run ended, after a complete log and final shot (38,000-frame tour); the same scene had passed at other settings, so treat that exit code as a flake and rerun.
- **Waiting on the user:** D7 (non-blocking): burning English subtitles into the FMVs is this run's default, not an owner ruling. Song audio and gameplay voice samples stay Japanese. Earlier patch search was partial: romhacking.net unchecked, GameFAQs returned 403.
