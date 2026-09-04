# CMB Google Semantic Bridge

> Experimental Go implementation for translating human-authored CMB artifacts into standards-based web semantics that search engines and other machine readers can parse.

```text
HUMAN SOURCE
    |
    v
CMB ARTIFACT v1
    |
    v
GO SEMANTIC BRIDGE
    |
    +--> Article JSON-LD
    +--> canonical link
    +--> sitemap.xml
    +--> robots.txt
    +--> SHA-256 output manifest
    +--> complete static HTML publication
    |
    v
HUMAN + MACHINE READABLE WEB LAYER

PATTERN != PROOF
INDEX != IDENTITY
RANKING != TRUTH
DISCOVERABILITY != OWNERSHIP
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## What this project is

The bridge creates public, standards-based representations of a human-authored artifact.

It is designed to help a website expose:

- Schema.org / JSON-LD metadata;
- canonical URL signals;
- XML sitemap entries;
- robots.txt sitemap discovery;
- byte-level SHA-256 integrity metadata;
- deterministic build outputs.

The default JSON-LD representation is `Article` because CMB manifestos and authored written works fit an article-like publication model.

## What this project is not

This project does **not**:

- translate into Google's private ranking algorithm;
- guarantee crawling, indexing, ranking, rich results, AI Overview inclusion, or AI Mode inclusion;
- bypass Google Search policies;
- perform cloaking, keyword stuffing, mass page generation, or crawler deception;
- prove authorship, copyright ownership, originality, or legal enforceability;
- tell a search engine that a machine-readable profile is the human being.

Google documents JSON-LD as a supported structured-data format and currently recommends it primarily because it is generally easier to implement and maintain. Structured data still must follow the documentation for the relevant Search feature.

Google also documents canonical annotations and XML sitemaps as signals used in crawling/indexing. They are not ranking commands.

## Requirements

- Go 1.27+

The module intentionally uses only the Go standard library.

## Try it

From this directory:

```bash
go test ./...
go run ./cmd/cmb-gsb validate -in examples/cmb-manifesto.json
go run ./cmd/cmb-gsb render -in examples/cmb-manifesto.json -out build/
go run ./cmd/cmb-gsb publish \
  -in examples/sovereign-transmission.json \
  -source ../../manifestos/CMB_SOVEREIGN_TRANSMISSION.md \
  -out build/sovereign-transmission/
```

Generated files:

```text
build/
  article.jsonld
  cmb-semantic.json
  head.html
  sitemap.xml
  robots.txt
  manifest.json

build/sovereign-transmission/
  index.html
  site.css
  source.md
  article.jsonld
  cmb-semantic.json
  head.html
  sitemap.xml
  robots.txt
  manifest.json
```

The example uses `example.org` deliberately. Replace it with a real HTTPS publication URL before deploying generated metadata.

## Artifact contract

Input:

```json
{
  "schema_version": "cmb-gsb.artifact.v1",
  "id": "cmb-sovereignty-protocol",
  "url": "https://example.org/cmb/sovereignty-protocol",
  "title": "CMB Sovereignty Protocol",
  "description": "Human-authored CMB artifact.",
  "author": {
    "name": "Jupiter Hudson / WisdomLoveThePoet / Jupiter 8"
  },
  "date_published": "2026-09-04T09:00:00-04:00",
  "date_modified": "2026-09-04T09:00:00-04:00",
  "language": "en",
  "provenance": {
    "human_authored": true,
    "human_authority": "HUMAN_FINAL"
  }
}
```

Unknown input fields are rejected. This is deliberate. A field such as `ranking_override` or `machine_authority` is not silently accepted.

## CLI

Validate:

```bash
cmb-gsb validate -in artifact.json
```

Render metadata only:

```bash
cmb-gsb render -in artifact.json -out public-meta/
```

Publish a complete static page from an exact human-authored source file:

```bash
cmb-gsb publish \
  -in artifact.json \
  -source MANIFESTO.md \
  -out public/
```

Override the canonical publication URL without modifying the human source:

```bash
cmb-gsb publish \
  -in artifact.json \
  -source MANIFESTO.md \
  -out public/ \
  -url https://example.org/cmb/manifesto/
