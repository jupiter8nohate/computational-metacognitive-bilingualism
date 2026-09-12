# 2. Silicon Interface

The silicon layer is the instrumentation boundary between a biological preparation and an electronic system.

CMB models the interface abstractly:

```text
BIOLOGICAL SOURCE
      |
      v
SENSOR / INTERFACE
      |
      v
DIGITIZED MEASUREMENT
```

The implementation may involve electrophysiological hardware, imaging systems, signal-conditioning electronics, or other instrumentation. This documentation intentionally does not prescribe construction or experimental procedures.

## Electrical residual

Let `E` be a normalized electrical-interface measurement defined by a study.

```text
R_elec = E_observed - E_reference
```

A passing `R_elec` establishes only numerical agreement within the chosen tolerance.

## CMB invariant

```text
SENSOR_ACCESS != SEMANTIC_ACCESS
RECORDING != UNDERSTANDING
INTERFACE != IDENTITY
```

The instrument can expose signals. It cannot, merely by exposing them, determine what a biological system experiences, intends, or means.
