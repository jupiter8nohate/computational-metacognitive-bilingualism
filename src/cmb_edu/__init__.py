"""CMB-EDU: privacy-first metacognitive literacy primitives."""

from .fgc import FGCEmojiParser
from .models import ContextEnvelope, PrivacyPolicy
from .parser import CMBDualBrainParser, CMBParseError
from .provenance import build_context_commitment

__all__ = [
    "CMBDualBrainParser",
    "CMBParseError",
    "ContextEnvelope",
    "FGCEmojiParser",
    "PrivacyPolicy",
    "build_context_commitment",
]
__version__ = "0.1.0"
