"""Furtive pataḥ never bears primary stress (postpositive Segolta / milraʿ fallback)."""

from __future__ import annotations

from havarot import Text
from tiberian_ipa import transcribe

from tests.test_havarot_syllables import TIBERIAN_SYL_OPTS


def _accented_texts(hebrew: str) -> list[str]:
    t = Text(hebrew, TIBERIAN_SYL_OPTS)
    out: list[str] = []
    for w in t.words:
        for s in w.syllables:
            if s.isAccented:
                out.append(s.text)
    return out


def test_wlc_lone_segolta_stresses_pre_furtive():
    # Gen 1:7 form: postpositive Segolta on עַ only (not MAM-doubled).
    heb = "הָרָקִיעַ֒"
    accented = _accented_texts(heb)
    assert len(accented) == 1
    assert "קִי" in accented[0] or accented[0].startswith("קִ")
    assert "עַ" not in accented[0]
    assert transcribe(heb).ipa == "hɔːʀ̟ɔːˈq̟iːjaʕ"


def test_mam_doubled_segolta_still_correct():
    heb = "הָרָקִ֒יעַ֒"
    assert transcribe(heb).ipa == "hɔːʀ̟ɔːˈq̟iːjaʕ"


def test_zaqef_and_atnah_unchanged():
    assert transcribe("לָרָקִ֔יעַ").ipa == "lɔːʀ̟ɔːˈq̟iːjaʕ"
    assert transcribe("לָרָקִ֑יעַ").ipa == "lɔːʀ̟ɔːˈq̟iːjaʕ"


def test_gen_1_7_verse_matches_expected_stress():
    heb = (
        "וַיַּ֣עַשׂ אֱלֹהִים֮ אֶת־הָרָקִיעַ֒ וַיַּבְדֵּ֗ל בֵּ֤ין הַמַּ֙יִם֙ "
        "אֲשֶׁר֙ מִתַּ֣חַת לָרָקִ֔יעַ וּבֵ֣ין הַמַּ֔יִם אֲשֶׁ֖ר מֵעַ֣ל לָרָקִ֑יעַ וַֽיְהִי־כֵֽן׃"
    )
    ipa = transcribe(heb).ipa
    assert ipa is not None
    # Stress on qiː, not on furtive jaʕ
    assert "hɔːʀ̟ɔːˈq̟iːjaʕ" in ipa
    assert "hɔːʀ̟ɔːq̟iːˈjaʕ" not in ipa


def test_unaccented_ruach_stresses_long_vowel_not_furtive():
    heb = "רוּחַ"
    accented = _accented_texts(heb)
    assert len(accented) == 1
    assert "רוּ" in accented[0] or accented[0].startswith("ר")
    assert accented[0] != "חַ"
    assert transcribe(heb, allow_unaccented=True).ipa == "ˈʀ̟uːwaħ"
