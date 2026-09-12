from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest

from cmb_biosilicon import (
    BioSiliconBounds,
    BioSiliconState,
    validate_biosilicon_record,
    verify_biosilicon_state,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/cmb.bio-interface-state.v1.schema.json"
EXAMPLE_PATH = ROOT / "research/organoid-silicon/example_state.json"


def _schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_state_within_bounds_is_consistent() -> None:
    observed = BioSiliconState(0.97, 0.94, 0.96, 0.93)
    reference = BioSiliconState(1.0, 1.0, 1.0, 1.0)
    bounds = BioSiliconBounds(0.05, 0.10, 0.05, 0.10)

    result = verify_biosilicon_state(observed, reference, bounds)

    assert result.model_consistent is True
    assert result.claim == "WITHIN_DEFINED_BOUNDS"
    assert all(result.channels_within_bounds.values())
    assert result.residuals.max_abs() == pytest.approx(0.07)
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


def test_declared_decimal_boundary_survives_float_noise() -> None:
    observed = BioSiliconState(0.4, 1.0, 1.0, 1.0)
    reference = BioSiliconState(0.3, 1.0, 1.0, 1.0)
    bounds = BioSiliconBounds(0.1, 0.0, 0.0, 0.0)

    result = verify_biosilicon_state(observed, reference, bounds)

    assert result.residuals.biological > 0.1
    assert result.channels_within_bounds["R_bio"] is True
    assert result.model_consistent is True


def test_invalid_numbers_are_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        BioSiliconState(math.inf, 1.0, 1.0, 1.0)

    with pytest.raises(ValueError, match="nonnegative"):
        BioSiliconBounds(-0.1, 0.1, 0.1, 0.1)


def test_reference_verifier_output_conforms_to_public_schema() -> None:
    result = verify_biosilicon_state(
        BioSiliconState(0.97, 0.94, 0.96, 0.93),
        BioSiliconState(1.0, 1.0, 1.0, 1.0),
        BioSiliconBounds(0.05, 0.10, 0.05, 0.10),
    )

    schema = _schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result.to_dict())


def test_example_record_is_structurally_and_semantically_valid() -> None:
    record = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    schema = _schema()

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(record)

    result = validate_biosilicon_record(record)
    assert result.model_consistent is True
    assert result.claim == "WITHIN_DEFINED_BOUNDS"


def test_semantic_validator_rejects_contradictory_status() -> None:
    result = verify_biosilicon_state(
        BioSiliconState(0.97, 0.94, 0.96, 0.93),
        BioSiliconState(1.0, 1.0, 1.0, 1.0),
        BioSiliconBounds(0.05, 0.10, 0.05, 0.10),
    )
    tampered = deepcopy(result.to_dict())
    verification = tampered["verification"]
    assert isinstance(verification, dict)
    verification["status"] = "BACKTRACE_REQUIRED"

    Draft202012Validator(_schema()).validate(tampered)
    with pytest.raises(ValueError, match="status contradicts recomputation"):
        validate_biosilicon_record(tampered)
