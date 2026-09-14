"""Parity: native IPA == JS Tiberian schema oracle."""

from __future__ import annotations

import json
from pathlib import Path

from tiberian_ipa import transcribe

ORACLE = Path(__file__).resolve().parent / "fixtures" / "js_oracle.json"


def test_oracle_ipa_cases():
    data = json.loads(ORACLE.read_text(encoding="utf-8"))
    for name, row in data.items():
        from tiberian_ipa import has_cantillation

        allow = not has_cantillation(row["hebrew"])
        r = transcribe(row["hebrew"], allow_unaccented=allow)
        if allow:
            assert r.mode == "native-tiberian-basic", name
            assert r.warnings
        else:
            assert r.mode == "native-tiberian", name
        assert r.ipa == row["ipa"], f"{name}: {r.ipa!r} != {row['ipa']!r}"


def test_user_verse_locked():
    text = "מִֽי־פָקַ֣ד עָלָ֣יו אָ֑רְצָה וּמִ֥י שָׂ֝֗ם תֵּבֵ֥ל כֻּלָּֽהּ׃"
    expected = "ˌmiˑ-ppʰɔːˈq̟aːað ʕɔːˈlɔːɔw ˈʔɔːɔʀ̟sˁɔː wuˈmiː ˈsɔːɔm tʰeːˈveːel kʰulˈlɔːɔh"
    assert transcribe(text).ipa == expected
