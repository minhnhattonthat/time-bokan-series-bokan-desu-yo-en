# Disc layout

Game: Time Bokan Series: Bokan desu yo (SLPS-01211). Banpresto / Eleven, PlayStation, 1998-03-12, 1-2 players,
vertical-scrolling shooter (ja.wikipedia). Sequel to Bokan to Ippatsu! Doronbo. No earlier fan patch found, but
romhacking.net and GameFAQs were not reachable or not checked this session (GameFAQs returned 403).

**Verified** by `tools/disc.py list` and `tests/test_recon.py` unless marked.

- 24 tracks: Track 01 MODE2/2352 data (148,388 sectors), Tracks 02-24 CD audio (songs).
- `/DA/DATA00-22.DA` are ISO entries that point past Track 01 into the audio tracks. Never rewritten.
- `disc.py` reads the ISO9660 tree, and rewrites form 1 files in place with fresh EDC/ECC. Files keep their LBA, and
  form 2 sectors are never touched by `write_file`.
- `disc.py verify` recomputes EDC/ECC for every form 1 sector and matches all but LBA 148387, the last sector of the
  track. It lies past MOVIE15's end (LBA 148237) in no file, so `verify` exits 1 on the clean dump; "bad 1" is the baseline.
- Boot: `SLPS_012.11` (4 KB loader) -> `TARGET.EXE` (load 0x80010000, text 0x14A000 bytes, entry 0x800132A4).

| Path | Count | What it is |
|---|---|---|
| `TARGET.EXE` | 1 | main program; debug strings, no Japanese |
| `S1OVER`-`S7OVER.BIN` | 7 | one overlay per stage; starts with a table of RAM pointers and the stage's file names |
| `S8OVER.BIN` | 1 | title, options and extras (names SUBDATA/TITLE*, CONFIG*, OPTI*, OPTI/*) |
| `S9OVER.BIN` | 1 | movie player (names /STR/MOVIE00-15) |
| `S10OVER.BIN` | 1 | ending (names /DATA/END_0-6) |
| `LOGO.BIN` | 1 | Banpresto logo, 16 bpp TIM |
| `DATA/ SUBDATA/ CUT/ OPTI/ STAGE1-7/` | 248 | uncompressed TIM images, one per file |
| `STR/MOVIE00-15.STR` | 16 | MDEC video with XA audio; form 2 sectors, about 130k sectors in all |
| `SE/BANK0-1/*.VH,*.VB` | 48 | VAB sound banks, including in-game voice samples (guess: `VOICE CUT` debug flag) |

## Compression

None on the image files: every one is a plain TIM at offset 0 (`tools/tim.py scan work/x`). Overlays and `TARGET.EXE`
hold no embedded TIM (`tools/tim_survey.py embedded work/x`: 0 hits). `OPTI/CARD*`, `DATA/TITLE.BIN` and
`SUBDATA/KABE256.BIN` carry 7,680 trailing zero bytes (checked on CARD00 and TITLE; guess for the others).

## Free space

The plan needs none so far: graphics are replaced at the same TIM size, so no file moves. 29 sectors of gaps exist
between files on the data track, and the data track has no room past MOVIE15 (next free sector unverified).
Re-encoded FMV must fit the original sector count of its file.

## Debug leftovers (phase 2)

`TARGET.EXE` strings at 0x854-0x9A4: `SYS >$%X`, `EXTRA`, `VOICE CUT`, `SUB VOICE CUT`, `V SCROLL SYNC.`, `JOY CUT`,
`1/30 SYNC`, `CD NON-BRO.`, `CD-DA READ`, `PAUSE`, `ST.SEL>$%X`, `ST.IND.>$%X`, `ST.>$%X`, `1P SC.UP>%d`, `GAME>$%X`,
`1P.NOW`, `2P.NOW`, `SKY.`, `NOT PAUSE`, `NOT BOMB`, `NOT BIG`, `NOT INTER`, `1STU>$%X`, ` CND>$%X`, `  NO>$%X`,
` ATR>$%X`, `2STU>$%X`. **Guess:** a leftover debug screen with stage select (`ST.SEL`) and game-mode variables. Find its
caller first: it may give the warp tool its stage and mode addresses directly.
