Time Bokan Series: Bokan desu yo (PlayStation) - English translation patch v$version

Unofficial fan translation. This zip holds the patch and this file only. No game data is included, and pre-patched
images must not be shared.


WHAT YOU NEED

Your own dump of the Japanese disc, SLPS-01211, as BIN/CUE with 24 tracks (Redump: Time Bokan Series - Bokan desu yo
(Japan), http://redump.org/discs/quicksearch/SLPS-01211/). The patch changes Track 01 only:

    Time Bokan Series - Bokan desu yo (Japan) (Track 01).bin
    Size    $size bytes
    CRC32   $crc32
    MD5     $md5
    SHA-1   $sha1

After patching, Track 01 has:

    CRC32   $new_crc32
    SHA-1   $new_sha1


HOW TO PATCH

1. Copy the whole game folder, so your original stays as it is.
2. Apply $patch to Track 01 with xdelta3 or Delta Patcher:

       xdelta3 -d -s "original Track 01.bin" $patch "patched Track 01.bin"

3. Replace Track 01 in the copy with the patched file, under the same file name. The .cue and tracks 02-24 stay as they
   are.
4. Open the .cue in your emulator and start from a cold boot. Savestates made on the original disc hold the old graphics
   and will not show the English.


TRANSLATION STATUS

Movie dialogue               English subtitles burned into all 16 movies; voices stay Japanese
Menus, options, ship names   Translated
Stage cards, banners, HUD    Translated
Credits                      Translated
Sound test lyric cards       English title and a short summary, not line-by-line lyrics
Title logo                   Left in Japanese, as no official English logo is known
Song captions in the movies  Left in Japanese, burned into the picture
Songs and voice samples      Left in Japanese


KNOWN ISSUES

- Nobody checked the movie subtitles by ear. They come from machine transcription, corrected from the frames, context
  and knowledge of the series. Some are best guesses, among them the hamburger and ketchup gag in Prologue B, "Skull
  Bun" and "Doku-Melon".
- A few short lines had audio too unclear to read and have no subtitle: 3 in the Normal Game's self-destruct scene,
  1 in Dokurobey's betrayal and 4 in the Good Guys' attack.
- Subtitles use official English names, so they say "Tonzra" and "Rescueman" where the voice says "Tonzura" and
  "Otasukeman".
- Some credit name readings are unconfirmed, because their kanji can be read more than one way.
- 38 graphics labels were never seen drawn in testing and are probably unused. They are translated anyway.

Tested on PCSX-Redux 30282.20261104.5 only, by scripted warps to every scene rather than a full playthrough. Not tested
on real hardware or other emulators. Please report bugs:
https://github.com/minhnhattonthat/time-bokan-series-bokan-desu-yo-en/issues


CREDITS

Translation and tools: minhnhattonthat, with extensive AI assistance (Claude by Anthropic), including the machine
transcription of the movies. Corrections are very welcome.
Fonts: Bangers, Jersey 10, Jersey 15, Liberation Serif and Liberation Sans, under the SIL Open Font License 1.1.
Time Bokan Series: Bokan desu yo is (c) Banpresto and Tatsunoko Production. This project is not affiliated with them.
