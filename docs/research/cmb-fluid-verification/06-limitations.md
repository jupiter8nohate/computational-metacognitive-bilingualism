# Limitations and falsifiability

This laboratory is intentionally narrow.

## What is verified

The reference script verifies an exact symbolic cancellation for a reduced forced model with:

```text
rho = constant
u = 0
v = 0
w = 0
E = constant
p(x,t) = cos(k*x - omega*t)
f_x = dp/dx
```

Under the implemented sign convention, the mass, x-momentum, and reduced energy residuals simplify exactly to zero.

## What is not established

The experiment does not establish:

- a general solution of the full 3D Navier-Stokes equations;
- existence or smoothness for arbitrary initial data;
- uniqueness;
- stability of the forced state;
- experimental realizability of the prescribed forcing;
- a thermodynamically closed compressible-fluid model;
- an entropy-production result;
- a physical interpretation for dimensions 5 through 8;
- superiority of CMB over established numerical-analysis or verification methods.

## Falsification conditions

The implementation should be considered incorrect if any of these occur:

```text
1. The symbolic derivative dp/dx is wrong.
2. The balancing force does not use the declared sign convention.
3. Any required residual is nonzero after simplification.
4. The documentation labels the reduced result a general Navier-Stokes solution.
5. The 5D-8D audit coordinates are represented as discovered physical dimensions.
```

## Evidence discipline

```text
EXACT_SYMBOLIC_ZERO != EXPERIMENTAL_VALIDATION
SELF_TEST != INDEPENDENT_AUDIT
VISUALIZATION != PHYSICAL_MECHANISM
MODEL != REALITY
PATTERN != PROOF
```

Independent review should focus first on the equations, sign convention, omitted terms, and the precise claim boundary before evaluating the artistic visualization layer.
