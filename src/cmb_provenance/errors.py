"""Domain exceptions with safe user-facing messages."""


class CMBProvenanceError(Exception):
    """Base exception for expected CMB provenance failures."""


class SchemaValidationError(CMBProvenanceError):
    """Raised when input does not exactly match a supported schema."""


class SealError(CMBProvenanceError):
    """Raised when an artifact cannot be sealed safely."""


class LedgerError(CMBProvenanceError):
    """Raised for malformed, corrupted, or inconsistent ledgers."""


class LockTimeoutError(LedgerError):
    """Raised when an exclusive ledger lock cannot be acquired in time."""