```

The publisher computes SHA-256 from the exact source bytes. If the artifact already declares a hash and the supplied source does not match it, publication fails.

Hash any source file:

```bash
cmb-gsb hash -file MANIFESTO.md
```

## Two-output semantic design

The bridge deliberately separates two machine-readable surfaces.

`article.jsonld` is the search-facing Schema.org `Article` representation. It contains ordinary article metadata such as headline, description, author, canonical URL, dates, language, keywords, article body, and identifiers.

`cmb-semantic.json` is the CMB interpretation/provenance sidecar. It carries invariants such as `PATTERN != PROOF` and the fixed `HUMAN_FINAL` authority declaration.

This prevents project-specific philosophy from being disguised as Google-supported Article properties.

```text
GOOGLE_JSON_LD != CMB_POLICY
CMB_POLICY != GOOGLE_RANKING_SIGNAL
BOTH_CAN_REFERENCE_THE_SAME_HUMAN_SOURCE
```

## Provenance boundary

```text
SHA256 == BYTE_INTEGRITY_IDENTIFIER
SHA256 != AUTHORSHIP
JSON_LD == DECLARED_METADATA
JSON_LD != GOOGLE_ENDORSEMENT
SITEMAP == DISCOVERY_HINT
SITEMAP != INDEXING_GUARANTEE
CANONICAL == PREFERRED_URL_SIGNAL
CANONICAL != ABSOLUTE_COMMAND
```

## Official references

- Google Search structured data introduction:
  https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
- Google Search canonicalization:
  https://developers.google.com/search/docs/crawling-indexing/canonicalization
- Google crawling robots.txt documentation:
  https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec
- Google Search sitemap documentation:
  https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- Schema.org:
  https://schema.org/

## Incubator status

This directory is intentionally self-contained as a nested Go module. The intended standalone repository name is:

```text
jupiter8nohate/cmb-google-semantic-bridge
```

Before extraction into its own repository:

1. copy this directory to the new repository root;
2. add the standalone repository license and security files;
3. update documentation paths;
4. run `go test ./...`;
5. enable branch protection and required CI;
6. tag the first release only after an external review of the generated metadata model.

The current incubator inherits the parent repository's engineering review process and licensing context.

## Publisher v0.2

The publisher adds a human-readable surface to the machine-readable bridge.

```text
EXACT HUMAN SOURCE BYTES
          |
          +--> SHA-256
          |
          v
      BIND SOURCE
          |
          +--> reject declared-hash mismatch
          +--> reject invalid UTF-8
          |
          v
     STATIC PAGE
          |
     +----+----+
     |         |
   HUMAN     MACHINE
   ARTICLE   JSON-LD
     |         |
     +----+----+
          |
          v
    SAME CANONICAL URL
```

The generated page is deliberately zero-dependency:

- no JavaScript application runtime;
- no remote font or stylesheet dependency;
- no analytics;
- no crawler-specific hidden content;
- human source is HTML-escaped before rendering;
- JSON-LD is generated from the same bound artifact used to render the visible page.

The canonical Sovereign Transmission source used by the repository test is:

```text
../../manifestos/CMB_SOVEREIGN_TRANSMISSION.md
```

The example publication URL remains `example.org` until an actual public HTTPS deployment target is chosen. Do not treat the fixture URL as a live publication.

```text
VISIBLE_PAGE == HUMAN_SOURCE_PRESENTATION
STRUCTURED_DATA == MACHINE_DESCRIPTION
VISIBLE_PAGE != HIDDEN_CLOAK
STRUCTURED_DATA != RANKING_COMMAND
```


## GitHub Pages deployment v0.3

The repository now contains an official deployment workflow:

```text
.github/workflows/cmb-google-semantic-pages.yml
```

Its production target is:

```text
https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/
```

On every relevant push to `main`, the workflow rebuilds the site from the canonical repository source:

```text
manifestos/CMB_SOVEREIGN_TRANSMISSION.md
```

and publishes only the generated static bundle.

The deployment command is equivalent to:

```bash
cmb-gsb publish \
  -in examples/sovereign-transmission.json \
  -source ../../manifestos/CMB_SOVEREIGN_TRANSMISSION.md \
  -out public/ \
  -url https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/ \
  -site-base https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/
```

### One-time GitHub setting

GitHub requires Pages to be enabled for the repository before the official deployment action can publish. In repository settings:

```text
Settings
  -> Pages
  -> Build and deployment
  -> Source
  -> GitHub Actions
```

After that one-time setting, the workflow can deploy subsequent updates automatically.

### GitHub Pages project-path boundary

The project is hosted below the shared GitHub Pages origin:

```text
https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/
```

Therefore the generated project-local file:

```text
/computational-metacognitive-bilingualism/robots.txt
```

is useful as a portable publication artifact but is **not** the origin-level robots policy at:

```text
https://jupiter8nohate.github.io/robots.txt
```

The project sitemap remains a valid URL:

```text
https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/sitemap.xml
```

and can be submitted directly through search-engine webmaster tooling.

```text
PROJECT_ROBOTS != ORIGIN_ROBOTS
SITEMAP_URL == SUBMITTABLE_DISCOVERY_ARTIFACT
DEPLOYMENT != INDEXING_GUARANTEE
```


## Cosmic publication system v0.3.1

The public CMB page now uses a deliberately layered visual system rather than a plain developer-output shell.

```text
FIRST IMPRESSION
      │
      ▼
COSMIC SOVEREIGN HERO
      │
      ▼
HUMAN SOURCE TRANSMISSION
      │
      ▼
PROVENANCE LEDGER
      │
      ▼
HUMAN ↔ MACHINE BOUNDARY
      │
      ▼
PUBLICATION SURFACES
      │
      ▼
FINAL CMB AXIOM
```

The visual language favors:

- warm gold for authorship, orientation, and stable hierarchy;
- soft violet for symbolic identity and metacognitive framing;
- sky accents for machine-facing structure;
- mint terminal text for the exact human source;
- large breathing space between conceptual layers;
- rounded framed panels instead of aggressive hard separators;
- `✦`, `·`, `│`, and CMB glyphs instead of em dash punctuation in presentation copy.

Accessibility remains part of the design contract:

- visible keyboard focus;
- skip navigation;
- responsive single-column layouts;
- reduced-motion support;
- printable light-mode fallback;
- no remote fonts;
- no remote CSS;
- no analytics;
- no application JavaScript.

The exact manifesto source remains available as `source.md` and is still copied byte-for-byte into the deployment bundle.

```text
DECORATION != OBFUSCATION
READABILITY > VISUAL_NOISE
SOURCE_BYTES == PRESERVED
HUMAN_AGENCY > MACHINE_AUTHORITY
```
