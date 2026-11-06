# Graphics-text survey

**Method (verified):** `tools/tim_sheets.py work/x work/recon/tims` rendered all 249 TIMs on the disc to 21 contact
sheets with CLUT 0, and every sheet was read. Skipped, printed by the tool: `SE/` sound banks, the overlays, `TARGET.EXE`,
`SLPS_012.11` and `SYSTEM.CNF`. None hold TIMs (`tools/tim_survey.py embedded`). `tim_survey.py hidden` shows CLUT 0 hides
pixels only in `ST3_SB0` (25%), `OPTI0` (7%) and `ST7_SA0` (2%). `OPTI0` and `ST7_SA0` were read zoomed, and `ST3_SB0` was
read by raw pixel index: no Japanese in it.

FMVs: `tools/str_frames.py` sampled one frame every 5 s of each movie (187 frames). A caption shorter than 5 s can be
missed, so phase 6 must watch each movie in full.

Tour: phase 2 scenes reach every screen class (`docs/re/state.md`). The phase 8 warp tour must still confirm each row in a zoomed shot.
Ship name tags show on the ship zoom after picking (`ship<game>_<cell>` scenes). Lyric cards are in the `sound` scene, and the Extras list needs L1+R1 held on entering Options.

Readings are by eye from zoomed sheets. Kanji marked (?) need a second look in phase 4.

## Title and menus

| File | Japanese elements |
|---|---|
| `SUBDATA/TITLE3` | ノーマルゲーム, スペシャルゲーム, オプション; ©タツノコプロ; description fragments 悪玉パワー炸裂!! / ビギナーに / ゲームに / 慣れたら / 各種設定が / おすすめよーん / ドクロベェ暗躍 / チャレンジ! / おこのみに / 変えられます!; 選ぶ, 決定, 戻る (plain and button forms) |
| `SUBDATA/TITLE0, TITLE1, OPTI1` | logo ボカンですよ, small タイムボカンシリーズ. **Stays Japanese** per the logo ruling (D5): no official English logo exists |
| `SUBDATA/OPTI0` | ボタン設定, クレジット, サウンド, ボイス, おまけ, 1プレイヤー, パット (drawn on the controller) |
| `SUBDATA/CONFIG01` | ローリング (English NO PLAYER, 1P, 2P, L1, R1 need nothing) |
| `SUBDATA/CONFIG02` | 巨大メカ, ショット, ドクロ爆弾 in several states; 戻る, 選ぶ, 決定; large stamp 決 (3 versions) |
| `SUBDATA/SELMAIN` | 整備中 stamp (1player, 2player, STAGE, L1, R1 are English) |
| `OPTI/OMAKE1` | movie list: プロローグA; 調子に乗る その1, その2, その3; 善玉の挑戦状; 自爆決着; エンディング; プロローグB; ドクチャン激励 その1; 特訓予告; 新機種プレゼント; ドクチャン激励 その2; ドクロベエの裏切り; 善玉の直接攻撃; おしおきだベー |

Checked, no Japanese: `OPTI/M_BOTAN`, `OMAKE2`, `OMAKE3`, `SUBDATA/MARK01-03`, `TITLE2`, `TITLEBG`, `KABE256`, `DATA/SYS`, `EFECT`,
`SFXSET`, `DATA/TITLE` (English "The TimeBokan! BOKAN DESUYO"), `DATA/FACE`, `DATA/END_0-3` (the THE banner is English),
`CUT/CUT00-06`, `TAIE_*`, `LOGO.BIN`.

## In-game HUD and game over

| File | Japanese elements |
|---|---|
| `DATA/STANDARD` | ゲームオーバー; 危 (plain and in a circle). SHIELD, LEVEL, MAX, CREDIT, NO CREDIT, PUSH START are English |
| `DATA/GO_S0` | large ゲーム / オーバー, split across tiles |
| `DATA/GO_S1` | none (GAME OVER is English) |
| `DATA/GO_S2` | おわり |

## Ship name tags (bottom-left strip, y 240-256)

