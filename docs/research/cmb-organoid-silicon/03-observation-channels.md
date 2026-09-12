# 3. Observation Channels

CMB separates observation channels so that agreement in one modality cannot silently stand in for agreement in another.

```text
BIOLOGICAL STATE
      |
      +--> B : biological-state measurement
      +--> E : electrical measurement
      +--> O : optical observation
      +--> M : measured interface response
```

## Channel separation

`B`, `E`, `O`, and `M` are not interchangeable. Each requires its own definition, reference, tolerance, uncertainty model, and provenance.

```text
ELECTRICAL_PATTERN != OPTICAL_PATTERN
OPTICAL_PATTERN != BIOLOGICAL_STATE
MULTIMODAL_AGREEMENT != CONSCIOUSNESS
```

## Optical residual

For a declared optical metric:

```text
R_opt = O_observed - O_reference
```

The same bounded logic applies to the remaining channels.

## Provenance requirement

A scientifically useful record should preserve at least:

- what each channel measures;
- units or normalization method;
- reference state;
- tolerance and uncertainty assumptions;
- acquisition timestamp or experimental identifier;
- preprocessing applied before verification.

CMB treats missing provenance as a reason to weaken the claim, not as permission to fill gaps with inference.
