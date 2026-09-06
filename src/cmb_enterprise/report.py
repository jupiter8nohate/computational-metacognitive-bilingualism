"""Compose CMB provenance and authority evidence without collapsing trust domains."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from cmb_cap.credential import (
    load_credential,
    public_key_fingerprint,
    verify_capability,
)
from cmb_provenance.sealing import load_receipt, verify


def build_trust_report(
    paths: Iterable[str | Path],
    *,
    receipt: str | Path,
    base_dir: str | Path,
    check_git_commit: bool = False,
    credential: str | Path | None = None,
    public_key: str | Path | None = None,
    parent_credential: str | Path | None = None,
    require_authority: bool = False,
) -> dict[str, Any]:
    """Return a deterministic enterprise trust report.

    Artifact integrity and enterprise authority are evaluated independently.
    A credential without an externally pinned public key is never upgraded to
    trusted enterprise authority.
    """
    protected = [Path(item) for item in paths]
    provenance = verify(
        protected,
        load_receipt(receipt),
        base_dir=base_dir,
        check_git_commit=check_git_commit,
    )

    artifact_status = "PASS" if provenance.ok else "FAIL"
    release_status = "NOT_CHECKED"
    if check_git_commit:
        release_status = "PASS" if provenance.git_commit_matches else "FAIL"

    authority_status = "NOT_CHECKED"
    authority_failures: list[str] = []
    key_fingerprint: str | None = None

    if credential is not None:
        if public_key is None:
            authority_status = "UNPINNED"
            authority_failures.append("ENTERPRISE_PUBLIC_KEY_REQUIRED")
        else:
            expected_key = Path(public_key).read_text(encoding="utf-8").strip()
            key_fingerprint = public_key_fingerprint(expected_key)
            parent = (
                load_credential(Path(parent_credential))
                if parent_credential is not None
                else None
            )
            valid, failures = verify_capability(
                load_credential(Path(credential)),
                expected_key_fingerprint=key_fingerprint,
                parent_credential=parent,
            )
            authority_status = "PASS" if valid else "FAIL"
            authority_failures.extend(failures)
    elif require_authority:
        authority_status = "FAIL"
        authority_failures.append("ENTERPRISE_AUTHORITY_REQUIRED")

    if artifact_status == "FAIL" or release_status == "FAIL":
        decision = "DENY"
    elif require_authority and authority_status != "PASS":
        decision = "DENY"
    elif authority_status == "FAIL":
        decision = "DENY"
    elif authority_status == "PASS":
        decision = "ALLOW"
    else:
        decision = "HUMAN_REVIEW"

    return {
        "schema": "cmb.enterprise-trust-report.v1",
        "decision": decision,
        "artifact_integrity": {
            "status": artifact_status,
            "manifest_sha256": provenance.manifest_sha256,
            "checked_paths": list(provenance.checked_paths),
            "failures": [
                {
                    "path": failure.path,
                    "code": failure.code,
                    "message": failure.message,
                }
                for failure in provenance.failures
            ],
        },
        "release_provenance": {
            "status": release_status,
            "git_commit_checked": check_git_commit,
            "git_commit_matches": provenance.git_commit_matches,
        },
        "enterprise_authority": {
            "status": authority_status,
            "required": require_authority,
            "key_fingerprint": key_fingerprint,
            "failures": authority_failures,
        },
        "boundaries": {
            "signature_proves_authorship": False,
            "hash_proves_ownership": False,
            "report_is_legal_compliance": False,
            "creator_provenance_is_enterprise_admin": False,
        },
        "invariants": [
            "HASH != AUTHORSHIP",
            "SIGNATURE != ORIGINALITY",
            "PROVENANCE != ADMINISTRATOR_ACCESS",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
    }
