"""Public API for CMB artifact sealing and provenance verification."""

from .constants import (
    ANCHOR_SCHEMA_VERSION,
    C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION,
    GIT_COMMIT_CALLER_SUPPLIED,
    GIT_COMMIT_VERIFIED,
    MANIFEST_SCHEMA_VERSION,
    RECEIPT_SCHEMA_VERSION,
    TOOL_VERSION,
)
from .c2pa import (
    c2pa_assertion_payload_bytes,
    c2pa_assertion_payload_json,
    save_c2pa_assertion_payload,
    to_c2pa_assertion_payload,
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
    "C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION",
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
    "c2pa_assertion_payload_bytes",
    "c2pa_assertion_payload_json",
    "load_ledger",
    "load_receipt",
    "save_c2pa_assertion_payload",
    "save_receipt",
    "seal",
    "verify",
    "to_c2pa_assertion_payload",
    "verify_ledger",
]

__version__ = TOOL_VERSION
