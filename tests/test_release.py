"""The release script's own gates, and that --help builds nothing."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import release


def test_open_polish():
    assert release.open_polish("- [x] done\n- [ ] open\ntext\n") == ["- [ ] open"]


def test_placeholders():
    assert release.placeholders("clone .../<repo>\nplain text, 1 < 2\n") == ["<repo>"]


def test_docs_have_no_gaps():
    assert release.open_polish((ROOT / "docs/polish.md").read_text(encoding="utf-8")) == []
    assert release.placeholders((ROOT / "README.md").read_text(encoding="utf-8")) == []


def test_help_builds_nothing():
    r = subprocess.run([sys.executable, str(ROOT / "tools/release.py"), "--help"], capture_output=True, text=True)
    assert r.returncode == 0 and "--no-build" in r.stdout
