"""Public API for CMB artifact sealing and provenance verification."""

from .constants import (
    ANCHOR_SCHEMA_VERSION,
    GIT_COMMIT_CALLER_SUPPLIED,
    GIT_COMMIT_VERIFIED,
    MANIFEST_SCHEMA_VERSION,
    RECEIPT_SCHEMA_VERSION,
    TOOL_VERSION,
)
from .errors import (
    CMBProvenanceError,
    LedgerError,
    LockTimeoutError,
    SchemaValidationError,
    SealError,
)
from .ledger import AnchorRecord, append_anchor, load_ledger, verify_ledger
from .models import (
    ArtifactDigest,
    ArtifactManifest,
    Coverage,
    SealReceipt,
    VerificationFailure,
    VerificationResult,
)
from .sealing import load_receipt, save_receipt, seal, verify

__all__ = [
    "ANCHOR_SCHEMA_VERSION",
    "GIT_COMMIT_CALLER_SUPPLIED",
    "GIT_COMMIT_VERIFIED",
    "MANIFEST_SCHEMA_VERSION",
    "RECEIPT_SCHEMA_VERSION",
    "TOOL_VERSION",
    "AnchorRecord",
    "ArtifactDigest",
    "ArtifactManifest",
    "CMBProvenanceError",
    "Coverage",
    "LedgerError",
    "LockTimeoutError",
    "SchemaValidationError",
    "SealError",
    "SealReceipt",
    "VerificationFailure",
    "VerificationResult",
    "append_anchor",
    "load_ledger",
    "load_receipt",
    "save_receipt",
    "seal",
    "verify",
    "verify_ledger",
]

__version__ = TOOL_VERSION
