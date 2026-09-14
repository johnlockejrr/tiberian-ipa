"""Faithful Python port of docs/tiberian.ts (Tiberian IPA schema)."""

from __future__ import annotations

import re
from typing import Any

from hebtrans.schema import Schema

# ---------------------------------------------------------------------------
# Helpers for HEBREW str | Pattern replacements (JS String.replace parity)
# ---------------------------------------------------------------------------


def _sub(text: str, heb: Any, repl: str) -> str:
    if isinstance(heb, re.Pattern):
        return heb.sub(repl, text, count=1)
    return text.replace(str(heb), repl, 1)


def _heb_source(heb: Any) -> str:
    if isinstance(heb, re.Pattern):
        return heb.pattern
    return str(heb)


def _sheva_syllable_match(text: str) -> bool:
    """Emulate JS lookbehind: sheva not preceded by full vowel or shureq."""
    for m in re.finditer(r"\u05B0", text):
        before = text[: m.start()]
        if not re.search(r"[\u05B4-\u05BB\u05C7]|\u05D5\u05BC", before):
            return True
    return False


class _ShevaHebrew:
    """Matcher standing in for /(?<!.*([...]).*)\\u05B0/u (variable lookbehind)."""

    pattern = r"\u05B0"

    def search(self, text: str) -> re.Match[str] | bool | None:
        return True if _sheva_syllable_match(text) else None


# ---------------------------------------------------------------------------
# ADDITIONAL_FEATURES callbacks
# ---------------------------------------------------------------------------


def _yod_with_dagesh(cluster: Any, hebrew: Any, schema: Schema | None = None) -> str:
    return _sub(cluster.text, hebrew, "ɟɟ")


def _digraph_dagesh_chazaq(
    cluster: Any,
    heb: Any,
    schema: Schema,
    digraph_key: str,
    second_char: str,
    *,
    prev_coda_mode: str = "includes",
) -> str:
    digraph = schema.get(digraph_key) or ""
    no_second = digraph.replace(second_char, "") if digraph else ""

    prev_word = None
    if cluster.syllable and cluster.syllable.word and cluster.syllable.word.prev:
        prev_word = cluster.syllable.word.prev.value
    if (
        prev_word is not None
        and getattr(prev_word, "isInConstruct", False)
        and prev_word.syllables
        and not prev_word.syllables[-1].isClosed
    ):
        return _sub(cluster.text, heb, f"{no_second}{digraph}")

    if not cluster.prev or (
        cluster.prev.value is not None and getattr(cluster.prev.value, "isNotHebrew", False)
    ):
        return cluster.text

    prev_coda = None
    if cluster.syllable and cluster.syllable.prev and cluster.syllable.prev.value:
        prev_coda = cluster.syllable.prev.value.codaWithGemination

    dagesh = "\u05BC"
    no_dagesh_hebrew = _heb_source(heb).replace(dagesh, "")
    if prev_coda_mode == "regex":
        if not re.search(no_dagesh_hebrew, prev_coda or "", re.UNICODE):
            return cluster.text
    else:
        if not prev_coda or no_dagesh_hebrew not in prev_coda:
            return cluster.text

    return _sub(cluster.text, heb, f"{no_second}{digraph}")


def _tav_with_dagesh(cluster: Any, heb: Any, schema: Schema) -> str:
    return _digraph_dagesh_chazaq(cluster, heb, schema, "TAV_DAGESH", "ʰ")


def _pe_with_dagesh(cluster: Any, heb: Any, schema: Schema) -> str:
    return _digraph_dagesh_chazaq(cluster, heb, schema, "PE_DAGESH", "ʰ")


def _kaf_with_dagesh(cluster: Any, heb: Any, schema: Schema) -> str:
    return _digraph_dagesh_chazaq(
        cluster, heb, schema, "KAF_DAGESH", "ʰ", prev_coda_mode="regex"
    )


def _tet_with_dagesh(cluster: Any, heb: Any, schema: Schema) -> str:
    return _digraph_dagesh_chazaq(cluster, heb, schema, "TET", "ˁ")


def _tsadi_with_dagesh(cluster: Any, heb: Any, schema: Schema) -> str:
    return _digraph_dagesh_chazaq(cluster, heb, schema, "TSADI", "ˁ")


def _quiescent_alef(cluster: Any, heb: Any, schema: Schema | None = None) -> str:
    nxt = cluster.next.value if cluster.next else None
    if (nxt is not None and getattr(nxt, "isShureq", False)) or not cluster.prev:
        return cluster.text
    return _sub(cluster.text, heb, "")


