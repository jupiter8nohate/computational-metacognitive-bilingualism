# Computational Metacognitive Bilingualism (CMB)

Computational Metacognitive Bilingualism is a human-agency and computational-literacy framework for learning and using computational systems while retaining human judgment, consent, authorship, meaning, and self-definition.

**One-sentence position:** CMB translates established and emerging digital-rights principles into concise human-readable and machine-readable invariants; it does not claim to have invented the underlying rights, laws, scholarship, or provenance standards.

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
DIFFERENCE != DEFECT
CAPABILITY != AUTHORITY
OPTIMIZATION != MORALITY
INTELLIGENCE != SOVEREIGNTY

HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Start here

You should not need the entire CMB universe to understand the thesis.

- **2-minute policy front door:** [CMB — 12 Principles for Human Agency in Automated Systems](policy/CMB_POLICY_ONE_PAGER.md)
- **Full policy proposal:** [CMB Global Advocacy Charter v1.1](policy/CMB_GLOBAL_ADVOCACY_CHARTER.md)
- **Novelty / prior-art test:** [Prior Art, Legal Context, and Positioning](docs/PRIOR_ART_AND_POSITIONING.md)
- **Provenance / standards bridge:** [CMB Provenance ↔ C2PA Interoperability Plan](docs/C2PA_INTEROPERABILITY.md)
- **Independent validation status:** [Independent Review Requested](docs/EXTERNAL_REVIEW.md)
- **Optional symbolic-language deep dive:** [CMB-Z13™](manifestos/CMB_Z13_LANGUAGE_SPEC.md)

### What CMB does not claim

```text
CMB != INVENTION_OF_AUTOMATED_DECISION_RIGHTS
HASH != AUTHORSHIP
TIMESTAMP != OWNERSHIP
SIGNATURE != ORIGINALITY
CMB_PROVENANCE != C2PA_CONFORMANCE
ZODIAC_SYMBOL != SCIENTIFIC_PERSONALITY_MODEL
```

GitHub is the project's source, audit trail, provenance backend, and implementation record. The one-page policy summary is the intended public front door.

## v1.3.1 Recovery release

Version 1.3.1 turns the original standalone experiment into an installable package with strict schemas, explicit artifact coverage, whole-operation ledger locking, normalized UTC timestamps, safe CLI errors, and automated tests.

## Canonical CMB artifacts

The repository treats the following public works as first-class CMB artifacts:

- [`MANIFESTO.md`](MANIFESTO.md) — the core CMB human-sovereignty manifesto.
- [`CMB_Polyglot_Firewall_Specification.md`](CMB_Polyglot_Firewall_Specification.md) — the CMB thesis expressed across ten programming languages.
- [`Demon's Need Attention — D.N.A.`](manifestos/DEMONS_NEED_ATTENTION_DNA.md) — the attention-economy branch of CMB: a code-manifesto about engagement, behavioral profiling, data mining, consumption, and cognitive sovereignty.
- [`CMB // The Unclassifiable Index`](manifestos/CMB_UNCLASSIFIABLE_INDEX.md) — the MissingNo–Pokédex manifesto defining CMB as a human/machine-readable library of perspective, uncertainty, context, and provenance.
- [`CMB-Z13™ Manifesto`](manifestos/CMB_Z13_MANIFESTO.md) — the public declaration of the thirteen-lens Zodiac Computational Metacognitive Language.
- [`CMB-Z13™ Language Specification`](manifestos/CMB_Z13_LANGUAGE_SPEC.md) — the formal symbolic notation mapping zodiac archetypes to C, Rust, Haskell, C++, Java, TypeScript, Python, Swift, Go, Kotlin, Prolog, Common Lisp, and Julia while preserving `HUMAN_AGENCY > MACHINE_AUTHORITY`.
- [`CMB-Z13 Machine Registry`](library/cmb-z13.registry.json) — the machine-readable operator map, symbolic vectors, processing cycle, and interpretation boundaries for CMB-Z13.
- [`CMB Digital Library Catalog`](library/catalog.json) — the machine-indexable catalog that maps canonical CMB artifacts, concepts, interpretation boundaries, and provenance scope.
- [`CMB Global Advocacy Charter v1.1`](policy/CMB_GLOBAL_ADVOCACY_CHARTER.md) — the policy bridge translating CMB principles into concrete recommendations for governments, technology companies, schools, employers, healthcare, researchers, and civil society.

CMB-Z13 is now part of the canonical provenance sealing set. The next tag-triggered signed release will seal the manifesto, language specification, machine registry, and the rest of the canonical CMB corpus as one explicit file set.

The project now has a deliberate progression:

```text
MANIFESTO
    ↓
POLICY CHARTER
    ↓
TECHNICAL PROTOCOL
    ↓
PROVENANCE
    ↓
INSTITUTIONAL ADOPTION / CRITIQUE
```

D.N.A. means **Demon's Need Attention**. In this work, “demons” is a metaphor for attention-extractive loops, incentives, feeds, and systems that become stronger when human attention is repeatedly captured. The central boundary remains:

