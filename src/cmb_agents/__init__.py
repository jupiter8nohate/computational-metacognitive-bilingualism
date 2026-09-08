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

__all__ = [
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
__version__ = "0.1.0"
