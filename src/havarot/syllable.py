"""Syllable linguistic unit (ported from havarotjs)."""

from __future__ import annotations

import re
from typing import List, Optional, Tuple, TYPE_CHECKING

from .node import Node
from .utils.char_map import (
    consonant_name_to_char_map,
    taamim_name_to_char_map,
    vowel_char_to_name_map,
    vowel_name_to_char_map,
)
from .utils.remove_taamim import remove_taamim

if TYPE_CHECKING:
    from .cluster import Cluster
    from .word import Word

syl_vowel_char_to_name_map = {
    **vowel_char_to_name_map,
    "\u05B0": "SHEVA",
    "\u05D5\u05BC": "SHUREQ",
}

syl_vowel_name_to_char_map = {
    **vowel_name_to_char_map,
    "SHEVA": "\u05B0",
    "SHUREQ": "\u05D5\u05BC",
}


class Syllable(Node["Syllable"]):
    """A subunit of a Word: onset, nucleus, coda."""

    def __init__(
        self,
        clusters: List["Cluster"],
        *,
        isClosed: bool = False,
        isAccented: bool = False,
        isFinal: bool = False,
    ) -> None:
        super().__init__()
        self.value = self
        self._clusters = clusters
        self._is_closed = isClosed
        self._is_accented = isAccented
        self._is_final = isFinal
        self._cached_structure: Optional[Tuple[str, str, str]] = None
        self._cached_structure_with_gemination: Optional[Tuple[str, str, str]] = None
        self._vowels_cache: Optional[List[str]] = None
        self._vowel_names_cache: Optional[List[str]] = None
        self._word: Optional["Word"] = None

    @property
    def chars(self):
        return [c for cluster in self.clusters for c in cluster.chars]

    @property
    def clusters(self) -> List["Cluster"]:
        return self._clusters

    @property
    def coda(self) -> str:
        return self.structure()[2]

    @property
    def codaWithGemination(self) -> str:
        return self.structure(True)[2]

    @property
    def consonants(self) -> List[str]:
        return [c for cluster in self.clusters for c in cluster.consonants]

    @property
    def consonantNames(self) -> List[str]:
        return [c for cluster in self.clusters for c in cluster.consonantNames]

    def hasConsonantName(self, name: str) -> bool:
        if name not in consonant_name_to_char_map:
            raise ValueError(f"{name} is not a valid value")
        return name in self.consonantNames

    def hasVowelName(self, name: str) -> bool:
        if name not in syl_vowel_name_to_char_map:
            raise ValueError(f"{name} is not a valid value")
        return name in self.vowelNames

    def hasTaamName(self, name: str) -> bool:
        if name not in taamim_name_to_char_map:
            raise ValueError(f"{name} is not a valid value")
        return name in self.taamimNames

    @property
    def isAccented(self) -> bool:
        return self._is_accented

    @isAccented.setter
    def isAccented(self, accented: bool) -> None:
        self._is_accented = accented

    @property
    def isClosed(self) -> bool:
        return self._is_closed

    @isClosed.setter
    def isClosed(self, closed: bool) -> None:
        self._is_closed = closed

    @property
    def isFinal(self) -> bool:
        return self._is_final

    @isFinal.setter
    def isFinal(self, final: bool) -> None:
        self._is_final = final

    @property
    def nucleus(self) -> str:
        return self.structure()[1]

    @property
    def onset(self) -> str:
        return self.structure()[0]

    def structure(self, withGemination: bool = False) -> Tuple[str, str, str]:
        if withGemination and self._cached_structure_with_gemination is not None:
            return self._cached_structure_with_gemination
        if not withGemination and self._cached_structure is not None:
            return self._cached_structure

        he_clusters = [c for c in self.clusters if not c.isNotHebrew]
        if not he_clusters:
            structure: Tuple[str, str, str] = ("", "", "")
            self._cached_structure = structure
            self._cached_structure_with_gemination = structure
            return structure

        first = he_clusters[0]
        if first.isShureq:
            structure = (
                "",
                first.text,
                "".join(c.text for c in he_clusters[1:]),
            )
            self._cached_structure = structure
            self._cached_structure_with_gemination = structure
            return structure

        if self.isFinal and not self.isClosed:
            match_furtive = re.search(
                r"(\u05D7|\u05E2|\u05D4\u05BC)(\u05B7)(\u05C3)?$",
                self.text,
            )
            if match_furtive:
                structure = (
                    "",
                    match_furtive.group(2),
                    match_furtive.group(1) + (match_furtive.group(3) or ""),
                )
                self._cached_structure = structure
                self._cached_structure_with_gemination = structure
                return structure

        onset, nucleus, coda = "", "", ""
        i = 0
        while i < len(first.chars) and (
            first.chars[i].sequencePosition < 3 or first.chars[i].text == "\u05BD"
        ):
            onset += first.chars[i].text
            i += 1
        while i < len(first.chars) and first.chars[i].sequencePosition in (3, 4):
            nucleus += first.chars[i].text
            i += 1
        while i < len(first.chars):
            coda += first.chars[i].text
            i += 1

        clusters_processed = 1
        if (
            len(coda) == 0
            and len(he_clusters) > 1
            and (he_clusters[1].isShureq or he_clusters[1].isMater)
        ):
            nucleus += he_clusters[1].text
            clusters_processed += 1

        coda += "".join(c.text for c in he_clusters[clusters_processed:])

        if withGemination and len(coda) == 0 and not re.search(r"\u05B0", nucleus):
            if isinstance(self.next, Syllable):
                next_onset = self.next.onset
                if re.search(r"\u05BC", next_onset):
                    coda = next_onset

        structure = (onset, nucleus, coda)
        if withGemination:
            self._cached_structure_with_gemination = structure
        else:
            self._cached_structure = structure
        return structure

    @property
    def taamim(self) -> List[str]:
        return [t for c in self.clusters for t in c.taamim]

    @property
    def taamimNames(self) -> List[str]:
        return [t for c in self.clusters for t in c.taamimNames]

    @property
    def text(self) -> str:
        return "".join(c.text for c in self.clusters)

    @property
    def vowelNames(self) -> List[str]:
        if self._vowel_names_cache is not None:
            return self._vowel_names_cache
        names: List[str] = []
        for vowel in self.vowels:
            if vowel in syl_vowel_char_to_name_map:
                names.append(syl_vowel_char_to_name_map[vowel])
        self._vowel_names_cache = names
        return names

    @property
    def vowels(self) -> List[str]:
        if self._vowels_cache is not None:
            return self._vowels_cache
        nucleus = self.nucleus
        no_taamim, _ = remove_taamim(nucleus)
        shureq = syl_vowel_name_to_char_map["SHUREQ"]
        shureq_presentation = "\uFB35"
        vowels_list: List[str] = []
        for v in no_taamim.replace(shureq, shureq_presentation):
            if v in syl_vowel_char_to_name_map:
                vowels_list.append(v)
            if v == shureq_presentation:
                vowels_list.append(shureq)
        self._vowels_cache = vowels_list
        return vowels_list

    @property
    def word(self) -> Optional["Word"]:
        return self._word

    @word.setter
    def word(self, word: Optional["Word"]) -> None:
        self._word = word

    def __repr__(self) -> str:
        return f"Syllable({self.text!r})"