def _alef_with_dagesh(cluster: Any, heb: Any = None, schema: Schema | None = None) -> str:
    return cluster.text.replace("\u05BC", "")


def _pharyngealized_resh(syllable: Any, heb: Any = None, schema: Schema | None = None) -> str:
    alveolars = re.compile(r"[דזצתטסלנ]|שׂ")
    clusters = [c for c in syllable.clusters if "ר" in c.text]
    if not clusters:
        return syllable.text
    cluster = clusters[0]
    prev_cluster = cluster.prev.value if cluster.prev else None
    current_syllable = cluster.syllable
    if current_syllable:
        onset, _, coda = current_syllable.structure(True)
    else:
        onset, coda = "", ""

    if prev_cluster and alveolars.search(prev_cluster.text):
        if "ר" in onset and not prev_cluster.hasVowel:
            return syllable.text.replace("ר", "rˁ")
        if "ר" in coda and prev_cluster.hasVowel:
            return syllable.text.replace("ר", "rˁ")

    next_cluster = cluster.next.value if cluster.next else None
    lamed_and_nun = re.compile(r"[לנן]")
    if next_cluster and lamed_and_nun.search(next_cluster.text):
        if "ר" in onset and not cluster.hasVowel:
            return syllable.text.replace("ר", "rˁ")
        if "ר" in coda and cluster.hasSheva:
            return syllable.text.replace("ר", "rˁ")

    return syllable.text


def _furtive_patach(
    syllable: Any,
    _hebrew: Any,
    schema: Schema,
    consonant_key: str,
) -> str:
    prev_text = ""
    if syllable.prev and syllable.prev.value:
        prev_text = syllable.prev.value.text or ""
    if syllable.isFinal and prev_text:
        if re.search(r"[יו]", prev_text):
            glide = "w" if re.search(r"ו", prev_text) else "j"
            return glide + schema["PATAH"] + schema[consonant_key]
        return schema["PATAH"] + schema[consonant_key]
    return syllable.text


def _furtive_het(syllable: Any, hebrew: Any, schema: Schema) -> str:
    return _furtive_patach(syllable, hebrew, schema, "HET")


def _furtive_ayin(syllable: Any, hebrew: Any, schema: Schema) -> str:
    return _furtive_patach(syllable, hebrew, schema, "AYIN")


def _furtive_he(syllable: Any, hebrew: Any, schema: Schema) -> str:
    return _furtive_patach(syllable, hebrew, schema, "HE")


def _word_initial_shureq(syllable: Any, _: Any, schema: Schema) -> str:
    if not syllable.prev and syllable.clusters and syllable.clusters[0].isShureq:
        text = syllable.text
        has_meteg = any(c.hasMeteg for c in syllable.clusters)
        secondary_accent = "ˌ" if has_meteg else ""
        half_length = "ˑ" if has_meteg else ""
        return text.replace("וּ", f"{secondary_accent}wu{half_length}")

    if syllable.isAccented and syllable.isClosed:
        no_length = schema["SHUREQ"].replace("ː", "")
        return syllable.text.replace("וּ", schema["SHUREQ"] + no_length)

    return syllable.text


