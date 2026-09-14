"""Sequence Hebrew text into Char lists (ported from havarotjs)."""

from __future__ import annotations

import re
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..char import Char


def sequence(text: str) -> List[List["Char"]]:
    """Return a two-dimensional array of sequenced Char objects."""
    from ..cluster import Cluster

    splits = re.compile(r"(?=[\u05C0\u05D0-\u05F2])")
    hiriq_patah = re.compile(r"\u05B4\u05B7")
    hiriq_qamets = re.compile(r"\u05B4\u05B8")

    if hiriq_patah.search(text):
        text = hiriq_patah.sub("\u05B7\u05B4", text)
    elif hiriq_qamets.search(text):
        text = hiriq_qamets.sub("\u05B8\u05B4", text)

    return [
        Cluster(word).chars
        for word in splits.split(text)
    ]
