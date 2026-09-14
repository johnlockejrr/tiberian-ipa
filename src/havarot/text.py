"""Text entry point (ported from havarotjs)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .utils.holem_waw import holem_waw
from .utils.qamets_qatan import converts_qamets_qatan
from .utils.regular_expressions import split_group, taamim, taamim_capture_group
from .utils.sequence import sequence
from .word import Word

# Defaults matching hebrew-transliteration Tiberian / dump_oracle usage
DEFAULT_SYL_OPTS: Dict[str, Any] = {
    "allowNoNiqqud": True,
    "article": True,
    "holemHaser": "unique",
    "ketivQeres": [],
    "longVowels": True,
    "qametsQatan": True,
    "shevaAfterMeteg": True,
    "shevaWithMeteg": False,
    "sqnmlvy": True,
    "strict": False,
    "wawShureq": True,
}

KetivQere = Dict[str, Any]
SylOpts = Dict[str, Any]


class Text:
    """Process Hebrew text with niqqud into words / syllables / clusters / chars."""

    def __init__(self, text: str, options: Optional[SylOpts] = None) -> None:
        options = options or {}
        self._options = self._set_options(options)
        self._ketiv_qere_cache: Dict[str, str] = {}
        if self._options["allowNoNiqqud"]:
            self._original = text
        else:
            self._original = self._validate_input(text)

    @property
    def chars(self):
        return [c for cluster in self.clusters for c in cluster.chars]

    @property
    def clusters(self):
        return [c for syl in self.syllables for c in syl.clusters]

    @property
    def original(self) -> str:
        return self._original

    @property
    def syllables(self):
        return [s for word in self.words for s in word.syllables]

    @property
    def text(self) -> str:
        return "".join(f"{w.text}{w.whiteSpaceAfter or ''}" for w in self.words)

    @property
    def words(self) -> List[Word]:
        split = split_group.split(self._sanitized)
        groups = [g for g in split if g]
        words = []
        for original in groups:
            word = self._process_ketiv_qeres(original)
            words.append(
                Word(
                    word,
                    self._options,
                    original if word != original else None,
                )
            )
        if words:
            first, *rest = words
            first.siblings = rest
        return words

    def _apply_ketiv_qere(self, text: str, kq: KetivQere) -> Optional[str]:
        inp = kq.get("input", kq.get("ketiv"))
        output = kq.get("output", kq.get("qere"))
        if isinstance(inp, re.Pattern):
            if inp.search(text):
                if isinstance(output, str):
                    return output
                return output(text, inp)
        if inp == text:
            if isinstance(output, str):
                return output
            return output(text, inp)
        return None

    def _capture_taamim(self, text: str):
        return list(taamim_capture_group.finditer(text))

    def _process_ketiv_qeres(self, text: str) -> str:
        if text in self._ketiv_qere_cache:
            return self._ketiv_qere_cache[text]
        ketiv_qeres = self._options.get("ketivQeres") or []
        if not ketiv_qeres:
            return text
        for ketiv_qere in ketiv_qeres:
            start_match = re.match(r"^\s*", text)
            end_match = re.search(r"\s*$", text)
            white_space_before = start_match.group(0) if start_match else ""
            white_space_after = end_match.group(0) if end_match else ""
            text_without_taamim = (
                self._remove_taamim(text) if ketiv_qere.get("ignoreTaamim") else text
            ).strip()
            applied = self._apply_ketiv_qere(text_without_taamim, ketiv_qere)
            if not applied:
                return white_space_before + text.strip() + white_space_after
            taamim_chars = (
                self._capture_taamim(text) if ketiv_qere.get("captureTaamim") else None
            )
            new_text = (
                self._set_taamim(applied, taamim_chars) if taamim_chars else applied
            )
            self._ketiv_qere_cache[text] = new_text
            return white_space_before + new_text + white_space_after
        return text

    def _validate_input(self, text: str) -> str:
        niqqud = re.compile(r"[\u05B0-\u05BC\u05C7]")
        if not niqqud.search(text):
            raise ValueError("Text must contain niqqud")
        return text

    def _validate_ketiv_qeres(self, ketiv_qeres: Optional[List[KetivQere]]) -> bool:
        if not ketiv_qeres:
            return True
        for index, ketiv_qere in enumerate(ketiv_qeres):
            inp = ketiv_qere.get("input", ketiv_qere.get("ketiv"))
            output = ketiv_qere.get("output", ketiv_qere.get("qere"))
            if inp is None:
                raise ValueError(f"The ketivQere at index {index} must have an input")
            if not isinstance(inp, (str, re.Pattern)):
                raise ValueError(
                    f"The input property of the ketivQere at index {index} must be a string or RegExp"
                )
            if output is None:
                raise ValueError(f"The ketivQere at index {index} must have an output")
            if not isinstance(output, (str,)) and not callable(output):
                raise ValueError(
                    f"The output property of the ketivQere at index {index} must be a string or function"
                )
            ignore = ketiv_qere.get("ignoreTaamim")
            if ignore is not None and not isinstance(ignore, bool):
                raise ValueError(
                    f"The ignoreTaamim property of the ketivQere at index {index} must be a boolean"
                )
            capture = ketiv_qere.get("captureTaamim")
            if capture is not None and not isinstance(capture, bool):
                raise ValueError(
                    f"The captureTaamim property of the ketivQere at index {index} must be a boolean"
                )
        return True

    def _validate_options(self, options: SylOpts) -> SylOpts:
        valid_opts = {
            "allowNoNiqqud",
            "article",
            "holemHaser",
            "ketivQeres",
            "longVowels",
            "qametsQatan",
            "shevaAfterMeteg",
            "shevaWithMeteg",
            "sqnmlvy",
            "strict",
            "wawShureq",
        }
        for k, v in options.items():
            if k not in valid_opts:
                raise ValueError(f"{k} is not a valid option")
            if k == "ketivQeres":
                self._validate_ketiv_qeres(v)
                continue
            if k == "holemHaser" and str(v) not in ("update", "preserve", "remove", "unique"):
                raise ValueError(f"The value {v} is not a valid option for {k}")
            if not isinstance(v, bool) and k != "holemHaser" and k != "ketivQeres":
                raise ValueError(f"The value {v} is not a valid option for {k}")
        return options

    def _remove_taamim(self, text: str) -> str:
        return taamim.sub("", text)

    def _set_options(self, options: SylOpts) -> SylOpts:
        valid = self._validate_options(options)
        ketiv = valid.get("ketivQeres") or []
        mapped_ketiv = [
            {
                **kq,
                "captureTaamim": kq.get("captureTaamim", False),
                "ignoreTaamim": kq.get("ignoreTaamim", True),
            }
            for kq in ketiv
        ]
        return {
            "allowNoNiqqud": valid.get("allowNoNiqqud", DEFAULT_SYL_OPTS["allowNoNiqqud"]),
            "article": valid.get("article", DEFAULT_SYL_OPTS["article"]),
            "holemHaser": valid.get("holemHaser", DEFAULT_SYL_OPTS["holemHaser"]),
            "ketivQeres": mapped_ketiv,
            "longVowels": valid.get("longVowels", DEFAULT_SYL_OPTS["longVowels"]),
            "qametsQatan": valid.get("qametsQatan", DEFAULT_SYL_OPTS["qametsQatan"]),
            "shevaAfterMeteg": valid.get(
                "shevaAfterMeteg", DEFAULT_SYL_OPTS["shevaAfterMeteg"]
            ),
            "shevaWithMeteg": valid.get(
                "shevaWithMeteg", DEFAULT_SYL_OPTS["shevaWithMeteg"]
            ),
            "sqnmlvy": valid.get("sqnmlvy", DEFAULT_SYL_OPTS["sqnmlvy"]),
            "strict": valid.get("strict", DEFAULT_SYL_OPTS["strict"]),
            "wawShureq": valid.get("wawShureq", DEFAULT_SYL_OPTS["wawShureq"]),
        }

    def _set_taamim(self, new_text: str, taamim_capture: List[re.Match]) -> str:
        text = new_text
        for group in taamim_capture:
            idx = group.start()
            text = text[:idx] + group.group(1) + text[idx:]
        return text

    @property
    def _normalized(self) -> str:
        from unicodedata import normalize

        return normalize("NFKD", self.original)

    @property
    def _sanitized(self) -> str:
        text = self._normalized.strip()
        sequenced_char = [c for cluster_chars in sequence(text) for c in cluster_chars]
        sequenced_text = "".join(c.text for c in sequenced_char)
        text_arr = [g for g in split_group.split(sequenced_text) if g]
        map_qqatan = (
            [converts_qamets_qatan(w) for w in text_arr]
            if self._options["qametsQatan"]
            else text_arr
        )
        map_holem = [holem_waw(w, self._options) for w in map_qqatan]
        return "".join(map_holem)

    def __repr__(self) -> str:
        return f"Text({self.original!r})"
