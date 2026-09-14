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
