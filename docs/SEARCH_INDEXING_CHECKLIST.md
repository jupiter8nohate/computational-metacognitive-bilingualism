# Discovery and Indexing | Verification Checklist

**Purpose:** Make the canonical public archive findable without falsely claiming indexing or search-engine endorsement.

| Layer | Inspect | How to verify |
| --- | --- | --- |
| Publication | GitHub Pages homepage and each canonical reading route | Request the URL and verify HTTP status and rendered title |
| Links | Internal anchors, script, image and stylesheet paths | Run the docs build and archive experience audit |
| Search discovery | `sitemap.xml`, `llms.txt`, structured metadata | Confirm reachable assets and self-consistent canonical URLs |
| Search index | Google Search Console URL Inspection | Check real indexed status; submitting a sitemap is not indexing |
| Site ownership | Search Console verification | Requires authorized owner action |
| Repository metadata | Homepage, Topics, social preview | Requires repository settings permissions |
| External discovery | Bing Webmaster Tools | Submit sitemap and inspect actual coverage |

**Canonical origin:** https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/

**High-priority pages:** homepage, [What Is CMB](concepts/what-is-cmb.md), [reader map](ARCHIVE_READING_MAP.md), [Story Library](story-universe/index.md), [Anomaly Codex](dna-codex/index.md), [Evidence Ledger](DEATH_NOTE_2084_EVIDENCE_LEDGER.md), [symbol dictionary](GLITCHOLOGY_SYMBOL_DICTIONARY.md).

**Privacy boundary:** Do not introduce cross-site trackers, third-party fonts, forced cookies, behavioral profiling, or covert analytics for SEO.

```text
PUBLISHED != INDEXED
INDEXED != RANKED
URL_SUBMITTED != INDEX_CONFIRMED
DISCOVERY != TRAINING_CONSENT
```

For detailed existing infrastructure see [Search & AI Discovery Operations](SEARCH_DISCOVERY.md).
