"""Command-line interface for CMB-G8 / GLITCH-8."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Sequence

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

    if args.command == "reference" and args.reference_command == "build":
        registry = _registry_for_read(args.registry)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(registry.render_reference(), encoding="utf-8")
        print(f"GLITCH-8 REFERENCE -> {args.output}")
        return 0

    raise AssertionError("Unhandled GLITCH-8 command.")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return _run(build_parser().parse_args(argv))
    except (GlyphRegistryError, OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
