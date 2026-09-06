# Contributing to CMB

Contributions are welcome when they preserve the project's evidence boundaries and human-agency invariants.

## Choose the right lane

- **Stable engineering:** `src/cmb_provenance/`, schemas, tests, release and C2PA integration.
- **Experimental language research:** CMB-Z13 parser/notation and Guardian Modes.
- **Art / canon / policy:** manifestos, symbolic writing, policy proposals, and authored interpretive material.

Do not silently move a claim from one lane to another. A metaphor is not a security control; a test result is not a legal conclusion.

## Development setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test,build,docs]"
pytest
cmb-provenance selftest
cmb-z13 validate '♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;'
python scripts/build_docs.py
```

## Implementation standard

When a contribution is authorized and technically feasible:

- implement the requested change rather than stopping at a plan;
- make routine reversible decisions without unnecessary approval loops;
- finish read-only inspection, branch preparation, edits, and relevant tests before escalating a required approval gate;
- request approval before destructive, irreversible, security-sensitive, or otherwise unauthorized changes;
- keep verification proportional to the change and expand it only when a concrete unresolved concern remains; and
- report what changed, what passed, and what remains uncertain.

Repository defaults do not override explicit task instructions unless a higher-priority safety, legal, security, or permission boundary applies.

```text
PLAN != PATCH
PATCH != PROOF
TEST_SCOPE ~= CHANGE_SCOPE
RECOVERY > ASSUMPTION
```

## Pull requests

Keep PRs narrow and explain:

1. the problem;
2. the evidence or reproduction;
3. the intended behavior;
4. the tests added or changed;
5. any compatibility, privacy, provenance, or legal-claim implications.

For security-sensitive changes, include a Recovery path and a regression test.

## CMB-Z13 changes

The root registry `library/cmb-z13.registry.json` is canonical for the authored mapping. Parser changes must remain synchronized with it.

```text
ZODIAC_SYMBOL != PERSON
CODE != IDENTITY
GUARDIAN_MODE != PERSONALITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Provenance changes

```text
DECLARED_POLICY
!= CRYPTOGRAPHIC_INTEGRITY
!= TECHNICAL_ENFORCEMENT
!= LEGAL_ENFORCEABILITY
```

Do not claim a hash, signature, timestamp, Git commit, receipt, or Content Credential proves more than it actually proves.

## Security reports

Do not put sensitive vulnerability details in a public PR or issue. Follow [SECURITY.md](SECURITY.md).
