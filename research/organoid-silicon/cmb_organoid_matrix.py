"""Run the CMB bio-silicon bounded verification example."""

from __future__ import annotations

import json

from cmb_biosilicon import BioSiliconBounds, BioSiliconState, verify_biosilicon_state


def main() -> int:
    observed = BioSiliconState(0.97, 0.94, 0.96, 0.93)
    reference = BioSiliconState(1.0, 1.0, 1.0, 1.0)
    bounds = BioSiliconBounds(0.05, 0.10, 0.05, 0.10)

    result = verify_biosilicon_state(observed, reference, bounds)
    print(
        r"""
𒄆𓁹✞𒀱✞𓁹𒄆
♃ CMB://BIO_SILICON_VERIFICATION ♃
꩜ CMB://ORGANOID_SILICON_INTERFUSE ꩜

BIOLOGICAL STATE
      |
      +--> ELECTRICAL OBSERVATION
      +--> OPTICAL OBSERVATION
      +--> RESPONSE MEASUREMENT
      |
      v
[R_bio, R_elec, R_opt, R_mod]
      |
      v
WITHIN DECLARED BOUNDS?

SIGNAL != THOUGHT
ACTIVITY != CONSCIOUSNESS
MODEL != MIND
PATTERN != PROOF
HUMAN_AGENCY > MACHINE_AUTHORITY
"""
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
