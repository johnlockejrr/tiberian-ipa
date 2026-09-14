"""Transliteration rules (faithful port of hebrew-transliteration/dist/rules.js)."""

from __future__ import annotations

import re
from typing import Any, Callable

from havarot import Cluster, Syllable, Word

from hebtrans.schema import Schema

# Taamim stripped before most rule matching (same range as rules.js)
_TAAMIM = re.compile(r"[\u0591-\u05AF\u05BD\u05BF]", re.UNICODE)

# Positive lookahead cluster splitter (havarotjs clusterSplitGroup)
_CLUSTER_SPLIT_GROUP = re.compile(
    r"(?=[\u05BE\u05C3\u05C6\u05D0-\u05F2\u2000-\u206F\u2E00-\u2E7F"
    r"'!\"#$%&()*+,\-./:;<=>?@\[\]^_`{|}~])",
    re.UNICODE,
)

_HEB_CHARS = re.compile(r"[\u0590-\u05FF\uFB1D-\uFB4F]", re.UNICODE)

_CHAR_MAP: dict[str, str] = {
    "\u05B0": "VOCAL_SHEVA",
    "\u05B1": "HATAF_SEGOL",
    "\u05B2": "HATAF_PATAH",
    "\u05B3": "HATAF_QAMATS",
    "\u05B4": "HIRIQ",
    "\u05B5": "TSERE",
    "\u05B6": "SEGOL",
    "\u05B7": "PATAH",
    "\u05B8": "QAMATS",
    "\u05B9": "HOLAM",
    "\u05BA": "HOLAM",
    "\u05BB": "QUBUTS",
    "\u05BC": "DAGESH",
    "\u05BE": "MAQAF",
    "\u05C0": "PASEQ",
    "\u05C3": "SOF_PASUQ",
    "\u05C7": "QAMATS_QATAN",
    "א": "ALEF",
    "ב": "BET",
    "ג": "GIMEL",
    "ד": "DALET",
    "ה": "HE",
    "ו": "VAV",
    "ז": "ZAYIN",
    "ח": "HET",
    "ט": "TET",
    "י": "YOD",
    "ך": "FINAL_KAF",
    "כ": "KAF",
    "ל": "LAMED",
    "ם": "FINAL_MEM",
    "מ": "MEM",
    "ן": "FINAL_NUN",
    "נ": "NUN",
    "ס": "SAMEKH",
    "ע": "AYIN",
    "ף": "FINAL_PE",
    "פ": "PE",
    "ץ": "FINAL_TSADI",
    "צ": "TSADI",
    "ק": "QOF",
    "ר": "RESH",
    "ש": "SHIN",
    "ת": "TAV",
}


def _as_pattern(hebrew: Any) -> re.Pattern[str] | Any:
    """Normalize HEBREW feature field to something with .search / usable in sub."""
    if isinstance(hebrew, re.Pattern):
        return hebrew
    if hasattr(hebrew, "search") and callable(hebrew.search):
        return hebrew
    return re.compile(str(hebrew), re.UNICODE)


def _hebrew_test(hebrew: Any, text: str) -> bool:
    pat = _as_pattern(hebrew)
    return pat.search(text) is not None


def _hebrew_sub(text: str, hebrew: Any, repl: str) -> str:
    pat = _as_pattern(hebrew)
    if isinstance(pat, re.Pattern):
        return pat.sub(repl, text, count=1)
    # Custom matcher without sub — fall back to no-op replace
    return text


def _remove_taamim(input_text: str) -> str:
    return _TAAMIM.sub("", input_text)


def _replace_with_regex(input_text: str, regex: re.Pattern[str], replace_value: str) -> str:
    return regex.sub(replace_value, input_text, count=1)


def _map_chars(schema: Schema) -> Callable[[str], str]:
    def mapper(input_text: str) -> str:
        out: list[str] = []
        for ch in input_text:
            key = _CHAR_MAP.get(ch)
            if key is not None and key in schema:
                val = schema[key]
                out.append("" if val is None else str(val))
            else:
                out.append(ch)
        return "".join(out)

    return mapper


