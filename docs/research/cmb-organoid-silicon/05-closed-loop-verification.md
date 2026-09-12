# 5. Closed-Loop Verification

The laboratory treats a bio-silicon experiment as an auditable feedback system rather than as a black box.

```text
OBSERVE
   |
   v
COMPARE TO REFERENCE
   |
   v
COMPUTE RESIDUALS
   |
   v
CHECK DECLARED BOUNDS
   |
   +------ PASS ------> BOUNDED CLAIM
   |
   +------ FAIL ------> BACKTRACE
                           |
                           v
                     inspect source,
                     preprocessing,
                     calibration,
                     assumptions,
                     reference,
                     tolerance
```

## Backtrace

`BACKTRACE_REQUIRED` means the verification layer has found at least one mismatch large enough to exceed a declared tolerance. It does not identify the cause automatically.

Potential categories include measurement error, preprocessing error, reference mismatch, biological variability, interface drift, or a model assumption that no longer fits the observation.

## No forced interpretation

CMB deliberately stops before semantic overreach:

```text
PASS != INTELLIGENCE
FAIL != ABSENCE_OF_INTELLIGENCE
RESPONSE != INTENT
ADAPTATION != CONSCIOUSNESS
```

The verifier determines whether declared numerical conditions were met. Researchers remain responsible for experimental interpretation and evidence quality.
