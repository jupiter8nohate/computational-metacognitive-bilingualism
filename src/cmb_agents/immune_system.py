"""CMB Digital Nervous Immune System orchestration.

This module models specialist agents as bounded "cells" that pass evidence through
an event pipeline. The biology language is an engineering metaphor. No component
claims biological consciousness, hidden network visibility, or self-replication.

HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Callable, Final, Mapping

DIGITAL_DNA: Final[tuple[str, ...]] = (
    "PATTERN != PROOF",
    "PROFILE != PERSON",
    "MODEL != MIND",
    "PREDICTION != DESTINY",
    "CAPABILITY != AUTHORITY",
    "AGENT_CAN_PROPOSE != AGENT_CAN_MERGE",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)

_SHA256_RE: Final[re.Pattern[str]] = re.compile(r"^sha256:[0-9a-f]{64}$")


class Stage(str, Enum):
    SENSE = "SENSE"
    NORMALIZE = "NORMALIZE"
    POSITION = "POSITION"
    CHAPERONE = "CHAPERONE"
    POLICY = "POLICY"
    REFLEX = "REFLEX"
    DELIBERATE = "DELIBERATE"
    RECEIPT = "RECEIPT"
    MEMORY = "MEMORY"


class Decision(str, Enum):
    OBSERVE = "OBSERVE"
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    PROPOSE_RECOVERY = "PROPOSE_RECOVERY"


PolicyDecider = Callable[["Signal"], Decision]


@dataclass(frozen=True, slots=True)
class Signal:
    """A normalized unit of work entering the bounded nervous-immune pipeline."""

    event_id: str
    source_kind: str
    requested_action: str
    payload_digest: str
    sensitivity: float = 0.0
    consent_present: bool = True
    reversible: bool = True
    metadata: tuple[tuple[str, str], ...] = ()

    def validate(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id must be non-empty")
        if not self.source_kind.strip():
            raise ValueError("source_kind must be non-empty")
        if not self.requested_action.strip():
            raise ValueError("requested_action must be non-empty")
        if not _SHA256_RE.fullmatch(self.payload_digest):
            raise ValueError("payload_digest must be sha256:<64 lowercase hex chars>")
        if not 0.0 <= self.sensitivity <= 1.0:
            raise ValueError("sensitivity must be between 0.0 and 1.0")
        if len(self.metadata) > 32:
            raise ValueError("metadata is bounded to 32 entries")


@dataclass(frozen=True, slots=True)
class CellPacket:
    """Evidence packet emitted by one cell agent."""

    cell: str
    stage: Stage
    decision: Decision
    reason: str
    confidence: float
    evidence: tuple[str, ...]
    dna_digest: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["stage"] = self.stage.value
        payload["decision"] = self.decision.value
        payload["evidence"] = list(self.evidence)
        return payload


@dataclass(frozen=True, slots=True)
class ImmuneTrace:
    """Complete deterministic route for one signal."""

    signal: Signal
    position_score: float
    risk_score: float
    final_decision: Decision
    packets: tuple[CellPacket, ...]
    receipt: str
    memory_digest: str

    def to_dict(self) -> dict[str, object]:
        return {
            "signal": {
                "event_id": self.signal.event_id,
                "source_kind": self.signal.source_kind,
                "requested_action": self.signal.requested_action,
                "payload_digest": self.signal.payload_digest,
                "sensitivity": self.signal.sensitivity,
                "consent_present": self.signal.consent_present,
                "reversible": self.signal.reversible,
                "metadata": [list(item) for item in self.signal.metadata],
            },
            "position_score": self.position_score,
            "risk_score": self.risk_score,
            "final_decision": self.final_decision.value,
            "packets": [packet.to_dict() for packet in self.packets],
            "receipt": self.receipt,
            "memory_digest": self.memory_digest,
        }


def digital_dna_digest() -> str:
    encoded = json.dumps(DIGITAL_DNA, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def normalize_signal(signal: Signal) -> Signal:
    signal.validate()
    normalized_metadata = tuple(
        sorted(
            (
                str(key).strip()[:128],
                str(value).strip()[:512],
            )
            for key, value in signal.metadata
            if str(key).strip()
        )
    )
    normalized = replace(
        signal,
        source_kind=signal.source_kind.strip().lower(),
        requested_action=signal.requested_action.strip().upper(),
        metadata=normalized_metadata,
    )
    normalized.validate()
    return normalized


def position_score(signal: Signal) -> float:
    """Estimate how much human attention a signal deserves.

    This is routing friction, not a judgment about a person.
    """

    score = signal.sensitivity * 0.65
    if not signal.reversible:
        score += 0.20
    if not signal.consent_present:
        score += 0.15
    return round(min(1.0, max(0.0, score)), 6)


def risk_score(signal: Signal, position: float) -> float:
    """Compute bounded operational risk without profiling a human."""

    score = (signal.sensitivity * 0.55) + (position * 0.25)
    if not signal.reversible:
        score += 0.10
    if not signal.consent_present:
        score += 0.10
    return round(min(1.0, max(0.0, score)), 6)


def _packet(
    cell: str,
    stage: Stage,
    decision: Decision,
    reason: str,
    *,
    confidence: float = 1.0,
    evidence: tuple[str, ...] = (),
) -> CellPacket:
    return CellPacket(
        cell=cell,
        stage=stage,
        decision=decision,
        reason=reason,
        confidence=max(0.0, min(1.0, confidence)),
        evidence=evidence,
        dna_digest=digital_dna_digest(),
    )


def _receipt_payload(
    signal: Signal,
    final_decision: Decision,
    position: float,
    risk: float,
    packets: tuple[CellPacket, ...],
) -> Mapping[str, object]:
    return {
        "schema": "cmb.dnis.receipt.v1",
        "event_id": signal.event_id,
        "payload_digest": signal.payload_digest,
        "requested_action": signal.requested_action,
        "position_score": position,
        "risk_score": risk,
        "final_decision": final_decision.value,
        "digital_dna": digital_dna_digest(),
        "route": [
            {
                "cell": packet.cell,
                "stage": packet.stage.value,
                "decision": packet.decision.value,
            }
            for packet in packets
        ],
    }


def _digest_mapping(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def process_signal(
    signal: Signal,
    *,
    policy_decider: PolicyDecider,
    human_review_threshold: float = 0.75,
) -> ImmuneTrace:
    """Route a signal through bounded digital cell agents.

    The policy decider is injected so CMB policy remains the source of authority.
    This orchestrator does not invent policy and does not merge, publish, deploy,
    modify permissions, or execute arbitrary shell commands.
    """

    if not 0.0 <= human_review_threshold <= 1.0:
        raise ValueError("human_review_threshold must be between 0.0 and 1.0")

    normalized = normalize_signal(signal)
    packets: list[CellPacket] = [
        _packet(
            "RECEPTOR_CELL",
            Stage.SENSE,
            Decision.OBSERVE,
            "Accepted a caller-supplied event. No hidden network observation is implied.",
            evidence=(normalized.payload_digest,),
        ),
        _packet(
            "DENDRITIC_CELL",
            Stage.NORMALIZE,
            Decision.OBSERVE,
            "Normalized bounded event metadata and action syntax.",
            evidence=(normalized.requested_action, normalized.source_kind),
        ),
    ]

    position = position_score(normalized)
    risk = risk_score(normalized, position)
    packets.extend(
        [
            _packet(
                "POSITION_CELL",
                Stage.POSITION,
                Decision.OBSERVE,
                f"Computed routing position score {position:.6f}.",
                evidence=(f"position:{position:.6f}",),
            ),
            _packet(
                "CHAPERONE_CELL",
                Stage.CHAPERONE,
                Decision.OBSERVE,
                "Validated signal structure, score bounds, and Digital DNA continuity.",
                evidence=(digital_dna_digest(),),
            ),
        ]
    )

    policy_decision = policy_decider(normalized)
    if policy_decision not in {Decision.ALLOW, Decision.DENY, Decision.ESCALATE}:
        raise ValueError("policy_decider must return ALLOW, DENY, or ESCALATE")

    packets.append(
        _packet(
            "T_CELL_POLICY_GATE",
            Stage.POLICY,
            policy_decision,
            "Applied the caller-provided policy decision without expanding authority.",
            evidence=(normalized.requested_action,),
        )
    )

    if policy_decision is Decision.DENY:
        final = Decision.DENY
        packets.extend(
            [
                _packet(
                    "REFLEX_CELL",
                    Stage.REFLEX,
                    Decision.DENY,
                    "Fail-closed reflex preserved the policy denial.",
                    evidence=("policy:DENY",),
                ),
                _packet(
                    "MACROPHAGE_RECOVERY",
                    Stage.DELIBERATE,
                    Decision.PROPOSE_RECOVERY,
                    "May propose bounded cleanup or recovery. It receives no merge or release authority.",
                    evidence=("authority:propose_only",),
                ),
            ]
        )
    elif policy_decision is Decision.ESCALATE or risk >= human_review_threshold:
        final = Decision.ESCALATE
        packets.append(
            _packet(
                "CORTEX_LIAISON",
                Stage.DELIBERATE,
                Decision.ESCALATE,
                "Escalated consequential or high-risk judgment to the human authority.",
                evidence=(f"risk:{risk:.6f}", f"threshold:{human_review_threshold:.6f}"),
            )
        )
    else:
        final = Decision.ALLOW
        packets.append(
            _packet(
                "REFLEX_CELL",
                Stage.REFLEX,
                Decision.ALLOW,
                "Low-risk policy-authorized operation may continue.",
                evidence=("policy:ALLOW", f"risk:{risk:.6f}"),
            )
        )

    route_packets = tuple(packets)
    receipt_payload = _receipt_payload(normalized, final, position, risk, route_packets)
    receipt = _digest_mapping(receipt_payload)

    packets.append(
        _packet(
            "B_CELL_PROVENANCE",
            Stage.RECEIPT,
            Decision.OBSERVE,
            "Created a tamper-evident route receipt digest.",
            evidence=(receipt,),
        )
    )

    memory_payload = {
        "schema": "cmb.dnis.memory.v1",
        "event_id": normalized.event_id,
        "receipt": receipt,
        "outcome": final.value,
        "digital_dna": digital_dna_digest(),
    }
    memory_digest = _digest_mapping(memory_payload)
    packets.append(
        _packet(
            "MEMORY_CELL",
            Stage.MEMORY,
            Decision.OBSERVE,
            "Recorded a digest-only outcome reference for later verification.",
            evidence=(memory_digest,),
        )
    )

    return ImmuneTrace(
        signal=normalized,
        position_score=position,
        risk_score=risk,
        final_decision=final,
        packets=tuple(packets),
        receipt=receipt,
        memory_digest=memory_digest,
    )
