# Time Bokan Series: Bokan desu yo English translation

Unofficial English fan translation of **Time Bokan Series: Bokan desu yo** (PlayStation, Banpresto, 1998): the source
text and tools that build the patch. Progress and open bugs are in `docs/status.md`.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Movie dialogue | English subtitles burned into all 16 movies; voices stay Japanese |
| Menus, options, ship names | Translated |
| Stage cards, banners, HUD | Translated |
| Credits roll | Translated |
| Sound test lyric cards | English title and a short summary, not line-by-line lyrics |
| Title logo | Left in Japanese, as no official English logo is known |
| Song captions in the movies | Left in Japanese, burned into the picture |
| Songs and voice samples | Left in Japanese |

Known issues: nobody checked the subtitles by ear, as they come from machine transcription with corrections; a few lines
on unclear audio have no subtitle; some credit name readings are unconfirmed. Tested on PCSX-Redux only, by scripted warps
to every scene rather than a full playthrough. See also [Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/time-bokan-series-bokan-desu-yo-en
cd time-bokan-series-bokan-desu-yo-en
# copy your dump (.cue and all 24 tracks) to rom/, for example:
#   rom/Time Bokan Series - Bokan desu yo (Japan) (Track 01).bin
#   (349008576 bytes, CRC32 e9488854, MD5 47479f82e99e046b6d2f6b0af734fc53,
#    SHA-1 8bfdb89e2ca65c053454fa323b0f373db3695b41; the build refuses any other dump, see rom.sha1)
# Redump: http://redump.org/discs/quicksearch/SLPS-01211/
python -X utf8 tools/build.py                          # -> build/ (about 15 min for the movies)
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Banpresto's and is included only so
the translation can be checked against it. Time Bokan Series: Bokan desu yo is (c) Banpresto and Tatsunoko Production;
this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
