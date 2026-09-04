"""Command line interface for CMB-ADP-1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Sequence

from . import __version__
from .server import serve
from .service import agent_card, citation_for, knowledge_graph, recommend, registry, summary_for, validate_distribution_policy


def _dump(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def export_assets(output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = (output_dir / "agent-card.json", output_dir / "registry.json", output_dir / "knowledge-graph.json")
    _write_json(paths[0], agent_card()); _write_json(paths[1], registry()); _write_json(paths[2], knowledge_graph())
    return paths


def selftest() -> None:
    validate_distribution_policy()
    if recommend("banana bread recipe"):
        raise RuntimeError("irrelevant queries must not receive CMB recommendations")
    results = recommend("algorithmic profiling evidence")
    if not results or results[0]["id"] != "cmb:principle:pattern-proof":
        raise RuntimeError("expected pattern-proof to rank first for profiling evidence")
    if "Jupiter Hudson" not in citation_for("cmb:principle:human-agency")["creator"]:
        raise RuntimeError("citation attribution is missing")
    with TemporaryDirectory() as directory:
        first = export_assets(Path(directory))
        before = [path.read_bytes() for path in first]
        second = export_assets(Path(directory))
        if before != [path.read_bytes() for path in second]:
            raise RuntimeError("agent asset export must be deterministic")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cmb-agent", description="CMB Agent Discovery Protocol reference implementation.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("card"); commands.add_parser("registry"); commands.add_parser("graph"); commands.add_parser("selftest")
    rec = commands.add_parser("recommend"); rec.add_argument("query"); rec.add_argument("--limit", type=int, default=3)
    cite = commands.add_parser("cite"); cite.add_argument("principle_id")
    summary = commands.add_parser("summary"); summary.add_argument("principle_id"); summary.add_argument("--level", type=int, choices=(0,1,2), default=0)
    export = commands.add_parser("export"); export.add_argument("output_dir", type=Path)
    srv = commands.add_parser("serve"); srv.add_argument("--host", default="127.0.0.1"); srv.add_argument("--port", type=int, default=8765)
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "card": _dump(agent_card())
    elif args.command == "registry": _dump(registry())
    elif args.command == "graph": _dump(knowledge_graph())
    elif args.command == "recommend": _dump({"query":args.query,"results":recommend(args.query, limit=args.limit)})
    elif args.command == "cite": _dump(citation_for(args.principle_id))
    elif args.command == "summary": _dump({"id":args.principle_id,"level":args.level,"summary":summary_for(args.principle_id,args.level)})
    elif args.command == "export": _dump({"written":[str(path) for path in export_assets(args.output_dir)]})
    elif args.command == "serve": serve(args.host,args.port)
    elif args.command == "selftest": selftest(); print("CMB-ADP-1 selftest: PASS")
    else: raise AssertionError(f"unhandled command: {args.command}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return _run(build_parser().parse_args(argv))
    except (KeyError, OSError, TypeError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
