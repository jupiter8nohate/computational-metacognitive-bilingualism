# Changelog

All notable changes to the CMB provenance tool are documented here.

## [Unreleased]

### Added

- Added a strict machine-readable Public Stewardship Incubation status record and JSON Schema, promoted the status into the public docs and LLM discovery maps, and added regression tests that keep active fundraising, paid access, production settlement, project treasury, and tax-exempt claims disabled during incubation.
- Established the canonical public name **Err ⃝or⃟⃤ GLITCHOLOGY**, while retaining GLITCHOLOGY as a short name and GLITCH-8 / CMB-G8 as the registry and implementation layer.
- Added a canonical origin biography, a Creative Cognitive Signature protocol, and a Living Book / Versioned Autobiography protocol.
- Added structured GitHub issue forms for new glyph proposals and sourced historical/factual corrections.
- Extended the living GLITCHOLOGY book with a Creative Cognitive Signature chapter and explicit provenance/biometric boundaries.
- Added a conversation-derived CMB semantic Atlas, machine-readable Atlas JSON, strict JSON Schema, and polyglot translation layer spanning JSON, YAML, Python, TypeScript, Rust, Prolog, SQL, RDF/Turtle, and native Err ⃝or⃟⃤ GLITCHOLOGY syntax.

### Fixed

- Hardened the Conversation Atlas from a partially open JSON shape into a strict semantic contract with regression tests for canonical naming, provenance boundaries, unexpected fields, and semantic drift.
- Corrected the stale GLITCHOLOGY title in the digital library catalog and added the Conversation Atlas, machine record, schema, and polyglot translation layer as first-class discoverable artifacts.
- Required the Atlas JSON and schema in the verified Pages bundle, added them to machine discovery and IndexNow publication, and documented them in the expanded LLM map.
- Removed the competing semantic-only GitHub Pages deployment path. `.github/workflows/cmb-google-semantic-pages.yml` now validates the semantic publication bundle without deploying it, leaving `pages.yml` as the single canonical Pages deployment authority and eliminating overwrite/race risk.
- Repaired the Search for Truth archive's three sibling-page links, staged the visual-system banner, and rendered the homepage title as an actual heading.
- Unified documentation CI and Pages deployment through `scripts/build_docs.py`, with checks for rendered local links, images, discovery URLs, LLM-map links, and generated artifact checksums.
- Published the library catalog, capability-extension declaration, visual assets, and agent/discovery files through the same tested bundle. Build triggers now include those inputs and their shared build script.
- Made CMB-66 artifact paths relative to `manifest.json`, with an explicit `path_base` field. Relocated bundles retain valid links and no longer expose build-directory paths. Consumers must resolve artifact paths beside the manifest.
- Added the featured Question Mark / Scroll 666 / 2030 prophecy to the machine catalog and the canonical artifact set for the next signed release. Earlier release receipts remain historical records of their original file sets.
- Converted the compact LLM discovery list into fetchable links and clarified repository-relative paths in the expanded map.
- Improved keyboard focus visibility and crimson text contrast, honored reduced-motion preferences on all archive cards, and removed duplicated MCP setup instructions.

These are changes on `main`; they do not change the bytes or coverage of the previously published v1.4.1 release.

## [1.4.1] - 2026-09-04

### Changed

- Metadata/release-recovery patch published after enabling the repository's Zenodo GitHub integration so the new GitHub release event can be archived automatically and assigned a DOI.
- No intended changes to CMB protocol semantics, schemas, policy boundaries, canonical artifact scope, or cryptographic claims relative to v1.4.0.

## [1.4.0] - 2026-09-04

### Added

