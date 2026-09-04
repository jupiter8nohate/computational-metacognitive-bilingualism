"""Command-line interface for CMB Sovereignty Runtime Protocol v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .authorization import (
    create_authorization,
    load_authorization,
    write_keypair,
)
from .runtime import (
    RuntimePolicy,
    RuntimePolicyError,
    VerificationState,
    assess_operation,
    require_transition,
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
        policy = RuntimePolicy.load(Path(args.policy))
        print(
            json.dumps(
                {
                    "valid": True,
                    "protocol": policy.protocol,
                    "policy_digest": policy.digest,
                    "operations": sorted(policy.operations),
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

    if args.command == "selftest":
        policy = RuntimePolicy.load(Path(args.policy))
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
        print(
            json.dumps(
                {
                    "ok": True,
                    "low_friction_operation": low_name,
                    "high_friction_operation": high_name,
                    "invariants": [
                        "PATTERN != PROOF",
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
        controls = set(rule.controls)
        friction = max(policy.default_friction, rule.criticality)
        if friction >= policy.high_friction_threshold:
            controls.update(("human_signature", "isolated_verification"))
        if friction >= policy.critical_threshold:
            controls.add("two_party_review")
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
