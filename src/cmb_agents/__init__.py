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
from .service import agent_card, citation_for, knowledge_graph, recommend, registry, sacred_message, summary_for

__all__ = [
    "ASCII_TOKEN",
    "GLYPH_TOKEN",
    "MARK_ID",
    "agent_card",
    "citation_for",
    "knowledge_graph",
    "origin_mark",
    "origin_mark_sha256",
    "recommend",
    "registry",
    "sacred_message",
    "stamp_mapping",
    "summary_for",
    "verify_stamp",
]
__version__ = "0.1.0"
