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
    verify_biosilicon_state,
)

observed = BioSiliconState(0.97, 0.94, 0.96, 0.93)
reference = BioSiliconState(1.0, 1.0, 1.0, 1.0)
bounds = BioSiliconBounds(0.05, 0.10, 0.05, 0.10)

result = verify_biosilicon_state(observed, reference, bounds)
print(result.to_dict())
```

The values above are synthetic demonstration inputs. They are not biological thresholds and must not be treated as scientific or clinical reference values.

## Machine-readable resources

- `schemas/cmb.bio-interface-state.v1.schema.json`
- `research/organoid-silicon/example_state.json`
- `src/cmb_biosilicon/model.py`
- `tests/test_biosilicon.py`

## Verification principle

```text
REPRODUCIBLE_CODE != REPRODUCED_EXPERIMENT
SYNTHETIC_EXAMPLE != BIOLOGICAL_THRESHOLD
SOFTWARE_PASS != SCIENTIFIC_VALIDATION
```