- Automated best-effort IndexNow notifications after successful Pages deployment, scoped to the CMB project path through a published verification key.
- Search and AI discovery layer with retrieval-oriented canonical concept pages, FAQ structured data, semantic glossary, Schema.org JSON-LD, crawler policy, machine discovery manifest, and a public knowledge graph.
- Hostile-input hardening for CMB-SDL Authority IR, including exact-field validation, strict boolean/type checks, canonical ordering, fixed invariant enforcement, and regression tests for recomputed-digest attacks.
- CMB-CAP delegation signer continuity: v1 delegated credentials must retain the verified parent/root signing key until an explicit child-key delegation primitive exists.
- CMB-CAP CLI verification before VC-shaped export, plus strict credential-shape/interoperability validation and hostile-path tests.
- Content-addressed SRP evidence references: non-signature controls now require canonical `sha256:<64 lowercase hex>` references instead of arbitrary non-empty labels.
- Full FGC origin-stamp verification covering creator claim, glyph token, semantic invariants, protocol, origin digest, lineage mode, content digest, and exact field set.
- CMB-CAP-1 Capability Authorization Passport with Ed25519-signed self-contained authority credentials, offline verification, external key fingerprint pinning, expiry enforcement, parent-digest lineage, monotonic delegation validation, `cmb-cap` CLI, MCP verification without private-key transport, experimental A2A extension metadata, VC 2.0-shaped non-conformant projection, strict schema, and hostile-path tests.
- CMB-SDL-1 Sovereign Delegation Language with a deterministic parser/compiler, `cmb.authority-ir.v1` schema, tamper-detecting SHA-256 IR digest, monotonic child-agent delegation checks, `cmb-sdl` CLI, MCP compilation tool, machine/agent discovery metadata, reference example, and fail-closed regression tests.
- Experimental `cmb-edu` educational subsystem with a Dual-Brain Stream parser, strict `cmb.edu.v1` Metacognitive Context Envelope, deny-by-default privacy declarations, installed CLI, child-facing Flamingoglyph curriculum, runnable example, and parser/schema/CLI tests. Human-declared context remains explicitly distinct from machine inference.
- Framework-agnostic CMB boundary policy evaluator with deterministic rejection codes and human-final authority.
- Versioned `cmb.boundary-event.v1` JSON Schema for cross-language policy-event interoperability.
- Strict `cmb.library.catalog.v1` JSON Schema with CI validation through the test suite.
- Zero-dependency interactive browser playground for local SHA-256 hashing, CMB-Z13 symbolic projections, machine-readable declarations, and explicit boundary checks.
- Human-readable manifesto library index.
- FastAPI boundary-guard example using explicit application facts rather than behavioral inference.
- Shared `cmb.boundary-conformance.v1` fixtures that define deterministic policy semantics and violation order across languages.
- TypeScript/Express boundary adapter with strict runtime parsing and shared-fixture tests.
- Rust/Actix Web boundary adapter with `deny_unknown_fields`, internal `HUMAN_FINAL` construction, and shared-fixture tests.
- Hosted polyglot conformance workflow covering strict TypeScript build/test plus Rust fmt, Clippy, and test gates.

### Changed

- The CMB Sovereignty Gate now feeds pull-request scan reports into `cmbc gate-report`; high-friction findings fail closed instead of being printed without enforcement.
- Governance bootstrap recovery now requires both repository-owner GitHub authentication and an explicit latest-commit `CMB-AUTHORIZED:` marker when a high-friction workflow change would otherwise self-lock the gate. This marker is documented as weaker than CMB Ed25519 authorization and does not replace branch protection or independent review.
- Ed25519 key files are now created exclusively with restrictive creation modes and no overwrite window.
- MCP, documentation, and C2PA workflow path filters now cover the source/schema dependencies they actually consume.
- Security support documentation now tracks the 1.4.x development line while keeping v1.4.0 unreleased until tag gates succeed.
- Cleaned duplicated roadmap and changelog sections created during the previous rapid platform upgrade.
- Boundary compatibility is now defined by executable shared fixtures rather than prose similarity alone.

## [1.3.1] - 2026-09-04

### Added

- Repository-maturity hardening: `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CODEOWNERS`, Dependabot, CodeQL, dependency review, OpenSSF Scorecard, a buildable MkDocs documentation site, an explicit threat model, project-maturity boundaries, and a public engineering roadmap.
- Experimental CMB-Z13 reference parser and CLI (`cmb-z13 parse|validate|explain|export-json`) with deterministic AST schema, fixed 13-lens conformance checks, machine-registry synchronization tests, and human-final authority encoded in the AST.
- Five minimal examples covering sealing, verification, C2PA interoperability, CMB-Z13 parsing, and the Guardian safety pipeline.
- Phase 2 C2PA interoperability round-trip: deterministic C2PA manifest-definition generation, reverse-domain assertion-label validation, a pinned/checksummed c2patool integration workflow, deterministic test media, and generic-reader verification that the exact CMB payload survives asset signing/binding and readback. Test credentials remain explicitly non-production and non-conformant.
- Deterministic `CMB receipt -> C2PA-facing assertion payload` adapter with privacy-minimized defaults, canonical JSON serialization, strict JSON Schema, CLI export, deterministic fixtures, and tests. The adapter explicitly does not create a C2PA manifest, Content Credential, signature, asset binding, or conformance result.
- Prior-art and legal-positioning document covering GDPR Article 22, EU AI Act Article 14, relevant scholarship, and C2PA as an external provenance standard.
- Two-minute CMB policy one-pager as the public front door, with deeper technical and symbolic materials moved to optional follow-on paths.
- C2PA interoperability design that explicitly treats `cmb_provenance` as complementary infrastructure and forbids false conformance claims.
- Public independent-review request defining a narrow security, provenance, and policy audit scope.
- **CMB-Z13™ ✦ Zodiac Computational Metacognitive Language** as a three-part canonical bundle: public manifesto, formal language specification, and machine-readable registry mapping thirteen zodiac archetypes to thirteen software-language lenses.
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

- CMB-Z13 advanced to registry v1.1.0 with a synchronized Guardian Modes teaching layer: thirteen fixed guardian aliases mapped directly to the existing thirteen software languages/operators, a seven-lens safety pipeline ending in human decision, and explicit rules that guardian, zodiac, and code labels do not define a person.
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