def _full_vowel_syllable(syllable: Any, _: Any, schema: Schema) -> str:
    vowel_names = syllable.vowelNames
    vowels = syllable.vowels
    vowel_name = vowel_names[0] if vowel_names else None
    vowel = vowels[0] if vowels else None

    if not vowel or not vowel_name:
        return syllable.text

    if vowel_name == "SHEVA":
        raise ValueError(f"Syllable {syllable.text} has a sheva as vowel, should not have matched")

    if any(c.hasHalfVowel for c in syllable.clusters):
        raise ValueError(f"Syllable {syllable.text} has a hataf as vowel, should not have matched")

    onset, _nucleus, coda = syllable.structure(True)

    def determine_patach_realization(vowel_char: str) -> str:
        if vowel_name not in ("PATAH", "HATAF_PATAH"):
            return vowel_char
        pharyngealized = re.compile(r"rˁ|ט|צ|ץ")
        if pharyngealized.search(onset) or pharyngealized.search(coda):
            return "ɑ"
        next_syllable = syllable.next.value if syllable.next else None
        next_onset = next_syllable.onset if next_syllable else None
        alveolars = re.compile(r"[דזצתטסלנ]|שׂ")
        if next_onset == "ר" and alveolars.search(coda):
            return "ɑ"
        return vowel_char

    no_mater_text = "".join(c.text for c in syllable.clusters if not c.isMater)
    no_mater_text = re.sub(
        r"([\u05B5\u05B6\u05B9].{0,1})\u05D4(?!\u05BC)",
        r"\1",
        no_mater_text,
        flags=re.UNICODE,
    )

    has_maters = any(c.isMater for c in syllable.clusters)
    length_marker = "ː"
    half_length_marker = "ˑ"

    has_meteg = any(c.hasMeteg for c in syllable.clusters)
    if has_meteg:
        has_long_vowel = any(c.hasLongVowel for c in syllable.clusters)
        first_consonant = no_mater_text[0] if no_mater_text else ""
        realized = determine_patach_realization(vowel)
        marker = length_marker if has_long_vowel else half_length_marker
        return (
            no_mater_text.replace(first_consonant, f"ˌ{first_consonant}", 1).replace(
                vowel, f"{realized}{marker}", 1
            )
        )

    is_closed = syllable.isClosed
    is_accented = syllable.isAccented

    if is_accented and is_closed:
        sep = schema.get("SYLLABLE_SEPARATOR") or ""
        realized = determine_patach_realization(vowel)
        return no_mater_text.replace(
            vowel, f"{realized}{length_marker}{sep}{realized}", 1
        )

    longer_vowels = ("HOLAM", "TSERE", "QAMATS")
    if (
        not is_accented
        and is_closed
        and not syllable.isFinal
        and vowel_name in longer_vowels
    ):
        sep = schema.get("SYLLABLE_SEPARATOR") or ""
        realized = determine_patach_realization(vowel)
        return no_mater_text.replace(
            vowel, f"{realized}{length_marker}{sep}{realized}", 1
        )

    if is_accented or (not is_accented and not is_closed):
        return no_mater_text.replace(
            vowel, f"{determine_patach_realization(vowel)}{length_marker}", 1
        )

    if not has_maters and not is_closed and not is_accented:
        return no_mater_text.replace(vowel, determine_patach_realization(vowel), 1)

    return syllable.text.replace(vowel, determine_patach_realization(vowel), 1)


def _hataf_vowel_syllable(syllable: Any, _: Any = None, schema: Schema | None = None) -> str:
    vowel_names = syllable.vowelNames
    vowels = syllable.vowels
    vowel_name = vowel_names[0] if vowel_names else None
    vowel = vowels[0] if vowels else None

    if not vowel or not vowel_name:
        return syllable.text

    if vowel_name == "SHEVA":
        raise ValueError(f"Syllable {syllable.text} has a sheva as vowel, should not have matched")

    if any(c.hasShortVowel or c.hasLongVowel for c in syllable.clusters):
        raise ValueError(
            f"Syllable {syllable.text} does not have a hataf vowel, should not have matched"
        )

    onset, _nucleus, coda = syllable.structure(True)

    def determine_patach_realization(vowel_char: str) -> str:
        if vowel_name != "HATAF_PATAH":
            return vowel_char
        pharyngealized = re.compile(r"rˁ|ט|צ|ץ")
        if pharyngealized.search(onset) or pharyngealized.search(coda):
            return "ɑ"
        next_syllable = syllable.next.value if syllable.next else None
        next_onset = next_syllable.onset if next_syllable else None
        alveolars = re.compile(r"[דזצתטסלנ]|שׂ")
        if next_onset == "ר" and alveolars.search(coda):
            return "ɑ"
        if next_onset and re.search(r"[צץט]", next_onset):
            return "ɑ"
        return vowel_char

    return syllable.text.replace(vowel, determine_patach_realization(vowel), 1)


