"""Reference parser for the CMB-Z13 symbolic notation."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Final, Iterable

Z13_AST_SCHEMA_VERSION: Final[str] = "cmb.z13.ast.v1"
Z13_REGISTRY_VERSION: Final[str] = "1.1.0"


class Z13Error(ValueError):
    """Base error for CMB-Z13 parsing and validation."""


class Z13ParseError(Z13Error):
    """Raised when a statement does not match CMB-Z13 syntax."""


class Z13ValidationError(Z13Error):
    """Raised when syntax is valid but canonical mappings do not match."""


@dataclass(frozen=True)
class LensDefinition:
    sign: str
    glyph: str
    language: str
    language_aliases: tuple[str, ...]
    operator: str
    function: str
    guardian_mode: str


@dataclass(frozen=True)
class Z13Statement:
    glyph: str
    sign: str
    language: str
    operator: str
    function: str
    guardian_mode: str
    operation: str
    target: str
    result: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": Z13_AST_SCHEMA_VERSION,
            "protocol": "CMB-Z13",
            "registry_version": Z13_REGISTRY_VERSION,
            **asdict(self),
            "human_authority_final": True,
        }


_LENSES: Final[tuple[LensDefinition, ...]] = (
    LensDefinition("Capricorn", "♑", "C", ("C",), "FOUNDATION", "BUILD", "The Foundation Warden"),
    LensDefinition("Aquarius", "♒", "Rust", ("RUST",), "FUTURE", "INNOVATE", "The Future Architect"),
    LensDefinition("Pisces", "♓", "Haskell", ("HASKELL",), "MEANING", "ABSTRACT", "The Dream Keeper"),
    LensDefinition("Aries", "♈", "C++", ("C++", "CPP"), "ACTION", "INITIATE", "The Action Engine"),
    LensDefinition("Taurus", "♉", "Java", ("JAVA",), "STABILITY", "PRESERVE", "The Iron Covenant"),
    LensDefinition("Gemini", "♊", "TypeScript", ("TYPESCRIPT", "TS"), "BILINGUALISM", "TRANSLATE", "The Twin Translator"),
    LensDefinition("Cancer", "♋", "Python", ("PYTHON", "PY"), "CONTEXT", "HUMANIZE", "The Context Shield"),
    LensDefinition("Leo", "♌", "Swift", ("SWIFT",), "EXPRESSION", "AUTHOR", "The Author Crown"),
    LensDefinition("Virgo", "♍", "Go", ("GO", "GOLANG"), "PRECISION", "VERIFY", "The Verification Sentinel"),
    LensDefinition("Libra", "♎", "Kotlin", ("KOTLIN",), "BALANCE", "MEDIATE", "The Balance Gate"),
    LensDefinition("Scorpio", "♏", "Prolog", ("PROLOG",), "INFERENCE", "INVESTIGATE", "The Forensic Oracle"),
    LensDefinition("Ophiuchus", "⛎", "Common Lisp", ("LISP", "COMMONLISP"), "METACOGNITION", "REWRITE", "The Override Architect"),
    LensDefinition("Sagittarius", "♐", "Julia", ("JULIA",), "EXPLORATION", "DISCOVER", "The Horizon Scout"),
)

_BY_GLYPH: Final[dict[str, LensDefinition]] = {lens.glyph: lens for lens in _LENSES}

_STATEMENT_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*"
    r"(?P<glyph>[♑♒♓♈♉♊♋♌♍♎♏⛎♐])"
    r"\s*::\s*"
    r"(?P<language>[A-Za-z0-9+ _-]+?)"
    r"\s*->\s*"
    r"(?P<operation>[A-Za-z_][A-Za-z0-9_]*)"
    r"\[(?P<target>[^\]\r\n]+)\]"
    r"\s*=>\s*"
    r"(?P<result>[^;\r\n]+)"
    r";\s*$"
)


def _normalize_language(value: str) -> str:
    return re.sub(r"[\s_-]+", "", value).upper()


def iter_lenses() -> Iterable[LensDefinition]:
    """Return the canonical runtime lens definitions."""
    return tuple(_LENSES)


def parse_statement(text: str) -> Z13Statement:
    """Parse and validate one native CMB-Z13 statement."""

    if not isinstance(text, str) or not text.strip():
        raise Z13ParseError("CMB-Z13 statement must be a non-empty string.")

    match = _STATEMENT_RE.fullmatch(text)
    if match is None:
        raise Z13ParseError(
            "Expected: GLYPH::LANGUAGE -> OPERATION[target] => RESULT;"
        )

    glyph = match.group("glyph")
    lens = _BY_GLYPH[glyph]
    supplied_language = _normalize_language(match.group("language"))
    allowed = {_normalize_language(alias) for alias in lens.language_aliases}
    allowed.add(_normalize_language(lens.language))

    if supplied_language not in allowed:
        raise Z13ValidationError(
            f"{glyph} {lens.sign} requires {lens.language}; "
            f"received {match.group('language').strip()}."
        )

    target = match.group("target").strip()
    result = match.group("result").strip()
    if not target:
        raise Z13ParseError("Target cannot be empty.")
    if not result:
        raise Z13ParseError("Result cannot be empty.")

    return Z13Statement(
        glyph=glyph,
        sign=lens.sign,
        language=lens.language,
        operator=lens.operator,
        function=lens.function,
        guardian_mode=lens.guardian_mode,
        operation=match.group("operation").upper(),
        target=target,
        result=result,
    )


def explain_statement(statement: Z13Statement) -> str:
    """Return a compact human-readable explanation."""

    return (
        f"{statement.glyph} {statement.sign} | {statement.language} | "
        f"{statement.operator} | {statement.guardian_mode}\n"
        f"operation={statement.operation}\n"
        f"target={statement.target}\n"
        f"result={statement.result}\n"
        "boundary=HUMAN_AGENCY > MACHINE_AUTHORITY"
    )
