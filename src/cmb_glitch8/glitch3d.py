"""Deterministic GLITCH-3D v1 spatial source parser.

GLITCH-3D makes spatial layout explicit data rather than asking machines to infer
semantics from whitespace or decorative art.

DISPLAY != IDENTIFIER
POSITION == INFORMATION
DEPTH == SEMANTIC_LAYER
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Iterable

GLITCH3D_PROTOCOL: Final[str] = "GLITCH-3D"
GLITCH3D_SCHEMA_VERSION: Final[str] = "glitch3d.program.v1"
GLITCH3D_VERSION: Final[str] = "1.0.0"

_LAYER_KIND: Final[dict[int, str]] = {
    0: "EVENT",
    1: "MACHINE",
    2: "SEMANTIC",
    3: "PROVENANCE",
    4: "HUMAN",
}

_OPERATORS: Final[set[str]] = {
    "DOWN",
    "UP",
    "BACKTRACE",
    "PROPAGATE",
    "REJECT",
    "RETRY",
    "ESCALATE",
    "APPEAL",
}

_DISTORTIONS: Final[set[str]] = {
    "NONE",
    "UNCERTAIN",
    "ABSENT",
    "REDACTED",
    "INVALID",
    "OBSERVED",
}

_BOUNDARY_MODES: Final[set[str]] = {
    "HUMAN_AUTHORITY_REQUIRED",
    "PROVENANCE_REQUIRED",
    "READ_ONLY",
}

_PROGRAM_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_NODE_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_-]{0,47}$")
_BOUNDARY_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_-]{0,47}$")


class Glitch3DError(ValueError):
    """Raised when GLITCH-3D source violates the v1 contract."""


@dataclass(frozen=True, slots=True)
class Glitch3DNode:
    id: str
    x: int
    y: int
    z: int
    kind: str
    state: str
    distortion: str = "NONE"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Glitch3DEdge:
    source: str
    target: str
    operator: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Glitch3DBoundary:
    id: str
    z: int
    mode: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Glitch3DProgram:
    program_id: str
    nodes: tuple[Glitch3DNode, ...]
    edges: tuple[Glitch3DEdge, ...]
    boundaries: tuple[Glitch3DBoundary, ...]
    invariants: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": GLITCH3D_SCHEMA_VERSION,
            "protocol": GLITCH3D_PROTOCOL,
            "protocol_version": GLITCH3D_VERSION,
            "program_id": self.program_id,
            "axes": {
                "x": "RELATION_LANE",
                "y": "EXECUTION_ORDER",
                "z": "SEMANTIC_DEPTH",
            },
            "layers": [
                {"z": z, "kind": kind}
                for z, kind in sorted(_LAYER_KIND.items())
            ],
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "boundaries": [boundary.to_dict() for boundary in self.boundaries],
            "invariants": list(self.invariants),
        }

    def canonical_bytes(self) -> bytes:
        """Return deterministic UTF-8 JSON bytes for hashing and conformance."""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _parse_assignments(parts: Iterable[str], *, line_number: int) -> dict[str, str]:
    values: dict[str, str] = {}
    for part in parts:
        if "=" not in part:
            raise Glitch3DError(
                f"line {line_number}: expected KEY=VALUE token, got {part!r}"
            )
        key, value = part.split("=", 1)
        if not key or not value or key in values:
            raise Glitch3DError(
                f"line {line_number}: invalid or duplicate assignment {part!r}"
            )
        values[key.upper()] = value
    return values


def _parse_int(value: str, *, field: str, line_number: int) -> int:
    try:
        result = int(value, 10)
    except ValueError as exc:
        raise Glitch3DError(
            f"line {line_number}: {field} must be a base-10 integer"
        ) from exc
    if not -999 <= result <= 999:
        raise Glitch3DError(
            f"line {line_number}: {field} must be between -999 and 999"
        )
    return result


def _require_state(value: str, *, line_number: int) -> str:
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", value):
        raise Glitch3DError(
            f"line {line_number}: STATE must use uppercase machine identifier syntax"
        )
    return value


def _validate_node(node: Glitch3DNode, *, line_number: int) -> None:
    expected_kind = _LAYER_KIND.get(node.z)
    if expected_kind is None:
        raise Glitch3DError(
            f"line {line_number}: Z={node.z} is not a defined GLITCH-3D v1 layer"
        )
    if node.kind != expected_kind:
        raise Glitch3DError(
            f"line {line_number}: Z={node.z} requires KIND={expected_kind}, "
            f"got {node.kind}"
        )
    if node.distortion not in _DISTORTIONS:
        raise Glitch3DError(
            f"line {line_number}: unsupported DISTORTION={node.distortion}"
        )


def _validate_graph(
    nodes: tuple[Glitch3DNode, ...],
    edges: tuple[Glitch3DEdge, ...],
    boundaries: tuple[Glitch3DBoundary, ...],
) -> None:
    by_id = {node.id: node for node in nodes}
    if len(by_id) != len(nodes):
        raise Glitch3DError("node IDs must be unique")

    boundary_ids = {boundary.id for boundary in boundaries}
    if len(boundary_ids) != len(boundaries):
        raise Glitch3DError("boundary IDs must be unique")

    boundary_by_z = {boundary.z: boundary for boundary in boundaries}

    seen_edges: set[tuple[str, str, str]] = set()
    for edge in edges:
        key = (edge.source, edge.target, edge.operator)
        if key in seen_edges:
            raise Glitch3DError(f"duplicate edge: {key}")
        seen_edges.add(key)

        if edge.source not in by_id or edge.target not in by_id:
            raise Glitch3DError(
                f"edge {edge.source}->{edge.target} references unknown node"
            )
        if edge.operator not in _OPERATORS:
            raise Glitch3DError(f"unsupported operator: {edge.operator}")

        source = by_id[edge.source]
        target = by_id[edge.target]

        if edge.operator in {"DOWN", "PROPAGATE"} and target.y <= source.y:
            raise Glitch3DError(
                f"{edge.operator} requires increasing Y execution order: "
                f"{source.id}->{target.id}"
            )
        if edge.operator == "UP" and target.y >= source.y:
            raise Glitch3DError(
                f"UP requires decreasing Y execution order: {source.id}->{target.id}"
            )
        if edge.operator == "BACKTRACE" and target.kind != "PROVENANCE":
            raise Glitch3DError(
                f"BACKTRACE must target a PROVENANCE node: {source.id}->{target.id}"
            )
        if edge.operator in {"ESCALATE", "APPEAL"} and target.kind != "HUMAN":
            raise Glitch3DError(
                f"{edge.operator} must target a HUMAN node: {source.id}->{target.id}"
            )
        if target.z == 4 and source.z < 4:
            boundary = boundary_by_z.get(4)
            if boundary is None or boundary.mode != "HUMAN_AUTHORITY_REQUIRED":
                raise Glitch3DError(
                    "crossing into Z=4 HUMAN requires a "
                    "HUMAN_AUTHORITY_REQUIRED boundary"
                )
            if edge.operator not in {"ESCALATE", "APPEAL"}:
                raise Glitch3DError(
                    f"entry into HUMAN layer requires ESCALATE or APPEAL, got "
                    f"{edge.operator}"
                )


def parse_glitch3d(source: str) -> Glitch3DProgram:
    """Parse and validate one GLITCH-3D/1 spatial source program."""
    if not isinstance(source, str):
        raise TypeError("source must be a string")

    lines = [
        (index, line.strip())
        for index, line in enumerate(source.splitlines(), start=1)
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines:
        raise Glitch3DError("GLITCH-3D source is empty")
    if lines[0][1] != "GLITCH-3D/1":
        raise Glitch3DError("line 1: expected GLITCH-3D/1 protocol header")

    program_id: str | None = None
    nodes: list[Glitch3DNode] = []
    edges: list[Glitch3DEdge] = []
    boundaries: list[Glitch3DBoundary] = []
    invariants: list[str] = []

    for line_number, line in lines[1:]:
        parts = line.split()
        keyword = parts[0]

        if keyword == "PROGRAM":
            if len(parts) != 2 or program_id is not None:
                raise Glitch3DError(
                    f"line {line_number}: PROGRAM requires one unique identifier"
                )
            if not _PROGRAM_RE.fullmatch(parts[1]):
                raise Glitch3DError(
                    f"line {line_number}: invalid PROGRAM identifier"
                )
            program_id = parts[1]
            continue

        if keyword == "NODE":
            if len(parts) < 2:
                raise Glitch3DError(f"line {line_number}: NODE requires an identifier")
            node_id = parts[1]
            if not _NODE_ID_RE.fullmatch(node_id):
                raise Glitch3DError(f"line {line_number}: invalid NODE identifier")
            values = _parse_assignments(parts[2:], line_number=line_number)
            required = {"X", "Y", "Z", "KIND", "STATE"}
            allowed = required | {"DISTORTION"}
            if set(values) != required and not (
                required <= set(values) and set(values) <= allowed
            ):
                raise Glitch3DError(
                    f"line {line_number}: NODE fields must be "
                    "X Y Z KIND STATE [DISTORTION]"
                )
            node = Glitch3DNode(
                id=node_id,
                x=_parse_int(values["X"], field="X", line_number=line_number),
                y=_parse_int(values["Y"], field="Y", line_number=line_number),
                z=_parse_int(values["Z"], field="Z", line_number=line_number),
                kind=values["KIND"].upper(),
                state=_require_state(values["STATE"], line_number=line_number),
                distortion=values.get("DISTORTION", "NONE").upper(),
            )
            _validate_node(node, line_number=line_number)
            nodes.append(node)
            continue

        if keyword == "EDGE":
            if len(parts) < 3:
                raise Glitch3DError(
                    f"line {line_number}: EDGE requires source and target"
                )
            values = _parse_assignments(parts[3:], line_number=line_number)
            if set(values) != {"OP"}:
                raise Glitch3DError(
                    f"line {line_number}: EDGE requires exactly OP=<operator>"
                )
            edges.append(
                Glitch3DEdge(
                    source=parts[1],
                    target=parts[2],
                    operator=values["OP"].upper(),
                )
            )
            continue

        if keyword == "BOUNDARY":
            if len(parts) < 2:
                raise Glitch3DError(
                    f"line {line_number}: BOUNDARY requires an identifier"
                )
            boundary_id = parts[1]
            if not _BOUNDARY_ID_RE.fullmatch(boundary_id):
                raise Glitch3DError(
                    f"line {line_number}: invalid BOUNDARY identifier"
                )
            values = _parse_assignments(parts[2:], line_number=line_number)
            if set(values) != {"Z", "MODE"}:
                raise Glitch3DError(
                    f"line {line_number}: BOUNDARY requires Z and MODE"
                )
            mode = values["MODE"].upper()
            if mode not in _BOUNDARY_MODES:
                raise Glitch3DError(
                    f"line {line_number}: unsupported boundary MODE={mode}"
                )
            boundaries.append(
                Glitch3DBoundary(
                    id=boundary_id,
                    z=_parse_int(values["Z"], field="Z", line_number=line_number),
                    mode=mode,
                )
            )
            continue

        if keyword == "INVARIANT":
            invariant = line[len("INVARIANT") :].strip()
            if not invariant:
                raise Glitch3DError(
                    f"line {line_number}: INVARIANT requires an expression"
                )
            invariants.append(invariant)
            continue

        raise Glitch3DError(f"line {line_number}: unknown keyword {keyword!r}")

    if program_id is None:
        raise Glitch3DError("PROGRAM declaration is required")
    if not nodes:
        raise Glitch3DError("at least one NODE is required")
    if not invariants:
        raise Glitch3DError("at least one INVARIANT is required")
    if len(set(invariants)) != len(invariants):
        raise Glitch3DError("INVARIANT declarations must be unique")

    program = Glitch3DProgram(
        program_id=program_id,
        nodes=tuple(nodes),
        edges=tuple(edges),
        boundaries=tuple(boundaries),
        invariants=tuple(invariants),
    )
    _validate_graph(program.nodes, program.edges, program.boundaries)
    return program


def load_glitch3d(path: Path | str) -> Glitch3DProgram:
    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise Glitch3DError(f"cannot read GLITCH-3D source {source}: {exc}") from exc
    return parse_glitch3d(text)


def render_spatial_summary(program: Glitch3DProgram) -> str:
    """Render a deterministic human-readable layer summary."""
    lines = [
        "GLITCH://3D_RUNTIME",
        f"PROGRAM://{program.program_id}",
        "",
    ]
    by_layer: dict[int, list[Glitch3DNode]] = {z: [] for z in _LAYER_KIND}
    for node in program.nodes:
        by_layer[node.z].append(node)

    for z, kind in sorted(_LAYER_KIND.items()):
        lines.append(f"Z={z} {kind}")
        values = sorted(by_layer[z], key=lambda node: (node.y, node.x, node.id))
        if not values:
            lines.append("  ∅")
        for node in values:
            distortion = "" if node.distortion == "NONE" else f" [{node.distortion}]"
            lines.append(
                f"  ({node.x:+d},{node.y:+d},{node.z}) "
                f"{node.id} :: {node.state}{distortion}"
            )
    lines.append("")
    lines.append("EDGES")
    for edge in program.edges:
        lines.append(f"  {edge.source} --{edge.operator}--> {edge.target}")
    lines.append("")
    lines.append(f"SHA256://{program.sha256()}")
    return "\n".join(lines) + "\n"
