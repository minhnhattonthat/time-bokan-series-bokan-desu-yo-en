# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [disc.md](disc.md) | disc layout, file types, loaders, free space, debug strings | verified except where marked |
| [state.md](state.md) | game state variables, main states, story script, title sub-states, debug tool | verified except where marked |
| [text.md](text.md) | no text encoding: why every Japanese string is a graphic or a video frame | verified by scan; draw path is a guess until phase 5 |
| [graphics.md](graphics.md) | graphics-text survey: every Japanese element and FMV caption | static sweep complete; tour check in phase 8 |
| [cells.md](cells.md) | sprite cells, GPU quads, credit strips, marker tour, font spike, width gate, FMV burn | verified except where marked |
