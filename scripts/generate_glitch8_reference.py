"""Generate the GLITCH-8 glyph reference from the canonical registry."""

from __future__ import annotations

from pathlib import Path

from cmb_glitch8.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "books" / "GLITCH8_GLYPH_REFERENCE.md"


def main() -> int:
    registry = load_registry(ROOT / "src" / "cmb_glitch8" / "glyphs.v1.json")
    OUTPUT.write_text(registry.render_reference(), encoding="utf-8")
    print(f"GLITCH-8 glyph reference -> {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
