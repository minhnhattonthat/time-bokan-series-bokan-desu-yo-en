# Sprite cells, GPU quads and credit strips (phase 5)

**Verified** by `tools/cells.py`, `tools/prims.py` on RAM dumps from `warp_all.py --prims`, and the marker build.

## Cell groups

All sprite layouts are data: a u32 part count, then 12-byte parts:

| Offset | Type | Field |
|---|---|---|
| 0, 1 | u8 | u, v inside the TIM |
| 2, 3 | s8 | dx, dy from the group's anchor |
| 4, 6 | u16 | w, h |
| 8, 10 | u16 | sx, sy (4096 = 1:1) |

`TARGET.EXE` holds 807 groups, the overlays 135-487 each. Parts can be rewritten without moving anything, so a label can
point at any rectangle of its TIM. Tables don't name their TIM: the texture page comes from the draw call.

## GPU packets

The game builds two display lists in RAM (around 80090600 and 800C6C00):

- Sprites: n=7, `E1` draw mode word, two zero words, then `SPRT` (code 64): xy, uv + CLUT, wh.
- Rotated or scaled: `POLY_FT4` (n=9, code 2C).
- `SPRT8` also occurs (n=3, code 74). `tools/prims.py` doesn't decode it; so far only small HUD marks use it.

`prims.py rows` matches a dump's quads to `script/graphics.tsv` through the TIMs found in the VRAM dump. Stale packets
can pass its link test, so a quad may be from an earlier frame.

## What the quads showed

Most labels sit in far larger slots than their Japanese, so English fits without code changes:

| Label | Japanese rect | Quad |
|---|---|---|
| Main menu rows | up to 124x18 | 176x32 |
| Options rows | up to 81x20 | 144x32 |
| Extras list | up to 164x16 | window 168x128 scrolled in 16 px steps |
| Stage cards | 250x90 | 256x160 |

The per-row table is `script/budgets.tsv` (`tools/budgets.py`), from dumps in `work/qa/prim`: 221 rows from a quad, 21 from
a cell table, 24 with only the row's own rect (`source` = none), which are not measured.

These rows are cut across quads drawn apart, so one rect is not one budget:

- `go.fin` was three 48x48 quads drawn 64 px apart. Lettered as one rect it came out "TH E EN D", so it is now `go.fin1-3`,
  one word per quad.
- `go.game` and `go.over` are stacked pieces; letter them per quad in phase 7.
- `title.desc6` was split into `title.desc6a` (32 px, line 1 of the Options text) and `title.desc6b` (47 px, line 3). Each
  description draws four cells: Normal desc1/2/3/7, Special desc8/4/5/9, Options desc6a/10/6b/11.
- Every split `end.*` row: see Credits below.

## Marker tour (phase 5)

`build.py --marker` booted and all 73 scenes passed on it. The group sheets in `work/qa/msheets` were read at contact-sheet
zoom (implementer, not an independent reviewer; stage tours by final shot only). Marked labels showed their numbers in
place, and no unmarked Japanese was seen outside the logo art, which D5 keeps. Exact clipping wasn't measured per row.

45 rows drew no quad in any dump, so they are unconfirmed in game. Some may be leftovers or need a state the tour doesn't
reach: `title.hint_*`, `opt.player1`, `opt.pad`, `cfg.*` states (`big2-4`, `bomb1/3/4`, `shot2-4`, `back`, `stamp1-3`),
`plate.dokuro`, `sel.repair`, `extra.m14`, `hud.danger_c`, all `tag.*`, `sprite.ikari`, `sprite.harawata`,
`sprite.itadaki2/3`, `scribble.st2c0`, and 7 `end.*` pieces. `work/recon/prims_rows.tsv` has the list. The dumps were a
smaller set of shots than the tour, so a row can be on screen in the tour and still be listed; `extra.m14` was seen there.

## Font spike (phase 5)

`build.py --spike` letters `script/spike.tsv` through `gfx.typeset`; shots are in `work/qa/spike*`. Proven in game: main
menu, options, button config, Extras list, stage cards, ship plate, HUD, "THE END", credit lines 1-3.

What it showed:

- **Part scale does nothing:** `sx = sy = 8192` on a credit part still draws 1:1. So English can't be stored small and
  drawn large; every glyph costs its full size in VRAM.
- **Bar labels are row gradients:** background and fill use one palette index per row, so a flat clear wipes the bar art.
  `gfx.sampled_inks` samples per row when no one colour dominates.