def _replace_and_transliterate(
    input_text: str, regex: Any, replace_value: str, schema: Schema
) -> str:
    syl_seq = _hebrew_sub(input_text, regex, replace_value)
    map_fn = _map_chars(schema)
    return "".join(map_fn(ch) for ch in syl_seq)


def add_stress_marker(text: str, syl: Syllable, schema: Schema) -> str:
    """Add a stress marker to a syllable according to schema settings."""
    stress = schema.get("STRESS_MARKER")
    if not stress or not text:
        return text
    if not syl.isAccented:
        return text

    exclude = stress.get("exclude", "never") if isinstance(stress, dict) else getattr(stress, "exclude", "never")
    if exclude is None:
        exclude = "never"
    if exclude == "single" and not syl.prev and not syl.next:
        return text
    if exclude == "final" and not syl.next:
        return text

    location = stress["location"] if isinstance(stress, dict) else stress.location
    mark = stress["mark"] if isinstance(stress, dict) else stress.mark

    if mark in text:
        return text

    if location == "before-syllable":
        is_doubled = any(is_dagesh_chazaq(c, schema) for c in syl.clusters)
        if is_doubled:
            first_cluster = syl.clusters[0]
            name = first_cluster.chars[0].characterName if first_cluster.chars else None
            output = schema[name] if name and name in schema else ""
            if not isinstance(output, str):
                output = ""
            first = text[: len(output)]
            rest = text[len(output) :]
            return f"{first}{mark}{rest}"
        return f"{mark}{text}"

    if location == "after-syllable":
        return f"{text}{mark}"

    vowels = [
        schema.get(k)
        for k in (
            "PATAH",
            "HATAF_PATAH",
            "QAMATS",
            "HATAF_QAMATS",
            "SEGOL",
            "HATAF_SEGOL",
            "TSERE",
            "HIRIQ",
            "HOLAM",
            "QAMATS_QATAN",
            "QUBUTS",
            "QAMATS_HE",
            "SEGOL_HE",
            "TSERE_HE",
            "HIRIQ_YOD",
            "TSERE_YOD",
            "SEGOL_YOD",
            "HOLAM_VAV",
            "SHUREQ",
        )
    ]
    vowel_strs = sorted(
        (v for v in vowels if isinstance(v, str) and v),
        key=len,
        reverse=True,
    )
    if not vowel_strs:
        return text
    vowel_rgx = re.compile("|".join(re.escape(v) for v in vowel_strs))
    match = vowel_rgx.search(text)
    if location == "before-vowel":
        if match:
            return text[: match.start()] + mark + match.group(0) + text[match.end() :]
        return text
    # after-vowel
    if match:
        return text[: match.start()] + match.group(0) + mark + text[match.end() :]
    return text


def _copy_syllable(new_text: str, old: Syllable) -> Syllable:
    parts = _split_clusters(new_text)
    new_clusters = [Cluster(s, True) for s in parts]
    old_clusters = list(old.clusters)

    if len(new_clusters) == len(old_clusters):
        for i, c in enumerate(new_clusters):
            c.prev = old_clusters[i].prev
            c.next = old_clusters[i].next
    else:
        i = 0
        while i < len(new_clusters):
            c = new_clusters[i]
            if i < len(old_clusters) and old_clusters[i].text[:1] == c.text[:1]:
                c.prev = old_clusters[i].prev
                c.next = old_clusters[i].next
            else:
                c.prev = old_clusters[i].prev if i < len(old_clusters) else None
                c.next = (
                    old_clusters[i + 1].next
                    if (i + 1) < len(old_clusters)
                    else None
                )
                i += 1
            i += 1

    try:
        new_syl = Syllable(
            new_clusters,
            isClosed=old.isClosed,
            isAccented=old.isAccented,
            isFinal=old.isFinal,
        )
    except TypeError:
        new_syl = Syllable(
            new_clusters,
            {"isClosed": old.isClosed, "isAccented": old.isAccented, "isFinal": old.isFinal},
        )
    for c in new_clusters:
        c.syllable = new_syl
    new_syl.prev = old.prev
    new_syl.next = old.next
    new_syl.word = old.word
    return new_syl


