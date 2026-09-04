"""Deterministic integrity commitments for CMB-EDU context envelopes.

A commitment proves byte-level consistency of the structured payload. It does
not prove identity, psychological truth, valid consent, or legal ownership.
"""

from __future__ import annotations

from typing import Any

from cmb_provenance.canonical import canonical_json_bytes, sha256_bytes

from .models import ContextEnvelope


def build_context_commitment(envelope: ContextEnvelope) -> dict[str, Any]:
    payload = envelope.to_dict()
    return {
        "schema": "cmb.edu.commitment.v1",
        "payload_sha256": sha256_bytes(canonical_json_bytes(payload)),
        "payload": payload,
        "evidence_boundary": {
            "integrity_is_identity": False,
            "declaration_is_psychological_truth": False,
            "hash_is_consent": False,
            "metadata_is_enforcement": False,
        },
    }
