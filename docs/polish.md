# Polish list

Minors deferred to one pass before release. Tick each `[x]`, fixed or `waived: reason`; the release script refuses to
run while a line is unticked.

- [x] MOVIE06.8, .11, .12 - dropped as unclear in the audio; MOVIE06 ends on the kimono figure with no line. waived: no one here can listen, and two Whisper passes gave no usable reading. No subtitle beats a guessed one. Listed in the README's known issues.
- [x] MOVIE13.11 - dropped (出張な, unclear). waived: as above.
- [x] MOVIE14.13, .18, .37, .38 - dropped as unclear. waived: as above.
- [x] MOVIE08.2, .3, .17 - hamburger and ketchup gag rests on an uncertain reading and speakers. waived: no ear-check possible; the lines read as one absurd gag in story order. Listed in the README's known issues.
- [x] MOVIE10.1 - "Skull Bun" for ドクロマンジュウ is a guess at the audio. waived: no ear-check possible; it works as an insult in context.
- [x] MOVIE12.1 - "Doku-Melon" is a guess at the audio. waived: no ear-check possible; the self-correction "er, Dokurobey" holds whatever the first word is.
- [x] MOVIE14.27 - 嘘だよ is a guess; Whisper heard 凄いよ. waived: no ear-check possible; the denial fits between 14.26 and 14.29 ("It's true!").
- [x] MOVIE02.6, MOVIE10.6, MOVIE14.16, .19, .36 - also on unclear audio. waived: no ear-check possible; each reads correctly in story order.
- [x] Credit readings not confirmed by a source: lines 23, 25, 26, 27, 34, 62, 73. Fixed from MobyGames' credits (user-contributed): 25 Minoru Kibata, 73 Yoshinobu Oyama; it confirms 23, 27, 34. waived for 26 (李 載束) and 62 (速瀬 陰): kanji match three staff lists, but no source gives a reading.
- [x] Credit line 55 - "Bokan Birth" for ボカンと出産 keeps the joke only half. waived: no better nickname came up; it is a staff joke with no plot weight.
- [x] MOVIE05.1 - "Yatterman duo": fixed, Tatsunoko's own Yatterman page says "The Yatterman duo".
- [x] `sprite.sign2` "Doron Company": zoomed crop reads ドロンカンパニー as far as 4 px tall text allows. Kept.
- [x] MOVIE00.1, 01.14, 01.18, 04.1, 05.14, 05.15, 06.7, 07.8, 13.7 - also marked `?` in the source. waived: no ear-check possible; all read correctly in story order. MOVIE04.1's reversed raw reading is corrected by the scene, where the trio are winning.
- [x] Credit line 51 (荘埜(らい)毅明) - fixed: three staff lists confirm the kanji, and MobyGames gives Takaaki Sono.
- [x] Credit line 60 (横山 祥) - MobyGames reads Hiroshi, which overflows END_6. waived: Sho is a common reading of 祥 and the source is user-contributed.
- [x] Credit line 79 (とまとあき) - fixed: Tomato Aki, a kana pen name kept in written order, as on MobyGames.
- [x] MOVIE11.4 - "another bomb" implied a bomb the Special route never showed: fixed, "a bomb" (story pass).
- [x] MOVIE13.5 - "You're done here" undersold 用済み at the betrayal: fixed, "You've served your purpose." (story pass).
- [x] Credit lines 77 and 80 say Tatsunoko Pro and Tatsunoko Production. waived: line 80 is never drawn (`tools/credits.py`).
- [x] `sprite.sign2` overruns its quad at x=116: fixed, `gfx.widened` keeps it inside the quad.
- [x] MOVIE05.5 overlaps the next subtitle by 0.08 s: fixed, `tl_check.subs` ends a line where the next starts.
- [x] `tools/tl_check.py` sums credit strips: fixed, it runs the real pack. Honorific check added for 様; ちゃん and さん hit too many other words.
- [x] Template briefs filled: `docs/reviewer-brief.md`, `docs/story-reviewer-brief.md`, `docs/visual-qa-brief.md`, `docs/translator-brief.md`, `docs/playtester-brief.md`.
- [x] `script/fmv/*.tsv` speaker column: normalized to Dokurobey, Tonzra, Yatterwan.
