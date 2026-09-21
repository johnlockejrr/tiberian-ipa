#!/usr/bin/env python3
"""Batch-transcribe pointed Hebrew to Tiberian IPA.

Supports:

1. Chapter blobs (e.g. ``Genesis_1.txt``)::

       1 בְּרֵאשִׁ֖ית …׃ 2 וְהָאָ֗רֶץ …׃

   Output (txt)::

       1\\t<ipa>
       2\\t<ipa>

2. Pipe-CSV like ``BHS5.csv``::

       book_number|chapter|verse|text

   Output (same CSV shape, IPA in the text column)::

       book_number|chapter|verse|ipa

Preprocessing (always):

- Strip HTML (e.g. ``<i>[32:1]</i>`` English versification notes)
- Strip Petucha / Setuma markers (``׃ פ`` / ``׃ ס`` / ``{פ}`` / ``{ס}``) so they
  are **not** turned into IPA (bare ``פ`` otherwise becomes ``ˈf``)
- Apply known WLC/BHS pointing repairs (see ``BHS_POINTING_FIXES``)

Qere / Ketiv:

- IPA follows what is **read** (Qere), not the bare consonantal Ketiv.
- This engine applies perpetual Qere already in the Tiberian schema
  (e.g. יהוה → Adonai/Elohim, הִוא → הִיא).
- Plain BHS/WLC-style lines are usually the hybrid (Ketiv consonants + Qere
  vowels). Without a separate Qere apparatus, full Qere-consonant restoration
  is not available for every ketiv/qere pair.

Usage::

    python scripts/batch_transcribe.py -i BHS5.csv -o BHS5.ipa.csv
    python scripts/batch_transcribe.py -i Genesis_1.txt -o Genesis_1.ipa.txt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from tiberian_ipa import transcribe

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None  # type: ignore[assignment]

# --- chapter-blob parsing ---------------------------------------------------

_VERSE_START = re.compile(r"(?:(?<=^)|(?<=\s))(\d+)\s+", re.UNICODE)
_SECTION_BRACE = re.compile(r"\s*\{[פס]\}")
_JUNK = re.compile(r"[\ufeff\u00ad]")

# --- shared cleanup ---------------------------------------------------------

_HTML_TAG = re.compile(r"<[^>]+>")
# Petucha / Setuma after sof pasuq (BHS/WLC paragraph markers — not speech).
_PETUCHA_SETUMA = re.compile(r"(?:׃|\.)\s*[פס]\s*$")
_PETUCHA_SETUMA_SPACE = re.compile(r"\s+[פס]\s*$")

# Known defective WLC/BHS5 pointing that breaks syllabification (JS fails the same).
# Apply as literal substring replacements before IPA.
BHS_POINTING_FIXES: tuple[tuple[str, str], ...] = (
    # 1Sam 2:35 — missing ḥiriq on he of hithpael
    ("וְהתְהַלֵּ֥ךְ", "וְהִתְהַלֵּ֥ךְ"),
    # 2Kgs 21:26 — sheva + holem on bet; should be holem only
    ("וַיִּקְבְֹּ֥ר", "וַיִּקְבֹּ֥ר"),
    # Song 5:11 — sheva before shureq; should be qubuts on vav
    ("קְוּצֹּותָיו֙", "קְוֻצֹּותָיו֙"),
)


def clean_hebrew(text: str) -> str:
    """Normalize verse text for IPA (strip markup / section letters, keep teʿamim)."""
    text = _JUNK.sub("", text)
    text = _HTML_TAG.sub("", text)
    text = _SECTION_BRACE.sub("", text)
    text = _PETUCHA_SETUMA.sub("׃", text)
    text = _PETUCHA_SETUMA_SPACE.sub("", text)
    for bad, good in BHS_POINTING_FIXES:
        if bad in text:
            text = text.replace(bad, good)
    return text.strip()


def parse_verses(text: str) -> list[tuple[str, str]]:
    """Return ``[(verse_number, hebrew), ...]`` from a chapter blob."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _JUNK.sub("", text).strip()
    if not text:
        return []

    matches = list(_VERSE_START.finditer(text))
    if not matches:
        cleaned = clean_hebrew(text)
        return [("?", cleaned)] if cleaned else []

    verses: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        num = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heb = clean_hebrew(text[start:end])
        if heb:
            verses.append((num, heb))
    return verses


