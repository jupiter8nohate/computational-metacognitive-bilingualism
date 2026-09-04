"""Machine-native CMB-66 compiler and deterministic target encodings."""

from .compiler import MachineArtifact, compile_bundle, render_target, supported_targets
from .ir import build_core_ir, normalize_ir

__all__ = [
    "MachineArtifact",
    "build_core_ir",
    "compile_bundle",
    "normalize_ir",
    "render_target",
    "supported_targets",
]

__version__ = "0.1.0"
