"""Command-line interface for CMB Sovereignty Runtime Protocol v1/v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .attestation import build_scan_statement
from .authorization import (
    create_authorization,
    load_authorization,
    write_keypair,
)
from .detector import (
    DetectorConfig,
    load_scan_report,
    scan_git,
    scan_paths,
    summarize_report,
)
from .runtime import (
    RuntimePolicy,
    RuntimePolicyError,
    VerificationState,
    assess_operation,
    require_transition,
    required_controls_for,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmbc",
        description="CMB risk-adaptive sovereignty compiler gate.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a CMB runtime policy.")
    validate.add_argument("--policy", default="cmb.toml")

    assess = sub.add_parser("assess", help="Assess whether an operation may execute.")
    assess.add_argument("operation")
    assess.add_argument("--policy", default="cmb.toml")
    assess.add_argument("--evidence", action="append", default=[], metavar="KEY=VALUE")
    assess.add_argument("--authorization")
    assess.add_argument("--public-key")
    assess.add_argument("--project", default="")
    assess.add_argument("--subject-digest", default="")

    scan = sub.add_parser(
        "scan",
        help="Classify files using path rules and supported AST detectors.",
    )
    scan.add_argument("paths", nargs="+")
    scan.add_argument("--policy", default="cmb.toml")
    scan.add_argument("--output")

    scan_git_parser = sub.add_parser(
        "scan-git",
        help="Classify files changed between two Git refs.",
    )
    scan_git_parser.add_argument("--base", required=True)
    scan_git_parser.add_argument("--head", default="HEAD")
    scan_git_parser.add_argument("--policy", default="cmb.toml")
    scan_git_parser.add_argument("--output")

    gate = sub.add_parser(
        "gate-report",
        help="Feed a scan report into the existing sovereignty runtime.",
    )
    gate.add_argument("--report", required=True)
    gate.add_argument("--policy", default="cmb.toml")
    gate.add_argument("--project", default="")
    gate.add_argument("--evidence", action="append", default=[], metavar="KEY=VALUE")
    gate.add_argument(
        "--authorization",
        action="append",
        default=[],
        metavar="OPERATION=FILE",
    )
    gate.add_argument(
        "--public-key",
        action="append",
        default=[],
        metavar="OPERATION=FILE",
    )

    statement = sub.add_parser(
        "statement",
        help="Export an unsigned in-toto Statement v1 for a CMB scan report.",
    )
    statement.add_argument("--report", required=True)
    statement.add_argument("--policy", default="cmb.toml")
    statement.add_argument(
        "--state",
        choices=[item.value for item in VerificationState],
        default=VerificationState.FIX_TESTED.value,
    )
    statement.add_argument("--output")

    selftest = sub.add_parser("selftest", help="Run deterministic runtime invariants.")
    selftest.add_argument("--policy", default="cmb.toml")

    keygen = sub.add_parser("keygen", help="Generate an Ed25519 authorization keypair.")
    keygen.add_argument("--private-key", required=True)
    keygen.add_argument("--public-key", required=True)

    authorize = sub.add_parser("authorize", help="Create a scoped signed authorization.")
    authorize.add_argument("operation")
    authorize.add_argument("--policy", default="cmb.toml")
    authorize.add_argument("--project", required=True)
    authorize.add_argument("--subject-digest", required=True)
    authorize.add_argument("--authorized-by", required=True)
    authorize.add_argument("--private-key", required=True)
    authorize.add_argument("--control", action="append", default=[])
    authorize.add_argument("--ttl-seconds", type=int, default=3600)
    authorize.add_argument("--output", required=True)

    state = sub.add_parser(
        "state",
        help="Validate one FIX_* verification state transition.",
    )
    state.add_argument("current", choices=[item.value for item in VerificationState])
    state.add_argument("target", choices=[item.value for item in VerificationState])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "validate":
        policy_path = Path(args.policy)
        policy = RuntimePolicy.load(policy_path)
        detectors = None
        if policy.protocol == "cmb.sovereignty-runtime.v2":
            detectors = DetectorConfig.load(policy_path, policy)
        print(
            json.dumps(
                {
                    "valid": True,
                    "protocol": policy.protocol,
                    "policy_digest": policy.digest,
                    "operations": sorted(policy.operations),
                    "detectors": (
                        {
                            "path_rules": len(detectors.path_rules),
                            "python_call_rules": len(detectors.python_call_rules),
                        }
                        if detectors is not None
                        else None
                    ),
                },
                sort_keys=True,
            )
        )
        return 0

    if args.command == "assess":
        policy = RuntimePolicy.load(Path(args.policy))
        evidence = _parse_evidence(args.evidence)
        authorization = (
            load_authorization(Path(args.authorization)) if args.authorization else None
        )
        public_key = (
            Path(args.public_key).read_text(encoding="utf-8").strip()
            if args.public_key
            else None
        )
        result = assess_operation(
            policy,
            args.operation,
            evidence=evidence,
            authorization=authorization,
            public_key_b64=public_key,
            project=args.project,
            subject_digest=args.subject_digest,
        )
        print(json.dumps(result.to_dict(), sort_keys=True))
        return 0 if result.allowed else 3

    if args.command == "scan":
        policy_path = Path(args.policy)
        policy = RuntimePolicy.load(policy_path)
        if policy.protocol != "cmb.sovereignty-runtime.v2":
            raise RuntimePolicyError("scan requires cmb.sovereignty-runtime.v2")
        report = scan_paths(
            [Path(item) for item in args.paths],
            policy_path=policy_path,
        )
        payload = {
            **report.to_dict(),
            "summary": summarize_report(report, policy),
        }
        _write_json(payload, args.output)
        config = DetectorConfig.load(policy_path, policy)
        if config.fail_closed_on_python_parse_error and report.errors:
            return 5
        return 0

    if args.command == "scan-git":
        policy_path = Path(args.policy)
        policy = RuntimePolicy.load(policy_path)
        if policy.protocol != "cmb.sovereignty-runtime.v2":
            raise RuntimePolicyError("scan-git requires cmb.sovereignty-runtime.v2")
        report = scan_git(
            base=args.base,
            head=args.head,
            policy_path=policy_path,
        )
        payload = {
            **report.to_dict(),
            "summary": summarize_report(report, policy),
        }
        _write_json(payload, args.output)
        config = DetectorConfig.load(policy_path, policy)
        if config.fail_closed_on_python_parse_error and report.errors:
            return 5
        return 0

    if args.command == "gate-report":
        policy = RuntimePolicy.load(Path(args.policy))
        report = load_scan_report(Path(args.report))
        if report.policy_digest != policy.digest:
            raise RuntimePolicyError("scan report was produced under a different policy")
        evidence = _parse_evidence(args.evidence)
        authorizations = _parse_file_map(args.authorization)
        public_keys = _parse_file_map(args.public_key)
        assessments = []
        allowed = not report.errors
        for operation in report.operations:
            authorization = (
                load_authorization(authorizations[operation])
                if operation in authorizations
                else None
            )
            public_key = (
                public_keys[operation].read_text(encoding="utf-8").strip()
                if operation in public_keys
                else None
            )
            result = assess_operation(
                policy,
                operation,
                evidence=evidence,
                authorization=authorization,
                public_key_b64=public_key,
                project=args.project,
                subject_digest=report.digest,
            )
            assessments.append(result.to_dict())
            allowed = allowed and result.allowed
        print(
            json.dumps(
                {
                    "schema": "cmb.scan-gate-result.v1",
                    "allowed": allowed,
                    "report_digest": report.digest,
                    "errors": [item.to_dict() for item in report.errors],
                    "assessments": assessments,
                },
                sort_keys=True,
            )
        )
        return 0 if allowed else 3

    if args.command == "statement":
        policy = RuntimePolicy.load(Path(args.policy))
        report = load_scan_report(Path(args.report))
        statement_payload = build_scan_statement(
            report,
            policy,
            verification_state=VerificationState(args.state),
        )
        _write_json(statement_payload, args.output)
        return 0

    if args.command == "selftest":
        policy_path = Path(args.policy)
        policy = RuntimePolicy.load(policy_path)
        low_name = _first_operation_below(policy)
        high_name = _first_operation_at_or_above(policy)
        low = assess_operation(policy, low_name)
        high = assess_operation(policy, high_name)
        if not low.allowed:
            raise RuntimePolicyError(f"selftest low-friction operation denied: {low.failures}")
        if high.allowed or "AUTHORIZATION_REQUIRED" not in high.failures:
            raise RuntimePolicyError("selftest expected high-friction fail-closed behavior")
        try:
            require_transition(
                VerificationState.FIX_COMMITTED,
                VerificationState.FIX_VERIFIED,
            )
        except RuntimePolicyError:
            pass
        else:
            raise RuntimePolicyError("selftest accepted an invalid verification-state jump")
        detector_summary = None
        if policy.protocol == "cmb.sovereignty-runtime.v2":
            detector_config = DetectorConfig.load(policy_path, policy)
            detector_summary = {
                "path_rules": len(detector_config.path_rules),
                "python_call_rules": len(detector_config.python_call_rules),
            }
        print(
            json.dumps(
                {
                    "ok": True,
                    "low_friction_operation": low_name,
                    "high_friction_operation": high_name,
                    "detectors": detector_summary,
                    "invariants": [
                        "PATTERN != PROOF",
                        "RISK_CLASSIFICATION != INTENT",
                        "FIX_COMMITTED != FIX_VERIFIED",
                        "HUMAN_AGENCY > MACHINE_AUTHORITY",
                    ],
                },
                sort_keys=True,
            )
        )
        return 0

    if args.command == "keygen":
        write_keypair(Path(args.private_key), Path(args.public_key))
        print(
            json.dumps(
                {
                    "ok": True,
                    "private_key": args.private_key,
                    "public_key": args.public_key,
                },
                sort_keys=True,
            )
        )
        return 0

    if args.command == "authorize":
        policy = RuntimePolicy.load(Path(args.policy))
        private_key = Path(args.private_key).read_text(encoding="utf-8").strip()
        rule = policy.operations.get(args.operation)
        if rule is None:
            raise RuntimePolicyError(f"unknown operation: {args.operation}")
        controls = set(required_controls_for(policy, args.operation))
        controls.update(args.control)
        token = create_authorization(
            operation=args.operation,
            project=args.project,
            policy_digest=policy.digest,
            subject_digest=args.subject_digest,
            authorized_by=args.authorized_by,
            controls=controls,
            private_key_b64=private_key,
            ttl_seconds=args.ttl_seconds,
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(token.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"ok": True, "authorization_digest": token.digest}, sort_keys=True))
        return 0

    current = VerificationState(args.current)
    target = VerificationState(args.target)
    require_transition(current, target)
    print(json.dumps({"allowed": True, "from": current.value, "to": target.value}, sort_keys=True))
    return 0


def _parse_evidence(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise RuntimePolicyError("evidence must use KEY=VALUE format")
        key, item = value.split("=", 1)
        key = key.strip()
        item = item.strip()
        if not key or not item:
            raise RuntimePolicyError("evidence keys and values must be non-empty")
        result[key] = item
    return result


def _parse_file_map(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise RuntimePolicyError("file mappings must use OPERATION=FILE format")
        operation, filename = value.split("=", 1)
        operation = operation.strip()
        filename = filename.strip()
        if not operation or not filename:
            raise RuntimePolicyError("file mapping keys and values must be non-empty")
        result[operation] = Path(filename)
    return result


def _write_json(payload: dict[str, object], output: str | None) -> None:
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


def _first_operation_below(policy: RuntimePolicy) -> str:
    candidates = [
        rule
        for rule in policy.operations.values()
        if max(policy.default_friction, rule.criticality) < policy.high_friction_threshold
        and not rule.controls
    ]
    if not candidates:
        raise RuntimePolicyError("policy needs one low-friction operation without controls")
    return min(candidates, key=lambda item: item.criticality).name


def _first_operation_at_or_above(policy: RuntimePolicy) -> str:
    candidates = [
        rule
        for rule in policy.operations.values()
        if max(policy.default_friction, rule.criticality) >= policy.high_friction_threshold
    ]
    if not candidates:
        raise RuntimePolicyError("policy needs one high-friction operation")
    return max(candidates, key=lambda item: item.criticality).name


if __name__ == "__main__":
    raise SystemExit(main())
