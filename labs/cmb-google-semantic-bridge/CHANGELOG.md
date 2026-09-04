# Changelog

## [0.5.0] - 2026-09-04

### Added

- `cmb-gsb publish-canon` for deterministic whole-library compilation from the repository canon, catalog, and exact declared source files.
- Strict `cmb.library.catalog.v1` Go loader with unknown-field rejection, interpretation-boundary checks, artifact-ID uniqueness, and repository-relative path validation.
- `cmb-gsb.library-index.v1` binding every published artifact to its canonical URL, source digest, repository path, output path, status, provenance scope, concepts, and declared meaning.
- Per-artifact Schema.org `CreativeWork` JSON-LD and `cmb-gsb.library-semantic.v1` sidecars without invented publication dates.
- Root Schema.org `CollectionPage`, full sitemap, exact canon/catalog copies, and deterministic agent discovery outputs.
- Nested staged output trees inside the existing atomic publication process.
- Cross-contract verification that exact canon/catalog bytes match their recorded SHA-256 values and every catalog invariant exists in the canon.
- Repository-root containment checks that reject traversal and symlinked catalog paths.
- Formatting-gate diagnostics that print the exact `gofmt` diff on failure.

### Changed

- GitHub Pages now builds the whole catalog-declared CMB digital library instead of using one manifesto as the root publication.
- Sovereign Transmission remains available as a normal indexed artifact rather than being removed.
- Repository corpus changes now trigger the semantic-library CI path so publication drift is caught automatically.

### Guardrails

- Catalog status is preserved; `planned`, `open`, and `derived` entries are not silently promoted to `canonical`.
- The compiler does not invent publication dates, authorship evidence, ownership claims, or ranking guarantees.
- Exact source SHA-256 values remain integrity identifiers, not independent proof of authorship or copyright.

## [0.4.0] - 2026-09-04

### Added

- Strict canon loader that consumes `library/canon.json`, rejects unknown top-level fields, verifies invariant uniqueness, and binds semantic output to the canon SHA-256.
- `cmb-gsb.semantic.v2` with a canon binding and the full canonical CMB invariant set.
- Exact `cmb-canon.json` copy in every metadata and publication bundle.
- Staged atomic publication replacement with complete-generation manifests.
- Regular-file Recovery reader with symlink, size, UTF-8, and file-change checks.

### Changed

- `render` no longer synthesizes a provenance SHA-256 from an embedded JSON body.
- JSON-LD preserves article body text exactly instead of trimming it.
- URL validation now uses one HTTPS parser and rejects userinfo, fragments, and surrounding whitespace.
- CI and Pages builds are canon-sensitive and verify the published canon bytes against the repository source.


## [0.3.1] - 2026-09-04

### Changed

- Rebuilt the public page shell as a cosmic sovereign manuscript with stronger visual hierarchy and deliberate whitespace.
- Replaced mechanical punctuation in presentation copy with decorative separators such as `✦`, `·`, and `│`.
- Added a provenance ledger, human ↔ machine boundary cards, publication-surface navigation, and symbolic framing.
- Added mobile layout refinement, keyboard focus treatment, print mode, text selection styling, and reduced-motion support.
- Preserved the canonical manifesto bytes as the authority source instead of visually rewriting provenance content.

### Guardrails

- The live publication frame is tested to contain no em dash characters.
- The canonical source and generated publication are checked for em dash regressions during Pages deployment.
- The site remains zero-dependency, static, deterministic, and free of external font, script, analytics, or stylesheet calls.

## [0.3.0] - 2026-09-04

### Added

- GitHub Pages deployment workflow for the canonical Sovereign Transmission.
- Real project-site canonical target at `https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/`.
- Explicit `-site-base` option for project-hosted sitemap discovery paths.
- Exact-commit pinning for GitHub Pages deployment actions.
- Deployment contract checks for canonical URL, sitemap location, source-byte equality, and static bundle completeness.

### Corrected

- Sitemap discovery generation now preserves project-site base paths instead of collapsing every deployment to the host root.
- Documentation distinguishes a project-path `robots.txt` artifact from an origin-root robots policy.

## [0.2.0] - 2026-09-04

### Added

- Static publication mode for complete human-readable CMB pages.
- Source-file binding with SHA-256 mismatch rejection.
- Accessible standalone HTML with embedded Schema.org Article JSON-LD.
- Zero-dependency dark terminal stylesheet.
- Published source copy and deterministic output manifest.
- Sovereign Transmission publication fixture sourced from the canonical repository manifesto.

### Preserved

- Google-facing structured metadata remains separate from CMB policy semantics.
- Search-engine discoverability remains a signal surface, not a ranking or indexing guarantee.
- SHA-256 remains integrity evidence, not independent proof of authorship or ownership.

## [0.1.0] - 2026-09-04

### Added

- Strict CMB artifact contract.
- Schema.org Article JSON-LD.
- CMB semantic sidecar.
- Canonical link generation.
- XML sitemap generation.
- robots.txt sitemap discovery.
- SHA-256 output manifest.