def parse_bhs_csv(text: str) -> list[tuple[str, str, str, str]]:
    """Return ``[(book, chapter, verse, hebrew), ...]`` from pipe-CSV."""
    rows: list[tuple[str, str, str, str]] = []
    for i, line in enumerate(text.replace("\r\n", "\n").replace("\r", "\n").splitlines()):
        line = line.strip()
        if not line:
            continue
        if i == 0 and line.lower().startswith("book_number"):
            continue
        parts = line.split("|", 3)
        if len(parts) < 4:
            print(f"# skip malformed line {i + 1}: {line[:60]!r}", file=sys.stderr)
            continue
        book, chapter, verse, heb = parts
        heb = clean_hebrew(heb)
        if heb:
            rows.append((book, chapter, verse, heb))
    return rows


def format_line(num: str, ipa: str | None, *, mode: str) -> str:
    if ipa is None:
        return f"{num}\t# FAILED ({mode})"
    return f"{num}\t{ipa}"


def _progress(iterable, *, total: int, desc: str, disable: bool):
    if disable or tqdm is None:
        if not disable and tqdm is None:
            print("# tip: pip install tqdm  for a progress bar", file=sys.stderr)
        return iterable
    return tqdm(iterable, total=total, desc=desc, unit="verse", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Batch Tiberian IPA transcription (chapter text or BHS5-style CSV).",
    )
    parser.add_argument("-i", "--input", type=Path, required=True, help="Input UTF-8 file")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output path")
    parser.add_argument(
        "--format",
        choices=("auto", "txt", "jsonl", "csv"),
        default="auto",
        help="Output format (auto: .csv→csv, .jsonl→jsonl, else txt; CSV in→csv)",
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
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process only the first N verses (0 = all; useful for smoke tests)",
    )
    args = parser.parse_args(argv)

    if not args.input.is_file():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 1

    raw = args.input.read_text(encoding="utf-8")
    is_csv_in = (
        args.input.suffix.lower() == ".csv"
        or raw.lstrip().lower().startswith("book_number|")
    )

    fmt = args.format
    if fmt == "auto":
        if args.output.suffix.lower() == ".jsonl":
            fmt = "jsonl"
        elif is_csv_in or args.output.suffix.lower() == ".csv":
            fmt = "csv"
        else:
            fmt = "txt"

    if is_csv_in:
        records = parse_bhs_csv(raw)
        # normalize to (label, hebrew, meta)
        items = [
            (f"{b}:{c}:{v}", heb, {"book": b, "chapter": c, "verse": v, "hebrew": heb})
            for b, c, v, heb in records
        ]
    else:
        verses = parse_verses(raw)
        items = [(num, heb, {"verse": num, "hebrew": heb}) for num, heb in verses]

    if args.limit and args.limit > 0:
        items = items[: args.limit]

    if not items:
        print("no verses found in input", file=sys.stderr)
        return 1

    lines_out: list[str] = []
    if fmt == "csv":
        lines_out.append("book_number|chapter|verse|text")

    n_ok = 0
    n_fail = 0

    for label, heb, meta in _progress(
        items, total=len(items), desc="tiberian-ipa", disable=args.no_progress
    ):
        result = transcribe(
            heb,
            profile=args.profile,
            allow_unaccented=args.allow_unaccented,
        )
        if result.ipa is None:
            n_fail += 1
            for w in result.warnings:
                print(f"# {label}: warning: {w}", file=sys.stderr)
            for u in result.unresolved:
                print(
                    f"# {label}: {u.get('reason')}: {u.get('message') or ''}",
                    file=sys.stderr,
                )
        else:
            n_ok += 1
            for w in result.warnings:
                print(f"# {label}: warning: {w}", file=sys.stderr)

        if fmt == "jsonl":
            payload = {
                **meta,
                "ipa": result.ipa,
                "mode": result.mode,
                "warnings": result.warnings,
                "unresolved": result.unresolved,
            }
            lines_out.append(json.dumps(payload, ensure_ascii=False))
        elif fmt == "csv":
            book = meta.get("book", "?")
            chapter = meta.get("chapter", "?")
            verse = meta.get("verse", meta.get("verse", "?"))
            cell = result.ipa if result.ipa is not None else f"# FAILED ({result.mode})"
            # Keep pipe-CSV; IPA has no pipes
            lines_out.append(f"{book}|{chapter}|{verse}|{cell}")
        else:
            num = str(meta.get("verse", label))
            lines_out.append(format_line(num, result.ipa, mode=result.mode))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print(
        f"wrote {args.output} ({n_ok} ok, {n_fail} failed, {len(items)} verses)",
        file=sys.stderr,
    )
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
