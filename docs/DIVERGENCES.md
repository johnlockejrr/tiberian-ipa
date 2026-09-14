# Divergences (JS schema vs I.5.4 gold)

Native Python matches the `docs/tiberian.ts` / hebrew-transliteration Tiberian schema by default.

Where printed I.5.4 samples differ from that schema (stress on construct `beːen`, half-length vs epenthesis details, etc.), prefer **T1 gold** when adjusting behavior, and record the change here.

## Currently aligned

| Case | Status |
|------|--------|
| Gen 1:1 | Native == JS == I.5.4 `forte_lene` |
| User verse (Job 38:5-ish sample) | Native == JS schema |
| שָׁלוֹם / אֱלֹהִים | Native == JS |

## Known JS vs gold micro-diffs (Gen 1.4+)

Tracked against fixtures in `../tests/fixtures/genesis_1_1_13.json`. Native follows JS until a T1-directed override is applied.
