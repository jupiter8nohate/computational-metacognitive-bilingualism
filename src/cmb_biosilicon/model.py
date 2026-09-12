"""Bounded verification for bio-silicon interface observations.

The module intentionally separates measurement from interpretation. A passing
residual test means only that observed channels fall within declared bounds for
a stated reference condition. It does not establish consciousness, cognition,
intent, or identity.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
import math
from typing import Final

PROTOCOL_ID: Final = "CMB://BIO_SILICON_VERIFICATION"
SYMBOLIC_ALIAS: Final = "CMB://ORGANOID_SILICON_INTERFUSE"
PROTOCOL_VERSION: Final = "1.0"
VERIFICATION_METHOD: Final = "bounded_residual"

# Relative tolerance protects a declared nonzero boundary from binary float
# representation noise. Zero tolerance remains exact. The absolute tolerance is
# used only when comparing serialized residuals with recomputed residuals.
_COMPARISON_REL_TOL: Final = 1e-12
_SERIALIZATION_ABS_TOL: Final = 1e-15

CLAIM_BOUNDARIES: Final[tuple[str, ...]] = (
    "ORGANOID != BRAIN",
    "SIGNAL != THOUGHT",
    "ACTIVITY != CONSCIOUSNESS",
    "STIMULATION != CONTROL",
    "MODEL != MIND",
    "PATTERN != PROOF",
    "CAPABILITY != AUTHORITY",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)


def _finite_nonnegative(name: str, value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if number < 0:
        raise ValueError(f"{name} must be nonnegative")
    return number


def _finite(name: str, value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _within_bound(residual: float, tolerance: float) -> bool:
    """Return whether a residual is within a declared bound.

    The direct comparison handles ordinary cases. ``math.isclose`` protects a
    nonzero decimal boundary from binary floating-point representation noise.
    A declared zero tolerance remains an exact-zero requirement.
    """

    magnitude = abs(residual)
    if magnitude <= tolerance:
        return True
    if tolerance == 0.0:
        return False
    return math.isclose(
        magnitude,
        tolerance,
        rel_tol=_COMPARISON_REL_TOL,
        abs_tol=0.0,
    )


@dataclass(frozen=True, slots=True)
class BioSiliconState:
    """Observed or reference state for the four-channel verification model."""

    biological: float
    electrical: float
    optical: float
    modulation: float

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            object.__setattr__(self, name, _finite(name, value))


@dataclass(frozen=True, slots=True)
class BioSiliconBounds:
    """Per-channel absolute residual tolerances."""

    biological: float
    electrical: float
    optical: float
    modulation: float

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            object.__setattr__(self, name, _finite_nonnegative(name, value))


@dataclass(frozen=True, slots=True)
class BioSiliconResiduals:
    """Signed residual vector: observed minus reference."""

    biological: float
    electrical: float
    optical: float
    modulation: float

    def max_abs(self) -> float:
        return max(abs(value) for value in asdict(self).values())


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """Result of a bounded four-channel residual audit."""

    observed: BioSiliconState
    reference: BioSiliconState
    bounds: BioSiliconBounds
    residuals: BioSiliconResiduals
    channels_within_bounds: dict[str, bool]
    model_consistent: bool
    claim: str

    @property
    def protocol(self) -> str:
        return PROTOCOL_ID

    @property
    def symbolic_alias(self) -> str:
        return SYMBOLIC_ALIAS

    @property
    def version(self) -> str:
        return PROTOCOL_VERSION

    @property
    def claim_boundaries(self) -> tuple[str, ...]:
        return CLAIM_BOUNDARIES

    def to_dict(self) -> dict[str, object]:
        """Serialize to the canonical public verification-record contract."""

        return {
            "protocol": self.protocol,
            "symbolic_alias": self.symbolic_alias,
            "version": self.version,
            "observation": asdict(self.observed),
            "reference": asdict(self.reference),
            "tolerance": asdict(self.bounds),
            "residuals": asdict(self.residuals),
            "channels_within_bounds": dict(self.channels_within_bounds),
            "verification": {
                "method": VERIFICATION_METHOD,
                "status": self.claim,
                "model_consistent": self.model_consistent,
            },
            "claim_boundaries": list(self.claim_boundaries),
        }


def verify_biosilicon_state(
    observed: BioSiliconState,
    reference: BioSiliconState,
    bounds: BioSiliconBounds,
) -> VerificationResult:
    """Compare observed state with a reference using declared channel bounds.

    The function performs no biological or cognitive inference. It only answers
    whether each numerical observation lies within the caller-declared tolerance
    of the caller-declared reference.
    """

    residuals = BioSiliconResiduals(
        biological=observed.biological - reference.biological,
        electrical=observed.electrical - reference.electrical,
        optical=observed.optical - reference.optical,
        modulation=observed.modulation - reference.modulation,
    )

    channels = {
        "R_bio": _within_bound(residuals.biological, bounds.biological),
        "R_elec": _within_bound(residuals.electrical, bounds.electrical),
        "R_opt": _within_bound(residuals.optical, bounds.optical),
        "R_mod": _within_bound(residuals.modulation, bounds.modulation),
    }
    consistent = all(channels.values())

    return VerificationResult(
        observed=observed,
        reference=reference,
        bounds=bounds,
        residuals=residuals,
        channels_within_bounds=channels,
        model_consistent=consistent,
        claim="WITHIN_DEFINED_BOUNDS" if consistent else "BACKTRACE_REQUIRED",
    )


def _record_mapping(record: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = record.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"{key} must be an object")
    return value


def _record_number(section: Mapping[str, object], key: str, label: str) -> float:
    try:
        value = section[key]
    except KeyError as exc:
        raise ValueError(f"{label}.{key} is missing") from exc
    if isinstance(value, bool):
        raise ValueError(f"{label}.{key} must be numeric, not boolean")
    try:
        return _finite(f"{label}.{key}", float(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}.{key} is invalid") from exc


def _state_from_record(record: Mapping[str, object], key: str) -> BioSiliconState:
    section = _record_mapping(record, key)
    return BioSiliconState(
        biological=_record_number(section, "biological", key),
        electrical=_record_number(section, "electrical", key),
        optical=_record_number(section, "optical", key),
        modulation=_record_number(section, "modulation", key),
    )


def _bounds_from_record(record: Mapping[str, object]) -> BioSiliconBounds:
    section = _record_mapping(record, "tolerance")
    values = {
        key: _record_number(section, key, "tolerance")
        for key in ("biological", "electrical", "optical", "modulation")
    }
    return BioSiliconBounds(**values)


def validate_biosilicon_record(record: Mapping[str, object]) -> VerificationResult:
    """Recompute a serialized record and reject contradictory derived fields.

    JSON Schema validates the public record's structure. This function performs
    the arithmetic semantic check that JSON Schema cannot express: residuals,
    channel verdicts, model consistency, and status must all match recomputation.
    The verified result is returned when the record is semantically consistent.
    """

    if record.get("protocol") != PROTOCOL_ID:
        raise ValueError("protocol does not match the CMB bio-silicon protocol")
    if record.get("symbolic_alias") != SYMBOLIC_ALIAS:
        raise ValueError("symbolic_alias does not match the canonical alias")
    if record.get("version") != PROTOCOL_VERSION:
        raise ValueError("version is not supported")

    observed = _state_from_record(record, "observation")
    reference = _state_from_record(record, "reference")
    bounds = _bounds_from_record(record)
    expected = verify_biosilicon_state(observed, reference, bounds)

    residual_record = _record_mapping(record, "residuals")
    expected_residuals = asdict(expected.residuals)
    for channel, expected_value in expected_residuals.items():
        actual_value = _record_number(residual_record, channel, "residuals")
        if not math.isclose(
            actual_value,
            expected_value,
            rel_tol=_COMPARISON_REL_TOL,
            abs_tol=_SERIALIZATION_ABS_TOL,
        ):
            raise ValueError(f"residuals.{channel} contradicts recomputation")

    channels_record = _record_mapping(record, "channels_within_bounds")
    if dict(channels_record) != expected.channels_within_bounds:
        raise ValueError("channels_within_bounds contradicts recomputation")

    verification = _record_mapping(record, "verification")
    if verification.get("method") != VERIFICATION_METHOD:
        raise ValueError("verification.method is not supported")
    if verification.get("status") != expected.claim:
        raise ValueError("verification.status contradicts recomputation")
    if verification.get("model_consistent") is not expected.model_consistent:
        raise ValueError("verification.model_consistent contradicts recomputation")

    boundaries = record.get("claim_boundaries")
    if boundaries != list(CLAIM_BOUNDARIES):
        raise ValueError("claim_boundaries do not match the canonical boundaries")

    return expected
