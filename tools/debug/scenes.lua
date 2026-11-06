-- Scene list for warp.lua: name -> function run as a coroutine from cold boot. See docs/re/state.md.
SCENES = {}
local S = SCENES

-- Skip the opening FMV: state 6 reads Start held, then loads S8OVER (title).
local function to_title()
  W.wait_m(5, 4000)
  L.press("start", 80) -- held across state 6, which samples the held mask once
  W.wait_m(7, 4000)
  W.wait_t(0x11, 1200)
  W.frames(30)
end

local function to_menu()
  to_title()
  W.tap("start")
  W.wait_t(0x22, 900)
  W.frames(60)
end

-- Options submenu cursor: 0 buttons, 1 credits (value), 2 sound, 3 voice (value), 4 extras.
-- Extras shows only with SYS & 0x300: L1+R1 held on entering Options (0x100), or the game cleared (0x200).
local function to_options(unlock)
  to_menu()
  W.tap("down"); W.frames(20)
  W.tap("down"); W.frames(20)
  W.check(W.r16(W.PICK) == 2, "menu cursor on options")
  W.tap("circle")
  if unlock then L.press("l1+r1", 240) end
  W.wait_t(0x43, 900)
  W.frames(60)
  if unlock then W.wait(L.route_done, "buttons released", 400) end
end

-- Starts a game and jumps the story script to entry `ind` before state 0x11 reads it. The script tables are in
-- docs/re/state.md. Everything after this runs the game's own code, so movies, cards and stages enter normally.
local function new_game(gametype, ind)
  to_menu()
  if gametype == 1 then W.tap("down"); W.frames(20) end
  W.check(W.r16(W.PICK) == gametype, "menu cursor on game type")
  W.tap("circle")
  W.wait_m(8, 900)
  W.w16(W.IND, ind)
  W.wait(function() return W.r16(W.M) ~= 8 end, "left state 8", 900)
  W.frames(1)
  W.check(W.r16(W.TYPE) == gametype, "game type set")
end

local function to_ship_select(gametype, ind)
  new_game(gametype, ind)
  W.wait_m(0x19, 900)
  W.frames(240)
end

local function to_stage(gametype, ind, card_only)
  to_ship_select(gametype, ind)
  W.tap("circle")
  W.wait_m(0x27, 1200)
  W.frames(170)
  W.shot("card")
  if card_only then W.done() end
  W.wait_m(0x41, 1200)
  W.frames(240)
end

S.logo = function()
  W.wait_m(1, 4000)
  W.frames(60)
  W.check(W.r16(W.M) <= 4, "logo states")
  W.done()
end

S.title = function()
  to_title()
  W.check(W.r16(W.T) == 0x11, "press-start screen")
  W.done()
end

S.menu = function()
  to_menu()
  W.frames(150)
  W.shot("normal")
  W.tap("down"); W.frames(170)
  W.shot("special")
  W.tap("down"); W.frames(170)
  W.check(W.r16(W.T) == 0x22 and W.r16(W.PICK) == 2, "main menu, options selected")
  W.done()
end

S.options = function()
  to_options(true)
  for i = 0, 4 do
    W.check(W.r16(W.OPT) == i, "options cursor " .. i)
    W.shot("opt" .. i)
    W.tap("down"); W.frames(30)
  end
  W.done()
end

S.buttons = function()
  to_options()
  W.tap("circle")
  W.wait_t(0x51, 900)
  W.frames(120)
  W.shot("buttons")
  for i = 1, 3 do W.tap("down"); W.frames(30); W.shot("buttons" .. i) end
  W.done()
end

-- Rebinding: left and right swap the row's action, so the other label strips and the decide stamp draw.
S.buttons_edit = function()
  to_options()
  W.tap("circle")
  W.wait_t(0x51, 900)
  W.frames(120)
  for row = 0, 3 do
    for i = 1, 3 do W.tap("right"); W.frames(20); W.shot(string.format("r%d_right%d", row, i)) end
    W.tap("circle"); W.frames(12); W.shot(string.format("r%d_ok", row))
    W.frames(30)
    W.tap("down"); W.frames(30)
  end
  W.tap("cross"); W.frames(20); W.shot("exit1")
  W.frames(20); W.shot("exit2")
  W.done()
