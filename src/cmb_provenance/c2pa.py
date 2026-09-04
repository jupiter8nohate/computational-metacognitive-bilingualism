"""Deterministic CMB receipt adapter for C2PA-facing assertion payloads.

This module deliberately does not create a C2PA manifest, Content Credential,
claim signature, asset binding, or conformance result. It only converts a
validated CMB seal receipt into a minimal deterministic payload body that an
external C2PA implementation may embed in an entity-specific assertion.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .canonical import canonical_json_bytes
from .constants import C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION
from .sealing import PathInput, ReceiptInput, coerce_receipt

_FRAMEWORK_NAME = "Computational Metacognitive Bilingualism"


def to_c2pa_assertion_payload(
    receipt: ReceiptInput,
    *,
    include_paths: bool = False,
) -> dict[str, Any]:
    """Return a deterministic, privacy-minimized C2PA-facing payload body.

    Artifact paths are omitted by default because repository paths can expose
    unnecessary information. Set include_paths=True only when the caller has
    decided those paths are appropriate for the eventual credential.

    The returned mapping is not itself a C2PA assertion envelope, manifest,
    Content Credential, signature, or conformance claim.
    """

    sealed = coerce_receipt(receipt)
    paths = list(sealed.coverage.paths) if include_paths else []

    return {
        "schema_version": C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION,
        "framework": _FRAMEWORK_NAME,
        "source_receipt_schema": sealed.schema_version,
        "source_tool_version": sealed.tool_version,
        "source_manifest_sha256": sealed.manifest_sha256,
        "hash_algorithm": sealed.manifest.hash_algorithm,
        "coverage": {
            "type": sealed.coverage.type,
            "artifact_count": len(sealed.coverage.paths),
            "excludes_unlisted": sealed.coverage.excludes_unlisted,
            "paths_included": include_paths,
            "paths": paths,
        },
        "git": {
            "commit": sealed.manifest.git_commit,
            "status": sealed.manifest.git_commit_status,
        },
        "evidence_boundary": {
            "integrity_is_authorship": False,
            "signature_is_originality": False,
            "provenance_is_legal_judgment": False,
            "assertion_is_truth": False,
        },
        "c2pa_status": {
            "payload_is_c2pa_manifest": False,
            "payload_is_content_credential": False,
            "project_claims_c2pa_conformance": False,
            "requires_external_c2pa_tooling": True,
        },
    }


def c2pa_assertion_payload_bytes(
    receipt: ReceiptInput,
    *,
    include_paths: bool = False,
) -> bytes:
    """Serialize the adapter payload using CMB canonical JSON."""

    return canonical_json_bytes(
        to_c2pa_assertion_payload(receipt, include_paths=include_paths)
    )


def save_c2pa_assertion_payload(
    receipt: ReceiptInput,
    path: PathInput,
    *,
    include_paths: bool = False,
) -> Path:
    """Atomically write one canonical adapter payload plus a trailing newline."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = c2pa_assertion_payload_bytes(
        receipt,
        include_paths=include_paths,
    ) + b"\n"

    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
        temporary_name = None
        if os.name != "nt":
            directory_fd = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass

    return destination


def c2pa_assertion_payload_json(
    receipt: ReceiptInput,
    *,
    include_paths: bool = False,
    pretty: bool = False,
) -> str:
    """Render the payload as JSON for display or integration testing."""

    payload = to_c2pa_assertion_payload(receipt, include_paths=include_paths)
    if pretty:
        return json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    return c2pa_assertion_payload_bytes(
        receipt,
        include_paths=include_paths,
    ).decode("utf-8")