def _split_clusters(text: str) -> list[str]:
    """Split text on cluster boundaries (JS clusterSplitGroup lookahead)."""
    if not text:
        return []
    indices = [0]
    for m in _CLUSTER_SPLIT_GROUP.finditer(text):
        if m.start() > indices[-1]:
            indices.append(m.start())
    indices.append(len(text))
    parts = [text[indices[i] : indices[i + 1]] for i in range(len(indices) - 1)]
    return [p for p in parts if p]


def _get_dagesh_chazaq_val(input_text: str, schema: Schema, is_chazaq: bool) -> str:
    if not is_chazaq:
        return input_text
    dagesh = schema.get("DAGESH_CHAZAQ")
    syllable_separator = schema.get("SYLLABLE_SEPARATOR") or ""
    if isinstance(dagesh, bool):
        return input_text + syllable_separator + input_text
    return input_text + str(dagesh)


def _get_divine_name(string: str, schema: Schema) -> str:
    begn = string[0] if string else ""
    end = string[-1] if string else ""
    divine_name = (
        schema.get("DIVINE_NAME_ELOHIM")
        if schema.get("DIVINE_NAME_ELOHIM") and re.search(r"\u05B4", string, re.UNICODE)
        else schema.get("DIVINE_NAME")
    )
    left = "" if _HEB_CHARS.search(begn) else begn
    right = "" if _HEB_CHARS.search(end) else end
    return f"{left}{divine_name}{right}"


def is_dagesh_chazaq(cluster: Cluster, schema: Schema) -> bool:
    if not schema.get("DAGESH_CHAZAQ"):
        return False
    if cluster.isShureq:
        return False
    if not re.search(r"\u05BC", cluster.text, re.UNICODE):
        return False
    prev_cluster = cluster.prev.value if cluster.prev else None
    if prev_cluster is not None and getattr(prev_cluster, "hasSheva", False):
        return False
    syl = cluster.syllable
    word = syl.word if syl else None
    prev_word = word.prev.value if word and word.prev else None
    if prev_word is not None and getattr(prev_word, "isInConstruct", False):
        syllables = prev_word.syllables
        if syllables and not syllables[-1].isClosed:
            return True
    prev_syllable_node = syl.prev if syl else None
    if not prev_syllable_node:
        return False
    prev_syllable = prev_syllable_node.value
    if not prev_syllable:
        return False
    prev_coda = prev_syllable.codaWithGemination
    if not prev_coda:
        return False
    return prev_coda == (syl.onset if syl else None)


def _join_syllable_chars(syl: Syllable, syl_chars: list[str], schema: Schema) -> str:
    map_fn = _map_chars(schema)
    return "".join(map_fn(c) for c in syl_chars)


def _mater_features(syl: Syllable, schema: Schema) -> str:
    mater = next(c for c in syl.clusters if c.isMater)
    prev = mater.prev if isinstance(mater.prev, Cluster) else None
    # JS also works when prev is Node with value=self (Cluster)
    if prev is None and mater.prev is not None:
        prev = mater.prev.value if hasattr(mater.prev, "value") else None
    mater_text = mater.text
    prev_text = _remove_taamim(prev.text if prev else "")

    no_mater_text = "".join(
        cluster_rules(c, schema) for c in syl.clusters if not c.isMater
    )
    if "־" in mater_text:
        no_mater_text = no_mater_text + "־"

    if re.search(r"י", mater_text):
        if re.search(r"\u05B4", prev_text, re.UNICODE):
            return _replace_with_regex(no_mater_text, re.compile(r"\u05B4", re.UNICODE), schema["HIRIQ_YOD"])
        if re.search(r"\u05B5", prev_text, re.UNICODE):
            return _replace_with_regex(no_mater_text, re.compile(r"\u05B5", re.UNICODE), schema["TSERE_YOD"])
        if re.search(r"\u05B6", prev_text, re.UNICODE):
            return _replace_with_regex(no_mater_text, re.compile(r"\u05B6", re.UNICODE), schema["SEGOL_YOD"])

    if re.search(r"ו", mater_text, re.UNICODE):
        if re.search(r"\u05B9", prev_text, re.UNICODE):
            return _replace_with_regex(no_mater_text, re.compile(r"\u05B9", re.UNICODE), schema["HOLAM_VAV"])

    if re.search(r"ה", mater_text):
        if re.search(r"\u05B8", prev_text, re.UNICODE):
            return _replace_with_regex(no_mater_text, re.compile(r"\u05B8", re.UNICODE), schema["QAMATS_HE"])

    return mater_text


