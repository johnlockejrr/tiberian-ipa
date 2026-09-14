#!/usr/bin/env python3
"""Smoke-check havarot against known JS syllabification."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from havarot import Text  # noqa: E402

BERESHIT = "בְּרֵאשִׁ֖ית"
EXPECTED = [
    {"text": "בְּ", "isClosed": False, "isAccented": False, "onset": "בּ", "coda": ""},
    {"text": "רֵא", "isClosed": False, "isAccented": False, "onset": "ר", "coda": "א"},
    {"text": "שִׁ֖ית", "isClosed": True, "isAccented": True, "onset": "שׁ", "coda": "ת"},
]


def main() -> int:
    t = Text(BERESHIT)
    syls = t.syllables
    got = [
        {
            "text": s.text,
            "isClosed": s.isClosed,
            "isAccented": s.isAccented,
            "onset": s.onset,
            "coda": s.coda,
        }
        for s in syls
    ]
    print("syllables:", [s["text"] for s in got])
    ok = got == EXPECTED
    if not ok:
        print("MISMATCH")
        print("expected:", json.dumps(EXPECTED, ensure_ascii=False, indent=2))
        print("got:     ", json.dumps(got, ensure_ascii=False, indent=2))
        return 1
    print("OK — matches JS oracle for בְּרֵאשִׁ֖ית")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
