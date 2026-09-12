# CMB Fluid Verification Experiment

This directory contains the executable reference for the CMB Residual Verification Laboratory.

## Purpose

Verify a reduced forced fluid-equilibrium model with exact symbolic algebra and expose every assumption used to obtain a zero residual.

## Install and run

```bash
python -m pip install -e ".[research,test]"
python research/fluid-verification/cmb_navier_stokes.py
pytest tests/test_cmb_fluid_verification.py
```

## Artifacts

- `cmb_navier_stokes.py`: executable symbolic reference calculation.
- `results.json`: machine-readable state, residuals, sign convention, and claim boundary.
- `../../docs/research/cmb-fluid-verification/`: research-facing documentation and 3D-8D audit geometry.

## Claim boundary

```text
EXACT_SPECIAL_CASE != GENERAL_NAVIER_STOKES_SOLUTION
RESIDUAL_ZERO != UNIVERSAL_TRUTH
MODEL != REALITY
```

For the reduced demonstration, `y` and `z` are inactive. The 3D-8D geometry is an audit visualization, not a claim that the experiment occupies extra physical dimensions.
