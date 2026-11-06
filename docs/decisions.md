# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

D1-D3, D5 and D6 come from the owner's standing answers for one-shot runs. D4 is the skill's default. D7 and D8 are
defaults this run chose, so the owner can overrule them.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-06 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western name order (given name first). Owner's standing answer. |
| D2 | 2026-11-06 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. Owner's standing answer. |
| D3 | 2026-11-06 | Credits | stay Japanese, translate | English. Owner's standing answer. |
| D4 | 2026-11-06 | Abbreviations | engine work first (default), abbreviate | Engine work first; abbreviate only as a flagged last resort. Skill default, not overridden. |
| D5 | 2026-11-06 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards). The original Japanese logo stays only if it has no official English version; none is known for ボカンですよ, so it stays. Owner's standing answer. |
| D6 | 2026-11-06 | Specs and plans | need approval, pre-approved | Pre-approved. Owner's standing answer. |
| D7 | 2026-11-06 | FMV dialogue: spoken Japanese with no subtitles carries the story | leave untranslated; burn English subtitles into the STR files | Burn in subtitles, if re-encoding fits each file's sector count. **Agent default, not an owner ruling:** the story is otherwise lost to English players. Noted in `docs/status.md` under "Waiting on the user". |
| D8 | 2026-11-06 | Verbatim song lyrics (17 cards, FMV song captions) in the repo | commit like other script text; keep local | Keep them out of git: `work/script/lyrics_jp.tsv` (gitignored, re-readable from the cards) and no text on `song` rows in `script/fmv/`. **Agent default, not an owner ruling:** these are third-party songs and the repo may go public, while line rects are all the build needs from git. How the English lyrics ship is still open for phase 6. Noted in `docs/status.md` under "Waiting on the user". |