end

S.sound = function()
  to_options()
  W.tap("down"); W.frames(30)
  W.tap("down"); W.frames(30)
  W.check(W.r16(W.OPT) == 2, "options cursor on sound")
  W.tap("circle")
  W.wait_t(0x71, 900)
  W.frames(180)
  W.shot("card00")
  -- Lyric cards: right loads the next one from disc.
  for i = 1, 16 do
    W.tap("right"); W.frames(150)
    W.shot(string.format("card%02d", i))
  end
  W.done()
end

local function to_extras()
  to_options(true)
  for _ = 1, 4 do W.tap("down"); W.frames(30) end
  W.check(W.r16(W.OPT) == 4, "options cursor on extras")
  W.tap("circle")
  W.wait_t(0x91, 900)
  W.frames(180)
end

S.extras = function()
  to_extras()
  W.shot("extras")
  for i = 1, 15 do W.tap("down"); W.frames(40); W.shot(string.format("row%02d", i)) end
  W.done()
end

-- The movie viewer: circle plays the row under the cursor.
S.viewer = function()
  to_extras()
  W.tap("circle")
  W.frames(600)
  W.done()
end

S.ships = function()
  to_ship_select(0, 1)
  W.shot("ship0")
  for i = 1, 8 do
    W.tap(i % 3 == 0 and "down" or "right"); W.frames(30)
    W.shot("ship" .. i)
  end
  W.check(W.r16(W.M) == 0x19, "ship select")
  W.done()
end

-- The ship's name tag shows once it is picked. Cells 0-8 row by row; `gametype` 1 has its own ships in some cells.
for g = 0, 1 do
  for n = 0, 8 do
    S[string.format("ship%d_%d", g, n)] = function()
      to_ship_select(g, 1)
      for _ = 1, n % 3 do W.tap("right"); W.frames(30) end
      for _ = 1, math.floor(n / 3) do W.tap("down"); W.frames(30) end
      W.tap("circle")
      W.wait_m(0x1A, 300)
      W.frames(60)
      W.done()
    end
  end
end

S.ships_special = function()
  to_ship_select(1, 1)
  W.check(W.r16(W.M) == 0x19, "ship select, special game")
  W.done()
end

-- Story script index of each stage: normal 1,3,5,7,9; special 1,3,5,7,9,11,13 (ST 0,1,5,2,3,4,6).
local CARDS = { st1 = { 0, 1 }, st2 = { 0, 3 }, st3 = { 0, 5 }, st4 = { 0, 7 }, st5 = { 0, 9 }, sts = { 1, 5 }, stf = { 1, 13 } }
for name, c in pairs(CARDS) do
  S["card_" .. name] = function()
    to_stage(c[1], c[2], true)
  end
  S["play_" .. name] = function()
    to_stage(c[1], c[2])
    W.check(W.r16(W.M) == 0x41, "in stage")
    W.done()
  end
end

-- Movies 1-7 run in the normal script at index movie-1 (with 5-7 past stage entries), the rest in the special script.
local MOVIES = { [1] = { 0, 0 }, [2] = { 0, 2 }, [3] = { 0, 4 }, [4] = { 0, 6 }, [5] = { 0, 8 }, [6] = { 0, 10 }, [7] = { 0, 11 },
                 [8] = { 1, 0 }, [9] = { 1, 2 }, [10] = { 1, 4 }, [11] = { 1, 6 }, [12] = { 1, 8 }, [13] = { 1, 12 },
                 [14] = { 1, 14 }, [15] = { 1, 17 } }
for n, m in pairs(MOVIES) do
  S[string.format("movie%02d", n)] = function()
    new_game(m[1], m[2])
    W.wait_m(0x30, 900)
    W.check(W.r16(W.ST) == 0x10 + n, "script entry is movie " .. n)
    W.frames(500)
    W.done()
  end
end

-- Movie 0 is the opening: unpressed, state 6 plays it before the title.
S.movie00 = function()
  W.wait_m(6, 4000)
  W.frames(600)
  W.check(W.r16(W.M) == 6, "opening movie playing")
  W.done()
end

