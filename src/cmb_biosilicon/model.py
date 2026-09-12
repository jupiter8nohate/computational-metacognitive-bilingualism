"""Bounded verification for bio-silicon interface observations.

The module intentionally separates measurement from interpretation. A passing
residual test means only that observed channels fall within declared bounds for
a stated reference condition. It does not establish consciousness, cognition,
intent, or identity.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Final

PROTOCOL_ID: Final = "CMB://BIO_SILICON_VERIFICATION"
SYMBOLIC_ALIAS: Final = "CMB://ORGANOID_SILICON_INTERFUSE"
PROTOCOL_VERSION: Final = "1.0"

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

    protocol: str
    symbolic_alias: str
    version: str
    residuals: BioSiliconResiduals
    channels_within_bounds: dict[str, bool]
    model_consistent: bool
    claim: str
    claim_boundaries: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "protocol": self.protocol,
            "symbolic_alias": self.symbolic_alias,
            "version": self.version,
            "residuals": asdict(self.residuals),
            "channels_within_bounds": dict(self.channels_within_bounds),
            "model_consistent": self.model_consistent,
            "claim": self.claim,
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
        "R_bio": abs(residuals.biological) <= bounds.biological,
        "R_elec": abs(residuals.electrical) <= bounds.electrical,
        "R_opt": abs(residuals.optical) <= bounds.optical,
        "R_mod": abs(residuals.modulation) <= bounds.modulation,
    }
    consistent = all(channels.values())

    return VerificationResult(
        protocol=PROTOCOL_ID,
        symbolic_alias=SYMBOLIC_ALIAS,
        version=PROTOCOL_VERSION,
        residuals=residuals,
        channels_within_bounds=channels,
        model_consistent=consistent,
        claim="WITHIN_DEFINED_BOUNDS" if consistent else "BACKTRACE_REQUIRED",
        claim_boundaries=CLAIM_BOUNDARIES,
    )
