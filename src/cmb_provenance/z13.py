"""Reference parser for the experimental CMB-Z13 symbolic notation.

The parser is intentionally narrow. It validates the authored CMB-Z13 mapping
and produces a deterministic AST. It does not classify people, infer personality
from zodiac symbols, or give machines final authority over consequential action.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

Z13_SPEC_VERSION: Final[str] = "1.1.0"
Z13_AST_SCHEMA_VERSION: Final[str] = "cmb.z13.ast.v1"

_STATEMENT_RE = re.compile(
    r"""^\s*
    (?P<glyph>[♑♒♓♈♉♊♋♌♍♎♏⛎♐])
    \s*::\s*
    (?P<language>[A-Za-z][A-Za-z0-9+_ -]*)
    \s*->\s*
    (?P<operation>[A-Za-z_][A-Za-z0-9_]*)
    \s*\[\s*(?P<target>[^\]\n]+?)\s*\]
    \s*=>\s*
    (?P<result>[A-Za-z_][A-Za-z0-9_.:()\-]*)
    \s*;\s*$""",
    re.VERBOSE,
)


class Z13Error(ValueError):
    """Base error for CMB-Z13 parsing and conformance failures."""


@dataclass(frozen=True, slots=True)
class Z13Lens:
    sign: str
    glyph: str
    language: str
    language_aliases: tuple[str, ...]
    canonical_operator: str
    canonical_function: str
    guardian_name: str
    guardian_team: str
    allowed_operations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Z13Statement:
    glyph: str
    sign: str
    language: str
    canonical_operator: str
    guardian_name: str
    guardian_team: str
    operation: str
    target: str
    result: str
    authority: str = "HUMAN_FINAL"

    def to_dict(self) -> dict[str, str]:
        return {
            "schema_version": Z13_AST_SCHEMA_VERSION,
            "spec_version": Z13_SPEC_VERSION,
            "glyph": self.glyph,
            "sign": self.sign,
            "language": self.language,
            "canonical_operator": self.canonical_operator,
            "guardian_name": self.guardian_name,
            "guardian_team": self.guardian_team,
            "operation": self.operation,
            "target": self.target,
            "result": self.result,
            "authority": self.authority,
        }


_CANONICAL_LENSES: Final[tuple[Z13Lens, ...]] = (
    Z13Lens("Capricorn", "♑", "C", ("C",), "FOUNDATION", "BUILD", "The Foundation Warden", "EARTH", ("BUILD",)),
    Z13Lens("Aquarius", "♒", "Rust", ("RUST",), "FUTURE", "INNOVATE", "The Future Architect", "AIR", ("INNOVATE",)),
    Z13Lens("Pisces", "♓", "Haskell", ("HASKELL",), "MEANING", "ABSTRACT", "The Dream Keeper", "WATER", ("ABSTRACT",)),
    Z13Lens("Aries", "♈", "C++", ("C++", "CPP"), "ACTION", "INITIATE", "The Action Engine", "FIRE", ("INITIATE", "REQUEST", "REQUEST_ACTION")),
    Z13Lens("Taurus", "♉", "Java", ("JAVA",), "STABILITY", "PRESERVE", "The Iron Covenant", "EARTH", ("PRESERVE",)),
    Z13Lens("Gemini", "♊", "TypeScript", ("TYPESCRIPT", "TS"), "BILINGUALISM", "TRANSLATE", "The Twin Translator", "AIR", ("TRANSLATE",)),
    Z13Lens("Cancer", "♋", "Python", ("PYTHON",), "CONTEXT", "HUMANIZE", "The Context Shield", "WATER", ("HUMANIZE", "ADD_CONTEXT")),
    Z13Lens("Leo", "♌", "Swift", ("SWIFT",), "EXPRESSION", "AUTHOR", "The Author Crown", "FIRE", ("AUTHOR",)),
    Z13Lens("Virgo", "♍", "Go", ("GO",), "PRECISION", "VERIFY", "The Verification Sentinel", "EARTH", ("VERIFY",)),
    Z13Lens("Libra", "♎", "Kotlin", ("KOTLIN",), "BALANCE", "MEDIATE", "The Balance Gate", "AIR", ("MEDIATE", "AUDIT")),
    Z13Lens("Scorpio", "♏", "Prolog", ("PROLOG",), "INFERENCE", "INVESTIGATE", "The Forensic Oracle", "WATER", ("INVESTIGATE", "INFER")),
    Z13Lens("Ophiuchus", "⛎", "Common Lisp", ("LISP", "COMMON_LISP", "COMMONLISP"), "METACOGNITION", "REWRITE", "The Override Architect", "OPHIUCHUS", ("REWRITE", "INSPECT", "INSPECT_RULE")),
    Z13Lens("Sagittarius", "♐", "Julia", ("JULIA",), "EXPLORATION", "DISCOVER", "The Horizon Scout", "FIRE", ("DISCOVER", "EXPLORE")),
)

LENSES_BY_GLYPH: Final[dict[str, Z13Lens]] = {lens.glyph: lens for lens in _CANONICAL_LENSES}


def canonical_lenses() -> tuple[Z13Lens, ...]:
    """Return the immutable canonical CMB-Z13 lens table."""
    return _CANONICAL_LENSES


def _normalize_language(value: str) -> str:
    return value.strip().upper().replace("-", "_").replace(" ", "_")


def parse_z13_statement(source: str) -> Z13Statement:
    """Parse and strictly validate one CMB-Z13 statement."""

    if not isinstance(source, str) or not source.strip():
        raise Z13Error("CMB-Z13 source must be a non-empty string.")

    match = _STATEMENT_RE.fullmatch(source)
    if match is None:
        raise Z13Error(
            "Invalid CMB-Z13 syntax. Expected: "
            "GLYPH::LANGUAGE -> OPERATION[target] => result;"
        )

    glyph = match.group("glyph")
    lens = LENSES_BY_GLYPH[glyph]
    language_token = _normalize_language(match.group("language"))
    normalized_aliases = {_normalize_language(alias) for alias in lens.language_aliases}
    if language_token not in normalized_aliases:
        raise Z13Error(
            f"{glyph} is canonically mapped to {lens.language}; "
            f"received {match.group('language').strip()!r}."
        )

    operation = match.group("operation").upper()
    if operation not in lens.allowed_operations:
        allowed = ", ".join(lens.allowed_operations)
        raise Z13Error(
            f"{lens.sign}/{lens.language} does not define operation {operation!r}; "
            f"allowed: {allowed}."
        )

    target = match.group("target").strip()
    result = match.group("result").strip()
    if not target:
        raise Z13Error("CMB-Z13 target cannot be empty.")

    return Z13Statement(
        glyph=glyph,
        sign=lens.sign,
        language=lens.language,
        canonical_operator=lens.canonical_operator,
        guardian_name=lens.guardian_name,
        guardian_team=lens.guardian_team,
        operation=operation,
        target=target,
        result=result,
    )


def explain_z13_statement(statement: Z13Statement) -> str:
    """Return a concise human explanation of a parsed statement."""
    return (
        f"{statement.sign} / {statement.language} / {statement.guardian_name}: "
        f"{statement.operation} targets {statement.target!r} and yields "
        f"{statement.result!r}. Canonical lens: "
        f"{statement.canonical_operator}. Human authority remains final."
    )
