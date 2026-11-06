# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build next. No build yet (phase 2 debug tool finished 2026-11-06).
- **Done:**
  - Step 0: dump pinned, hooks, check, emulator smoke on the original. Guard blocks `sed -i`; a failing test blocks a commit. Scripted Start press changes the screen. Not tested: GUI keyboard input (headless run, no person at the keyboard).
  - Phase 1: `docs/re/` holds disc layout, the no-text-encoding finding, and the graphics survey. All 249 TIMs were read. FMVs were sampled every 5 s only. Fixed an ECC offset bug in `tools/disc.py` (any write would have crashed).
  - Phase 2: `tools/debug/warp_all.py` reaches all 73 scenes from a cold boot on the original disc, each with shots in `work/qa/warp/`: logo, title, menus, options, button config, sound test with all 17 lyric cards, Extras list and viewer, ship select and name tags, 7 cards, 7 stages, 7 god-mode tours, 16 movies, continue, 3 game overs, stage clear, ending and credits. 72 ran in one pass, then `sprite_itadaki` was added and passed alone. Scenes assert game state; a wrong warp exits 2. `docs/re/state.md` has the variables and the story script. Shots were read by the implementer on contact sheets, not by a separate reviewer.
- **Next:** phase 3. Identity test is TIM and file rewrite through `disc.py`: rewrite every Form 1 file unchanged and require a byte-identical Track 01, as a test. Then add the Build command to `AGENTS.md`.
- **Later phases, what differs here:** no script bytes exist.
  - Phase 4: the "script" is Japanese read from images and captions, plus FMV dialogue. FMV speech needs a transcript: try faster-whisper with VAD off (not installed yet; platform-ps1.md), and check it by ear-free means, e.g. against lyric cards.
  - Phase 5: redraw tiles with a font; check UV rectangles for labels that must grow.
  - FMV subtitles: jPSXdec `-replaceframes` is the documented route (not installed; Java is). ffmpeg decodes STR for sampling.
- **Open bugs:** none. Two graphics rows not yet seen in game: 怒 (`ST3_S2F`) and はらわた (`ST3_S5D`), see `docs/re/graphics.md`. PCSX-Redux once exited 0xC0000374 (heap corruption) as a run ended, after a complete log and final shot (38,000-frame tour); the same scene had passed at other settings, so treat that exit code as a flake and rerun.
- **Waiting on the user:** D7 (non-blocking): burning English subtitles into the FMVs is this run's default, not an owner ruling. Song audio and gameplay voice samples stay Japanese. Earlier patch search was partial: romhacking.net unchecked, GameFAQs returned 403.
