# CMB Fluid Verification Experiment

This directory contains the executable reference for the CMB Residual Verification Laboratory.

## Purpose

Verify a reduced forced fluid-equilibrium model with exact symbolic algebra and expose every assumption used to obtain a zero residual.

## Run

```bash
python research/fluid-verification/cmb_navier_stokes.py
```

## Claim boundary

```text
EXACT_SPECIAL_CASE != GENERAL_NAVIER_STOKES_SOLUTION
RESIDUAL_ZERO != UNIVERSAL_TRUTH
MODEL != REALITY
```

Documentation: `docs/research/cmb-fluid-verification/`.
