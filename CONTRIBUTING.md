# Contributing to CMB

CMB accepts technical corrections, tests, security improvements, documentation,
interoperability work, policy critique, prior-art research, and carefully scoped
symbolic-language changes.

## Start with the project layer

- **Stable / operational:** `src/cmb_provenance/`, schemas, release tooling,
  interoperability, and policy.
- **Experimental:** CMB-Z13 parser/runtime and symbolic-language research.
- **Art / canon:** manifestos and code-poetry.

See `docs/PROJECT_LAYERS.md`.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test,build]"
pytest
cmb-provenance selftest
cmb-z13 validate '♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;'
```

## Pull-request standard

A strong pull request should solve one coherent problem, explain the evidence
boundary, include tests for executable behavior, update schemas/docs when
machine-readable behavior changes, avoid novelty claims without prior-art review,
preserve historical receipts, and keep CMB-Z13 mappings synchronized.

## AI-assisted implementation

AI assistance is allowed. Contributors remain responsible for review, testing,
and submitted claims. Generated code is not independently audited merely because
tests pass.

## CMB-Z13 changes

The 13 canonical sign/language/operator mappings are stable inputs to the current
specification. Proposed changes must be versioned and synchronized across the
specification, machine registry, runtime, and tests.

```text
PATTERN != PROOF
PROFILE != PERSON
GUARDIAN_MODE != PERSONALITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```
