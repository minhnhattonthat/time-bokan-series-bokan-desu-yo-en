# Polish list

Minors deferred to one pass before release. Tick each `[x]`, fixed or `waived: reason`; the release script refuses to
run while a line is unticked.

- [ ] MOVIE06.8, .11, .12 - dropped as unclear in the audio; MOVIE06 ends on the kimono figure with no line. Ear-check, or waive.
- [ ] MOVIE13.11 - dropped (出張な, unclear). Ear-check, or waive.
- [ ] MOVIE14.13, .18, .37, .38 - dropped as unclear. Ear-check, or waive.
- [ ] MOVIE08.2, .3, .17 - hamburger and ketchup gag rests on an uncertain reading and speakers. Ear-check.
- [ ] MOVIE10.1 - "Skull Bun" for ドクロマンジュウ is a guess at the audio. Ear-check.
- [ ] MOVIE12.1 - "Doku-Melon" is a guess at the audio. Ear-check.
- [ ] MOVIE14.27 - 嘘だよ is a guess; Whisper heard 凄いよ. Ear-check.
- [ ] MOVIE02.6, MOVIE10.6, MOVIE14.16, .19, .36 - also on unclear audio. Ear-check, or waive.
- [ ] Credit readings not confirmed by a source: lines 23, 25, 26, 27, 34, 62, 73. Check against an official credit or waive.
- [ ] Credit line 55 - "Bokan Birth" for ボカンと出産 keeps the joke only half; a better nickname if one comes up.
- [x] MOVIE05.1 - "Yatterman duo": fixed, Tatsunoko's own Yatterman page says "The Yatterman duo".
- [ ] `sprite.sign2` "Doron Company" - reading of the sign is uncertain; check a zoomed shot in phase 8.
- [ ] MOVIE00.1, 01.14, 01.18, 04.1, 05.14, 05.15, 06.7, 07.8, 13.7 - also marked `?` in the source. MOVIE04.1 most of all: raw reading こりゃいけません is the reverse of the corrected こりゃいけまっせ. Ear-check, or waive.
- [ ] Credit line 51 (荘埜(らい)毅明) - kanji and readings uncertain. Check against an official credit or waive.
- [x] `sprite.sign2` overruns its quad at x=116: fixed, `gfx.widened` keeps it inside the quad.
- [x] MOVIE05.5 overlaps the next subtitle by 0.08 s: fixed, `tl_check.subs` ends a line where the next starts.
- [x] `tools/tl_check.py` sums credit strips: fixed, it runs the real pack. Honorific check added for 様; ちゃん and さん hit too many other words.
- [x] Template briefs filled: `docs/reviewer-brief.md`, `docs/story-reviewer-brief.md`, `docs/visual-qa-brief.md`, `docs/translator-brief.md`, `docs/playtester-brief.md`.
- [x] `script/fmv/*.tsv` speaker column: normalized to Dokurobey, Tonzra, Yatterwan.
