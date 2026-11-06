# Game state and flow

Addresses are RAM; `TARGET.EXE` loads at 0x80010000 (file offset = addr - 0x8000F800), overlays at 0x80159E50.
**Verified** means read in the disassembly and reached by a `tools/debug/` scene that asserts it from a cold boot.

## Variables (verified)

| Address | Size | Name | Meaning |
|---|---|---|---|
| 8008EB8C | u16 | M | main state, dispatched by the jump table at 80010CC8 in 800160F8 |
| 800FC9AC | u16 | T | title and options sub-state, S8OVER 8015A468 |
| 800FC854 | u16 | ST.IND | index into the story script |
| 80159E3C | u16 | ST. | current script entry |
| 80159E44 | u16 | TYPE | 0 normal game, 1 special game |
| 8008EB98 | u16 | ST.SEL | stage select cursor; also counts stages cleared |
| 801499FC | u16 | OVL | overlay loaded: n means `S<n+1>OVER.BIN` (name table 8005C108) |
| 800FC9A0 | u32 | SYS | flags: 0x100 Extras unlocked by L1+R1, 0x200 EXTRA (game cleared), 0x400 VOICE CUT, 0x800 SUB VOICE CUT |
| 800FCA0C | u16 | GAME | flags: 0x10 1P in play, 0x20 2P in play; 0x200 NOT PAUSE, 0x2000 NOT BOMB, 0x4000 NOT BIG, 0x8000 NOT INTER (labels from the debug print) |
| 8008EB34 | s32 | credits | continues left |
| 8008EB94 | u16 | menu cursor | 0 normal, 1 special, 2 options |
| 8008EB96 | u16 | options cursor | 0 buttons, 1 credits, 2 sound, 3 voice, 4 extras |
| 80106BDC | struct | 1P | 0xCC bytes; 2P at 80106CA8. +0 STU, +2 CND, +4 mode (0x10 at rest, 0x20 playing), +6 ship, +0x24 ATR, +0x82 shield hits (4 full, -1 dead) |
| 80146E08 | u16[2] | pad edge | 1P, 2P presses: 0x800 Start, 0x20 circle, 0x40 cross, 0x4000 down |
| 8008E980 | 24 B x 16 | stage tasks | +0 bit 0 live, +4 function, +8 state, +0x14 timer (allocator 80023534) |
| 800FC860 | 20 B x 16 | per-frame callbacks | +0 flag (0x10 live), +4 tick, +8 function, run at the top of 800160F8 |

The debug print routine at 80013E60 prints these, but nothing calls it: a `jal` scan of `TARGET.EXE` and all overlays finds
no caller. The game's level select needs SYS 0x200 (ship select, up and down move ST.SEL).

## Main states

| M | What |
|---|---|
| 0-5 | Banpresto logo |
| 6 | Start held: load S8OVER (title). Else play MOVIE00, the opening, first |
| 7, 9 | title and options, exit to 0x10 (game) or back to 6 (attract) |
| 0x10, 0x11 | next script entry; high nibble picks the state below |
| 0x18-0x1D | ship select (`SELMAIN`, name tags at 0x1A). With SYS 0x200, 0x1D jumps ST.IND by ST.SEL (table 8005C010) |
| 0x20-0x27 | load stage overlay and art; 0x27 is the stage card (`TAIM_*`, 350 frames) |
| 0x30 | movie `ST & 0xF`, blocking in S9OVER; Start skips, ST.IND + 1 |
| 0x40, 0x41 | stage running. No player left: to 0x50, or to 0x81 with no credits |
| 0x50, 0x51 | continue countdown; circle ticks it; expiry shows `GO_S<TYPE>` |
| 0x70 | stage cleared: ST.IND + 1, ST.SEL + 1, back to 0x10 |
| 0x80, 0x81 | script end: `GO_S2` (おわり); Start returns to title |
| 0x90, 0x91 | ending and credits, S10OVER |

Game over from a stage with no credits picks `GO_S0` or `GO_S1` by `rand() & 1` (80016FBC).

## Story script (verified)

Tables at 8005C050 (normal) and 8005C0A8 (special), u32 per entry. `0n` stage overlay n, `1n` movie n, `F0` ending,
`20` end of game, -1 stop. Stage overlay n is `S<n+1>OVER`.

| ST.IND | Normal | Special |
|---|---|---|
| 0 | 11 | 18 |
| 1 | 00 (card ST1) | 00 (card ST1) |
| 2 | 12 | 19 |
| 3 | 01 (ST2) | 01 (ST2) |
| 4 | 13 | 1A |
| 5 | 02 (ST3) | 05 (STS) |
| 6 | 14 | 1B |
| 7 | 03 (ST4) | 02 (ST3) |
| 8 | 15 | 1C |
| 9 | 04 (ST5) | 03 (ST4) |
| 10 | 16 | 15 |
| 11 | 17 | 04 (ST5) |
| 12 | F0 | 1D |
| 13 | 20 | 06 (STF) |
| 14 | -1 | 1E |
| 15 | | 17 |
| 16 | | F0 |
| 17 | | 1F |
| 18 | | 20 |

MOVIE00 is the opening only. Every other movie is in a script, and the Extras viewer plays them too.

## Title sub-states (S8OVER, verified)

0x11 press-start screen (Start to 0x20, 1800 frames idle back to attract). 0x22 main menu. 0x43 options. 0x51 button
config. 0x71 sound test, with `OPTI/CARD*` lyric cards (right: next). 0x91 Extras movie list (`OPTI/OMAKE1`); circle plays.
0xF0 has code but nothing writes it: **guess** dead.

Reaching Extras: hold L1+R1 while Options opens, or have SYS 0x200 from clearing the game.

## Stage clear

Stage overlays call 80024A08, which starts task function 80024AC8 (STAGE CLEAR text in English, fade, M = 0x70). Its first
state waits for the player's mode to read 0x10. `tools/debug/scenes.lua` `clear` starts it directly; a long `tour_*` run
reaches it by real play.

## Debug tool

`tools/debug/warp.lua` plus `scenes.lua`; `warp_all.py` runs the list. God mode pins 1P shield at 4. With god mode and fire
held, stages 3 and 4 clear on their own after about 37,000 game frames, which is the slow way to any boss.
