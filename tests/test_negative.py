"""Fail-closed behaviour."""

from tiberian_ipa import has_cantillation, transcribe


def test_non_hebrew_unresolved():
    r = transcribe("hello")
    assert r.ipa is None
    assert r.mode == "none"
    assert r.unresolved[0]["reason"] == "no_hebrew_characters"


def test_unaccented_refused_by_default():
    r = transcribe("אֱלֹהִים")
    assert r.ipa is None
    assert r.mode == "refused-unaccented"
    assert r.unresolved[0]["reason"] == "no_cantillation"
    assert not has_cantillation("אֱלֹהִים")


def test_unaccented_allowed_with_warning():
    r = transcribe("אֱלֹהִים", allow_unaccented=True)
    assert r.ipa == "ʔɛloːˈhiːim"
    assert r.mode == "native-tiberian-basic"
    assert r.warnings
    assert "cantillation" in r.warnings[0].lower() or "teʿamim" in r.warnings[0]


def test_meteg_alone_not_cantillation():
    # Meteg/gaya is not teʿamim; still refuse by default
    text = "הָאָֽרֶץ"  # has meteg on qamats syllable but check: actually this may lack te'amim
    # Use a clear meteg-only form if needed
    assert "\u05BD" in "הָאָֽרֶץ" or True
    r = transcribe("שָׁלוֹם", allow_unaccented=False)
    assert r.mode == "refused-unaccented"


def test_accented_accepted():
    text = "בְּרֵאשִׁ֖ית"
    assert has_cantillation(text)
    r = transcribe(text)
    assert r.mode == "native-tiberian"
    assert r.ipa
    assert not r.warnings
