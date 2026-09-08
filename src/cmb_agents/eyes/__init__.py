"""Glitch Eye perception subsystem for CMB agents."""

from .engine import (
    EXPERIMENTAL,
    OBSERVE_ONLY,
    Eye,
    EyeProposal,
    GlitchEyeEngine,
    Perception,
    build_default_engine,
    hidden_coupling_detector,
    propose_composite_eye,
    provenance_drift_detector,
    semantic_parallax_detector,
)

__all__ = [
    "EXPERIMENTAL",
    "OBSERVE_ONLY",
    "Eye",
    "EyeProposal",
    "GlitchEyeEngine",
    "Perception",
    "build_default_engine",
    "hidden_coupling_detector",
    "propose_composite_eye",
    "provenance_drift_detector",
    "semantic_parallax_detector",
]
