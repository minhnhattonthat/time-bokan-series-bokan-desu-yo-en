# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool next. No build yet (phase 1 recon finished 2026-11-06).
- **Done:**
  - Step 0: dump pinned, hooks, check, emulator smoke on the original. Guard blocks `sed -i`; a failing test blocks a commit. Scripted Start press changes the screen. Not tested: GUI keyboard input (headless run, no person at the keyboard).
  - Phase 1: `docs/re/` holds disc layout, the no-text-encoding finding, and the graphics survey. All 249 TIMs were read. FMVs were sampled every 5 s only. Fixed an ECC offset bug in `tools/disc.py` (any write would have crashed).
- **Next:** phase 2. Read `references/emulator-qa.md` §Debug tool. Start from the leftover debug strings in `TARGET.EXE` (0x854-0x9A4, `docs/re/disc.md`), find their caller and the stage and mode variables, then write `tools/debug/warp.lua` and a scene list covering all menus, 7 stage cards, game over, ending and credits, and the movie viewer.
- **Later phases, what differs here:** no script bytes exist.
  - Phase 3: identity test is TIM and file rewrite through `disc.py`.
  - Phase 4: the "script" is Japanese read from images and captions, plus FMV dialogue. FMV speech needs a transcript: try faster-whisper with VAD off (not installed yet; platform-ps1.md), and check it by ear-free means, e.g. against lyric cards.
  - Phase 5: redraw tiles with a font; check UV rectangles for labels that must grow.
  - FMV subtitles: jPSXdec `-replaceframes` is the documented route (not installed; Java is). ffmpeg decodes STR for sampling.
- **Open bugs:** none.
- **Waiting on the user:** D7 (non-blocking): burning English subtitles into the FMVs is this run's default, not an owner ruling. Song audio and gameplay voice samples stay Japanese. Earlier patch search was partial: romhacking.net unchecked, GameFAQs returned 403.
