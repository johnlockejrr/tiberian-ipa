"""Native Tiberian IPA package (schema + API)."""

from tiberian_ipa.api import Result, has_cantillation, transcribe
from tiberian_ipa.schema import build_tiberian_schema, tiberian

__all__ = [
    "Result",
    "has_cantillation",
    "transcribe",
    "tiberian",
    "build_tiberian_schema",
]