| File | Tag | File | Tag |
|---|---|---|---|
| `DATA/DORON` | ドロンジョカー | `DATA/BOYA` | ボヤッキーカー |
| `DATA/TONZR` | トンズラーカー | `DATA/DENDEN` | デンデンメカ |
| `DATA/ANDORO` | アンドロメダマ号 | `DATA/DOKUROBE` | アンドロメダマ号 |
| `DATA/GAIKOTU` | ガイコッツ | `DATA/RAKUDA` | タイムラクーダ |
| `DATA/SYAREKO` | シャレコーベメカ | `DATA/SYA_BAGI` | シャレコーベバギー |

## Stage cards (`SUBDATA/TAIM_*`; STAGE n labels are already English)

| File | Card |
|---|---|
| `TAIM_ST1` | 鷹は舞い戻っただコロン |
| `TAIM_ST2` | 眠らぬ森のドロンボーだよゼンダマン |
| `TAIM_ST3` | 巨大勇者と異次元ランデブー! |
| `TAIM_ST4` | ボカンと登場! 元祖タイムメカだペッチャ |
| `TAIM_ST5` | 正義の切り札! ヤッターワンFZだコロン |
| `TAIM_STF` | 驚き決戦! 影の支配者ドクロベェ |
| `TAIM_STS` | 戦場に駆ける、おだてブタだコロン! |

## In-stage sprites

| File | Element |
|---|---|
| `STAGE3/DATA/ST3_S2F` | 怒 (red kanji, lower left) |
| `STAGE3/DATA/ST3_S5D` | はらわた (on a monitor) |
| `STAGE4/BG/ST4_SB0` | イタだきまん (banner, split across tiles) |
| `STAGE7/BG/ST7_SA0` | sign 私有地・立入禁止, ドロンカンパニー (?) |

Seen in game (phase 2): the `ST4_SB0` name on a walking enemy (`sprite_itadaki`, the text is イタだきまん in red), and the
`ST7_SA0` sign on a fence at the start of the final stage (`play_stf`). **Not yet seen:** 怒 and はらわた. Dense god-mode runs
of Stage 3 found neither by template match (`tools/debug/find_sprite.py`: 怒 every 6 frames from 600 to about 4,700 and
every 40 for the whole stage, CLUT 0; はらわた every 8 frames from 29,500 to the clear, CLUT 0, and every 40 for the whole
stage, all CLUTs). A match can miss a scaled or tinted sprite, and they may need a boss state that god-mode fire does not
trigger. Phase 8 must see them, or record them as unreached with the evidence.

Developer scribbles on spare tiles, probably never shown (confirm in phase 8): `ST2_C0` アコリ (?), and non-Japanese A3,
B2, B4, 5P, 5B and 0-4 marks in stage BG files. X-boxes and square grids are padding.

## Song lyric cards (`OPTI/CARD00-16`, 8 bpp, 304x208, text baked over art)

Lyrics must be read from each image in phase 4; these are the titles.

| Card | Title | Card | Title |
|---|---|---|---|
| 00 | 天才ドロンボー | 09 | ヤットデタマンの歌 |
| 01 | ヤッターマンの歌 | 10 | 空からブタが降ってくる |
| 02 | ドロンボーのシラーケッ (?) | 11 | 逆転イッパツマン |
| 03 | ヤッターキング | 12 | 嗚呼!逆転王 |
| 04 | ドロンボーのなげき唄 | 13 | いただきマンボ |
| 05 | ゼンダマンの歌 | 14 | タイムボカン |
| 06 | ドクロベエさまに捧げる歌 | 15 | ーさんあく18年ー 君を離さない チュ★ |
| 07 | オタスケマンの歌 | 16 | 悪役ドアが開く |
| 08 | おだてブタ | | |

The art under the text has to be kept or rebuilt: **guess** that dimming a text band behind new English is the practical
route, decide in phase 5.

## Credits (`DATA/END_4, END_5, END_6`)

Dense staff-name and role tiles, translated to English per the credits ruling. Staff names need romanizing: see D3. The
strip layout (which tile rows make which roll line) comes from `S10OVER.BIN`, to read in phase 5.

## Text baked into FMV frames

| Movie | Sample | Content |
|---|---|---|
| `MOVIE00` | f0003-f0012 | opening song lyric captions (e.g. キライキライキライキライ...) at the bottom of the frame |
| `MOVIE05` | f0004 | 大勝利 banner in the scene |
| `MOVIE13` | f0002 | title card: タイムドクロベー (?) |
| `MOVIE14` | f0006 | caption 声は山本正之 |
