"""Transliterate Hebrew text according to a Schema (port of transliterate.js)."""

from __future__ import annotations

from typing import Any

from havarot import Text, Word

from hebtrans.rules import syl_rules, word_rules
from hebtrans.schema import Schema


def _get_syl_opts(schema: Schema) -> dict[str, Any]:
    return {
        "allowNoNiqqud": schema.get("allowNoNiqqud"),
        "article": schema.get("article"),
        "holemHaser": schema.get("holemHaser"),
        "ketivQeres": schema.get("ketivQeres"),
        "longVowels": schema.get("longVowels"),
        "qametsQatan": schema.get("qametsQatan"),
        "shevaAfterMeteg": schema.get("shevaAfterMeteg"),
        "shevaWithMeteg": schema.get("shevaWithMeteg"),
        "sqnmlvy": schema.get("sqnmlvy"),
        "strict": schema.get("strict"),
        "wawShureq": schema.get("wawShureq"),
    }


def transliterate(text: str | Text, schema: Schema | dict[str, Any] | None = None) -> str:
    """Transliterate Hebrew text according to a given schema.

    Parameters
    ----------
    text:
        A Hebrew string or havarot ``Text``.
    schema:
        A ``Schema`` instance or mapping. Required for full control (no SBL default
        is bundled in the native port — pass the Tiberian schema for IPA).
    """
    if schema is None:
        raise ValueError("schema is required (pass Schema or dict)")
    trans_schema = schema if isinstance(schema, Schema) else Schema(schema)

    syl_opts = {k: v for k, v in _get_syl_opts(trans_schema).items() if v is not None}
    if isinstance(text, Text):
        new_text = text
    else:
        new_text = Text(text, syl_opts)

    parts: list[str] = []
    for word in new_text.words:
        transliteration = word_rules(word, trans_schema)
        if not isinstance(transliteration, Word):
            parts.append(f"{transliteration}{word.whiteSpaceAfter or ''}")
            continue

        syl_parts: list[str] = []
        for i, s in enumerate(transliteration.syllables):
            piece = syl_rules(s, trans_schema)
            if i == 0:
                syl_parts.append(piece)
                continue
            sep = trans_schema.get("SYLLABLE_SEPARATOR")
            if not sep:
                syl_parts.append(piece)
            elif sep in piece:
                syl_parts.append(piece)
            else:
                syl_parts.append(sep + piece)
        parts.append(f"{''.join(syl_parts)}{word.whiteSpaceAfter or ''}")

    result = "".join(parts)
    on_complete = trans_schema.get("ON_COMPLETE")
    if on_complete:
        try:
            result = on_complete(
                result,
                {
                    "original": new_text.original,
                    "schema": trans_schema,
                    "text": new_text,
                },
            )
        except TypeError:
            result = on_complete(result)
    return result
