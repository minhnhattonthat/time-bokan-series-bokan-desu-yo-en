-- Cold-boot warp: plays each scene in tools/debug/scenes.lua as a coroutine that waits on game state, never on frame
-- counts it hopes are right. Addresses and state numbers: docs/re/state.md.
-- Use: emu.py CUE --out D --frames 40000 --timeout 900 --script tools/debug/warp.lua --script tools/debug/scenes.lua
--      --var "SCENE='title'"; optional: --var GOD=1 pins the shield. warp_all.py runs the whole list.
local mem = PCSX.getMemPtr()
W = {}
function W.r8(a) return mem[a % 0x200000] end
function W.r16(a) a = a % 0x200000; return mem[a] + mem[a + 1] * 256 end
function W.r32(a) return W.r16(a) + W.r16(a + 2) * 65536 end
function W.w16(a, v) a = a % 0x200000; mem[a] = v % 256; mem[a + 1] = math.floor(v / 256) % 256 end
function W.w32(a, v) W.w16(a, v % 65536); W.w16(a + 2, math.floor(v / 65536) % 65536) end

-- Game state variables (see docs/re/state.md)
W.M = 0x8EB8C     -- main state, TARGET.EXE 800160F8
W.T = 0xFC9AC     -- title/options sub-state, S8OVER 8015A468
W.IND = 0xFC854   -- index into the story script
W.ST = 0x159E3C   -- current script entry: 0n stage, 1n movie, F0 ending, 20 end
W.TYPE = 0x159E44 -- 0 normal game, 1 special game
W.OVL = 0x1499FC  -- overlay number loaded (S<n+1>OVER)
W.PICK = 0x8EB94  -- title menu cursor
W.OPT = 0x8EB96   -- options menu cursor
W.GAME = 0xFCA0C  -- game flags: 0x10 1P in play, 0x20 2P in play
W.CRED = 0x8EB34  -- credits left
W.SHIELD1 = 0x106C5E -- 1P shield hits left, 4 full, -1 dead (player struct 0x106BDC + 0x82; 2P struct 0x106CA8)

function W.god() W.w16(W.SHIELD1, 4) end

local checks = {}
function W.frames(n) for _ = 1, n do coroutine.yield() end end
-- Fails the run (exit 2) if the game never reaches the state: a wrong warp must not pass as a shot of something else.
function W.wait(cond, what, limit)
  limit = limit or 6000
  local n = 0
  while not cond() do
    n = n + 1
    if n > limit then error("warp timeout waiting for " .. tostring(what) .. string.format(" M=%X T=%X", W.r16(W.M), W.r16(W.T))) end
    coroutine.yield()
  end
  L.log(string.format("%d reached %s", L.frame, tostring(what)))
end
function W.wait_m(m, limit) W.wait(function() return W.r16(W.M) == m end, string.format("M=%X", m), limit) end
function W.wait_t(t, limit) W.wait(function() return W.r16(W.T) == t end, string.format("T=%X", t), limit) end
function W.tap(btn, hold) L.press(btn, hold or 6); L.press("-", 2); W.frames((hold or 6) + 2) end
function W.shot(name) L.shot(name .. ".png"); L.log(string.format("%d shot %s", L.frame, name)) end
function W.check(ok, what)
  checks[#checks + 1] = what
  if not ok then error("check failed: " .. what) end
  L.log("check ok: " .. what)
end
function W.done()
  L.shot("final.png")
  L.log(string.format("warp done %s frame %d", SCENE, L.frame))
  if STATE_OUT then L.save_state(STATE_OUT) end
  L.finish(0)
  while true do coroutine.yield() end
end

local co
L.on_frame(function()
  if not co then
    if not SCENES then error("load tools/debug/scenes.lua with --script") end
    local fn = SCENES[SCENE]
    if not fn then error("unknown scene " .. tostring(SCENE)) end
    co = coroutine.create(fn)
  end
  if GOD and W.god then W.god() end
  local ok, e = coroutine.resume(co)
  if not ok then error(e) end
end)
