"""Holem-waw sequencing (ported from havarotjs)."""

from __future__ import annotations

import re
from typing import Any, Callable, Dict

from .regular_expressions import taamim
from .remove_taamim import remove_taamim


def _find_matches(word: str, regx: re.Pattern[str], cb: Callable[..., str]) -> str:
    no_taamim, char_pos = remove_taamim(word)
    for match in re.finditer(regx.pattern, no_taamim):
        start = char_pos[match.start()]
        # Faithful to JS: charPos[match[0].length] + start
        length = len(match.group(0))
        end = (char_pos[length] + start) if length < len(char_pos) else len(word)
        word = cb(word, start, end)
    return word


def holem_waw(word: str, options: Dict[str, Any]) -> str:
    waw_re = re.compile(r"\u05D5")
    holem_re = re.compile(r"\u05B9")
    holem_haser_re = re.compile(r"\u05BA")
    waw_holem_re = re.compile(r"\u05D5\u05B9")
    vowels = re.compile(r"[\u05B0-\u05BB\u05C7]")

    vav_holem_male = re.compile(
        r"(?<!" + vowels.pattern + r")" + waw_holem_re.pattern
    )
    vav_holem_haser = re.compile(
        r"(?<=" + vowels.pattern + r")"
        + waw_re.pattern
        + taamim.pattern
        + r"?"
        + holem_re.pattern
    )

    holem_haser_opt = options.get("holemHaser", "preserve")
    # "unique" accepted as Tiberian-facing alias of "preserve"
    if holem_haser_opt == "remove" and holem_haser_re.search(word):
        word = holem_haser_re.sub("\u05B9", word)

    if not waw_re.search(word) or not holem_re.search(word) or not waw_holem_re.search(word):
        return word

    if vav_holem_male.search(word):
        word = _find_matches(
            word,
            vav_holem_male,
            lambda w, start=0, end=0: vav_holem_male.sub("\u05B9\u05D5", w),
        )

    if holem_haser_opt == "update" and vav_holem_haser.search(remove_taamim(word)[0]):
        def _haser_cb(w: str, start: int = 0, end: int = 0) -> str:
            vav_taam_holem = re.compile(
                rf"{waw_re.pattern}({taamim.pattern})?{holem_re.pattern}"
            )
            return vav_taam_holem.sub("\u05D5\u05BA\\1", w)

        word = _find_matches(word, vav_holem_haser, _haser_cb)

    return word
