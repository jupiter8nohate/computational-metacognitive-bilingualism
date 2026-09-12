# CMB Residual Verification Laboratory

**Symbolic fluid balance, residual verification, and 3D-8D audit geometry**

This research note presents a bounded Computational Metacognitive Bilingualism (CMB) experiment around a simplified forced fluid-equilibrium model. The purpose is not to claim a general solution of the Navier-Stokes equations. The purpose is to demonstrate a reproducible verification pipeline:

```text
MODEL -> DIFFERENTIATE -> RESIDUAL -> BACKTRACE -> CORRECT -> VERIFY
```

## Claim boundary

This work **does not** claim:

- a general solution of the three-dimensional Navier-Stokes equations;
- that five through eight physical spatial dimensions are required;
- that geometric projection changes the governing physics;
- that a zero symbolic residual establishes universal physical truth.

This work **does** demonstrate:

- exact symbolic differentiation with SymPy;
- a forced zero-velocity pressure-field equilibrium;
- explicit residual computation and exact cancellation;
- bounded verification under stated assumptions;
- a 3D-8D **audit-state visualization** for communicating physical variables, residuals, provenance, and verification state.

## Core experiment

Let

```text
theta = k*x - omega*t
u = 0
p = cos(theta)
```

Then

```text
dp/dx = -k*sin(theta)
```

The unforced x-momentum residual is therefore nonzero in general. Introduce an external balancing force density using the sign convention implemented in the reference script:

```text
f_x = dp/dx
R_momentum = dp/dx - f_x = 0
```

The result is an exact symbolic balance for the reduced model.

## 3D-8D audit geometry

The geometric layer is an explanatory coordinate system, not a claim about extra physical dimensions.

```text
3D  CUBE       -> physical space (x,y,z)
4D  TESSERACT  -> spacetime (x,y,z,t)
5D  PENTERACT  -> continuity residual R_mass
6D  HEXERACT   -> momentum residual norm ||R_momentum||
7D  HEPTERACT  -> energy residual R_energy
8D  OCTERACT   -> verification / assumptions / provenance state
```

A compact audit-state representation is

```text
S_CMB = (x, y, z, t, R_mass, ||R_momentum||, R_energy, V)
```

where `V` is a bounded verification state. Dimensions 5-8 are bookkeeping coordinates in an augmented audit state space.

## CMB interpretation

```text
PATTERN != PROOF
MODEL != REALITY
RESIDUAL_ZERO != UNIVERSAL_TRUTH
SYMBOLIC_EXACTNESS != PHYSICAL_COMPLETENESS
CAPABILITY != AUTHORITY
```

A machine may differentiate, simplify, derive balancing terms, and verify a symbolic residual. Human researchers still define the modeling assumptions, physical interpretation, scope of the claim, and whether the model is appropriate for a real system.

## Reproduce

See:

- [Governing equations](01-equations.md)
- [Exact forced equilibrium](02-exact-forced-equilibrium.md)
- [Residual verification method](03-residual-method.md)
- [3D-8D audit geometry](04-hypergeometry-3d-8d.md)
- [AI verification bridge](05-ai-verification.md)
- [Limitations](06-limitations.md)
- [Reproduction](07-reproduction.md)

Reference implementation: `research/fluid-verification/cmb_navier_stokes.py`.
