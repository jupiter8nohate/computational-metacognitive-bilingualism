# Exact forced equilibrium

The central result is a conditional symbolic equilibrium.

```text
              PRESSURE FIELD
                   |
                   v
        p(x,t) = cos(kx - omega*t)
                   |
                   v
        dp/dx = -k*sin(theta)
                   |
             ( ꩜ ᯅ ꩜;)
                   |
                   v
           UNFORCED R != 0
                   |
                  <-
               BACKTRACE
                   |
                   v
          IDENTIFY SOURCE TERM
                   |
                   v
              f_x = dp/dx
                   |
                   v
          dp/dx - f_x = 0
                   |
                   v
               VERIFIED
```

## Exact symbolic cancellation

```python
import sympy as sp

x, t = sp.symbols("x t", real=True)
k, omega = sp.symbols("k omega", real=True)

theta = k*x - omega*t
p = sp.cos(theta)

pressure_gradient = sp.diff(p, x)
force_x = pressure_gradient
R_momentum = sp.simplify(pressure_gradient - force_x)

assert R_momentum == 0
```

Expected symbolic values:

```text
pressure_gradient = -k*sin(k*x - omega*t)
force_x            = -k*sin(k*x - omega*t)
R_momentum         = 0
```

## What the zero means

`R_momentum == 0` means the chosen field and balancing term satisfy the stated reduced equation exactly in symbolic algebra. It does not by itself establish experimental realizability, stability, uniqueness, thermodynamic closure, or validity for an arbitrary physical fluid.

```text
RESIDUAL_ZERO != UNIVERSAL_TRUTH
MODEL_VALIDITY != REALITY
```
