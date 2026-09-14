"""Orthographic cluster (ported from havarotjs)."""

from __future__ import annotations

import re
from typing import List, Optional, TYPE_CHECKING

from .char import Char
from .node import Node
from .utils.char_map import (
    char_to_name_map,
    consonant_name_to_char_map,
    is_char_consonant,
    is_char_taam,
    is_char_vowel,
    taamim_name_to_char_map,
    vowel_name_to_char_map,
)
from .utils.regular_expressions import heb_chars, meteg, punctuation, taamim

if TYPE_CHECKING:
    from .syllable import Syllable


class Cluster(Node["Cluster"]):
    """Group of Hebrew characters around one consonant."""

    def __init__(self, cluster: str, no_sequence: bool = False) -> None:
        super().__init__()
        self.value = self
        self._original = cluster
        self._syllable: Optional["Syllable"] = None
        self._consonants_cache: Optional[List[str]] = None
        self._consonant_name_cache: Optional[List[str]] = None
        self._taamim_cache: Optional[List[str]] = None
        self._vowels_cache: Optional[List[str]] = None
        self._vowel_names_cache: Optional[List[str]] = None
        self._taamim_names_cache: Optional[List[str]] = None
        self._sequenced = self._sequence(no_sequence)
        for char in self._sequenced:
            char.cluster = self

    def _sequence(self, no_sequence: bool = False) -> List[Char]:
        chars = [Char(c) for c in self._original]
        if no_sequence:
            return chars
        return sorted(chars, key=lambda a: a.sequencePosition)

    @property
    def chars(self) -> List[Char]:
        return self._sequenced

    @property
    def consonants(self) -> List[str]:
        if self._consonants_cache is not None:
            return self._consonants_cache
        consonants: List[str] = []
        for char in self.chars:
            text = char.text
            if char.isConsonant and is_char_consonant(text):
                consonants.append(text)
        self._consonants_cache = consonants
        return consonants

    @property
    def consonantNames(self) -> List[str]:
        if self._consonant_name_cache is not None:
            return self._consonant_name_cache
        names: List[str] = []
        for char in self.chars:
            text = char.text
            if char.isConsonant and is_char_consonant(text):
                names.append(char_to_name_map[text])
        self._consonant_name_cache = names
        return names

    def hasConsonantName(self, name: str) -> bool:
        if name not in consonant_name_to_char_map:
            raise ValueError(f"{name} is not a valid value")
        return name in self.consonantNames

    @property
    def hasHalfVowel(self) -> bool:
        return bool(re.search(r"[\u05B1-\u05B3]", self.text))

    @property
    def hasLongVowel(self) -> bool:
        return bool(re.search(r"[\u05B5\u05B8\u05B9\u05BA]", self.text))

    @property
    def hasMetheg(self) -> bool:
        return self.hasMeteg

    @property
    def _has_meteg_character(self) -> bool:
        return bool(meteg.search(self.text))

    @property
    def hasMeteg(self) -> bool:
        if not self._has_meteg_character:
            return False
        nxt = self.next
        while nxt is not None:
            if isinstance(nxt, Cluster):
                next_text = nxt.text
                if meteg.search(next_text):
                    return True
                if re.search(r"\u05C3", next_text):
                    return False
                nxt = nxt.next
            else:
                break
        return True

    @property
    def hasSheva(self) -> bool:
        return bool(re.search(r"\u05B0", self.text))

    @property
    def hasShewa(self) -> bool:
        return self.hasSheva

    @property
    def hasShortVowel(self) -> bool:
        return bool(re.search(r"[\u05B4\u05B6\u05B7\u05BB\u05C7]", self.text))

    @property
    def hasSilluq(self) -> bool:
        if self._has_meteg_character and not self.hasMeteg:
            return True
        return False

    def hasTaamName(self, name: str) -> bool:
        if name not in taamim_name_to_char_map:
            raise ValueError(f"{name} is not a valid value")
        return name in self.taamimNames

    @property
    def hasTaamim(self) -> bool:
        return bool(taamim.search(self.text))

    @property
    def hasVowel(self) -> bool:
        return self.hasLongVowel or self.hasShortVowel or self.hasHalfVowel

    @property
    def hasDagesh(self) -> bool:
        """True if the cluster contains a dagesh (U+05BC)."""
        return bool(re.search(r"\u05BC", self.text))

    def hasVowelName(self, name: str) -> bool:
        if name not in vowel_name_to_char_map:
            raise ValueError(f"{name} is not a valid value")
        return name in self.vowelNames

    @property
    def isMater(self) -> bool:
        nxt_is_shureq = self.next.isShureq if isinstance(self.next, Cluster) else False
        if not self.hasVowel and not self.isShureq and not self.hasSheva and not nxt_is_shureq:
            text = self.text
            prev_text = self.prev.text if isinstance(self.prev, Cluster) else ""
            if not re.search(r"[היו](?!\u05BC)", text):
                return False
            if re.search(r"ה", text) and re.search(r"\u05B8", prev_text):
                return True
            if re.search(r"ו", text) and re.search(r"\u05B9", prev_text):
                return True
            if re.search(r"י", text) and re.search(r"\u05B4|\u05B5|\u05B6", prev_text):
                return True
        return False

    @property
    def isNotHebrew(self) -> bool:
        return not bool(heb_chars.search(self.text))

    @property
    def isPunctuation(self) -> bool:
        punctuation_only = re.compile(rf"^{punctuation.pattern}+$")
        return bool(punctuation_only.search(self.text))

    @property
    def isShureq(self) -> bool:
        shureq = re.compile(r"\u05D5\u05BC")
        prv_has_vowel = False
        if self.prev is not None and self.prev.value is not None:
            prv_has_vowel = bool(getattr(self.prev.value, "hasVowel", False))
        if not self.hasVowel and not self.hasSheva and not prv_has_vowel:
            return bool(shureq.search(self.text))
        return False

    @property
    def isTaam(self) -> bool:
        return self.isPunctuation

    @property
    def original(self) -> str:
        return self._original

    @property
    def syllable(self) -> Optional["Syllable"]:
        return self._syllable

    @syllable.setter
    def syllable(self, syllable: Optional["Syllable"]) -> None:
        self._syllable = syllable

    @property
    def taamim(self) -> List[str]:
        if self._taamim_cache is not None:
            return self._taamim_cache
        chars: List[str] = []
        for char in self.chars:
            if char.isTaamim and is_char_taam(char.text):
                chars.append(char.text)
        self._taamim_cache = chars
        return chars

    @property
    def taamimNames(self) -> List[str]:
        if self._taamim_names_cache is not None:
            return self._taamim_names_cache
        names: List[str] = []
        for char in self.chars:
            text = char.text
            if char.isTaamim and is_char_taam(text):
                names.append(char_to_name_map[text])
        self._taamim_names_cache = names
        return names

    @property
    def text(self) -> str:
        return "".join(char.text for char in self.chars)

    @property
    def vowelNames(self) -> List[str]:
        if self._vowel_names_cache is not None:
            return self._vowel_names_cache
        names: List[str] = []
        for char in self.chars:
            if char.isVowel and is_char_vowel(char.text):
                names.append(char_to_name_map[char.text])
        self._vowel_names_cache = names
        return names

    @property
    def vowels(self) -> List[str]:
        if self._vowels_cache is not None:
            return self._vowels_cache
        vowels_list: List[str] = []
        for char in self.chars:
            text = char.text
            if char.isVowel and is_char_vowel(text):
                vowels_list.append(text)
        self._vowels_cache = vowels_list
        return vowels_list

    def __repr__(self) -> str:
        return f"Cluster({self.text!r})"
