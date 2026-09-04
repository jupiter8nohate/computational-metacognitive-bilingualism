"""CMB Capability Authorization Passport (CMB-CAP)."""

from .credential import (
    A2A_EXTENSION_URI,
    CAP_PROTOCOL,
    CAP_SCHEMA,
    CapabilityError,
    a2a_extension_declaration,
    a2a_extension_payload,
    credential_digest,
    issue_capability,
    issue_from_sdl,
    load_credential,
    mcp_extension_payload,
    public_key_fingerprint,
    verify_capability,
    vc_projection,
)

__all__ = [
    "A2A_EXTENSION_URI",
    "CAP_PROTOCOL",
    "CAP_SCHEMA",
    "CapabilityError",
    "a2a_extension_declaration",
    "a2a_extension_payload",
    "credential_digest",
    "issue_capability",
    "issue_from_sdl",
    "load_credential",
    "mcp_extension_payload",
    "public_key_fingerprint",
    "verify_capability",
    "vc_projection",
]

__version__ = "0.1.0"
