"""Bounded Glitch Eye perception engine for CMB agents.

The engine translates visual glyphs into explicit repository perception roles.
It only produces observations and experimental proposals. It has no mutation,
merge, release, signing, or authority-expansion capability.

PATTERN != PROOF
ANOMALY != DEFECT
CORRELATION != DEPENDENCY
PERCEPTION != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Final


class Eye(str, Enum):
    """Stable glyph identifiers for bounded perception roles."""

    WITNESS = "𓁹"
    STEREO = "𓁹𓁹"
    ALERT = "(⚆_⚆)"
    MACHINE_GAZE = "(𖠂_𖠂)"
    LOW_LIGHT = "𓁼"
    FOCUS = "𓁽"
    PERIPHERAL = "𓁺"
    HIDDEN_CONTEXT = "𓁿"
    INNER_EYE = "𓂀"
    REFRACTION = "༗"
    SENSOR = "𖠂"
    RECOGNITION = "◉‿◉"
    TEMPORAL = "𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃"


OBSERVE_ONLY: Final[str] = "observe_only"
EXPERIMENTAL: Final[str] = "EXPERIMENTAL"


@dataclass(frozen=True, slots=True)
class Perception:
    """Evidence-linked observation emitted by an Eye detector."""

    eye: Eye
    detector: str
    evidence: tuple[str, ...]
    confidence: float
    hypothesis: str

    def __post_init__(self) -> None:
        if not self.detector.strip():
            raise ValueError("detector must not be empty")
        if not self.hypothesis.strip():
            raise ValueError("hypothesis must not be empty")
        if not self.evidence:
            raise ValueError("perception requires evidence")
        if not math.isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be finite and between 0 and 1")


@dataclass(frozen=True, slots=True)
class EyeProposal:
    """Non-executable proposal for a new composite perception operator."""

    glyph: str
    name: str
    parent_eyes: tuple[Eye, ...]
    supporting_detectors: tuple[str, ...]
    evidence: tuple[str, ...]
    logic_expression: str
    confidence: float
    authority: str = OBSERVE_ONLY
    status: str = EXPERIMENTAL

    def __post_init__(self) -> None:
        if not self.glyph.strip():
            raise ValueError("glyph must not be empty")
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if len(set(self.parent_eyes)) < 2:
            raise ValueError("proposal requires at least two independent parent Eyes")
        if len(set(self.supporting_detectors)) < 2:
            raise ValueError("proposal requires at least two detector families")
        if not self.evidence:
            raise ValueError("proposal requires evidence")
        if not math.isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be finite and between 0 and 1")
        if self.authority != OBSERVE_ONLY:
            raise ValueError("Eye proposals are observe-only")
        if self.status != EXPERIMENTAL:
            raise ValueError("new Eyes must remain experimental")


Detector = Callable[[Mapping[str, object]], Iterable[Perception]]


class GlitchEyeEngine:
    """Registry and fusion layer for deterministic bounded detectors."""

    def __init__(self) -> None:
        self._detectors: dict[Eye, list[Detector]] = {}

    def register(self, eye: Eye, detector: Detector) -> None:
        """Register a detector under a glyph-defined perception role."""

        bucket = self._detectors.setdefault(eye, [])
        if detector not in bucket:
            bucket.append(detector)

    def perceive(
        self,
        eye: Eye,
        repository_state: Mapping[str, object],
    ) -> tuple[Perception, ...]:
        """Run every detector registered for one Eye."""

        observations: list[Perception] = []
        for detector in self._detectors.get(eye, ()):
            observations.extend(detector(repository_state))
        return _normalize(observations)

    def fusion(
        self,
        eyes: Iterable[Eye],
        repository_state: Mapping[str, object],
    ) -> tuple[Perception, ...]:
        """Fuse multiple Eyes while preserving evidence and determinism."""

        observations: list[Perception] = []
        for eye in eyes:
            observations.extend(self.perceive(eye, repository_state))
        return _normalize(observations)


def _normalize(observations: Iterable[Perception]) -> tuple[Perception, ...]:
    unique: dict[tuple[object, ...], Perception] = {}
    for item in observations:
        key = (
            item.eye,
            item.detector,
            item.evidence,
            item.hypothesis,
        )
        current = unique.get(key)
        if current is None or item.confidence > current.confidence:
            unique[key] = item

    return tuple(
        sorted(
            unique.values(),
            key=lambda item: (
                -item.confidence,
                item.eye.value,
                item.detector,
                item.evidence,
                item.hypothesis,
            ),
        )
    )


def _records(state: Mapping[str, object], key: str) -> tuple[Mapping[str, object], ...]:
    raw = state.get(key)
    if not isinstance(raw, list):
        return ()
    return tuple(item for item in raw if isinstance(item, Mapping))


def _confidence(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        return None
    return number


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(
        text
        for item in value
        if (text := str(item).strip())
    )


def semantic_parallax_detector(state: Mapping[str, object]) -> Iterable[Perception]:
    """Detect conflicting representations of the same repository concept."""

    for record in _records(state, "semantic_contradictions"):
        files = _string_tuple(record.get("files"))
        confidence = _confidence(record.get("confidence"))
        description = str(record.get("description", "")).strip()

        if len(set(files)) < 2 or confidence is None or not description:
            continue

        yield Perception(
            eye=Eye.STEREO,
            detector="semantic_parallax",
            evidence=files,
            confidence=confidence,
            hypothesis=description,
        )


def hidden_coupling_detector(state: Mapping[str, object]) -> Iterable[Perception]:
    """Detect strong co-change behavior without an explicit dependency."""

    for record in _records(state, "cochange_relations"):
        file_a = str(record.get("file_a", "")).strip()
        file_b = str(record.get("file_b", "")).strip()
        score = _confidence(record.get("score"))
        explicit_dependency = bool(record.get("explicit_dependency", False))

        if (
            not file_a
            or not file_b
            or file_a == file_b
            or score is None
            or score < 0.80
            or explicit_dependency
        ):
            continue

        yield Perception(
            eye=Eye.HIDDEN_CONTEXT,
            detector="hidden_coupling",
            evidence=(file_a, file_b),
            confidence=score,
            hypothesis=(
                "Files repeatedly change together despite having no explicit dependency."
            ),
        )


def provenance_drift_detector(state: Mapping[str, object]) -> Iterable[Perception]:
    """Detect evidence-linked meaning or provenance drift across repository time."""

    for record in _records(state, "provenance_drift"):
        artifacts = _string_tuple(record.get("artifacts"))
        confidence = _confidence(record.get("confidence"))
        description = str(record.get("description", "")).strip()

        if not artifacts or confidence is None or not description:
            continue

        yield Perception(
            eye=Eye.TEMPORAL,
            detector="provenance_drift",
            evidence=artifacts,
            confidence=confidence,
            hypothesis=description,
        )


def propose_composite_eye(
    perceptions: Iterable[Perception],
    *,
    glyph: str,
    name: str,
    min_detector_families: int = 3,
    min_confidence: float = 0.65,
) -> EyeProposal | None:
    """Propose, but never activate, a new composite Eye.

    A proposal requires multiple independent detector families and multiple
    parent Eyes. Its confidence is the weakest supporting observation so the
    proposal cannot become stronger than its weakest evidence.
    """

    if min_detector_families < 2:
        raise ValueError("min_detector_families must be at least 2")
    if not 0.0 <= min_confidence <= 1.0:
        raise ValueError("min_confidence must be between 0 and 1")

    eligible = tuple(
        item
        for item in perceptions
        if item.confidence >= min_confidence
    )
    detectors = tuple(sorted({item.detector for item in eligible}))
    parent_eyes = tuple(sorted({item.eye for item in eligible}, key=lambda eye: eye.value))

    if len(detectors) < min_detector_families or len(parent_eyes) < 2:
        return None

    evidence = tuple(
        sorted(
            {
                evidence_item
                for item in eligible
                for evidence_item in item.evidence
            }
        )
    )
    logic_expression = " AND ".join(detectors)

    return EyeProposal(
        glyph=glyph,
        name=name,
        parent_eyes=parent_eyes,
        supporting_detectors=detectors,
        evidence=evidence,
        logic_expression=logic_expression,
        confidence=min(item.confidence for item in eligible),
    )


def build_default_engine() -> GlitchEyeEngine:
    """Create the v1 engine with the first three production detectors."""

    engine = GlitchEyeEngine()
    engine.register(Eye.STEREO, semantic_parallax_detector)
    engine.register(Eye.HIDDEN_CONTEXT, hidden_coupling_detector)
    engine.register(Eye.TEMPORAL, provenance_drift_detector)
    return engine