def _syllable_with_sheva(syllable: Any, _hebrew: Any, schema: Schema) -> str:
    # Extra guard when HEBREW matcher is broadened
    base = re.sub(r"[\u0591-\u05AF\u05BD\u05BF]", "", syllable.text)
    if not _sheva_syllable_match(base):
        return syllable.text

    next_syllable = syllable.next.value if syllable.next else None
    if not next_syllable:
        return syllable.text

    next_syl_first = next_syllable.clusters[0].text if next_syllable.clusters else ""
    if not next_syl_first:
        return syllable.text

    onset, _, coda = syllable.structure(True)

    def is_back_unrounded() -> bool:
        pharyngealized = re.compile(r"rˁ|ט|צ|ץ")
        if pharyngealized.search(onset) or pharyngealized.search(coda):
            return True
        ns = syllable.next.value if syllable.next else None
        if not ns:
            return False
        if pharyngealized.search(ns.onset or ""):
            return True
        return False

    def transliterate_sheva_as_vowel(vowel: str) -> str:
        has_meteg = any(c.hasMeteg for c in syllable.clusters)
        secondary = "ˌ" if has_meteg else ""
        half = "ˑ" if has_meteg else ""
        new_vowel = vowel.replace("ː", "") + half
        return secondary + re.sub(r"\u05B0", new_vowel, syllable.text, count=1)

    if "י" in next_syl_first:
        return transliterate_sheva_as_vowel("ɑ" if is_back_unrounded() else schema["HIRIQ"])

    if not re.search(r"[אהחע]", next_syl_first):
        return transliterate_sheva_as_vowel("ɑ" if is_back_unrounded() else schema["PATAH"])

    next_vowel = next_syllable.vowelNames[0] if next_syllable.vowelNames else None
    if not next_vowel:
        raise ValueError(
            f"Syllable {syllable.text} has a sheva as a vowel, but the next syllable "
            f"{next_syl_first} does not have a vowel"
        )
    if next_vowel == "SHEVA":
        raise ValueError(
            f"Syllable {syllable.text} has a sheva as a vowel, but the next syllable "
            f"{next_syl_first} also has a sheva as a vowel"
        )
    return transliterate_sheva_as_vowel(schema[next_vowel])


def _jerusalem(syl: Any, heb: Any, schema: Schema) -> str:
    prev = syl.prev.value if syl.prev else None
    if (
        prev
        and not prev.isClosed
        and not prev.hasVowelName("QAMATS")
        and not prev.hasVowelName("PATAH")
        and prev.onset != "ל"
    ):
        return syl.text
    return _sub(syl.text, heb, f"{schema['YOD']}{schema['HIRIQ']}{schema['FINAL_MEM']}")


def _issachar(word: Any, heb: Any, schema: Schema | None = None) -> str:
    taamim = re.compile(r"[\u0590-\u05AF\u05BD\u05BF]", re.UNICODE)
    text = taamim.sub("", word.text)
    match = _as_match(text, heb)
    vav = ""
    if match is not None and match.lastindex and match.lastindex >= 1:
        vav = match.group(1) or ""
    return f"{vav}jissɔːˈχɔːɔʀ̟"


def _as_match(text: str, heb: Any) -> re.Match[str] | None:
    if isinstance(heb, re.Pattern):
        return heb.search(text)
    return re.search(str(heb), text, re.UNICODE)


def _interrogative_construct(word: Any, heb: Any, schema: Schema) -> str:
    return _sub(
        word.text,
        heb,
        schema["MEM"] + schema["PATAH"] + schema["HE"] + schema["MAQAF"],
    )


def _on_complete(res: str, *_args: Any) -> str:
    return res.replace("  ", " ")


def _ketiv_hi_hi(heb: str, inp: Any) -> str:
    if isinstance(inp, re.Pattern):
        return inp.sub("הִיא", heb, count=1)
    return heb.replace(str(inp), "הִיא", 1)


# ---------------------------------------------------------------------------
# Schema inventory
# ---------------------------------------------------------------------------

