"""CMB-EDU: privacy-first metacognitive literacy primitives.

CMB-EDU represents human-declared interaction context. It does not infer,
diagnose, or persist psychological truth about a person.
"""

from .errors import CMBParseError
from .fgc import FGCEmojiParser
from .models import ContextEnvelope, PrivacyPolicy
from .parser import CMBDualBrainParser
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