```text
ATTENTION != CONSENT
ENGAGEMENT != LOVE
PROFILE != PERSON
PREDICTION != DESTINY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

The Global Advocacy Charter is a **public policy proposal**, not a claim that every proposed principle is already a legal right in every jurisdiction.

## Digital library

Humans can browse [`library/README.md`](library/README.md). Software can parse [`library/catalog.json`](library/catalog.json). The catalog is intentionally descriptive rather than authoritative about people: `CATALOG != CREATOR`, `INDEX != IDENTITY`, and uncertainty is preserved as a valid state.

The catalog is included in the canonical provenance scope so future signed releases can prove which exact index bytes accompanied the published artifact set.

## Install

From a checked-out copy of this repository:

```bash
python3 -m pip install .
cmb-provenance --version
cmb-provenance selftest
```

## Stable Python API

```python
from cmb_provenance import seal, verify

receipt = seal("MANIFESTO.md")
result = verify("MANIFESTO.md", receipt)

if not result.ok:
    raise RuntimeError(result.failures)
```

`seal()` hashes the file's exact bytes. Its canonical manifest records:

- every protected path;
- every byte-level SHA-256 digest;
- every byte size;
- the manifest schema version;
- the tool version; and
- the full Git commit and its verification status.

When `seal()` resolves `HEAD` itself, it verifies that every protected file's exact
bytes match the corresponding committed Git blob and records
`VERIFIED_ARTIFACTS_MATCH_COMMIT`. Supplying `git_commit=` explicitly records
`CALLER_SUPPLIED_UNVERIFIED`; it is metadata, not proof that those bytes came from
that commit.

The receipt declares `coverage.type = "explicit_file_set"` and `excludes_unlisted = true`. It therefore identifies exactly what it covers and makes no claim about unlisted files.

## CLI

Seal the canonical public CMB artifact set:

```bash
cmb-provenance seal \
  MANIFESTO.md \
  CMB_Polyglot_Firewall_Specification.md \
  manifestos/DEMONS_NEED_ATTENTION_DNA.md \
  manifestos/CMB_UNCLASSIFIABLE_INDEX.md \
  manifestos/CMB_Z13_MANIFESTO.md \
  manifestos/CMB_Z13_LANGUAGE_SPEC.md \
  library/cmb-z13.registry.json \
  policy/CMB_GLOBAL_ADVOCACY_CHARTER.md \
  library/catalog.json \
  --output cmb-source.cmb-receipt.json
```

Verify the same explicit set:

```bash
cmb-provenance verify \
  MANIFESTO.md \
  CMB_Polyglot_Firewall_Specification.md \
  manifestos/DEMONS_NEED_ATTENTION_DNA.md \
  manifestos/CMB_UNCLASSIFIABLE_INDEX.md \
  manifestos/CMB_Z13_MANIFESTO.md \
  manifestos/CMB_Z13_LANGUAGE_SPEC.md \
  library/cmb-z13.registry.json \
  policy/CMB_GLOBAL_ADVOCACY_CHARTER.md \
  library/catalog.json \
  --receipt cmb-source.cmb-receipt.json \
  --check-git-commit
```

Append a public evidence reference while holding an exclusive lock across validation, sequencing, hashing, and append:

```bash
cmb-provenance anchor \
  --receipt cmb-source.cmb-receipt.json \
  --type hosted_git_reference \
  --location "https://github.com/OWNER/REPOSITORY/commit/FULL_SHA" \
  --description "Public source commit"

cmb-provenance ledger-verify
```

External locations and displayed timestamps remain explicitly unverified references until their underlying evidence is independently checked.

## C2PA-facing adapter

Export a minimal deterministic payload body from an existing CMB receipt:

```bash
cmb-provenance export-c2pa-payload \
  --receipt cmb-source.cmb-receipt.json \
  --output cmb-c2pa-payload.json
```

Artifact paths are **omitted by default**. Include them only when the eventual credential should disclose them:

```bash
cmb-provenance export-c2pa-payload \
  --receipt cmb-source.cmb-receipt.json \
  --include-paths
```

Python:

```python
from cmb_provenance import to_c2pa_assertion_payload