_ADDITIONAL_FEATURES: list[dict[str, Any]] = [
    {
        "TITLE": "Yod with Dagesh",
        "DESCRIPTION": "Transliterate a yod with a dagesh as a palatal plosive (ɟɟ).",
        "FEATURE": "cluster",
        "HEBREW": "\u05D9\u05BC",
        "TRANSLITERATION": _yod_with_dagesh,
    },
    {
        "TITLE": "Tav with Dagesh",
        "DESCRIPTION": "The schema value is a digraph which needs to be handled differently depending on context.",
        "FEATURE": "cluster",
        "HEBREW": re.compile(r"תּ", re.UNICODE),
        "TRANSLITERATION": _tav_with_dagesh,
    },
    {
        "TITLE": "Pe with Dagesh",
        "DESCRIPTION": "The schema value is a digraph which needs to be handled differently depending on context.",
        "FEATURE": "cluster",
        "HEBREW": re.compile(r"פ", re.UNICODE),
        "TRANSLITERATION": _pe_with_dagesh,
    },
    {
        "TITLE": "Kaf with Dagesh",
        "DESCRIPTION": "The schema value is a digraph which needs to be handled differently depending on context.",
        "FEATURE": "cluster",
        "HEBREW": re.compile(r"כּ|ךּ", re.UNICODE),
        "TRANSLITERATION": _kaf_with_dagesh,
    },
    {
        "TITLE": "Tet with Dagesh",
        "DESCRIPTION": "The schema value is a digraph which needs to be handled differently depending on context.",
        "FEATURE": "cluster",
        "HEBREW": re.compile(r"טּ", re.UNICODE),
        "TRANSLITERATION": _tet_with_dagesh,
    },
    {
        "TITLE": "Tsadi with Dagesh",
        "DESCRIPTION": "The schema value is a digraph which needs to be handled differently depending on context.",
        "FEATURE": "cluster",
        "HEBREW": re.compile(r"צּ", re.UNICODE),
        "TRANSLITERATION": _tsadi_with_dagesh,
    },
    {
        "TITLE": "Quiescent Alef",
        "DESCRIPTION": "Transliterate an alef with no vowel as quiesced.",
        "FEATURE": "cluster",
        "HEBREW": re.compile(r"\u05D0(?![\u05B1-\u05BB\u05C7])", re.UNICODE),
        "TRANSLITERATION": _quiescent_alef,
    },
    {
        "TITLE": "Alef with Dagesh",
        "DESCRIPTION": "Remove the dagesh from an alef.",
        "FEATURE": "cluster",
        "HEBREW": "\u05D0\u05BC",
        "TRANSLITERATION": _alef_with_dagesh,
    },
    {
        "TITLE": "Pharyngealized Resh",
        "DESCRIPTION": "Transliterate a resh as pharyngealized depending on context with surrounding alveolars and other consonants.",
        "FEATURE": "syllable",
        "HEBREW": re.compile(r"ר", re.UNICODE),
        "TRANSLITERATION": _pharyngealized_resh,
    },
    {
        "TITLE": "Furtive Patach before Het",
        "DESCRIPTION": "Transliterate a furtive patach before a het when preceded by vav or yod.",
        "FEATURE": "syllable",
        "HEBREW": "ח\u05B7\u05C3?$",
        "PASS_THROUGH": True,
        "TRANSLITERATION": _furtive_het,
    },
    {
        "TITLE": "Furtive Patach before Ayin",
        "DESCRIPTION": "Transliterate a furtive patach before an ayin when preceded by vav or yod.",
        "FEATURE": "syllable",
        "HEBREW": "ע\u05B7\u05C3?$",
        "PASS_THROUGH": True,
        "TRANSLITERATION": _furtive_ayin,
    },
    {
        "TITLE": "Furtive Patach before He",
        "DESCRIPTION": "Transliterate a furtive patach before a he when preceded by vav or yod.",
        "FEATURE": "syllable",
        "HEBREW": "ה\u05BC\u05B7\u05C3?$",
        "PASS_THROUGH": True,
        "TRANSLITERATION": _furtive_he,
    },
    {
        "TITLE": "Word initial shureq",
        "DESCRIPTION": "Transliterate a shureq at the beginning of a word as wuː.",
        "FEATURE": "syllable",
        "HEBREW": re.compile(r"וּ(?![\u05B4-\u05BB])", re.UNICODE),
        "TRANSLITERATION": _word_initial_shureq,
    },
    {
        "TITLE": "Full Vowel Syllable",
        "DESCRIPTION": "Matches any syllable that has a full vowel character (i.e. not sheva) and determines the appropriate transliteration for length.",
        "FEATURE": "syllable",
        "HEBREW": re.compile(r"[\u05B4-\u05BB\u05C7]", re.UNICODE),
        "TRANSLITERATION": _full_vowel_syllable,
    },
    {
        "TITLE": "Hataf Vowel Syllable",
        "DESCRIPTION": "Matches any syllable that has a hataf vowel character and determines the appropriate transliteration.",
        "FEATURE": "syllable",
        "HEBREW": re.compile(r"[\u05B1-\u05B3]", re.UNICODE),
        "TRANSLITERATION": _hataf_vowel_syllable,
    },
    {
        "TITLE": "Syllable with Sheva",
        "DESCRIPTION": "Matches any syllable that contains a sheva that is not preceded by a full vowel character or shureq and determines the appropriate transliteration.",
        "FEATURE": "syllable",
        "HEBREW": _ShevaHebrew(),
        "TRANSLITERATION": _syllable_with_sheva,
    },
    {
        "TITLE": "Jerusalem",
        "DESCRIPTION": "Transliterate instances of Jerusalem spelled without a yod to match the later spelling convention.",
        "FEATURE": "syllable",
        "HEBREW": re.compile(r"^\u05B4\u05DD", re.UNICODE),
        "TRANSLITERATION": _jerusalem,
    },
    {
        "TITLE": "Issachar",
        "DESCRIPTION": "Transliterate instances of the name Issachar",
        "FEATURE": "word",
        "HEBREW": re.compile(r"(וְ)?יִשָּׂשכָר"),
        "PASS_THROUGH": True,
        "TRANSLITERATION": _issachar,
    },
    {
        "TITLE": "Interrogative in construct",
        "DESCRIPTION": "Transliterate instances of the interrogative word in construct form.",
        "FEATURE": "word",
        "HEBREW": "מַה־",
        "TRANSLITERATION": _interrogative_construct,
    },
]


