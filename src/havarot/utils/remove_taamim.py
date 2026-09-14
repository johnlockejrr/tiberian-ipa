"""Remove taamim while tracking original character positions."""

from __future__ import annotations

from typing import List, Tuple

from .regular_expressions import taamim


def remove_taamim(word: str) -> Tuple[str, List[int]]:
    """Return (text_without_taamim, char_pos) where char_pos maps
    indices in the stripped string back to indices in ``word``.
    """
    no_taamim = ""
    char_pos: List[int] = []
    for index, element in enumerate(word):
        # Avoid JS RegExp.lastIndex side-effects of .test() with /g
        if not taamim.search(element):
            no_taamim += element
            char_pos.append(index)
    return no_taamim, char_pos
