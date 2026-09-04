"""CMB Sovereign Delegation Language (CMB-SDL)."""

from .compiler import (
    PROTOCOL,
    SCHEMA,
    compile_document,
    compile_text,
    validate_authority_ir,
    validate_delegation,
)
from .model import AuthorityDocument, SDLValidationError, ScopeBinding
from .parser import parse

__all__ = [
    "AuthorityDocument",
    "PROTOCOL",
    "SCHEMA",
    "SDLValidationError",
    "ScopeBinding",
    "compile_document",
    "compile_text",
    "parse",
    "validate_authority_ir",
    "validate_delegation",
]

__version__ = "0.1.0"
