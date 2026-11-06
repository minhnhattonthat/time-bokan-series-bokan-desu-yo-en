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
- [ ] `sprite.sign2` overruns its quad at x=116: phase 7 moves the rect left into the quad, or re-letters both sign lines.
- [ ] MOVIE05.5 overlaps the next subtitle by 0.08 s; trim the end to 17.92 when wiring `subs`.
- [ ] `tools/tl_check.py` sums credit strips rather than packing, and has no honorific check (`references/translation.md` §Validation).
- [ ] Fill the template briefs before phases 8 and 9: `docs/reviewer-brief.md`, `docs/story-reviewer-brief.md`, `docs/visual-qa-brief.md`, `docs/translator-brief.md` (it also runs `tools/batches.py`, which doesn't exist here).
- [ ] `script/fmv/*.tsv` speaker column: 65 rows say Dokurobee, Tonzura or Yatter-Wan, the glossary's avoided spellings. Normalize.
