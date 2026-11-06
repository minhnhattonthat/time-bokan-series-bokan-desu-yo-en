# Time Bokan Series: Bokan desu yo (PS1) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `python tools/skill.py` prints its folder; `$SKILL` = that folder). Read its SKILL.md before ROM, text or QA work.

## Commands (run from repo root)
- Hooks:    `git config core.hooksPath tools/hooks` (once per clone)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this)
- Dump:     `python -X utf8 tools/check_rom.py` (checks the dump against `rom.sha1`)
- Extract:  `python -X utf8 tools/disc.py x "rom/Time Bokan Series - Bokan desu yo (Japan) (Track 01).bin" work/x` (Form 1 files; STR and DA stay on disc)
- Survey:   `python -X utf8 tools/tim_sheets.py work/x work/recon/tims` (all TIMs to contact sheets) and `tools/str_frames.py` (FMV samples)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py "rom/Time Bokan Series - Bokan desu yo (Japan).cue" --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp_all.py [--rom CUE] [--states] [scene ...]` (cold boot to any scene, shots in `work/qa/warp/<scene>/`; scene list `tools/debug/scenes.lua`, addresses `docs/re/state.md`)
- Build, release: not written yet (phases 3, 9); add each here when it exists. Never publish without the user.
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/` (gitignored; 24 .bin tracks plus .cue, SHA-1s in `rom.sha1`). Only Track 01 changes. Emulator: this repo's own PCSX-Redux in `tools/pcsx/` (version.json: 30282.20261104.5; gitignored). BIOS: `tools/bios/scph5500.bin`. Savestates: `work/states/`.
- Text: no text encoding exists; every string is a TIM region or an FMV frame. Survey: `docs/re/graphics.md`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens. In an Orca one-shot run nested workers are refused: do reviews yourself in a fresh read-only pass, or with `codex exec`.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Gotchas: Japanese games confirm with circle. `disc.py write_file` keeps LBAs, so a replacement must keep each file's exact size. `disc.py verify` reports "bad 1" on the clean dump (LBA 148387, in no file). Start skips the opening FMV: pressed at frame 1200 the title art shows by about frame 1800, while unpressed the FMV is still playing at 2590.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
