# Changelog

All notable changes to the CMB provenance tool are documented here.

## [1.3.1] - 2026-09-04

### Added

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
