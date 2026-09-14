"""Syllable structure matches JS oracle dumps."""

from __future__ import annotations

import json
from pathlib import Path

from havarot import DEFAULT_SYL_OPTS, Text

ORACLE = Path(__file__).resolve().parent / "fixtures" / "js_oracle.json"

# Match docs/tiberian.ts syl opts (used by IPA path)
TIBERIAN_SYL_OPTS = {
    **DEFAULT_SYL_OPTS,
    "allowNoNiqqud": False,
    "article": False,
    "holemHaser": "remove",
    "longVowels": False,
    "qametsQatan": True,
    "shevaAfterMeteg": False,
    "shevaWithMeteg": True,
    "sqnmlvy": False,
    "strict": True,
    "wawShureq": False,
}


def test_syllables_match_oracle():
    data = json.loads(ORACLE.read_text(encoding="utf-8"))
    for name, row in data.items():
        t = Text(row["hebrew"], TIBERIAN_SYL_OPTS)
        got = [
            {
                "text": w.text,
                "syls": [
                    {
                        "text": s.text,
                        "isClosed": s.isClosed,
                        "isAccented": s.isAccented,
                    }
                    for s in w.syllables
                ],
            }
            for w in t.words
        ]
        assert len(got) == len(row["syllables"]), name
        for gw, ew in zip(got, row["syllables"]):
            assert len(gw["syls"]) == len(ew["syls"]), f"{name} {ew.get('text')}"
            for gs, es in zip(gw["syls"], ew["syls"]):
                assert gs["text"] == es["text"], f"{name} syl text {gs} vs {es}"
                assert gs["isClosed"] == es["isClosed"], f"{name} {gs['text']} closed"
                assert gs["isAccented"] == es["isAccented"], f"{name} {gs['text']} accent"
