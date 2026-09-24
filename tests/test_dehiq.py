"""Deḥiq (Khan §I.2.8.1.2): half-long final lax vowel + following gemination."""

from __future__ import annotations

from tiberian_ipa import transcribe


def test_gen_1_11_oseh_peri_dehiq():
    # Conjunctive mahpakh; no maqqef — must still compress + geminate.
    heb = "עֹ֤שֶׂה פְּרִי֙"
    assert transcribe(heb).ipa == "ˈʕoːsɛˑ ppʰaˈʀ̟iː"


def test_gen_1_11_earlier_peri_not_dehiq():
    # Earlier פְּרִי after עֵץ is ordinary lene, not deḥiq.
    heb = "עֵ֣ץ פְּרִ֞י עֹ֤שֶׂה פְּרִי֙"
    ipa = transcribe(heb).ipa
    assert ipa is not None
    assert "pʰaˈʀ̟iː ˈʕoːsɛˑ ppʰaˈʀ̟iː" in ipa


def test_gen_1_12_oseh_peri_with_conjunctive():
    # BHS-style: merkha (not only maqqef).
    heb = "עֹ֥שֶׂה פְּרִ֛י"
    assert transcribe(heb).ipa == "ˈʕoːsɛˑ ppʰaˈʀ̟iː"


def test_gen_1_12_with_maqqef():
    heb = "עֹֽשֶׂה־פְּרִ֛י"
    ipa = transcribe(heb).ipa
    assert ipa is not None
    # Half-long + gemination; maqqef may remain as '-' in the schema.
    assert "ʕoːsɛˑ" in ipa
    assert "ppʰaˈʀ̟iː" in ipa
    assert "ʕoːsɛː" not in ipa


def test_classic_dehiq_deut_31_28():
    heb = "וְאָעִ֣ידָה בָּ֔ם"
    assert transcribe(heb).ipa == "vɔʔɔːˈʕiːðɔˑ ˈbbɔːɔm"


def test_eretz_kenaan_dehiq():
    heb = "אַ֣רְצָה כְּנַ֔עַן"
    ipa = transcribe(heb).ipa
    assert ipa is not None
    assert "ɔˑ" in ipa or "ʔɔˑ" in ipa or "sˁɔˑ" in ipa
    assert "kkʰ" in ipa or "kʰkʰ" in ipa or ipa.count("kʰ") >= 1
    # Geminate kaf after deḥiq
    assert "ˈkkʰ" in ipa or "kkʰə" in ipa or "kkʰa" in ipa or "kkʰɛ" in ipa or "kkʰɔ" in ipa or "kkʰ" in ipa


def test_tense_final_vowel_no_dehiq():
    # Final ḥireq (tense) — no compression / no extra gemination from deḥiq.
    heb = "בָחַ֙רְתִּי ב֥וֹ"
    ipa = transcribe(heb).ipa
    assert ipa is not None
    assert "iˑ" not in ipa
    # Following bet is fricative (no deḥiq dagesh in this form)
    assert "ˈvoː" in ipa or ipa.endswith("voː")


def test_gaya_on_final_blocks_dehiq():
    # Gaʿya on final qameṣ blocks compression (Khan §I.2.8.1.2).
    heb = "וְעָ֤שָֽׂה פֶ֙סַח֙"
    ipa = transcribe(heb).ipa
    assert ipa is not None
    # Final vowel of ʿasa keeps full length (not half-long).
    assert "ɔˑ p" not in ipa and "ɔˑ pp" not in ipa
