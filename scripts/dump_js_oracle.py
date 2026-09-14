#!/usr/bin/env python3
"""Refresh native/tests/fixtures/js_oracle.json from the JS Tiberian runner."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / "js"
OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "js_oracle.json"

CASES = {
    "user": "מִֽי־פָקַ֣ד עָלָ֣יו אָ֑רְצָה וּמִ֥י שָׂ֝֗ם תֵּבֵ֥ל כֻּלָּֽהּ׃",
    "shalom": "שָׁלוֹם",
    "elohim": "אֱלֹהִים",
    "bereshit": "בְּרֵאשִׁ֖ית",
    "gen1": "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃",
}


def main() -> int:
    script = JS / "dump_oracle.mjs"
    if not script.is_file():
        print(f"missing {script}; run from repo with js/ set up", file=sys.stderr)
        return 1
    subprocess.run(["npx", "tsx", str(script)], cwd=str(JS), check=True)
    print(f"refreshed {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
