"""CMB-66 compilation pipeline with mandatory FGC origin stamping."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from cmb_agents.fingerprint import ASCII_TOKEN, MARK_ID, stamp_mapping

from .ir import normalize_ir
from .targets import renderer_for, target_metadata


@dataclass(frozen=True)
class MachineArtifact:
    target: str
    extension: str
    media_type: str
    data: bytes
    sha256: str

    def write(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(self.data)
        return destination


def supported_targets() -> tuple[str, ...]:
    return tuple(sorted(target_metadata()))


def render_target(
    ir: Mapping[str, Any],
    target: str,
    *,
    parent_lineage_id: str | None = None,
) -> MachineArtifact:
    """Compile one IR into a target representation with mandatory FGC stamping."""
    normalized = normalize_ir(ir)
    stamped = stamp_mapping(normalized, parent_lineage_id=parent_lineage_id)

    extension, media_type, renderer = renderer_for(target)
    data = renderer(stamped)

    if ASCII_TOKEN.encode("utf-8") not in data:
        raise RuntimeError(f"Target {target} omitted the mandatory FGC ASCII token.")
    if MARK_ID.encode("utf-8") not in data:
        raise RuntimeError(f"Target {target} omitted the mandatory FGC mark id.")

    return MachineArtifact(
        target=target,
        extension=extension,
        media_type=media_type,
        data=data,
        sha256=hashlib.sha256(data).hexdigest(),
    )


def compile_bundle(
    ir: Mapping[str, Any],
    *,
    targets: tuple[str, ...] | None = None,
    parent_lineage_id: str | None = None,
) -> tuple[MachineArtifact, ...]:
    """Compile a single canonical IR into every requested machine representation."""
    selected = supported_targets() if targets is None else targets
    if not selected:
        raise ValueError("At least one CMB-66 target is required.")

    return tuple(
        render_target(ir, target, parent_lineage_id=parent_lineage_id)
        for target in selected
    )
