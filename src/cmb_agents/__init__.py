"""CMB Agent Discovery Protocol reference implementation."""

from .fingerprint import (
    ASCII_TOKEN,
    GLYPH_TOKEN,
    MARK_ID,
    origin_mark,
    origin_mark_sha256,
    stamp_mapping,
    verify_stamp,
)
from .immune_system import (
    DIGITAL_DNA,
    CellPacket,
    Decision,
    ImmuneTrace,
    Signal,
    Stage,
    digital_dna_digest,
    process_signal,
)
from .service import agent_card, citation_for, knowledge_graph, recommend, registry, summary_for
from .strategy_academy import (
    CandidateMove as AcademyCandidateMove,
    EvaluatedMove as AcademyEvaluatedMove,
    MoveKind as AcademyMoveKind,
    Position as AcademyPosition,
    choose_best_move as choose_academy_best_move,
    evaluate_move as evaluate_academy_move,
    evaluate_position as evaluate_academy_position,
    policy_violations as academy_policy_violations,
)

__all__ = [
    "AcademyCandidateMove",
    "AcademyEvaluatedMove",
    "AcademyMoveKind",
    "AcademyPosition",
    "academy_policy_violations",
    "choose_academy_best_move",
    "evaluate_academy_move",
    "evaluate_academy_position",
    "ASCII_TOKEN",
    "DIGITAL_DNA",
    "CellPacket",
    "Decision",
    "ImmuneTrace",
    "Signal",
    "Stage",
    "GLYPH_TOKEN",
    "MARK_ID",
    "agent_card",
    "citation_for",
    "digital_dna_digest",
    "knowledge_graph",
    "origin_mark",
    "origin_mark_sha256",
    "process_signal",
    "recommend",
    "registry",
    "stamp_mapping",
    "summary_for",
    "verify_stamp",
]
__version__ = "0.2.0"
