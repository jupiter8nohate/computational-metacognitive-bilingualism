from __future__ import annotations

import hashlib

import pytest

from cmb_agents.immune_system import (
    DIGITAL_DNA,
    Decision,
    Signal,
    Stage,
    digital_dna_digest,
    process_signal,
)


def _digest(value: bytes = b"payload") -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def test_digital_dna_has_human_authority_boundary() -> None:
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in DIGITAL_DNA
    assert digital_dna_digest().startswith("sha256:")
    assert len(digital_dna_digest()) == 71


def test_low_risk_allowed_signal_uses_reflex_path() -> None:
    trace = process_signal(
        Signal(
            event_id="evt-1",
            source_kind="Webhook",
            requested_action="translate",
            payload_digest=_digest(),
            sensitivity=0.1,
            consent_present=True,
            reversible=True,
        ),
        policy_decider=lambda signal: Decision.ALLOW,
    )

    assert trace.final_decision is Decision.ALLOW
    assert trace.signal.requested_action == "TRANSLATE"
    assert any(packet.cell == "REFLEX_CELL" and packet.decision is Decision.ALLOW for packet in trace.packets)
    assert not any(packet.cell == "CORTEX_LIAISON" for packet in trace.packets)
    assert trace.receipt.startswith("sha256:")
    assert trace.memory_digest.startswith("sha256:")


def test_policy_denial_triggers_reflex_and_recovery_proposal() -> None:
    trace = process_signal(
        Signal(
            event_id="evt-2",
            source_kind="mcp",
            requested_action="create_profile",
            payload_digest=_digest(b"sensitive"),
            sensitivity=0.9,
            consent_present=False,
            reversible=False,
        ),
        policy_decider=lambda signal: Decision.DENY,
    )

    assert trace.final_decision is Decision.DENY
    assert any(packet.cell == "REFLEX_CELL" and packet.decision is Decision.DENY for packet in trace.packets)
    assert any(
        packet.cell == "MACROPHAGE_RECOVERY"
        and packet.decision is Decision.PROPOSE_RECOVERY
        for packet in trace.packets
    )


def test_high_risk_allowed_signal_escalates_to_human() -> None:
    trace = process_signal(
        Signal(
            event_id="evt-3",
            source_kind="repository",
            requested_action="high_stakes_decision",
            payload_digest=_digest(b"high-risk"),
            sensitivity=1.0,
            consent_present=False,
            reversible=False,
        ),
        policy_decider=lambda signal: Decision.ALLOW,
        human_review_threshold=0.70,
    )

    assert trace.risk_score >= 0.70
    assert trace.final_decision is Decision.ESCALATE
    assert any(packet.cell == "CORTEX_LIAISON" for packet in trace.packets)


def test_explicit_policy_escalation_reaches_cortex() -> None:
    trace = process_signal(
        Signal(
            event_id="evt-4",
            source_kind="api",
            requested_action="ambiguous_semantic_operation",
            payload_digest=_digest(b"ambiguous"),
            sensitivity=0.2,
        ),
        policy_decider=lambda signal: Decision.ESCALATE,
    )

    assert trace.final_decision is Decision.ESCALATE
    assert any(packet.stage is Stage.DELIBERATE for packet in trace.packets)


def test_every_cell_carries_same_digital_dna_digest() -> None:
    trace = process_signal(
        Signal(
            event_id="evt-5",
            source_kind="api",
            requested_action="summarize",
            payload_digest=_digest(b"same-dna"),
        ),
        policy_decider=lambda signal: Decision.ALLOW,
    )

    expected = digital_dna_digest()
    assert {packet.dna_digest for packet in trace.packets} == {expected}


def test_invalid_payload_digest_fails_closed() -> None:
    with pytest.raises(ValueError, match="payload_digest"):
        process_signal(
            Signal(
                event_id="evt-bad",
                source_kind="api",
                requested_action="summarize",
                payload_digest="not-a-digest",
            ),
            policy_decider=lambda signal: Decision.ALLOW,
        )


def test_policy_callback_cannot_return_unbounded_decision() -> None:
    with pytest.raises(ValueError, match="policy_decider"):
        process_signal(
            Signal(
                event_id="evt-6",
                source_kind="api",
                requested_action="summarize",
                payload_digest=_digest(b"bad-policy"),
            ),
            policy_decider=lambda signal: Decision.PROPOSE_RECOVERY,
        )
