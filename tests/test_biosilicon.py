from __future__ import annotations

import math

import pytest

from cmb_biosilicon import (
    BioSiliconBounds,
    BioSiliconState,
    verify_biosilicon_state,
)


def test_state_within_bounds_is_consistent() -> None:
    observed = BioSiliconState(0.97, 0.94, 0.96, 0.93)
    reference = BioSiliconState(1.0, 1.0, 1.0, 1.0)
    bounds = BioSiliconBounds(0.05, 0.10, 0.05, 0.10)

    result = verify_biosilicon_state(observed, reference, bounds)

    assert result.model_consistent is True
    assert result.claim == "WITHIN_DEFINED_BOUNDS"
    assert all(result.channels_within_bounds.values())
    assert result.to_dict()["protocol"] == "CMB://BIO_SILICON_VERIFICATION"
    assert result.to_dict()["symbolic_alias"] == "CMB://ORGANOID_SILICON_INTERFUSE"


def test_failed_channel_requires_backtrace() -> None:
    observed = BioSiliconState(0.97, 0.60, 0.96, 0.93)
    reference = BioSiliconState(1.0, 1.0, 1.0, 1.0)
    bounds = BioSiliconBounds(0.05, 0.10, 0.05, 0.10)

    result = verify_biosilicon_state(observed, reference, bounds)

    assert result.model_consistent is False
    assert result.claim == "BACKTRACE_REQUIRED"
    assert result.channels_within_bounds["R_elec"] is False


def test_invalid_numbers_are_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        BioSiliconState(math.inf, 1.0, 1.0, 1.0)

    with pytest.raises(ValueError, match="nonnegative"):
        BioSiliconBounds(-0.1, 0.1, 0.1, 0.1)
