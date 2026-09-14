"""Word subunit of Text (ported from havarotjs)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .cluster import Cluster
from .node import Node
from .syllable import Syllable
from .utils.regular_expressions import cluster_split_group, jerusalem_test
from .utils.syllabifier import syllabify


class Word(Node["Word"]):
    """A subunit of Text: text separated by spaces or maqqefs."""

    _non_characters = re.compile(r"[^\u05D0-\u05F4]")

    def __init__(
        self,
        text: str,
        syl_opts: Dict[str, Any],
        original: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.value = self
        self._text = text
        self._original = original if original is not None else text
        self._syl_opts = syl_opts
        start_match = re.match(r"^\s*", text)
        end_match = re.search(r"\s*$", text)
        self.whiteSpaceBefore: Optional[str] = start_match.group(0) if start_match else None
        self.whiteSpaceAfter: Optional[str] = end_match.group(0) if end_match else None

    @property
    def chars(self):
        return [c for cluster in self.clusters for c in cluster.chars]

    def _make_clusters(self, word: str) -> List[Cluster]:
        match = jerusalem_test.search(word)
        if match and match.groupdict():
            captured = match.group(0)
            hiriq = match.group("hiriq")
            vowel = match.group("vowel")
            taamim_match = match.group("taamimMatch")
            mem = match.group("mem")
            partial = word.replace(captured, f"{vowel}{taamim_match}", 1)
            groups = cluster_split_group.split(partial) + [f"{hiriq}{mem}"]
            # filter empty like JS split behavior with lookahead
            groups = [g for g in groups if g]
            result: List[Cluster] = []
            for group in groups:
                if group == f"{hiriq}{mem}":
                    result.append(Cluster(group, True))
                else:
                    result.append(Cluster(group))
            return result
        parts = [g for g in cluster_split_group.split(word) if g]
        return [Cluster(group) for group in parts]

    @property
    def clusters(self) -> List[Cluster]:
        clusters = self._make_clusters(self.text)
        if not clusters:
            return []
        first = clusters[0]
        first.siblings = clusters[1:]
        return clusters

    @property
    def consonants(self) -> List[str]:
        return [c for cluster in self.clusters for c in cluster.consonants]

    @property
    def consonantNames(self) -> List[str]:
        return [c for cluster in self.clusters for c in cluster.consonantNames]

    def hasConsonantName(self, name: str) -> bool:
        return any(cluster.hasConsonantName(name) for cluster in self.clusters)

    @property
    def hasDivineName(self) -> bool:
        return bool(re.search(r"יהוה", self._non_characters.sub("", self.text)))

    def hasTaamName(self, name: str) -> bool:
        return any(syl.hasTaamName(name) for syl in self.syllables)

    def hasVowelName(self, name: str) -> bool:
        return any(syl.hasVowelName(name) for syl in self.syllables)

    @property
    def isDivineName(self) -> bool:
        return self._non_characters.sub("", self.text) == "יהוה"

    @property
    def isNotHebrew(self) -> bool:
        return False not in [c.isNotHebrew for c in self.clusters]

    @property
    def isInConstruct(self) -> bool:
        return "\u05BE" in self.text

    @property
    def original(self) -> str:
        return self._original.strip()

    @property
    def syllables(self) -> List[Syllable]:
        # JS /\w/ is ASCII-only [A-Za-z0-9_]; Python \w matches Hebrew letters.
        if re.search(r"[A-Za-z0-9_]", self.text) or self.isDivineName or self.isNotHebrew:
            syl = Syllable(self.clusters)
            syl.word = self
            return [syl]
        syllables = syllabify(self.clusters, self._syl_opts, self.isInConstruct)
        for syl in syllables:
            syl.word = self
        return syllables

    @property
    def taamim(self) -> List[str]:
        return [t for syl in self.syllables for t in syl.taamim]

    @property
    def taamimNames(self) -> List[str]:
        return [t for syl in self.syllables for t in syl.taamimNames]

    @property
    def text(self) -> str:
        return self._text.strip()

    @property
    def vowelNames(self) -> List[str]:
        return [v for syl in self.syllables for v in syl.vowelNames]

    @property
    def vowels(self) -> List[str]:
        return [v for syl in self.syllables for v in syl.vowels]

    def __repr__(self) -> str:
        return f"Word({self.text!r})"
