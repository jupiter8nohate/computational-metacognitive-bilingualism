"""Generate GLITCH-8 public artifacts from the canonical registry."""

from __future__ import annotations

import shutil
from pathlib import Path

from cmb_glitch8.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "cmb_glitch8" / "glyphs.v1.json"
REFERENCE = ROOT / "books" / "GLITCH8_GLYPH_REFERENCE.md"
PUBLIC_MIRROR = ROOT / "library" / "glitch8.glyphs.v1.json"


def main() -> int:
    registry = load_registry(REGISTRY)
    REFERENCE.write_text(registry.render_reference(), encoding="utf-8")
    shutil.copyfile(REGISTRY, PUBLIC_MIRROR)
    print(f"GLITCH-8 glyph reference -> {REFERENCE}")
    print(f"GLITCH-8 public registry -> {PUBLIC_MIRROR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
