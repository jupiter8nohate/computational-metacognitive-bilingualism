"""Typed models for the CMB Metacognitive Context Envelope."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class PrivacyPolicy:
    """Deny-by-default educational privacy declarations.

    These values are machine-readable policy metadata. They do not guarantee
    compliance by an unrelated downstream system.
    """

    persistence: str = "ephemeral"
    training_permission: bool = False
    profiling_permission: bool = False
    secondary_use_permission: bool = False
    psychological_inference_permission: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "persistence": self.persistence,
            "training_permission": self.training_permission,
            "profiling_permission": self.profiling_permission,
            "secondary_use_permission": self.secondary_use_permission,
            "psychological_inference_permission": self.psychological_inference_permission,
        }


@dataclass(frozen=True, slots=True)
class ContextEnvelope:
    """A human-declared, current-interaction CMB educational context envelope."""

    lens: str
    mode: str
    states: tuple[str, ...]
    raw_instruction: str
    operation: str
    subject: str
    boundary: str
    boundary_translation: str
    privacy: PrivacyPolicy = field(default_factory=PrivacyPolicy)
    schema: str = "cmb.edu.v1"
    framework: str = "CMB-EDU-v1.0"
    context_source: str = "human_declared"
    temporal_scope: str = "current_interaction"
    machine_inferred: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "meta": {
                "framework": self.framework,
                "human_lens": self.lens,
                "cognitive_mode": self.mode,
            },
            "context": {
                "source": self.context_source,
                "states": list(self.states),
                "machine_inferred": self.machine_inferred,
                "temporal_scope": self.temporal_scope,
            },
            "execution": {
                "raw_instruction": self.raw_instruction,
                "operation": self.operation,
                "subject": self.subject,
            },
            "sovereignty_gate": {
                "declared_invariant": self.boundary,
                "enforced_translation": self.boundary_translation,
            },
            "privacy": self.privacy.to_dict(),
            "epistemic_boundary": {
                "declaration_is_diagnosis": False,
                "self_report_is_permanent_profile": False,
                "current_state_is_identity": False,
                "machine_guess_is_human_truth": False,
            },
        }
