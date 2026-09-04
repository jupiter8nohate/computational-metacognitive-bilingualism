# Changelog

All notable changes to the CMB provenance tool are documented here.

## [1.3.1] - 2026-09-04

### Added

- Deterministic `CMB receipt -> C2PA-facing assertion payload` adapter with privacy-minimized defaults, canonical JSON serialization, strict JSON Schema, CLI export, deterministic fixtures, and tests. The adapter explicitly does not create a C2PA manifest, Content Credential, signature, asset binding, or conformance result.
- Prior-art and legal-positioning document covering GDPR Article 22, EU AI Act Article 14, relevant scholarship, and C2PA as an external provenance standard.
- Two-minute CMB policy one-pager as the public front door, with deeper technical and symbolic materials moved to optional follow-on paths.
- C2PA interoperability design that explicitly treats `cmb_provenance` as complementary infrastructure and forbids false conformance claims.
- Public independent-review request defining a narrow security, provenance, and policy audit scope.
- **CMB-Z13™ — Zodiac Computational Metacognitive Language** as a three-part canonical bundle: public manifesto, formal language specification, and machine-readable registry mapping thirteen zodiac archetypes to thirteen software-language lenses.
- Expanded canonical provenance sealing scope to include the CMB-Z13 manifesto, specification, registry, the Unclassifiable Index, and the digital-library catalog in the next signed release.
- Bilingual CMB digital-library layer: human navigation in `library/README.md`, a machine-indexable `library/catalog.json`, and tests that enforce catalog/release-scope consistency.
- **CMB // The Unclassifiable Index**, a canonical MissingNo–Pokédex manifesto defining a perspective-aware human/machine-readable library model and the CMB MissingNo Clause.
- Installable `cmb-provenance` Python package and console entry point.
- Stable `seal()` and `verify()` APIs for explicit artifact sets.
- Canonical artifact manifests containing normalized paths, byte-level SHA-256 digests, sizes, schema version, tool version, and full Git commit.
- Explicit Git-commit status distinguishing byte-verified committed artifacts from caller-supplied, unverified commit metadata.
- Self-describing seal receipts whose coverage excludes every unlisted path.
- Strict receipt, manifest, and anchor-ledger schema validation, including duplicate JSON-key rejection.
- Cross-platform, whole-operation ledger locking with bounded timeouts.
- Canonical UTC timestamp normalization.
- Pytest coverage for deterministic fixtures, corrupt inputs, exact coverage, lock timeouts, concurrent writers, CLI exit codes, and safe error output.
- Python 3.10–3.13 CI matrix and build verification.
- Keyless Sigstore release signing, SHA-256 checksum generation, and GitHub artifact attestations.
- Apache-2.0 licensing, citation metadata, and explicit authorship/implementation-assistance documentation.

### Changed

- Global Advocacy Charter advanced to v1.1 with explicit prior-art positioning, C2PA interoperability direction, and disclosure that the project has not yet received an independent security audit or outside certification.
- README now leads with a compressed policy front door, prior-art context, interoperability status, and explicit non-claims before the larger canonical corpus.
- Evidence anchors now bind to an explicit artifact-manifest digest under `cmb.anchor.v2` rather than a general framework hash.
- The versioned v1.3.0 standalone script is retained as a historical compatibility artifact; new automation should use the installed CLI.

### Security

- Ledger appends validate the complete existing chain while holding the same exclusive lock used for the append.
- File hashing detects changes made during the read and refuses symbolic links.
- Git identity verification compares the captured artifact digest directly with the committed blob, and ledger I/O refuses symbolic links and non-regular files.
- Receipt writes use atomic replacement and filesystem synchronization where supported.
- Expected operational failures return concise errors without default tracebacks.

## [1.3.0] - 2026-08-28

- Added the dependency-free CMB provenance and external-evidence reference script.
- Separated declaration and tool versions.
- Added a local JSONL hash chain and tamper-detection self-test.
