"""Immutable public data models for the v1.3.1 protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ArtifactDigest:
    path: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class ArtifactManifest:
    schema_version: str
    tool_version: str
    hash_algorithm: str
    git_commit: str
    git_commit_status: str
    artifacts: tuple[ArtifactDigest, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
            "hash_algorithm": self.hash_algorithm,
            "git_commit": self.git_commit,
            "git_commit_status": self.git_commit_status,
            "artifacts": [
                {
                    "path": artifact.path,
                    "sha256": artifact.sha256,
                    "size_bytes": artifact.size_bytes,
                }
                for artifact in self.artifacts
            ],
        }


@dataclass(frozen=True, slots=True)
class Coverage:
    type: str
    paths: tuple[str, ...]
    excludes_unlisted: bool


@dataclass(frozen=True, slots=True)
class SealReceipt:
    schema_version: str
    tool_version: str
    created_at_utc: str
    coverage: Coverage
    manifest: ArtifactManifest
    manifest_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
            "created_at_utc": self.created_at_utc,
            "coverage": {
                "type": self.coverage.type,
                "paths": list(self.coverage.paths),
                "excludes_unlisted": self.coverage.excludes_unlisted,
            },
            "manifest": self.manifest.to_dict(),
            "manifest_sha256": self.manifest_sha256,
        }


@dataclass(frozen=True, slots=True)
class VerificationFailure:
    path: str | None
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class VerificationResult:
    ok: bool
    manifest_sha256: str
    checked_paths: tuple[str, ...]
    git_commit_matches: bool | None
    failures: tuple[VerificationFailure, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "manifest_sha256": self.manifest_sha256,
            "checked_paths": list(self.checked_paths),
            "git_commit_matches": self.git_commit_matches,
            "failures": [
                {"path": failure.path, "code": failure.code, "message": failure.message}
                for failure in self.failures
            ],
        }
