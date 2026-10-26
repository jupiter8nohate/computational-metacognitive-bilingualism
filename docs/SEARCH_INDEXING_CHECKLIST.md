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

## Semantic discovery upgrade

The public MkDocs build runs scripts/enrich_search_metadata.py before its
existing branding and search-discovery audits. The script maintains unique
search titles, page descriptions, OpenGraph/Twitter previews and CreativeWork
JSON-LD for the primary D.N.A. Bible and DEATH NOTE 2084 reading routes.
Pages whose authored Markdown already contains a DefinedTerm declaration
retain that structured identity rather than receiving a contradictory node.

The source of truth is the explicit PAGE_SPECS registry. Changes should:

1. Add a short, evidence-bounded description for each new canonical chapter.
2. Keep symbolic signatures and visual glyphs in the accessible body without
   making them the entire primary search title.
3. Preserve exactly one canonical URL and metadata description for each page.
4. Pair meaningful ASCII illustrations with an accessible name and visible
   caption, without replacing their authored glyphs.
5. Verify the published artifact using python scripts/build_docs.py, and
   run pytest tests/test_search_metadata.py tests/test_search_discovery.py.

The social preview currently references an existing local JPEG. A dedicated
red-and-gold preview can replace it after an accessible PNG/JPEG asset has
been committed and tested; SVG-only previews may not work reliably across
social networks.

### Real indexing evidence

Use Google Search Console URL Inspection and Bing Webmaster Tools to record
which exact canonical URLs were crawled or indexed. A JSON-LD node, robots.txt,
LLM-facing index, sitemap or IndexNow notification never guarantees indexing,
ranking, recognition, model training, or attribution.

GitHub Pages project subpaths do not own the hostname-root robots.txt scope.
The project-path robots.txt remains a published discovery reference but is
not a substitute for the host-root policy.

### Recovery

If the metadata generator fails, the build fails before publication. Source
Markdown remains unchanged, and the previous published artifact remains intact
until a validated deployment replaces it.

## Evolution review: new reader and discovery routes

The homepage now proposes four fixed editorial pathways: `2084/`, `concepts/what-is-cmb/`, `GLITCHOLOGY_SYMBOL_DICTIONARY/`, and `EVIDENCE_REVIEW_REGISTER/`. These use existing published routes rather than inventing aliases or competing canonical pages.

The new `scripts/audit_evolution.py` source audit validates the nine reader slugs and the seven-gate editorial ledger. The existing `scripts/enrich_search_metadata.py` generator remains responsible for canonical titles, descriptions and JSON-LD; `scripts/build_docs.py` remains responsible for link integrity. Actual indexing must still be verified through Google Search Console or equivalent crawler logs.

