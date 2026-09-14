"""CLI entry point: ``tiberian``."""

from __future__ import annotations

import argparse
import json
import sys

from tiberian_ipa.api import transcribe


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tiberian",
        description="Native Tiberian Hebrew IPA (havarot + hebtrans + docs/tiberian.ts).",
    )
    parser.add_argument("text", nargs="?", help="Masoretic Hebrew (or stdin)")
    parser.add_argument(
        "--profile",
        "-p",
        default="forte_lene",
        help="Pronunciation stream label (default: forte_lene)",
    )
    parser.add_argument("--json", action="store_true", help="Emit full Result JSON")
    parser.add_argument(
        "--allow-unaccented",
        action="store_true",
        help=(
            "Allow text without cantillation (teʿamim); emit a basic/approximate "
            "IPA with a warning (default: refuse)"
        ),
    )
    args = parser.parse_args(argv)

    text = args.text if args.text is not None else sys.stdin.read()
    if not text or not str(text).strip():
        parser.error("No input text")

    result = transcribe(
        text,
        profile=args.profile,
        allow_unaccented=args.allow_unaccented,
    )

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ipa is not None else 2

    if result.ipa is None:
        print("IPA: (unresolved)", file=sys.stderr)
        for u in result.unresolved:
            msg = u.get("message") or u.get("reason")
            print(f"  - {u.get('reason')}: {msg}", file=sys.stderr)
        return 2

    print(result.ipa)
    for w in result.warnings:
        print(f"# warning: {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
