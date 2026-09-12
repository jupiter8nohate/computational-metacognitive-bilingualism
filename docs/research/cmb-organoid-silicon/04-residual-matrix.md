# 4. Residual Matrix

The core CMB bio-silicon object is a four-channel residual vector.

```text
S_observed  = (B_o, E_o, O_o, M_o)
S_reference = (B_r, E_r, O_r, M_r)

R = S_observed - S_reference
  = (R_bio, R_elec, R_opt, R_mod)
```

where:

```text
R_bio  = B_o - B_r
R_elec = E_o - E_r
R_opt  = O_o - O_r
R_mod  = M_o - M_r
```

## Bounded verification

Biological observations ordinarily contain variability and measurement uncertainty, so the default model is bounded rather than exact-zero verification.

```text
PASS_i := abs(R_i) <= epsilon_i
```

The complete state passes only when all declared channels pass:

```text
MODEL_CONSISTENT := PASS_bio
                 and PASS_elec
                 and PASS_opt
                 and PASS_mod
```

This produces two machine states:

```text
WITHIN_DEFINED_BOUNDS
BACKTRACE_REQUIRED
```

Neither state is an ontological statement about mind or consciousness. It is an audit result for a declared numerical model.

## Structural connection to CMB Physics Lab

```text
PHYSICS                     BIO-SILICON
--------                    -----------
state                       observation
reference equation          reference condition
physical residual           channel residual
tolerance / exactness       tolerance
verification                verification
bounded conclusion          bounded conclusion
```

The common architecture is:

```text
MODEL -> MEASURE -> RESIDUAL -> BACKTRACE -> VERIFY -> BOUNDED CLAIM
```
