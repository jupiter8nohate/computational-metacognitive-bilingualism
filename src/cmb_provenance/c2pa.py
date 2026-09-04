"""CMB receipt adapters for C2PA-facing assertion payloads and manifests.

This module does not sign assets, create C2PA claim signatures, establish trust,
or claim C2PA conformance. It produces deterministic payloads and manifest
definitions that can be handed to an external C2PA implementation such as
c2patool.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from .canonical import canonical_json_bytes
from .constants import C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION, TOOL_VERSION
from .errors import SealError
from .sealing import PathInput, ReceiptInput, coerce_receipt

_FRAMEWORK_NAME = "Computational Metacognitive Bilingualism"
_COMPONENT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_RESERVED_EXAMPLE_PREFIXES = {
    ("com", "example"),
    ("net", "example"),
    ("org", "example"),
}


def _atomic_write_bytes(destination: Path, encoded: bytes) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
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
    except OSError as exc:
        raise SealError(f"Unable to write {destination}: {exc}") from exc
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
    return destination


def validate_c2pa_assertion_label(
    label: str,
    *,
    allow_example_namespace: bool = False,
) -> str:
    """Validate conservative syntax for an entity-specific C2PA assertion label.

    This checks syntax only. It cannot verify that the caller controls the
    Internet domain represented by the namespace.
    """

    if not isinstance(label, str) or not label or label != label.strip():
        raise SealError("C2PA assertion label must be a non-empty trimmed string.")
    if len(label) > 255:
        raise SealError("C2PA assertion label exceeds 255 characters.")

    components = label.split(".")
    if len(components) < 3 or any(not _COMPONENT_RE.fullmatch(c) for c in components):
        raise SealError(
            "C2PA entity-specific assertion label must use reverse-domain syntax "
            "with at least three identifier components."
        )
    lowered = tuple(component.lower() for component in components)
    if lowered[0] in {"c2pa", "stds"}:
        raise SealError("Reserved C2PA/standards namespaces cannot be used here.")
    if lowered[:2] in _RESERVED_EXAMPLE_PREFIXES and not allow_example_namespace:
        raise SealError(
            "example.com/.net/.org namespaces are reserved for documentation and "
            "tests; use a domain-controlled namespace for production."
        )
    return label


def to_c2pa_assertion_payload(
    receipt: ReceiptInput,
    *,
    include_paths: bool = False,
) -> dict[str, Any]:
    """Return a deterministic, privacy-minimized C2PA-facing payload body."""

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


def build_c2pa_manifest_definition(
    receipt: ReceiptInput,
    *,
    assertion_label: str,
    include_paths: bool = False,
    allow_example_namespace: bool = False,
    claim_generator_name: str = "cmb-provenance",
) -> dict[str, Any]:
    """Build a C2PA SDK JSON manifest definition containing the CMB payload.

    The returned JSON definition still requires an external C2PA implementation
    and signer to create a signed, asset-bound Content Credential.
    """

    label = validate_c2pa_assertion_label(
        assertion_label,
        allow_example_namespace=allow_example_namespace,
    )
    if (
        not isinstance(claim_generator_name, str)
        or not claim_generator_name.strip()
        or claim_generator_name != claim_generator_name.strip()
        or len(claim_generator_name) > 128
    ):
        raise SealError("claim_generator_name must be a non-empty trimmed string.")

    return {
        "claim_generator_info": [
            {
                "name": claim_generator_name,
                "version": TOOL_VERSION,
            }
        ],
        "assertions": [
            {
                "label": label,
                "kind": "Json",
                "created": True,
                "data": to_c2pa_assertion_payload(
                    receipt,
                    include_paths=include_paths,
                ),
            }
        ],
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


def c2pa_assertion_payload_json(
    receipt: ReceiptInput,
    *,
    include_paths: bool = False,
    pretty: bool = False,
) -> str:
    """Render the payload as JSON for display or integration testing."""

    payload = to_c2pa_assertion_payload(receipt, include_paths=include_paths)
    if pretty:
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    return canonical_json_bytes(payload).decode("utf-8")


def save_c2pa_assertion_payload(
    receipt: ReceiptInput,
    path: PathInput,
    *,
    include_paths: bool = False,
) -> Path:
    """Atomically write one canonical adapter payload plus a trailing newline."""

    return _atomic_write_bytes(
        Path(path),
        c2pa_assertion_payload_bytes(receipt, include_paths=include_paths) + b"\n",
    )


def save_c2pa_manifest_definition(
    receipt: ReceiptInput,
    path: PathInput,
    *,
    assertion_label: str,
    include_paths: bool = False,
    allow_example_namespace: bool = False,
    claim_generator_name: str = "cmb-provenance",
) -> Path:
    """Atomically write a deterministic C2PA SDK JSON manifest definition."""

    definition = build_c2pa_manifest_definition(
        receipt,
        assertion_label=assertion_label,
        include_paths=include_paths,
        allow_example_namespace=allow_example_namespace,
        claim_generator_name=claim_generator_name,
    )
    encoded = canonical_json_bytes(definition) + b"\n"
    return _atomic_write_bytes(Path(path), encoded)
