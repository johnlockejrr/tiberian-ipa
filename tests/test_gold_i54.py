"""I.5.4 gold fixtures (T1 preferred where JS differs)."""

from __future__ import annotations

import json
from pathlib import Path

from tiberian_ipa import transcribe

ROOT_FIX = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "genesis_1_1_13.json"
LOCAL_FIX = Path(__file__).resolve().parent / "fixtures" / "genesis_1_1_13.json"


def _genesis():
    path = ROOT_FIX if ROOT_FIX.is_file() else LOCAL_FIX
    return json.loads(path.read_text(encoding="utf-8"))


def test_genesis_1_1_matches_i54():
    row = _genesis()[0]
    r = transcribe(row["hebrew"])
    assert r.ipa == row["forte_lene"]


def test_genesis_verses_run():
    for row in _genesis():
        r = transcribe(row["hebrew"])
        assert r.ipa
        assert "[" not in r.ipa


def test_shalom_elohim_basic():
    assert transcribe("שָׁלוֹם", allow_unaccented=True).ipa == "ʃɔːˈloːom"
    assert transcribe("אֱלֹהִים", allow_unaccented=True).ipa == "ʔɛloːˈhiːim"
    assert transcribe("שָׁלוֹם", allow_unaccented=True).mode == "native-tiberian-basic"
