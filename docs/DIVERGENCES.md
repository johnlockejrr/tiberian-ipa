# Divergences (JS schema vs I.5.4 gold)

Native Python matches the `docs/tiberian.ts` / hebrew-transliteration Tiberian schema by default.

Where printed I.5.4 samples and the schema implementation diverge, prefer **T1 gold** when adjusting behavior, and record the change here.

## Fixed port bugs (was native-only)

- **Double `ˌˌ` + spurious vocal shewa** (e.g. `ˌˌwuˑlaˑχɔl-…`): `syl_rules` updated the feature-match base after Word-initial shureq, so “Syllable with Sheva” re-matched Latinized text and added a second meteg accent. Closed-syllable silent sheva then never reached the strip step. Aligned with JS: keep matching against the original `baseSyllableText`.

- **Furtive pataḥ never stressed** (e.g. WLC `הָרָקִיעַ֒` → `hɔːʀ̟ɔːˈq̟iːjaʕ`, not `…q̟iːˈjaʕ`): lone postpositive Segolta and the milraʿ fallback land on the final letter, which hosts only epenthetic furtive pataḥ. After accent assignment, stress shifts one syllable left. **Intentional divergence from stock havarotjs** (and from MAM’s editorial double-Segolta workaround). Same-lemma zaqef/atnaḥ forms already marked `קִ` correctly.

- **Deḥiq** (e.g. `עֹ֤שֶׂה פְּרִי֙` → `ˈʕoːsɛˑ ppʰaˈʀ̟iː`): final unstressed long *qameṣ*/*segol* compresses to half-long and the next onset geminates when the first word is penultimately stressed and bound by a conjunctive or *maqqef* (Khan §I.2.8.1.2). **Intentional divergence from stock JS schema**, which omitted this sandhi.

## Currently aligned

| Case | Status |
|------|--------|
| Gen 1:1–31 | Native == JS Tiberian schema |
| User verse | Native == JS schema |
| שָׁלוֹם / אֱלֹהִים | Native == JS (with `allow_unaccented`) |

## Known JS vs gold micro-diffs (Gen 1.4+)

Tracked against fixtures in `../tests/fixtures/genesis_1_1_13.json`. Native follows JS until a T1-directed override is applied.
