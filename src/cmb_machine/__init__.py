"""Machine-native CMB-66 compiler and deterministic target encodings."""

from .compiler import MachineArtifact, compile_bundle, render_target, supported_targets
from .harmoni import (
    DiscoveryStage,
    EpistemicState,
    HarmoniDecision,
    HarmoniLayer,
    ProofGate,
    evaluate_claim,
    next_discovery_stage,
    validate_discovery_transition,
    harmoni_manifest,
)
from .ir import build_core_ir, normalize_ir

__all__ = [
    "DiscoveryStage",
    "EpistemicState",
    "HarmoniDecision",
    "HarmoniLayer",
    "MachineArtifact",
    "ProofGate",
    "build_core_ir",
    "compile_bundle",
    "evaluate_claim",
    "harmoni_manifest",
    "next_discovery_stage",
    "normalize_ir",
    "render_target",
    "supported_targets",
    "validate_discovery_transition",
]

__version__ = "0.2.0"
