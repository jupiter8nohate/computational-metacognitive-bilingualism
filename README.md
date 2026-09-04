# Computational Metacognitive Bilingualism (CMB)

Computational Metacognitive Bilingualism is a human-sovereignty framework for learning and using computational language while retaining human judgment, consent, authorship, meaning, and self-definition.

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

## v1.3.1 Recovery release

Version 1.3.1 turns the original standalone experiment into an installable package with strict schemas, explicit artifact coverage, whole-operation ledger locking, normalized UTC timestamps, safe CLI errors, and automated tests.

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

Seal one or more public artifacts:

```bash
cmb-provenance seal MANIFESTO.md \
  CMB_Polyglot_Firewall_Specification.md \
  --output cmb-source.cmb-receipt.json
```

Verify the same explicit set:

```bash
cmb-provenance verify MANIFESTO.md \
  CMB_Polyglot_Firewall_Specification.md \
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

## Repository contents

- [`MANIFESTO.md`](MANIFESTO.md) — the public CMB human-sovereignty manifesto.
- [`CMB_Polyglot_Firewall_Specification.md`](CMB_Polyglot_Firewall_Specification.md) — the CMB thesis expressed across ten programming languages.
- [`src/cmb_provenance`](src/cmb_provenance) — the supported v1.3.1 package and stable API.
- [`tests`](tests) — deterministic, corruption, concurrency, schema, and CLI tests.
- [`cmb_provenance_v1_3.py`](cmb_provenance_v1_3.py) — the retained historical v1.3.0 standalone tool.
- [`ATTRIBUTION.md`](ATTRIBUTION.md) and [`CITATION.cff`](CITATION.cff) — authorship boundaries and citation metadata.
- [`RELEASE.md`](RELEASE.md) — the checksum, Sigstore, and attestation release procedure.

## Development

Python 3.10 or newer is required.

```bash
python3 -m pip install -e ".[test,build]"
pytest
python3 -m build
```

CI runs the tests on Python 3.10–3.13. Tagging `v1.3.1` activates the signed-release workflow, which builds the wheel and source distribution, generates `SHA256SUMS`, signs the artifacts with keyless Sigstore, creates GitHub artifact attestations, and publishes the release.

## Evidence standard

CMB keeps four categories separate:

1. **Declared policy** — what a creator or system says machines may do.
2. **Cryptographic integrity** — whether recorded bytes have changed.
3. **Technical enforcement** — what a deployed system can actually prevent.
4. **Legal enforceability** — what applicable law and admissible evidence support.

The word “firewall” in the polyglot specification is a conceptual and architectural metaphor. The examples express invariants; they do not make copying impossible or create universal enforcement. Likewise, a local hash chain is tamper-evident, not an immutable public ledger, and a signature or timestamp may support provenance without automatically proving authorship in court.

## Registry gate

The public registry is intentionally deferred until v1.3.1 passes CI and the signed release is published. A future registry should store signed receipts and independently checkable timestamp evidence—not unpublished creative works or unnecessary personal information.

## Authorship and purpose

**Declared originator:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8

**Framework:** Computational Metacognitive Bilingualism (CMB)

**Artistic branch:** Algorithmic Disruption Art

**Year:** 2026

CMB supports computational literacy, neurodiversity, cognitive freedom, digital consent, provenance, and responsible human–AI collaboration.

The repository is licensed under [Apache-2.0](LICENSE). See [ATTRIBUTION.md](ATTRIBUTION.md) for the distinction between Jupiter Hudson's declared framework authorship and AI-assisted software implementation.
