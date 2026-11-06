# Text engine

**There is no text encoding to extract.** Every Japanese string the player sees is pixels: a region of a TIM image or
a frame of an FMV.

**Verified:**
- `jpscan.py` over `TARGET.EXE`, `SLPS_012.11` and `S1OVER`-`S10OVER` finds no Japanese. Its few Shift-JIS hits are noise
  (`羣mjuｊ}瀦`, `＝＝＝＝＝＝`), as are the UTF-16 hits (pointer tables read as text). `LOGO.BIN` hits are 16 bpp pixels.
- ASCII strings are file names, SDK messages and debug labels only (`docs/re/disc.md`).
- The static sweep (`docs/re/graphics.md`) shows the Japanese menus, stage cards, lyrics and credits as image files.

**Guess, to confirm in phase 5:** menus draw sprites by fixed UV rectangles held in overlay data or code, so each label's
position and size are data. If a longer English label needs a wider rectangle, those tables must change. Fitting
English inside the existing rectangles avoids this, so try that first.

So for this game:
- **Pointers:** none for text. **Text ranges:** none in code; the ranges are the rectangles in `graphics.md`.
- **Control codes, table files:** none. `tbl/` stays empty and `jp_left.py --sjis` can only confirm the absence.
- **Script source for translators:** the Japanese read from the images and captions (phase 4), not bytes from the disc.
- **Roundtrip test (phase 4):** decoding a TIM and re-encoding it gives identical bytes.

## Voice (no on-screen text)

The 16 FMVs carry spoken dialogue in XA audio with no subtitles, apart from the captions listed in `graphics.md`. That
is the story of the game, and of Special mode in particular. Gameplay voice samples sit in `SE/` banks.
An English patch needs burned-in subtitles to convey it; see `docs/decisions.md` D7.
