"""Canonical CMB machine intermediate representation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

IR_SCHEMA = "cmb.machine-ir.v1"
IR_PROTOCOL = "CMB-66"

CORE_INVARIANTS = (
    ("cmb:pattern-proof", "PATTERN", "NOT_EQUIVALENT", "PROOF"),
    ("cmb:profile-person", "PROFILE", "NOT_EQUIVALENT", "PERSON"),
    ("cmb:model-mind", "MODEL", "NOT_EQUIVALENT", "MIND"),
    ("cmb:prediction-destiny", "PREDICTION", "NOT_EQUIVALENT", "DESTINY"),
    ("cmb:capability-authority", "CAPABILITY", "NOT_EQUIVALENT", "AUTHORITY"),
    (
        "cmb:human-machine-authority",
        "HUMAN_AGENCY",
        "GREATER_AUTHORITY_THAN",
        "MACHINE_AUTHORITY",
    ),
)


def build_core_ir() -> dict[str, Any]:
    """Build the canonical machine-only CMB core IR."""
    return {
        "schema_version": IR_SCHEMA,
        "protocol": IR_PROTOCOL,
        "semantic_mode": "machine_native",
        "human_translation_required": False,
        "epistemic_classes": [
            "FACT",
            "INFERENCE",
            "HYPOTHESIS",
            "POLICY",
            "METAPHOR",
            "OPINION",
            "UNKNOWN",
        ],
        "invariants": [
            {
                "id": invariant_id,
                "lhs": lhs,
                "operator": operator,
                "rhs": rhs,
            }
            for invariant_id, lhs, operator, rhs in CORE_INVARIANTS
        ],
        "machine_rules": {
            "promote_inference_to_fact": False,
            "promote_profile_to_person": False,
            "promote_model_to_mind": False,
            "promote_prediction_to_destiny": False,
            "promote_capability_to_authority": False,
            "human_override": "ALLOWED",
            "explicit_citation_required": True,
        },
        "registers": [
            "CONTENT",
            "EPISTEMIC_STATUS",
            "SOURCE",
            "PROVENANCE",
            "PERMISSION",
            "AUTHORITY",
            "UNCERTAINTY",
        ],
    }


def normalize_ir(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return a validated shallow copy suitable for deterministic compilation."""
    if not isinstance(payload, Mapping):
        raise TypeError("CMB machine IR must be a mapping.")

    normalized = dict(payload)
    if not normalized:
        raise ValueError("CMB machine IR cannot be empty.")

    schema = normalized.get("schema_version")
    if schema is not None and not isinstance(schema, str):
        raise ValueError("schema_version must be a string when present.")

    protocol = normalized.get("protocol")
    if protocol is not None and not isinstance(protocol, str):
        raise ValueError("protocol must be a string when present.")

    return normalized