- **See-through atlases:** a rect with index 0 in it clears to 0, since a packed strip's margin holds other labels.
- **Rects holding a button mark** (`title.btn_*`, `cfg.back/select/ok`) must hug the word or the mark is erased.
- **Glyph torture:** all printable ASCII shows in Jersey 10 at 20 px. Bangers shows all but `$ ( )`, which the torture
  dropped as taller than its 16 px rows; they are in the font, but no shot proves them.

Rough spots still open after phase 7: `hud.gameover` fill is banded and the plate background is a flat patch over stone
texture (phase 8 judges both). Extras rows all take the inks of `extra.m00`, as a wider rect sampled striped fill.

**English build (phase 7):** `gfx.english_rows` letters `script/en/graphics.tsv`, growing a rect around its centre to the text
when needed, inside the drawn quad and clear of other rows. `gfx.go_banner` draws GAME and OVER across the split quads of
`GO_S0`. `gfx.lyric_card` paints out each card's two ink indices by diffusion from neighbours, mapped back to the palette,
then letters title and summary on the line rows. `tools/build_check.py` fails on any change outside these.

## Width gate

Text must fit the rect and class or the build stops: `gfx.typeset` raises `ValueError` and never clips, and
`gfx.row_width(text, form)` gives the pixels. `tests/test_gfx.py` holds an exact fit and one pixel over. FMV: 272 px per
line, `fmv_burn.MAX_LINES` (3) lines, asserted in `burn_movie`. No runtime strings exist, so odd-length names and pad
glyphs don't apply.

## FMV subtitles (phase 5)

`build.py --marker` burned a 3-line test line into every dialogue, caption and form row of all 16 movies, 8,724 of 13,989
frames, with no player change. All 16 movie scenes passed. Every edited frame needed a coarser qscale, by up to 2-5 steps
depending on the movie. **Guess:** fewer lines cost fewer steps, so aim at 2 lines. The MDEC size cap `WORDS_MAX` = 12544 is the
largest in the original movies; a larger frame is untested. Only the single final shot of each movie was read, plus the
viewer's; MOVIE01 and MOVIE08's final shots fall between rows, and only a viewer shot of MOVIE01 shows its subtitle.

## Ship name plates

The plates on the ship zoom are ten cells 127x31 in `SUBDATA/MARK03` (`TARGET.EXE` 8005BD5C-8005BDEC). Phase 1 read that
file at CLUT 0 and missed them. They use CLUT 3 and are engraved, so the rect is plate art plus text.

Rechecked at each file's highest-contrast CLUT: all 51 other non-stage "no text" TIMs at full size, and the 159 stage TIMs
scaled to 77%. No more Japanese found, but the scaling could hide very small kana in stage files.

`tag.*` strips (y 240 of the ship TIMs): the ship zoom doesn't draw them. **Guess:** unused leftovers.

## Credits (`S10OVER.BIN`, 8015DD88-8015EA34)

All of the roll is data, read by disassembly at 8015A848 and 8015BB7C, and it's not a scroll but a list of pages:

| Address | What |
|---|---|
| 8015EA4C | u32 group pointer per line, 82 lines (line = index). Line 0 is the 声の出演 heading |
| 8015EF4C | per line, 80 entries: u32 slot (TIM `END_<slot>`, texture page 0x15 + slot), u32 palette (CLUT row 0x1F0 + n) |
| 8015EC0C | u16 page script: -2, -3, -4 + arg are scene commands, -1 ends; else duration, n, then n x (line, x, y, end) |

- Every line has an explicit y on its page, so pages can be re-spaced freely. A page opens up only if a two-row role would
  collide; the curtain hides anything above screen y 38.
- Lines 77 and 78 are placed by code (8015BCE4), not by the script. Lines 80 and 81 have no ART entry and are never drawn.
- The old `credits.py FILES` table guessed the TIM by table stretch and was wrong at the edges: line 18 is アニメーション・スタッフ
  from END_5, 44 is 主題歌 from END_4, 0 was missing. The English followed that error until phase 7 fixed it.

**English:** `credits.py` packs one strip per string on 13 px shelves, first-fit decreasing, per TIM, all with one baseline,
and rewrites each line's parts. END_4 used 15 shelves, END_5 16, END_6 19. Lettered fill index 15 (the line's colour) with
outline 3 (roles) or 2 (names), as the Japanese. Spare parts sample transparent pixel (0, 0), proven in game. Part scale
does nothing (see Font spike). Headings and the kept (C) cell, BANPRESTO and 1998 stay where they were (`credits.KEEP`).

Rows `end.*` in `script/graphics.tsv` are pieces of the old layout, not translation units.
