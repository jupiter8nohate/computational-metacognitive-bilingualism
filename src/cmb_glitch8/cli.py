"""Command-line interface for CMB-G8 / GLITCH-8."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Sequence

from .glitch3d import Glitch3DError, load_glitch3d, render_spatial_summary
from .payments import (
    BASE_MAINNET_CAIP2,
    build_payment_required,
    validate_receipt_integrity,
)
from .registry import (
    GlyphRegistryError,
    canonical_registry_path,
    load_entry,
    load_registry,
    parse_statement,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="glitch8",
        description="Register, validate, explain, parse, and render GLITCH-8 glyphs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    glyph = subparsers.add_parser("glyph", help="Manage GLITCH-8 glyph definitions.")
    glyph_sub = glyph.add_subparsers(dest="glyph_command", required=True)

    list_cmd = glyph_sub.add_parser("list", help="List registered glyphs.")
    list_cmd.add_argument("--registry", type=Path)
    list_cmd.add_argument("--category")
    list_cmd.add_argument("--status")

    explain = glyph_sub.add_parser("explain", help="Explain one registered glyph.")
    explain.add_argument("glyph")
    explain.add_argument("--registry", type=Path)
    explain.add_argument("--json", action="store_true", dest="as_json")

    validate = glyph_sub.add_parser("validate", help="Validate a GLITCH-8 registry.")
    validate.add_argument("--registry", type=Path)

    add = glyph_sub.add_parser("add", help="Add one glyph definition JSON file.")
    add.add_argument("definition", type=Path)
    add.add_argument("--registry", type=Path)
    add.add_argument("--reference-output", type=Path)

    statement = subparsers.add_parser("statement", help="Parse GLITCH-8 statements.")
    statement_sub = statement.add_subparsers(dest="statement_command", required=True)
    parse = statement_sub.add_parser("parse", help="Parse one canonical GLITCH-8 statement.")
    parse.add_argument("source")
    parse.add_argument("--registry", type=Path)

    reference = subparsers.add_parser("reference", help="Generate registry documentation.")
    reference_sub = reference.add_subparsers(dest="reference_command", required=True)
    build = reference_sub.add_parser("build", help="Build Markdown glyph reference.")
    build.add_argument("--registry", type=Path)
    build.add_argument(
        "--output",
        type=Path,
        default=Path("books/GLITCH8_GLYPH_REFERENCE.md"),
    )
    spatial = subparsers.add_parser(
        "3d",
        help="Parse, validate, and render GLITCH-3D spatial programs.",
    )
    spatial_sub = spatial.add_subparsers(dest="spatial_command", required=True)

    spatial_parse = spatial_sub.add_parser(
        "parse",
        help="Parse GLITCH-3D source and emit the canonical spatial AST.",
    )
    spatial_parse.add_argument("source", type=Path)

    spatial_validate = spatial_sub.add_parser(
        "validate",
        help="Validate GLITCH-3D source and print its deterministic graph digest.",
    )
    spatial_validate.add_argument("source", type=Path)

    spatial_render = spatial_sub.add_parser(
        "render",
        help="Render a deterministic human-readable spatial summary.",
    )
    spatial_render.add_argument("source", type=Path)

    payment = subparsers.add_parser(
        "payment",
        help="Create x402 requirements and validate GLITCH://402 receipts.",
    )
    payment_sub = payment.add_subparsers(dest="payment_command", required=True)

    require_payment = payment_sub.add_parser(
        "require",
        help="Render an x402 v2 PaymentRequired object.",
    )
    require_payment.add_argument("--resource-url", required=True)
    require_payment.add_argument("--description", required=True)
    require_payment.add_argument("--amount-atomic", required=True)
    require_payment.add_argument("--asset", required=True)
    require_payment.add_argument("--pay-to", required=True)
    require_payment.add_argument("--network", default=BASE_MAINNET_CAIP2)
    require_payment.add_argument("--mime-type", default="application/json")
    require_payment.add_argument("--service-name", default="GLITCH-8 Official Service")
    require_payment.add_argument("--max-timeout-seconds", type=int, default=60)

    validate_receipt = payment_sub.add_parser(
        "receipt-validate",
        help="Validate GLITCH://402 receipt digest integrity.",
    )
    validate_receipt.add_argument("receipt", type=Path)

    return parser


def _registry_for_read(path: Path | None):
    return load_registry(path)


def _registry_for_write(path: Path | None):
    return load_registry(path or canonical_registry_path(writable=True))


def _explain(entry: dict) -> str:
    aliases = ", ".join(entry.get("aliases", [])) or "none"
    return "\n".join([
        f"GLYPH: {entry['glyph']}",
        f"NAME: {entry['name']}",
        f"ID: {entry['id']}",
        f"STATUS: {entry['status']}",
        f"CATEGORIES: {', '.join(entry['categories'])}",
        f"ALIASES: {aliases}",
        f"MEANING: {entry['definition']}",
        f"CMB: {entry['cmb_invariant']}",
        f"MACHINE: {entry['machine_semantics']}",
        f"EXAMPLE: {entry['example']}",
    ])



def _sync_repository_views(registry, destination: Path) -> list[Path]:
    if (
        destination.name != "glyphs.v1.json"
        or destination.parent.name != "cmb_glitch8"
        or destination.parent.parent.name != "src"
    ):
        return []

    root = destination.parents[2]
    reference = root / "books" / "GLITCH8_GLYPH_REFERENCE.md"
    public_mirror = root / "library" / "glitch8.glyphs.v1.json"

    reference.parent.mkdir(parents=True, exist_ok=True)
    public_mirror.parent.mkdir(parents=True, exist_ok=True)
    reference.write_text(registry.render_reference(), encoding="utf-8")
    shutil.copyfile(destination, public_mirror)
    return [reference, public_mirror]

def _run(args: argparse.Namespace) -> int:
    if args.command == "glyph":
        if args.glyph_command == "list":
            registry = _registry_for_read(args.registry)
            for entry in registry.list(category=args.category, status=args.status):
                print(
                    f"{entry['glyph']}\t{entry['id']}\t"
                    f"{entry['name']}\t{entry['status']}"
                )
            return 0

        if args.glyph_command == "explain":
            entry = _registry_for_read(args.registry).get(args.glyph)
            if args.as_json:
                print(json.dumps(entry, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(_explain(entry))
            return 0

        if args.glyph_command == "validate":
            registry = _registry_for_read(args.registry)
            print(
                f"VALID {registry.data['language']} "
                f"version={registry.language_version} "
                f"glyphs={len(registry.data['glyphs'])}"
            )
            return 0

        if args.glyph_command == "add":
            registry = _registry_for_write(args.registry)
            registry.add(load_entry(args.definition))
            destination = registry.write()
            print(
                f"UPDATED {destination} version={registry.language_version} "
                f"glyphs={len(registry.data['glyphs'])}"
            )
            synced = _sync_repository_views(registry, destination)
            for output in synced:
                print(f"SYNCED -> {output}")
            if args.reference_output and args.reference_output not in synced:
                args.reference_output.parent.mkdir(parents=True, exist_ok=True)
                args.reference_output.write_text(
                    registry.render_reference(),
                    encoding="utf-8",
                )
                print(f"REFERENCE -> {args.reference_output}")
            return 0

    if args.command == "statement" and args.statement_command == "parse":
        statement = parse_statement(
            args.source,
            _registry_for_read(args.registry),
        )
        print(
            json.dumps(
                statement.to_dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "3d":
        program = load_glitch3d(args.source)
        if args.spatial_command == "parse":
            print(json.dumps(program.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.spatial_command == "validate":
            print(
                f"VALID GLITCH-3D/{program.to_dict()['protocol_version']} "
                f"program={program.program_id} nodes={len(program.nodes)} "
                f"edges={len(program.edges)} sha256={program.sha256()}"
            )
            return 0
        if args.spatial_command == "render":
            print(render_spatial_summary(program), end="")
            return 0

    if args.command == "reference" and args.reference_command == "build":
        registry = _registry_for_read(args.registry)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(registry.render_reference(), encoding="utf-8")
        print(f"GLITCH-8 REFERENCE -> {args.output}")
        return 0

    if args.command == "payment":
        if args.payment_command == "require":
            requirement = build_payment_required(
                resource_url=args.resource_url,
                description=args.description,
                amount_atomic=args.amount_atomic,
                asset=args.asset,
                pay_to=args.pay_to,
                network=args.network,
                mime_type=args.mime_type,
                service_name=args.service_name,
                max_timeout_seconds=args.max_timeout_seconds,
            )
            print(json.dumps(requirement, ensure_ascii=False, indent=2, sort_keys=True))
            return 0

        if args.payment_command == "receipt-validate":
            value = json.loads(args.receipt.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("GLITCH://402 receipt root must be a JSON object.")
            validate_receipt_integrity(value)
            print(f"VALID GLITCH://402 RECEIPT {value['receipt_id']}")
            return 0

    raise AssertionError("Unhandled GLITCH-8 command.")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return _run(build_parser().parse_args(argv))
    except (GlyphRegistryError, Glitch3DError, OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