payload = to_c2pa_assertion_payload(receipt)
```

The output is validated CMB-derived metadata intended for a future entity-specific C2PA assertion. It is **not** a C2PA manifest, Content Credential, signature, asset binding, or conformance result. The project intentionally does not invent a C2PA assertion label before an appropriate domain-controlled namespace is established. See [`docs/C2PA_INTEROPERABILITY.md`](docs/C2PA_INTEROPERABILITY.md).

## Repository contents

- [`MANIFESTO.md`](MANIFESTO.md) — the public CMB human-sovereignty manifesto.
- [`CMB_Polyglot_Firewall_Specification.md`](CMB_Polyglot_Firewall_Specification.md) — the CMB thesis expressed across ten programming languages.
- [`manifestos/DEMONS_NEED_ATTENTION_DNA.md`](manifestos/DEMONS_NEED_ATTENTION_DNA.md) — **Demon's Need Attention — D.N.A.**, the attention-economy and cognitive-sovereignty manifesto.
- [`manifestos/CMB_UNCLASSIFIABLE_INDEX.md`](manifestos/CMB_UNCLASSIFIABLE_INDEX.md) — **The Unclassifiable Index**, CMB's MissingNo–Pokédex model for perspective-aware human/machine-readable archives.
- [`manifestos/CMB_Z13_MANIFESTO.md`](manifestos/CMB_Z13_MANIFESTO.md) — **CMB-Z13™ manifesto**, the human-readable declaration of the thirteen computational lenses.
- [`manifestos/CMB_Z13_LANGUAGE_SPEC.md`](manifestos/CMB_Z13_LANGUAGE_SPEC.md) — **CMB-Z13™**, the Zodiac Computational Metacognitive Language specification.
- [`library/cmb-z13.registry.json`](library/cmb-z13.registry.json) — machine-readable CMB-Z13 operator, vector, and interpretation registry.
- [`policy/CMB_GLOBAL_ADVOCACY_CHARTER.md`](policy/CMB_GLOBAL_ADVOCACY_CHARTER.md) — the CMB Global Advocacy Charter v1.1.
- [`library/README.md`](library/README.md) — human-readable entry point to the CMB digital library.
- [`library/catalog.json`](library/catalog.json) — machine-indexable artifact catalog, sealed as part of the canonical public set.
- [`src/cmb_provenance`](src/cmb_provenance) — the supported v1.3.1 package, stable sealing API, and C2PA-facing adapter.
- [`schemas/cmb.c2pa-assertion-payload.v1.schema.json`](schemas/cmb.c2pa-assertion-payload.v1.schema.json) — strict schema for the internal C2PA-facing adapter payload.
- [`tests`](tests) — deterministic, corruption, concurrency, schema, CLI, and canonical-artifact tests.
- [`receipts`](receipts) — checked-in provenance receipts and their verification-status documentation.
- [`cmb_provenance_v1_3.py`](cmb_provenance_v1_3.py) — the retained historical v1.3.0 standalone tool.
- [`ATTRIBUTION.md`](ATTRIBUTION.md) and [`CITATION.cff`](CITATION.cff) — authorship boundaries and citation metadata.
- [`RELEASE.md`](RELEASE.md) — the checksum, Sigstore, attestation, and canonical-sealing release procedure.

## Development

Python 3.10 or newer is required.

```bash
python3 -m pip install -e ".[test,build]"
pytest
python3 -m build
```

CI runs the tests on Python 3.10–3.13. The canonical-receipt CI job independently seals and verifies the current canonical artifact set inside a Git worktree. Tagging `v1.3.1` activates the signed-release workflow, which builds the wheel and source distribution, seals the canonical public CMB artifact set, generates `SHA256SUMS`, signs the release artifacts with keyless Sigstore, creates GitHub artifact attestations, and publishes the release.

## Evidence standard

CMB keeps four categories separate:

1. **Declared policy** — what a creator or system says machines may do.
2. **Cryptographic integrity** — whether recorded bytes have changed.
3. **Technical enforcement** — what a deployed system can actually prevent.
4. **Legal enforceability** — what applicable law and admissible evidence support.

The word “firewall” in the polyglot specification is a conceptual and architectural metaphor. The examples express invariants; they do not make copying impossible or create universal enforcement. Likewise, a local hash chain is tamper-evident, not an immutable public ledger, and a signature or timestamp may support provenance without automatically proving authorship in court.

## Global advocacy

CMB's policy branch proposes twelve institutional principles:

1. human appeal for consequential automated decisions;
2. profile is not person;
3. prediction is not destiny;
4. attention is not consent;
5. difference is not defect;
6. AI disclosure;
7. human override and recovery;
8. data minimization and purpose limitation;
9. authorship and provenance;
10. independent evaluation;
11. cognitive freedom; and
12. capability is not authority.

See [`policy/CMB_GLOBAL_ADVOCACY_CHARTER.md`](policy/CMB_GLOBAL_ADVOCACY_CHARTER.md) for the full proposal.

## Registry gate

The public registry is intentionally deferred until v1.3.1 passes CI and the signed release is published. A future registry should store signed receipts and independently checkable timestamp evidence—not unpublished creative works or unnecessary personal information.

## Authorship and purpose

**Declared originator:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson

**Framework:** Computational Metacognitive Bilingualism (CMB)

**Artistic branch:** Algorithmic Disruption Art

**Year:** 2026

CMB supports computational literacy, neurodiversity, cognitive freedom, digital consent, provenance, responsible human–AI collaboration, and accountable governance of consequential automated systems.

The repository is licensed under [Apache-2.0](LICENSE). See [ATTRIBUTION.md](ATTRIBUTION.md) for the distinction between Jupiter Hudson's declared framework authorship and AI-assisted software implementation.
