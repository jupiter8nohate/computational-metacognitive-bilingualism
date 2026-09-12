# CMB Bio-Silicon Verification Laboratory

Protocol: `CMB://BIO_SILICON_VERIFICATION`

Symbolic alias: `CMB://ORGANOID_SILICON_INTERFUSE`

This directory contains a bounded, non-clinical verification model for describing measurements from bio-silicon research interfaces. It is a software and epistemic audit artifact, not a wet-lab protocol and not a claim that neural tissue is a person, a brain, or a conscious mind.

## Verification vector

```text
R = [R_bio, R_elec, R_opt, R_mod]
```

Each residual is defined as an observed numerical value minus a stated reference value. A channel passes only when its absolute residual is less than or equal to a declared tolerance.

```text
OBSERVATION
    |
    v
RESIDUAL VECTOR
    |
    v
WITHIN DECLARED BOUNDS?
   / \
 YES  NO
  |    |
  v    v
BOUNDED  BACKTRACE
CLAIM    REQUIRED
```

A passing result means only `WITHIN_DEFINED_BOUNDS`. It does not establish cognition, consciousness, intent, identity, sentience, or biological equivalence to a human brain.

## CMB claim boundaries

```text
ORGANOID != BRAIN
SIGNAL != THOUGHT
ACTIVITY != CONSCIOUSNESS
STIMULATION != CONTROL
MODEL != MIND
PATTERN != PROOF
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Software

The reference implementation is `src/cmb_biosilicon/model.py`. Tests are in `tests/test_biosilicon.py`. The public JSON Schema is `schemas/cmb.bio-interface-state.v1.schema.json`.

## Scientific context

The project is informed by published work on organoid intelligence, neural cultures, microelectrode arrays, calcium imaging, and biohybrid computing. Representative sources include:

- Smirnova L, Caffo B, Johnson EC. *Reservoir computing with brain organoids*. Nature Electronics 6, 943-944 (2023). DOI: 10.1038/s41928-023-01096-7.
- Cai H, Ao Z, Tian C, et al. *Brain organoid reservoir computing for artificial intelligence*. Nature Electronics 6, 1032-1039 (2023). DOI: 10.1038/s41928-023-01069-w.
- Smirnova L, et al. *Organoid intelligence (OI): the new frontier in biocomputing and intelligence-in-a-dish*. Frontiers in Science 1 (2023). DOI: 10.3389/fsci.2023.1017235.
- Gu L, et al. *Functional Neural Networks in Human Brain Organoids*. Neuroscience Bulletin (2024). PMID: 39314749.

These references establish research context. They do not validate every CMB interpretation or symbolic layer.