def cluster_rules(cluster: Cluster, schema: Schema) -> str:
    """Apply cluster-level rules (JS ``cluterRules``)."""
    cluster_text = _remove_taamim(cluster.text)
    cluster_features = [
        seq
        for seq in (schema.get("ADDITIONAL_FEATURES") or [])
        if seq.get("FEATURE") == "cluster"
    ]
    for feature in cluster_features:
        heb = feature["HEBREW"]
        if _hebrew_test(heb, cluster_text):
            transliteration = feature["TRANSLITERATION"]
            pass_through = feature.get("PASS_THROUGH", True)
            if isinstance(transliteration, str):
                return _replace_and_transliterate(cluster_text, heb, transliteration, schema)
            if not pass_through:
                return transliteration(cluster, heb, schema)
            cluster_text = transliteration(cluster, heb, schema)

    syl = cluster.syllable
    if cluster.hasSheva and syl is not None and syl.isClosed:
        cluster_text = re.sub(r"\u05B0", "", cluster_text, count=1, flags=re.UNICODE)

    # mappiq he
    if re.search(r"ה\u05BC$", cluster_text, re.UNICODE | re.MULTILINE):
        return _replace_with_regex(cluster_text, re.compile(r"ה\u05BC", re.UNICODE), schema["HE"])

    if syl is not None and syl.isFinal and not syl.isClosed:
        furtive_chet = re.compile(r"\u05D7\u05B7$", re.UNICODE | re.MULTILINE)
        if furtive_chet.search(cluster_text):
            return furtive_chet.sub("\u05B7\u05D7", cluster_text, count=1)
        furtive_ayin = re.compile(r"\u05E2\u05B7$", re.UNICODE | re.MULTILINE)
        if furtive_ayin.search(cluster_text):
            return furtive_ayin.sub("\u05B7\u05E2", cluster_text, count=1)
        furtive_he = re.compile(r"\u05D4\u05BC\u05B7$", re.UNICODE | re.MULTILINE)
        if furtive_he.search(cluster_text):
            return furtive_he.sub("\u05B7\u05D4\u05BC", cluster_text, count=1)

    is_chazaq = is_dagesh_chazaq(cluster, schema)

    pairs = [
        (schema.get("BET_DAGESH"), re.compile(r"ב\u05BC", re.UNICODE)),
        (schema.get("GIMEL_DAGESH"), re.compile(r"ג\u05BC", re.UNICODE)),
        (schema.get("DALET_DAGESH"), re.compile(r"ד\u05BC", re.UNICODE)),
        (schema.get("KAF_DAGESH"), re.compile(r"כ\u05BC", re.UNICODE)),
        (schema.get("KAF_DAGESH"), re.compile(r"ך\u05BC", re.UNICODE)),
        (schema.get("PE_DAGESH"), re.compile(r"פ\u05BC", re.UNICODE)),
        (schema.get("TAV_DAGESH"), re.compile(r"ת\u05BC", re.UNICODE)),
    ]
    for val, rgx in pairs:
        if val and rgx.search(cluster_text):
            return _replace_with_regex(
                cluster_text, rgx, _get_dagesh_chazaq_val(str(val), schema, is_chazaq)
            )

    if re.search(r"ש\u05C1", cluster_text, re.UNICODE):
        return _replace_with_regex(
            cluster_text,
            re.compile(r"ש\u05C1", re.UNICODE),
            _get_dagesh_chazaq_val(schema["SHIN"], schema, is_chazaq),
        )
    if re.search(r"ש\u05C2", cluster_text, re.UNICODE):
        return _replace_with_regex(
            cluster_text,
            re.compile(r"ש\u05C2", re.UNICODE),
            _get_dagesh_chazaq_val(schema["SIN"], schema, is_chazaq),
        )

    if is_chazaq:
        consonant = cluster.chars[0].text
        consonant_dagesh = re.compile(re.escape(consonant) + "\u05BC", re.UNICODE)
        return _replace_with_regex(
            cluster_text,
            consonant_dagesh,
            _get_dagesh_chazaq_val(consonant, schema, is_chazaq),
        )

    if cluster.isShureq:
        return cluster_text.replace("וּ", schema["SHUREQ"])

    return cluster_text


