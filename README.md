# tiberian-ipa

A **Python** package for transliterating pointed Biblical Hebrew into **Tiberian IPA**.

This package is Tiberian-only. It does not implement Modern Hebrew, SBL academic Latin, or other orthographic schemes.

Example:

```text
אֱלֹהִים  →  ʔɛloːˈhiːim
שָׁלוֹם   →  ʃɔːˈloːom
```

```text
מִֽי־פָקַ֣ד עָלָ֣יו אָ֑רְצָה וּמִ֥י שָׂ֝֗ם תֵּבֵ֥ל כֻּלָּֽהּ׃
→ ˌmiˑ-ppʰɔːˈq̟aːað ʕɔːˈlɔːɔw ˈʔɔːɔʀ̟sˁɔː wuˈmiː ˈsɔːɔm tʰeːˈveːel kʰulˈlɔːɔh
```

## Credits and sources

### Source of truth

Pronunciation conventions follow Geoffrey Khan’s description of the **Tiberian** reading tradition (Standard Tiberian), especially the inventory, length, shewa, and gemination rules reflected in the T1 materials in this repository:

- Geoffrey Khan, *The Tiberian Pronunciation Tradition of Biblical Hebrew* (and related TPT / T1 documentation in this repo: `T1_*.md`).

Where printed I.5.4 samples and the schema implementation diverge, this project prefers **Khan / T1** as authority. See [docs/DIVERGENCES.md](docs/DIVERGENCES.md).

### Implementation lineage

The engine architecture and Tiberian IPA schema are a **pure-Python port** of work by **Charles Loder**:

