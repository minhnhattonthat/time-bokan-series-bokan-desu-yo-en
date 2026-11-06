"""Recon facts the later phases build on. ROM-dependent tests skip when the dump is absent."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import disc
import tim

BIN = ROOT / "rom" / "Time Bokan Series - Bokan desu yo (Japan) (Track 01).bin"
needs_rom = pytest.mark.skipif(not BIN.exists(), reason="needs the dump in rom/")


def make_tim(bpp_mode=0):
    """A 4x1 VRAM-unit (16x1 pixel) 4bpp TIM with one 16-colour CLUT."""
    clut = struct.pack("<I4H", 12 + 32, 0, 480, 16, 1) + struct.pack("<16H", *range(16))
    px = struct.pack("<I4H", 12 + 8, 320, 0, 4, 1) + bytes(range(8))
    return struct.pack("<II", 0x10, 8 | bpp_mode) + clut + px


def test_tim_parse_fields():
    t = tim.parse(make_tim())
    assert (t.bpp, t.px_wh, t.px_xy, t.clut_wh, t.clut_xy) == (4, (4, 1), (320, 0), (16, 1), (0, 480))
    assert t.size == len(make_tim())


def test_tim_rejects_non_tim():
    assert tim.parse(b"PS-X EXE" + bytes(32)) is None
    assert tim.parse(make_tim()[:-1]) is None  # truncated pixel block


def test_form1_seal_keeps_a_clean_sector():
    """EDC/ECC of an all-zero form 1 sector are all zero, so sealing must not change it."""
    s = bytearray(disc.SECTOR)
    disc.form1_seal(s)
    assert bytes(s) == bytes(disc.SECTOR)


@needs_rom
def test_disc_layout():
    d = disc.Disc(str(BIN))
    assert d.files["/SYSTEM.CNF"].lba == 23
    assert d.read("/SYSTEM.CNF").startswith(b"BOOT = cdrom:\\SLPS_012.11;1")
    assert d.read("/SUBDATA/TITLE3.BIN")[:4] == b"\x10\0\0\0"
    assert tim.parse(d.read("/OPTI/CARD00.BIN")).bpp == 8


@needs_rom
def test_form1_seal_reproduces_real_sectors():
    d = disc.Disc(str(BIN))
    for lba in list(range(16, 60)) + [d.files["/TARGET.EXE"].lba]:
        s = d.raw(lba)
        assert not s[disc.SUB + 2] & disc.FORM2
        t = bytearray(s)
        disc.form1_seal(t)
        assert bytes(t) == s, lba
