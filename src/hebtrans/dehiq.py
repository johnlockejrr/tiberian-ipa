"""Deḥiq (דחיק) detection — Khan T1 §I.2.8.1.2.

Compress word-final unstressed long *qameṣ* / *segol* to half-long and
geminate the following word's initial consonant when the first word is
penultimately stressed and bound by a conjunctive accent or *maqqef*.
"""

from __future__ import annotations

import re
from typing import Any

# Conjunctive teʿamim (Yeivin / Unicode Hebrew accents).
# Munah, mahpakh, merkha(+kefula), darga, qadma, telisha qetana,
# yerah ben yomo, iluy.  (Deḥi U+05AD is disjunctive — excluded.)
_CONJUNCTIVE = re.compile(r"[\u05A3-\u05AA\u05AC]")

# Gutturals cannot take deḥiq dagesh; block compression before them.
_GUTTURAL_ONSET = re.compile(r"[אהחע]")


def _syl_has_meteg(syl: Any) -> bool:
    return any(getattr(c, "hasMeteg", False) for c in syl.clusters)


def _penultimately_stressed(word: Any) -> bool:
    syls = list(word.syllables)
    if len(syls) < 2 or syls[-1].isAccented:
        return False
    # Accent or gaʿya/meteg on a non-final syllable.
    return any(s.isAccented or _syl_has_meteg(s) for s in syls[:-1])


def _final_is_lax_open(word: Any) -> bool:
    syls = list(word.syllables)
    if not syls:
        return False
    final = syls[-1]
    if final.isClosed:
        return False
    # Gaʿya on the final vowel blocks compression (full length is required).
    if _syl_has_meteg(final):
        return False
    names = final.vowelNames
    return bool(names) and names[0] in ("QAMATS", "SEGOL")


def _initial_foot_stressed(word: Any) -> bool:
    syls = list(word.syllables)
    if not syls:
        return False
    if syls[0].isAccented:
        return True
    # Stress on the first full vowel after an initial vocalic shewa.
    if (
        len(syls) > 1
        and syls[0].vowelNames == ["SHEVA"]
        and syls[1].isAccented
    ):
        return True
    return False


def _following_has_dagesh(word: Any) -> bool:
    syls = list(word.syllables)
    if not syls or not syls[0].clusters:
        return False
    return bool(re.search(r"\u05BC", syls[0].clusters[0].text))


def is_dehiq_pair(first: Any, second: Any) -> bool:
    """True if ``first`` + ``second`` form a deḥiq / ʾathe me-raḥiq bond."""
    if first is None or second is None:
        return False
    if not _penultimately_stressed(first):
        return False
    if not _final_is_lax_open(first):
        return False
    bound = bool(getattr(first, "isInConstruct", False)) or bool(
        _CONJUNCTIVE.search(first.text)
    )
    if not bound:
        return False
    if not _initial_foot_stressed(second):
        return False
    onset = second.syllables[0].onset if second.syllables else ""
    if _GUTTURAL_ONSET.search(onset or ""):
        return False
    if not _following_has_dagesh(second):
        return False
    return True


def word_is_dehiq_host(word: Any) -> bool:
    """True if ``word`` is the first member of a deḥiq pair with its next word."""
    nxt = word.next.value if getattr(word, "next", None) else None
    return is_dehiq_pair(word, nxt)
