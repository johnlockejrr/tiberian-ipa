"""Qamets qatan conversion (ported from havarotjs)."""

from __future__ import annotations

import re
from typing import List
from unicodedata import normalize

from .remove_taamim import remove_taamim
from .sequence import sequence

_SNIPPETS = [
    "אָבְדַן",
    "אָבְנ",
    "אָזְנ",
    "אָכְל",
    "אָנִיּ",
    "אָפְנ",
    "אָרְח",
    "אָרְכּ",
    "אָשְׁר",
    "בָאְשׁ",
    "בָשְׁתּ",
    "בָּשְׁתּ",
    "גָבְה",
    "גָּבְה",
    "גָדְל",
    "גָּדְל",
    "גָּלְי",
    "גָרְנ",
    "גָּרְנ",
    "דָּכְי",
    "דָּרְבָֽן",
    "חָדְשׁ",
    "חָכְמ",
    "חָלְיֽוֹ",
    "חָלְיֹו",
    "חָפְנ",
    "חָפְשׁ",
    "חָרְב",
    "חָרְנֶפֶר",
    "חָרְפּ",
    "חָשְׁכּ",
    "יָפְי",
    "יָשְׁר",
    "מָרְדְּכַי",
    "מָתְנ",
    "סָלְתּ",
    "עָזּ",
    "עָמְר",
    "עָנְי",
    "עָפְנִי",
    "עָפְר",
    "עָרְל",
    "עָרְפּ",
    "עָשְׁר",
    "צָרְכּ",
    "קָדְק",
    "קָדְשׁ",
    "קָרְבּ",
    "קָרְח",
    "רָגְז",
    "רָחְבּ",
    "שָׁרְשׁ",
    "שָׁרָשׁ",
    "תָּכְנִית",
]

_WHOLE_WORDS = [
    "חׇפְרַע",
    "חָק־",
    r"(מִ)?כָּל־",
    r"(וּבְ|וְ|בְּ|לְ)?כָל־",
    r"^(מִ)?כָּל ?$",
    r"^(וּבְ|וְ|בְּ|לְ)?כָל ?$",
    "מָר־",
    "עָתְנִיאֵל",
    "רָב־",
    "תָם־",
    "תָּם־",
    "חָנֵּנִי",
    "וַיָּמָת",
    "וַיָּנָס",
    "וַיָּקָם",
    "וַיָּרָם",
    "וַיָּשָׁב",
    "וַתָּמָת",
    "וַתָּקָם",
    "וַתָּשָׁב",
]


def _sequence_snippets(arr: List[str]) -> List[str]:
    result = []
    for snippet in arr:
        chars = [c for cluster_chars in sequence(normalize("NFKD", snippet)) for c in cluster_chars]
        result.append("".join(c.text for c in chars))
    return result


_snippets_regx: List[str] | None = None
_whole_words_regx: List[str] | None = None


def _ensure_patterns() -> None:
    global _snippets_regx, _whole_words_regx
    if _snippets_regx is None:
        _snippets_regx = _sequence_snippets(_SNIPPETS)
        _whole_words_regx = _sequence_snippets(_WHOLE_WORDS)


def converts_qamets_qatan(word: str) -> str:
    _ensure_patterns()
    assert _snippets_regx is not None and _whole_words_regx is not None

    qamets_reg = re.compile(r"\u05B8")
    qamets_qat_reg = re.compile(r"\u05C7")
    hatef_qam_ref = re.compile(r"\u05B3")

    if not qamets_reg.search(word) or qamets_qat_reg.search(word):
        return word

    if hatef_qam_ref.search(word):
        hatef_pos = word.index("\u05B3")
        qam_pos = word.find("\u05B8")
        if qam_pos != -1 and qam_pos < hatef_pos:
            return word[:qam_pos] + "\u05C7" + word[qam_pos + 1 :]

    no_taamim, char_pos = remove_taamim(word)

    for whole_word in _whole_words_regx:
        if re.search(whole_word, no_taamim):
            last_qam = word.rfind("\u05B8")
            return word[:last_qam] + "\u05C7" + word[last_qam + 1 :]

    for snippet in _snippets_regx:
        match = re.search(snippet, no_taamim)
        if not match:
            continue
        start = char_pos[match.start()]
        length = len(match.group(0))
        end = char_pos[length] + start if length < len(char_pos) else len(word)
        matched = word[start:end]
        with_qqatan = qamets_reg.sub("\u05C7", matched)
        word = word.replace(matched, with_qqatan)
        return word

    return word
