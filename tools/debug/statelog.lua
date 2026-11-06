-- Logs every change of the game's state variables (addresses: docs/re/state.md). Use with --script.
local mem = PCSX.getMemPtr()
local function u16(a) return mem[a] + mem[a + 1] * 256 end
local function u32(a) return u16(a) + u16(a + 2) * 65536 end
local VARS = { { "M", 0x8EB8C, u16 }, { "IND", 0xFC854, u16 }, { "SEL", 0x8EB98, u16 }, { "ST", 0x159E3C, u16 },
               { "TYPE", 0x159E44, u16 }, { "SYS", 0xFC9A0, u32 }, { "GAME", 0xFCA0C, u16 } }
local last = {}
L.on_frame(function(n)
  local s, ch = {}, false
  for _, v in ipairs(VARS) do
    local x = v[3](v[2])
    s[#s + 1] = string.format("%s=%X", v[1], x)
    if v[1] ~= "SYS" and last[v[1]] ~= x then ch = true end -- SYS flickers every frame
    last[v[1]] = x
  end
  if ch then L.log(n .. " " .. table.concat(s, " ")) end
end)