def build_tiberian_schema() -> Schema:
    """Return a Schema matching docs/tiberian.ts."""
    return Schema(
        {
            "VOCAL_SHEVA": "a",
            "HATAF_SEGOL": "ɛ",
            "HATAF_PATAH": "a",
            "HATAF_QAMATS": "ɔ",
            "HIRIQ": "i",
            "TSERE": "e",
            "SEGOL": "ɛ",
            "PATAH": "a",
            "QAMATS": "ɔ",
            "HOLAM": "o",
            "HOLAM_HASER": "o",
            "QUBUTS": "u",
            "DAGESH": "",
            "DAGESH_CHAZAQ": True,
            "MAQAF": "-",
            "PASEQ": "",
            "SOF_PASUQ": "",
            "QAMATS_QATAN": "ɔ",
            "FURTIVE_PATAH": "a",
            "HIRIQ_YOD": "iː",
            "TSERE_YOD": "eː",
            "SEGOL_YOD": "ɛː",
            "SHUREQ": "uː",
            "HOLAM_VAV": "oː",
            "QAMATS_HE": "ɔː",
            "SEGOL_HE": "ɛː",
            "TSERE_HE": "eː",
            "MS_SUFX": "ɔw",
            "ALEF": "ʔ",
            "BET": "v",
            "BET_DAGESH": "b",
            "GIMEL": "ʁ",
            "GIMEL_DAGESH": "g",
            "DALET": "ð",
            "DALET_DAGESH": "d",
            "HE": "h",
            "VAV": "v",
            "ZAYIN": "z",
            "HET": "ħ",
            "TET": "tˁ",
            "YOD": "j",
            "FINAL_KAF": "χ",
            "KAF": "χ",
            "KAF_DAGESH": "kʰ",
            "LAMED": "l",
            "FINAL_MEM": "m",
            "MEM": "m",
            "FINAL_NUN": "n",
            "NUN": "n",
            "SAMEKH": "s",
            "AYIN": "ʕ",
            "FINAL_PE": "f",
            "PE": "f",
            "PE_DAGESH": "pʰ",
            "FINAL_TSADI": "sˁ",
            "TSADI": "sˁ",
            "QOF": "q̟",
            "RESH": "ʀ̟",
            "SHIN": "ʃ",
            "SIN": "s",
            "TAV": "θ",
            "TAV_DAGESH": "tʰ",
            "DIVINE_NAME": "ʔaðoːˈnɔːɔj",
            "DIVINE_NAME_ELOHIM": "ʔɛloːˈhiːim",
            "STRESS_MARKER": {"location": "before-syllable", "mark": "ˈ"},
            "ADDITIONAL_FEATURES": _ADDITIONAL_FEATURES,
            "ON_COMPLETE": _on_complete,
            "allowNoNiqqud": False,
            "article": False,
            "holemHaser": "remove",
            "ketivQeres": [
                {
                    "input": re.compile(r"הִוא"),
                    "output": _ketiv_hi_hi,
                    "captureTaamim": True,
                    "ignoreTaamim": True,
                }
            ],
            "longVowels": False,
            "qametsQatan": True,
            "shevaAfterMeteg": False,
            "shevaWithMeteg": True,
            "sqnmlvy": False,
            "strict": True,
            "wawShureq": False,
        }
    )


# Module-level schema instance (mirrors JS `export const tiberian`)
tiberian: Schema = build_tiberian_schema()
