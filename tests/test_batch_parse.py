"""batch_transcribe verse parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "batch_transcribe.py"


def _load():
    spec = importlib.util.spec_from_file_location("batch_transcribe", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parse_genesis_style():
    parse_verses = _load().parse_verses
    sample = (
        "1 בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים׃ 2 וְהָאָ֗רֶץ הָיְתָ֥ה תֹ֙הוּ֙׃ {פ}\n"
        "3 וַיֹּ֥אמֶר אֱלֹהִ֖ים׃"
    )
    verses = parse_verses(sample)
    assert [n for n, _ in verses] == ["1", "2", "3"]
    assert "בְּרֵאשִׁ֖ית" in verses[0][1]
    assert "{פ}" not in verses[1][1]


def test_clean_hebrew_strips_html_keeps_qere_text():
    clean = _load().clean_hebrew
    # Multi-word qere marked with <i>; Hebrew inside must survive.
    raw = "<i>מַה</i>־<i>זֶּ֣ה</i> בְיָדֶ֔ךָ"
    out = clean(raw)
    assert "<" not in out and ">" not in out
    assert "מַה" in out and "זֶּ֣ה" in out


def test_clean_hebrew_strips_verse_notes_and_puncta():
    clean = _load().clean_hebrew
    raw = "<i>[8:1]</i> וַיֹּ֤אמֶר יְהוָה֙ וַׄיִּׄשָּׁׄקֵ֑ׄהׄוּׄ"
    out = clean(raw)
    assert "[8:1]" not in out
    assert "8:1" not in out
    assert "\u05c4" not in out
    assert "וַיֹּ֤אמֶר" in out
