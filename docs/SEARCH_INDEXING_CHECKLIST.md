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

The MkDocs `on_post_page` hook in `scripts/enrich_search_metadata.py` now emits
one canonical, one title, one description and social previews for every
Markdown page. Authored front-matter titles and descriptions take precedence;
the existing `PAGE_SPECS` registry supplies curated chapter metadata. Other
pages use concise navigation titles and a bounded excerpt of their own visible
article prose. Add an authored description when that excerpt is not suitable.
Navigation, scripts, code blocks and hidden glyph art are excluded from excerpts.
The hook changes the HTML head, preserving the authored body and its glyphs.

Existing DefinedTerm, ProfilePage and other authored structured identities are
preserved. Generic documentation pages are not automatically labelled fiction.
The post-build pass handles the standalone illustrated Spider story and browser
playground, then adds both routes to the generated sitemap. The playground guide
at `PLAYGROUND/` and the functional tool at `playground/` have distinct canonicals.

Changes should:

1. Add a short, evidence-bounded description for each new canonical chapter.
2. Keep symbolic signatures and visual glyphs in the accessible body without
   making them the entire primary search title.
3. Preserve exactly one canonical URL and metadata description for each page.
4. Pair meaningful ASCII illustrations with an accessible name and visible
   caption, without replacing their authored glyphs.
5. Verify the published artifact using `python scripts/build_docs.py`, and
   run `pytest tests/test_search_metadata.py tests/test_search_discovery.py`.

The build checks all public HTML landing pages in both directions against the
sitemap, including unique titles, nonempty descriptions, self-canonicals and
indexing directives. Search/error utilities and the ownership-verification
file stay out of the sitemap. Search and error utilities receive `noindex,follow`.
Missing metadata is a publishing defect; a meta description is not a prerequisite
for Google indexing and Google may choose another snippet.

### Source dates and deployment checks

Sitemap `lastmod` values come from the last committed change to each authored
page source, not its checkout time or the hourly build clock. Untracked, dirty
or shallow-history sources receive no date rather than an invented timestamp.
Documentation workflows fetch full history. The compressed sitemap is regenerated
from the same XML and checked for equality.

After deployment, run:

```bash
python scripts/check_search_discovery.py --live --report-path /tmp/cmb-live-search.json
```

The deployment does this automatically. It checks priority URL responses,
canonical metadata, `X-Robots-Tag`, sitemap inclusion and the **host-root**
robots policy. Its report identifies the evidence as `publisher_http_checks`
and leaves `google_index_status` as `UNKNOWN`. A host-root robots response of
404 does not itself block Googlebot. Publication success is not an inspection
by Google and cannot replace Search Console.

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

### Google inspection evidence log

Use the URL-prefix property for the canonical origin above. Confirm ownership
and the sitemap's processing result, then inspect these pages first. Record
the actual inspected timestamp, coverage reason, last crawl and Google-selected
canonical from Search Console; do not infer them from a build or search query.

| Canonical route | Google inspection time (UTC) | Google coverage | Google-selected canonical |
| --- | --- | --- | --- |
| [Homepage](index.md) | Not recorded | Unknown | Unknown |
| [What Is CMB](concepts/what-is-cmb.md) | Not recorded | Unknown | Unknown |
| [Jupiter Hudson biography](JUPITER_HUDSON_BIOGRAPHY.md) | Not recorded | Unknown | Unknown |
| [Global AI Watch](GLOBAL_AI_WATCH.md) | Not recorded | Unknown | Unknown |
| [Story Library](story-universe/index.md) | Not recorded | Unknown | Unknown |
| [The Spider's Internet](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/spiders-internet/) | Not recorded | Unknown | Unknown |

For discovered-but-not-indexed pages, check discovery and internal links.
For crawled-but-not-indexed pages, review distinct usefulness, duplication and
content quality. Resolve robots/noindex/HTTP errors and conflicting canonicals
when the inspection reports them. After a meaningful repair, request indexing
for the affected priority URLs and record a later inspection result. Repeated
requests do not force indexing or accelerate the same URL's crawl.

The October 31 audit could not retrieve Search Console results because the GSC
Wizard account reported an inactive trial/subscription. Restore the connector's
active plan/trial and reconnect if needed, or use Google Search Console directly.
That connector error is not evidence that the site is absent from Google's index.

### Recovery

If the metadata generator fails, the build fails before publication. The previous published artifact remains intact
until a validated deployment replaces it.

## Evolution review: new reader and discovery routes

The homepage now proposes four fixed editorial pathways: `2084/`, `concepts/what-is-cmb/`, `GLITCHOLOGY_SYMBOL_DICTIONARY/`, and `EVIDENCE_REVIEW_REGISTER/`. These use existing published routes rather than inventing aliases or competing canonical pages.

The new `scripts/audit_evolution.py` source audit validates the nine reader slugs and the seven-gate editorial ledger. The existing `scripts/enrich_search_metadata.py` generator remains responsible for canonical titles, descriptions and JSON-LD; `scripts/build_docs.py` remains responsible for link integrity. Actual indexing must still be verified through Google Search Console or equivalent crawler logs.

