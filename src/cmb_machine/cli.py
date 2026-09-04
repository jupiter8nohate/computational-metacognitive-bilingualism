"""Command-line interface for machine-native CMB-66 compilation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .compiler import compile_bundle, supported_targets
from .harmoni import EpistemicState, ProofGate, evaluate_claim, harmoni_manifest
from .ir import build_core_ir


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cmb-machine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("targets", help="List supported CMB-66 target encodings.")
    subparsers.add_parser(
        "harmoni-manifest",
        help="Print the canonical HARMONI-666 triangle and proof-gate contract.",
    )

    evaluate_parser = subparsers.add_parser(
        "harmoni-evaluate",
        help="Evaluate an epistemic claim with fail-closed HARMONI-666 proof gates.",
    )
    evaluate_parser.add_argument(
        "--state",
        required=True,
        choices=[state.value for state in EpistemicState],
        help="Requested epistemic state.",
    )
    evaluate_parser.add_argument(
        "--pass-gate",
        action="append",
        default=[],
        choices=[gate.value for gate in ProofGate],
        help="Mark one proof gate as passing. Repeat as needed.",
    )
    evaluate_parser.add_argument(
        "--all-proof-gates",
        action="store_true",
        help="Mark all six proof gates as passing.",
    )

    compile_parser = subparsers.add_parser(
        "compile-core",
        help="Compile the canonical CMB machine IR with mandatory FGC stamping.",
    )
    compile_parser.add_argument(
        "--output-dir",
        default="dist/cmb-machine",
        help="Directory for generated artifacts.",
    )
    compile_parser.add_argument(
        "--target",
        action="append",
        choices=supported_targets(),
        help="Generate only this target. Repeat for multiple targets; default is all.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "targets":
        print("\n".join(supported_targets()))
        return 0

    if args.command == "harmoni-manifest":
        print(json.dumps(harmoni_manifest(), sort_keys=True))
        return 0

    if args.command == "harmoni-evaluate":
        passed = {ProofGate(value) for value in args.pass_gate}
        gate_results = {
            gate: args.all_proof_gates or gate in passed
            for gate in ProofGate
        }
        decision = evaluate_claim(args.state, gate_results=gate_results)
        print(json.dumps(decision.to_dict(), sort_keys=True))
        return 2 if decision.missingno else 0

    output_dir = Path(args.output_dir)
    selected = tuple(args.target) if args.target else None
    artifacts = compile_bundle(build_core_ir(), targets=selected)

    manifest = {
        "protocol": "CMB-66",
        "artifacts": [],
    }

    for artifact in artifacts:
        path = output_dir / f"cmb-core{artifact.extension}"
        artifact.write(path)
        manifest["artifacts"].append(
            {
                "target": artifact.target,
                "path": path.as_posix(),
                "media_type": artifact.media_type,
                "sha256": artifact.sha256,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
