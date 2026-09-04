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
    |
    v
MACHINE-READABLE WEB LAYER

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

Render:

```bash
cmb-gsb render -in artifact.json -out public-meta/
```

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
