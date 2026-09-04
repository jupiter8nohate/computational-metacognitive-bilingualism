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
    build_c2pa_manifest_definition,
    c2pa_assertion_payload_bytes,
    c2pa_assertion_payload_json,
    save_c2pa_assertion_payload,
    save_c2pa_manifest_definition,
    to_c2pa_assertion_payload,
    validate_c2pa_assertion_label,
)
from .boundary import (
    BOUNDARY_AUTHORITY,
    BOUNDARY_SCHEMA_VERSION,
    BoundaryCode,
    BoundaryContext,
    BoundaryDecision,
    BoundaryRejectedError,
    BoundaryViolation,
    evaluate_boundary,
    require_boundary,
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
    "BOUNDARY_AUTHORITY",
    "BOUNDARY_SCHEMA_VERSION",
    "C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION",
    "GIT_COMMIT_CALLER_SUPPLIED",
    "GIT_COMMIT_VERIFIED",
    "MANIFEST_SCHEMA_VERSION",
    "RECEIPT_SCHEMA_VERSION",
    "TOOL_VERSION",
    "AnchorRecord",
    "BoundaryCode",
    "BoundaryContext",
    "BoundaryDecision",
    "BoundaryRejectedError",
    "BoundaryViolation",
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
    "evaluate_boundary",
    "build_c2pa_manifest_definition",
    "c2pa_assertion_payload_bytes",
    "c2pa_assertion_payload_json",
    "load_ledger",
    "load_receipt",
    "save_c2pa_assertion_payload",
    "save_c2pa_manifest_definition",
    "save_receipt",
    "require_boundary",
    "seal",
    "verify",
    "to_c2pa_assertion_payload",
    "validate_c2pa_assertion_label",
    "verify_ledger",
]

__version__ = TOOL_VERSION
