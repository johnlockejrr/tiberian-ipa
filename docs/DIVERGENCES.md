# Divergences (JS schema vs I.5.4 gold)

Native Python matches the `docs/tiberian.ts` / hebrew-transliteration Tiberian schema by default.

Where printed I.5.4 samples and the schema implementation diverge, prefer **T1 gold** when adjusting behavior, and record the change here.

## Fixed port bugs (was native-only)

- **Double `ˌˌ` + spurious vocal shewa** (e.g. `ˌˌwuˑlaˑχɔl-…`): `syl_rules` updated the feature-match base after Word-initial shureq, so “Syllable with Sheva” re-matched Latinized text and added a second meteg accent. Closed-syllable silent sheva then never reached the strip step. Aligned with JS: keep matching against the original `baseSyllableText`.

## Currently aligned

| Case | Status |
|------|--------|
| Gen 1:1–31 | Native == JS Tiberian schema |
| User verse | Native == JS schema |
| שָׁלוֹם / אֱלֹהִים | Native == JS (with `allow_unaccented`) |

## Known JS vs gold micro-diffs (Gen 1.4+)

Tracked against fixtures in `../tests/fixtures/genesis_1_1_13.json`. Native follows JS until a T1-directed override is applied.
