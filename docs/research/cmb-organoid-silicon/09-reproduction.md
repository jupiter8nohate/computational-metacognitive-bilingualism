# 9. Reproduce

This page reproduces the **software verification model only**. It is not a biological laboratory protocol.

## Install

From the repository root:

```bash
python -m pip install -e ".[test]"
```

## Run the reference example

```bash
python research/organoid-silicon/cmb_organoid_matrix.py
```

Expected verification state:

```text
WITHIN_DEFINED_BOUNDS
```

for the bundled demonstration values.

## Run tests

```bash
pytest tests/test_biosilicon.py
```

## Python API

```python
from cmb_biosilicon import (
    BioSiliconBounds,
    BioSiliconState,
    validate_biosilicon_record,
    verify_biosilicon_state,
)

observed = BioSiliconState(0.97, 0.94, 0.96, 0.93)
reference = BioSiliconState(1.0, 1.0, 1.0, 1.0)
bounds = BioSiliconBounds(0.05, 0.10, 0.05, 0.10)

result = verify_biosilicon_state(observed, reference, bounds)
record = result.to_dict()
validate_biosilicon_record(record)
print(record)
```

The values above are synthetic demonstration inputs. They are not biological thresholds and must not be treated as scientific or clinical reference values.

## Two-stage machine validation

The public JSON Schema validates the **shape and types** of a record. JSON Schema does not perform the arithmetic needed to prove that residuals, channel verdicts, and status agree with the supplied observation, reference, and tolerance.

The complete validation pipeline is therefore:

```text
JSON RECORD
    |
    v
JSON SCHEMA
structural validation
    |
    v
validate_biosilicon_record(...)
semantic recomputation
    |
    v
RESIDUALS + CHANNEL VERDICTS + STATUS AGREE?
    |
   YES -> ACCEPT AS INTERNALLY CONSISTENT
   NO  -> REJECT / BACKTRACE
```

A consumer must not treat schema validity alone as a verified result. The semantic validator recomputes the derived fields and rejects a record whose declared status contradicts its numerical inputs.

## Machine-readable resources

- `schemas/cmb.bio-interface-state.v1.schema.json`
- `research/organoid-silicon/example_state.json`
- `src/cmb_biosilicon/model.py`
- `tests/test_biosilicon.py`

## Verification principle

```text
SCHEMA_VALID != ARITHMETICALLY_VERIFIED
REPRODUCIBLE_CODE != REPRODUCED_EXPERIMENT
SYNTHETIC_EXAMPLE != BIOLOGICAL_THRESHOLD
SOFTWARE_PASS != SCIENTIFIC_VALIDATION
```
