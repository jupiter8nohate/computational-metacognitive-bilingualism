"""Unsigned in-toto statement export for CMB-SRP-2 scan evidence."""

from __future__ import annotations

from typing import Any

from .detector import ScanReport, summarize_report
from .runtime import RuntimePolicy, VerificationState

IN_TOTO_STATEMENT_V1 = "https://in-toto.io/Statement/v1"
CMB_SRP2_PREDICATE_V1 = (
    "https://github.com/jupiter8nohate/"
    "computational-metacognitive-bilingualism/blob/main/"
    "spec/CMB-SRP-2.md#cmb-srp2-attestation-predicate-v1"
)


def build_scan_statement(
    report: ScanReport,
    policy: RuntimePolicy,
    *,
    verification_state: VerificationState = VerificationState.FIX_TESTED,
) -> dict[str, Any]:
    if report.policy_digest != policy.digest:
        raise ValueError("scan report policy digest does not match active policy")
    summary = summarize_report(report, policy)
    return {
        "_type": IN_TOTO_STATEMENT_V1,
        "subject": [
            {
                "name": "cmb-srp2-scan-report",
                "digest": {"sha256": report.digest.removeprefix("sha256:")},
            }
        ],
        "predicateType": CMB_SRP2_PREDICATE_V1,
        "predicate": {
            "schema": "cmb.srp2-predicate.v1",
            "policyDigest": policy.digest,
            "reportDigest": report.digest,
            "verificationState": verification_state.value,
            "summary": summary,
            "findings": [item.to_dict() for item in report.findings],
            "errors": [item.to_dict() for item in report.errors],
            "git": {"base": report.base, "head": report.head},
            "epistemicBoundaries": [
                "PATTERN != PROOF",
                "RISK_CLASSIFICATION != INTENT",
                "UNSIGNED_STATEMENT != ATTESTATION",
                "ATTESTATION != CORRECTNESS",
                "HUMAN_AGENCY > MACHINE_AUTHORITY",
            ],
        },
    }
