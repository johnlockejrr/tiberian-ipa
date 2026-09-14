"""Public API: Tiberian IPA transcription (native pure-Python engine)."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from hebtrans import transliterate
from tiberian_ipa.schema import tiberian

# Hebrew cantillation / teʿamim (U+0591–U+05AF). Meteg/silluq (U+05BD) alone
# does not count — primary stress placement needs teʿamim for a faithful reading.
_CANTILLATION = re.compile(r"[\u0591-\u05AF]")

_UNACCENTED_WARNING = (
    "Input has no cantillation marks (teʿamim). Stress, length, and epenthesis "
    "may be approximate — basic (unaccented) transcription only."
)


@dataclass
class Result:
    input: str
    reading: str
    ipa: str | None
    provenance: list[dict[str, Any]] = field(default_factory=list)
    unresolved: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    profile: str = "forte_lene"
    mode: str = "native-tiberian"

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": self.input,
            "reading": self.reading,
            "ipa": self.ipa,
            "provenance": self.provenance,
            "unresolved": self.unresolved,
            "warnings": self.warnings,
            "profile": self.profile,
            "mode": self.mode,
        }


def has_cantillation(text: str) -> bool:
    """True if text contains at least one Hebrew cantillation mark (teʿamim)."""
    return bool(_CANTILLATION.search(text))


def _has_hebrew(text: str) -> bool:
    return any("HEBREW" in unicodedata.name(ch, "") for ch in text if ch.strip())


def _bare_ipa(ipa: str | None) -> str | None:
    if ipa is None:
        return None
    out = str(ipa).strip().replace("\\-", "-")
    if out.startswith("[") and out.endswith("]"):
        out = out[1:-1].strip()
    out = out.replace("[", "").replace("]", "")
    out = " ".join(out.split())
    return out.strip() or None


def transcribe(
    text: str,
    profile: str | None = None,
    *,
    allow_unaccented: bool = False,
) -> Result:
    """Transcribe pointed Biblical Hebrew to Tiberian IPA.

    Uses the native havarot syllabifier + hebtrans rules engine with the
    Tiberian schema ported from ``docs/tiberian.ts``.

    By default, input must include cantillation marks (teʿamim). Without them,
    stress/length cannot be placed faithfully. Pass ``allow_unaccented=True``
    to proceed with a basic reading and a warning.
    """
    reading = unicodedata.normalize("NFD", text)
    provenance: list[dict[str, Any]] = [
        {"stage": "normalize", "form": "NFD"},
    ]
    unresolved: list[dict[str, Any]] = []
    warnings: list[str] = []
    prof = profile or "forte_lene"

    if not _has_hebrew(reading):
        unresolved.append(
            {
                "span": text,
                "reason": "no_hebrew_characters",
                "message": "Input contains no Hebrew characters.",
            }
        )
        return Result(
            input=text,
            reading=reading,
            ipa=None,
            provenance=provenance,
            unresolved=unresolved,
            warnings=warnings,
            profile=prof,
            mode="none",
        )

    accented = has_cantillation(reading)
    provenance.append(
        {
            "stage": "cantillation_check",
            "has_cantillation": accented,
            "allow_unaccented": allow_unaccented,
        }
    )

    if not accented and not allow_unaccented:
        unresolved.append(
            {
                "span": text,
                "reason": "no_cantillation",
                "message": (
                    "Input has no cantillation marks (teʿamim). "
                    "Faithful Tiberian IPA needs accents for stress. "
                    "Re-run with allow_unaccented=True / --allow-unaccented "
                    "for a basic (approximate) transcription."
                ),
            }
        )
        return Result(
            input=text,
            reading=reading,
            ipa=None,
            provenance=provenance,
            unresolved=unresolved,
            warnings=warnings,
            profile=prof,
            mode="refused-unaccented",
        )

    if not accented and allow_unaccented:
        warnings.append(_UNACCENTED_WARNING)

    try:
        raw = transliterate(reading, tiberian)
        ipa = _bare_ipa(raw)
        mode = "native-tiberian-basic" if not accented else "native-tiberian"
        provenance.append(
            {
                "stage": "rules",
                "engine": "hebtrans",
                "schema": "docs/tiberian.ts",
                "syllabifier": "havarot",
                "stream": prof,
                "faithful": accented,
            }
        )
        return Result(
            input=text,
            reading=reading,
            ipa=ipa,
            provenance=provenance,
            unresolved=unresolved,
            warnings=warnings,
            profile=prof,
            mode=mode,
        )
    except Exception as exc:  # noqa: BLE001 — surface engine errors in Result
        unresolved.append(
            {
                "span": reading,
                "reason": "native_engine_error",
                "message": str(exc),
            }
        )
        return Result(
            input=text,
            reading=reading,
            ipa=None,
            provenance=provenance,
            unresolved=unresolved,
            warnings=warnings,
            profile=prof,
            mode="error",
        )
