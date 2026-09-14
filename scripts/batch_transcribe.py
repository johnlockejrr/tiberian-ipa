#!/usr/bin/env python3
"""Batch-transcribe a pointed Hebrew text file to Tiberian IPA.

Designed for chapter files like Genesis_1.txt where verses look like::

    1 בְּרֵאשִׁ֖ית …׃ 2 וְהָאָ֗רֶץ …׃
    6 וַיֹּ֣אמֶר …׃ {פ}

Usage::

    python scripts/batch_transcribe.py -i ../Genesis_1.txt -o Genesis_1.ipa.txt
    python scripts/batch_transcribe.py -i ../Genesis_1.txt -o out.jsonl --format jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from tiberian_ipa import transcribe

# ASCII verse number at line start or after whitespace (SBL / Mechon Mamre style).
_VERSE_START = re.compile(r"(?:(?<=^)|(?<=\s))(\d+)\s+", re.UNICODE)
# Paragraph / closed-section markers often left in WLC exports.
_SECTION_MARK = re.compile(r"\s*\{[פס]\}")
# Soft hyphen / BOM leftovers
_JUNK = re.compile(r"[\ufeff\u00ad]")


def parse_verses(text: str) -> list[tuple[str, str]]:
    """Return ``[(verse_number, hebrew), ...]`` from a chapter blob."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _JUNK.sub("", text).strip()
    if not text:
        return []

    matches = list(_VERSE_START.finditer(text))
    if not matches:
        # Single blob without verse numbers
        cleaned = _SECTION_MARK.sub("", text).strip()
        return [("?", cleaned)] if cleaned else []

    verses: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        num = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heb = _SECTION_MARK.sub("", text[start:end]).strip()
        if heb:
            verses.append((num, heb))
    return verses


def format_line(num: str, ipa: str | None, *, hebrew: str, mode: str) -> str:
    if ipa is None:
        return f"{num}\t# FAILED ({mode})"
    return f"{num}\t{ipa}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Batch Tiberian IPA transcription (input file → output file).",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Input UTF-8 text (verse-numbered Hebrew chapter)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output path (.txt or .jsonl)",
    )
    parser.add_argument(
        "--format",
        choices=("txt", "jsonl"),
        default=None,
        help="Output format (default: jsonl if --output ends with .jsonl, else txt)",
    )
    parser.add_argument(
        "--allow-unaccented",
        action="store_true",
        help="Allow verses without teʿamim (basic IPA + warning)",
    )
    parser.add_argument(
        "-p",
        "--profile",
        default="forte_lene",
        help="Pronunciation stream (default: forte_lene)",
    )
    args = parser.parse_args(argv)

    if not args.input.is_file():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 1

    fmt = args.format
    if fmt is None:
        fmt = "jsonl" if args.output.suffix.lower() == ".jsonl" else "txt"

    raw = args.input.read_text(encoding="utf-8")
    verses = parse_verses(raw)
    if not verses:
        print("no verses found in input", file=sys.stderr)
        return 1

    lines_out: list[str] = []
    n_ok = 0
    n_fail = 0

    for num, heb in verses:
        result = transcribe(
            heb,
            profile=args.profile,
            allow_unaccented=args.allow_unaccented,
        )
        if result.ipa is None:
            n_fail += 1
            for w in result.warnings:
                print(f"# {num}: warning: {w}", file=sys.stderr)
            for u in result.unresolved:
                print(
                    f"# {num}: {u.get('reason')}: {u.get('message') or ''}",
                    file=sys.stderr,
                )
        else:
            n_ok += 1
            for w in result.warnings:
                print(f"# {num}: warning: {w}", file=sys.stderr)

        if fmt == "jsonl":
            lines_out.append(
                json.dumps(
                    {
                        "verse": num,
                        "hebrew": heb,
                        "ipa": result.ipa,
                        "mode": result.mode,
                        "warnings": result.warnings,
                        "unresolved": result.unresolved,
                    },
                    ensure_ascii=False,
                )
            )
        else:
            lines_out.append(
                format_line(num, result.ipa, hebrew=heb, mode=result.mode)
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print(
        f"wrote {args.output} ({n_ok} ok, {n_fail} failed, {len(verses)} verses)",
        file=sys.stderr,
    )
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