def syl_rules(syl: Syllable, schema: Schema) -> str:
    """Apply syllable-level rules (JS ``sylRules``)."""
    base_syllable_text = _TAAMIM.sub("", syl.text)
    syllable_features = [
        seq
        for seq in (schema.get("ADDITIONAL_FEATURES") or [])
        if seq.get("FEATURE") == "syllable"
    ]
    for feature in syllable_features:
        heb = feature["HEBREW"]
        if _hebrew_test(heb, base_syllable_text):
            transliteration = feature["TRANSLITERATION"]
            pass_through = feature.get("PASS_THROUGH", True)
            if isinstance(transliteration, str):
                return _replace_and_transliterate(
                    base_syllable_text, heb, transliteration, schema
                )
            if not pass_through:
                return transliteration(syl, heb, schema)
            new_text = transliteration(syl, heb, schema)
            if new_text != base_syllable_text:
                syl = _copy_syllable(new_text, syl)
                base_syllable_text = _TAAMIM.sub("", syl.text)

    has_mater = any(c.isMater for c in syl.clusters)
    if has_mater:
        mater_syl = _mater_features(syl, schema)
        text = _join_syllable_chars(syl, list(mater_syl), schema)
        return add_stress_marker(text, syl, schema)

    clusters = [cluster_rules(c, schema) for c in syl.clusters]
    joined = _TAAMIM.sub("", _join_syllable_chars(syl, clusters, schema))

    ms_suffix = re.compile(r"\u05B8\u05D9\u05D5", re.UNICODE)
    if syl.isFinal and ms_suffix.search(base_syllable_text):
        text = joined.replace(
            schema["QAMATS"] + schema["YOD"] + schema["VAV"], schema["MS_SUFX"]
        )
        return add_stress_marker(text, syl, schema)

    if schema.get("SEGOL_HE") and re.search(r"\u05B6\u05D4", base_syllable_text, re.UNICODE):
        text = joined.replace(schema["SEGOL"] + schema["HE"], schema["SEGOL_HE"])
        return add_stress_marker(text, syl, schema)

    if schema.get("TSERE_HE") and re.search(r"\u05B5\u05D4", base_syllable_text, re.UNICODE):
        text = joined.replace(schema["TSERE"] + schema["HE"], schema["TSERE_HE"])
        return add_stress_marker(text, syl, schema)

    if schema.get("PATAH_HE") and re.search(r"\u05B7\u05D4", base_syllable_text, re.UNICODE):
        text = joined.replace(schema["PATAH"] + schema["HE"], schema["PATAH_HE"])
        return add_stress_marker(text, syl, schema)

    text = _TAAMIM.sub("", joined)
    return add_stress_marker(text, syl, schema)


def word_rules(word: Word, schema: Schema) -> str | Word:
    """Apply word-level rules (JS ``wordRules``)."""
    if word.isDivineName:
        return _get_divine_name(word.text, schema)
    if word.hasDivineName:
        return f"{syl_rules(word.syllables[0], schema)}-{_get_divine_name(word.text, schema)}"
    if word.isNotHebrew:
        return word.text

    word_features = [
        seq
        for seq in (schema.get("ADDITIONAL_FEATURES") or [])
        if seq.get("FEATURE") == "word"
    ]
    if word_features:
        text = _TAAMIM.sub("", word.text)
        for feature in word_features:
            heb = feature["HEBREW"]
            if _hebrew_test(heb, text):
                transliteration = feature["TRANSLITERATION"]
                pass_through = feature.get("PASS_THROUGH", True)
                if isinstance(transliteration, str):
                    return _replace_and_transliterate(text, heb, transliteration, schema)
                if not pass_through:
                    return transliteration(word, heb, schema)
                return Word(
                    transliteration(word, heb, schema),
                    schema.syl_opts() if hasattr(schema, "syl_opts") else dict(schema),
                )
        return word
    return word


# JS-compatible aliases
sylRules = syl_rules
wordRules = word_rules
cluterRules = cluster_rules  # intentional JS typo preserved as alias
clusterRules = cluster_rules
