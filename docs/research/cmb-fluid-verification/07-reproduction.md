# Reproduce the experiment

The laboratory is designed to be auditable with a short symbolic script and a focused test.

## Install research dependencies

From the repository root:

```bash
python -m pip install -e ".[research,test]"
```

The research extra adds SymPy without making symbolic mathematics a required dependency of the core CMB package.

## Run the reference implementation

```bash
python research/fluid-verification/cmb_navier_stokes.py
```

Expected core result:

```text
□ MASS       -> 0
△ MOMENTUM   -> 0
⬡ ENERGY     -> 0
STATUS       -> VERIFIED_UNDER_STATED_ASSUMPTIONS
```

## Run the test

```bash
pytest tests/test_cmb_fluid_verification.py
```

## Independent verification checklist

A reviewer should independently confirm:

```text
[ ] theta = k*x - omega*t
[ ] p = cos(theta)
[ ] dp/dx = -k*sin(theta)
[ ] u = 0
[ ] rho = constant
[ ] E = constant
[ ] f_x = dp/dx under the implemented residual sign convention
[ ] R_mass = 0
[ ] R_momentum = 0
[ ] R_energy = 0
```

Then separately evaluate whether the reduced equation is an appropriate model for the physical question being studied.

## Research extension path

A stronger next experiment would replace the forced zero-velocity case with a nontrivial exact dynamic benchmark, such as a viscously decaying transverse shear mode, and compare symbolic residual verification against numerical discretization error.

That extension should remain separate from the present result so the current claim stays reproducible and bounded.
