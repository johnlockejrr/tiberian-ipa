"""Hebrew character with sequencing position (ported from havarotjs)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .utils.char_map import char_to_name_map, is_hebrew_character, name_to_char_map
from .utils.regular_expressions import (
    consonants,
    dagesh,
    ligatures,
    meteg,
    rafe,
    sheva,
    taamim,
    vowels,
)

if TYPE_CHECKING:
    from .cluster import Cluster


class Char:
    """A Hebrew character and its positioning number for sequencing."""

    def __init__(self, char: str) -> None:
        self._text = char
        self._cluster: Optional["Cluster"] = None
        self._sequence_position = self._find_pos()

    @property
    def cluster(self) -> Optional["Cluster"]:
        return self._cluster

    @cluster.setter
    def cluster(self, cluster: Optional["Cluster"]) -> None:
        self._cluster = cluster

    def isCharacterName(self, name: str) -> bool:
        if name not in name_to_char_map:
            raise ValueError(f"{name} is not a valid value")
        return bool(self._text == name_to_char_map[name] or name_to_char_map[name] in self._text)

    @property
    def isConsonant(self) -> bool:
        return bool(consonants.search(self._text))

    @property
    def isLigature(self) -> bool:
        return bool(ligatures.search(self._text))

    @property
    def isDagesh(self) -> bool:
        return bool(dagesh.search(self._text))

    @property
    def isRafe(self) -> bool:
        return bool(rafe.search(self._text))

    @property
    def isSheva(self) -> bool:
        return bool(sheva.search(self._text))

    @property
    def isVowel(self) -> bool:
        return bool(vowels.search(self._text))

    @property
    def isTaamim(self) -> bool:
        return bool(taamim.search(self._text))

    @property
    def isNotHebrew(self) -> bool:
        return self.sequencePosition == 10

    @property
    def characterName(self) -> Optional[str]:
        if is_hebrew_character(self._text):
            return char_to_name_map[self._text]
        return None

    @property
    def sequencePosition(self) -> int:
        return self._sequence_position

    @property
    def text(self) -> str:
        return self._text

    def _find_pos(self) -> int:
        char = self.text
        if consonants.search(char):
            return 0
        if ligatures.search(char):
            return 1
        if dagesh.search(char):
            return 2
        if rafe.search(char):
            return 2
        if vowels.search(char):
            return 3
        if sheva.search(char):
            return 3
        if taamim.search(char):
            return 4
        if meteg.search(char):
            return 4
        return 10

    def __repr__(self) -> str:
        return f"Char({self.text!r})"