local function to_continue(gametype, ind)
  to_stage(gametype, ind)
  W.w16(W.CRED, 3)
  W.w16(W.GAME, W.r16(W.GAME) - W.r16(W.GAME) % 0x40 + W.r16(W.GAME) % 0x10) -- clear 1P.NOW and 2P.NOW: all players out
  W.wait_m(0x51, 900)
  W.frames(60)
end

S.continue = function()
  to_continue(0, 1)
  W.done()
end

-- The continue timer ending picks GO_S<type>. Circle ticks the timer down.
local function gameover(gametype)
  to_continue(gametype, 1)
  while W.r16(W.M) == 0x51 do W.tap("circle"); W.frames(10) end
  W.wait_m(0x81, 300)
  W.frames(200)
end
S.gameover0 = function() gameover(0); W.done() end
S.gameover1 = function() gameover(1); W.done() end

-- Script entry 0x20 after the ending: state 0x80 picks GO_S2.
S.fin = function()
  new_game(0, 13)
  W.wait_m(0x81, 900)
  W.frames(200)
  W.done()
end

-- Rolls to the end; the last shots go black, so warp_all skips --smoke here and the check counts the roll instead.
S.ending = function()
  new_game(0, 12)
  W.wait_m(0x91, 1800)
  W.check(W.r16(W.OVL) == 9, "S10OVER loaded")
  local i = 0
  while W.r16(W.M) == 0x91 and i < 150 do
    W.frames(240)
    i = i + 1
    W.shot(string.format("end%03d", i))
  end
  W.check(i > 30, "ending rolled for " .. i .. " shots")
  W.done()
end

-- The danger mark on the HUD: shield nearly gone.
S.danger = function()
  to_stage(0, 1)
  W.w16(W.SHIELD1, 0)
  W.frames(30)
  W.shot("danger")
  W.check(W.r16(W.M) == 0x41 and W.r16(W.SHIELD1) == 0, "in stage on last shield")
  W.done()
end

-- Stage clear: starts the game's own clear task (TARGET.EXE 80024AC8) in a free slot of the task list, as a boss death
-- does. Rolls on into the next script entry. Slot layout: docs/re/state.md.
S.clear = function()
  to_stage(0, 1)
  local slot
  for i = 0, 15 do
    if W.r8(0x8E980 + i * 24) % 2 == 0 then slot = i; break end
  end
  W.check(slot ~= nil, "free task slot")
  for off = 0, 20, 4 do W.w32(0x8E980 + slot * 24 + off, 0) end
  W.w32(0x8E980 + slot * 24 + 4, 0x80024AC8)
  W.w16(0x8E980 + slot * 24, 1)
  W.w16(0x106BE0, 0x10) -- the task's first state waits for the player's mode to read "at rest"
  local i = 0
  while W.r16(W.M) == 0x41 and i < 40 do
    W.frames(60)
    i = i + 1
    W.shot(string.format("c%03d", i))
  end
  W.check(W.r16(W.M) ~= 0x41, "left the stage")
  W.wait_m(0x30, 900) -- the script moves on to movie 2
  W.check(W.r16(W.ST) == 0x12, "next script entry")
  W.frames(400)
  W.done()
end

-- God-mode run through a stage holding fire, for sprites only seen mid-stage. Ends at stage clear or the frame cap.
local function tour(gametype, ind)
  to_stage(gametype, ind)
  GOD = 1
  local limit = TOUR_FRAMES or 11900
  L.press("circle", limit + 100)
  local step = TOUR_STEP or 170
  local i = 0
  while W.r16(W.M) == 0x41 and i * step < limit do
    W.frames(step)
    i = i + 1
    if i * step >= (TOUR_FROM or 0) then W.shot(string.format("t%04d", i)) end
  end
  L.log(string.format("tour ended M=%X after %d shots", W.r16(W.M), i))
  W.done()
end
for name, c in pairs(CARDS) do
  S["tour_" .. name] = function() tour(c[1], c[2]) end
end

-- The red イタだきまん name on Stage 4's enemy, about 21,800 frames in with god mode and fire held.
S.sprite_itadaki = function()
  to_stage(0, 7)
  GOD = 1
  L.press("circle", 22400)
  W.frames(21600)
  for i = 1, 20 do
    W.frames(30)
    W.shot(string.format("t%04d", i))
  end
  W.check(W.r16(W.M) == 0x41, "still in stage")
  W.done()
end