- [hebrew-transliteration](https://github.com/charlesLoder/hebrew-transliteration) — schema-based transliteration (MIT)
- [havarotjs](https://github.com/charlesLoder/havarotjs) — Hebrew syllabification (MIT)
- Tiberian schema (IPA inventory + `ADDITIONAL_FEATURES`) as in this repo’s [`docs/tiberian.ts`](../docs/tiberian.ts)

Live JS demo of related tooling: [hebrewtransliteration.app](https://hebrewtransliteration.app).

Many thanks to Geoffrey Khan for the linguistic description, and to Charles Loder for the open-source syllabifier and schema engine that made a faithful Tiberian IPA pipeline practical.

## Requirements

- Python **3.11+**
- No Node.js required at runtime

## Install

### From this repository

```bash
cd native
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Check

```bash
tiberian --help
pytest -q
```

## Quickstart

### CLI

```bash
tiberian "אֱלֹהִים"
# ʔɛloːˈhiːim

tiberian "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃"
# baʀ̟eːˈʃiːiθ bɔːˈʀ̟ɔː ʔɛloːˈhiːim ˈʔeːeθ haʃʃɔːˈmaːjim veˈʔeːeθ hɔːˈʔɔːʀ̟ɛsˁ

tiberian --json "שָׁלוֹם"
```

Pipe from stdin:

```bash
echo "יִשְׂרָאֵל" | tiberian
```

### Python API

```python
from tiberian_ipa import transcribe

r = transcribe("אֱלֹהִים")
print(r.ipa)       # ʔɛloːˈhiːim
print(r.mode)      # native-tiberian
print(r.reading)   # NFD-normalized input
```

Full result (also available via `tiberian --json`):

```python
r = transcribe("שָׁלוֹם")
print(r.to_dict())
# {
#   "input": "...",
#   "reading": "...",
#   "ipa": "ʃɔːˈloːom",
#   "provenance": [...],
#   "unresolved": [],
#   "warnings": [],
#   "profile": "forte_lene",
#   "mode": "native-tiberian"
# }
```

Lower-level access (schema engine):

```python
from hebtrans import transliterate
from tiberian_ipa import tiberian

print(transliterate("בְּרֵאשִׁ֖ית", tiberian))
# baʀ̟eːˈʃiːiθ
```

## What you get

| Output | Notes |
|--------|--------|
| **Bare IPA** | No book-style `[…]` brackets |
| **Tiberian inventory** | Consonants/vowels as in the Tiberian schema (e.g. `ʃ`, `ʀ̟`, `q̟`, `ɔ`, length `ː`, epenthesis) |
| **Stress** | Primary stress mark `ˈ` before the stressed syllable; secondary `ˌ` / half-length `ˑ` with meteg where the schema applies |
| **Default stream** | *forte–lene* (first I.5.4-style reading; not prolonged word-initial BGDKPT) |

Input is normalized to **NFD** (niqqud and cantillation as combining marks). Non-Hebrew input fails closed (`ipa is None`).

### Cantillation required

Faithful Tiberian IPA needs **teʿamim** (cantillation marks) for stress. By default, text **without** cantillation is refused.

```bash
tiberian "אֱלֹהִים"                    # refused (exit 2)
tiberian --allow-unaccented "אֱלֹהִים" # ʔɛloːˈhiːim  (+ warning on stderr)
```

```python
transcribe("אֱלֹהִים")  # mode="refused-unaccented", ipa=None
transcribe("אֱלֹהִים", allow_unaccented=True)  # mode="native-tiberian-basic" + warning
```

Meteg alone does not count as cantillation.

## How it works

```text
pointed Hebrew
    → havarot          (syllabification)
    → hebtrans         (schema rule engine)
    → Tiberian schema  (IPA inventory + feature hooks)
    → bare IPA
```

Notable Tiberian features encoded in the schema:

- Vowel length and closed stressed-syllable **epenthesis**
- Vocal / silent **shewa** and **ḥaṭaf** vowels
- **BGDKPT** and digraph gemination (e.g. `tʰ`, `pʰ`, `kʰ`)
- Quiescent / dageshed **alef**, furtive **pataḥ**, pharyngealized **resh**
- Word-initial **shureq** as `wu…`
- Special forms (e.g. Jerusalem, Issachar, interrogative in construct)

## Package layout

```text
native/
  src/
    havarot/          # syllabifier (port of havarotjs)
    hebtrans/         # schema rules (port of hebrew-transliteration)
    tiberian_ipa/     # Tiberian schema, API, CLI
  tests/              # parity + I.5.4 gold + negatives
  docs/DIVERGENCES.md
  scripts/dump_js_oracle.py   # optional: refresh JS reference fixtures
```

## Batch processing

Transcribe a whole chapter file (verse-numbered Hebrew, e.g. `Genesis_1.txt`):

```bash
python scripts/batch_transcribe.py \
  -i ../Genesis_1.txt \
  -o Genesis_1.ipa.txt

# JSON Lines (one object per verse)
python scripts/batch_transcribe.py \
  -i ../Genesis_1.txt \
  -o Genesis_1.ipa.jsonl \
  --format jsonl
```

Text output lines look like ``1\tbaʀ̟eːˈʃiːiθ …``. Use `--allow-unaccented` if a verse lacks teʿamim.

```bash
cd native
source .venv/bin/activate
pytest -q
```

Optional: regenerate JS oracle fixtures (needs Node and `../js` dependencies):

```bash
cd ../js && npm install && cd ../native
python scripts/dump_js_oracle.py
```

## Related

| Resource | Role |
|----------|------|
| Repo root `T1_*.md` | Khan T1 source extracts (authority) |
| Repo `corpus/` | Extracted pronunciation rules |
| [`docs/tiberian.ts`](../docs/tiberian.ts) | Reference Tiberian schema (TypeScript) |
| [hebrew-transliteration](https://github.com/charlesLoder/hebrew-transliteration) | Original JS package |
| [havarotjs](https://github.com/charlesLoder/havarotjs) | Original JS syllabifier |

## License

MIT — see `pyproject.toml`. Upstream **hebrew-transliteration** and **havarotjs** are also MIT; this package’s ports inherit that lineage with gratitude.
