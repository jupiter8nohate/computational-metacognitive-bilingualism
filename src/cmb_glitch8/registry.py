"""Registry-driven core for the experimental CMB-G8 / GLITCH-8 language."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any, Final

GLITCH8_SCHEMA_VERSION: Final[str] = "glitch8.glyph-registry.v1"
_ALLOWED_STATUS: Final[set[str]] = {"experimental", "proposed", "canonical", "deprecated", "retired"}
_ALLOWED_RUNTIMES: Final[set[str]] = {"PY", "RS", "GO", "TS", "PL", "HS", "CL", "C", "G8"}
_STATEMENT_RE: Final[re.Pattern[str]] = re.compile(
    r"^\[(?P<runtime>[A-Z0-9]+)\]\s+"
    r"(?P<claim>.+?)\s*::\s*(?P<state>[^:]+?)\s*::\s*(?P<authority>.+?)\s*$"
)


class GlyphRegistryError(ValueError):
    """Raised when GLITCH-8 registry or syntax validation fails."""


@dataclass(frozen=True, slots=True)
class Glitch8Statement:
    glyph: str
    glyph_id: str
    runtime: str
    claim: str
    state: str
    authority: str

    def to_dict(self) -> dict[str, str]:
        return {
            "glyph": self.glyph,
            "glyph_id": self.glyph_id,
            "runtime": self.runtime,
            "claim": self.claim,
            "state": self.state,
            "authority": self.authority,
        }


def _package_registry_path() -> Path:
    return Path(str(files("cmb_glitch8").joinpath("glyphs.v1.json")))


def _repo_registry_path() -> Path | None:
    candidate = Path.cwd() / "src" / "cmb_glitch8" / "glyphs.v1.json"
    return candidate if candidate.is_file() else None


def canonical_registry_path(*, writable: bool = False) -> Path:
    if writable:
        path = _repo_registry_path()
        if path is None:
            raise GlyphRegistryError(
                "No writable GLITCH-8 source registry found. Run inside the repository "
                "or pass --registry PATH."
            )
        return path
    return _repo_registry_path() or _package_registry_path()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GlyphRegistryError(f"Cannot read registry {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GlyphRegistryError("Registry root must be a JSON object.")
    return value


def _required_string(entry: dict[str, Any], field: str) -> str:
    value = entry.get(field)
    if not isinstance(value, str) or not value.strip():
        raise GlyphRegistryError(f"Field {field!r} must be a non-empty string.")
    return value.strip()


def validate_glyph(entry: dict[str, Any], categories: set[str]) -> None:
    if not isinstance(entry, dict):
        raise GlyphRegistryError("Each glyph entry must be an object.")

    for field in (
        "id", "glyph", "name", "semantic_key", "version", "status", "definition",
        "cmb_invariant", "human_semantics", "machine_semantics", "example",
        "created_at", "author",
    ):
        _required_string(entry, field)

    if entry["status"] not in _ALLOWED_STATUS:
        raise GlyphRegistryError(f"Invalid glyph status: {entry['status']!r}")

    aliases = entry.get("aliases", [])
    if not isinstance(aliases, list) or any(
        not isinstance(alias, str) or not alias.strip() for alias in aliases
    ):
        raise GlyphRegistryError(f"Glyph {entry['id']!r} aliases must be strings.")

    entry_categories = entry.get("categories")
    if not isinstance(entry_categories, list) or not entry_categories:
        raise GlyphRegistryError(f"Glyph {entry['id']!r} requires categories.")

    unknown = {value for value in entry_categories if value not in categories}
    if unknown:
        raise GlyphRegistryError(
            f"Glyph {entry['id']!r} uses unknown categories: {', '.join(sorted(unknown))}"
        )

    if not isinstance(entry.get("runtime_behavior"), dict) or not entry["runtime_behavior"]:
        raise GlyphRegistryError(f"Glyph {entry['id']!r} requires runtime_behavior.")


def validate_registry(data: dict[str, Any]) -> None:
    if data.get("schema_version") != GLITCH8_SCHEMA_VERSION:
        raise GlyphRegistryError(
            f"Expected {GLITCH8_SCHEMA_VERSION!r}; got {data.get('schema_version')!r}."
        )

    for field in ("language", "language_version", "updated_at", "author"):
        _required_string(data, field)

    categories_raw = data.get("categories")
    if not isinstance(categories_raw, list) or not categories_raw:
        raise GlyphRegistryError("Registry categories must be a non-empty list.")

    categories = set(categories_raw)
    if len(categories) != len(categories_raw):
        raise GlyphRegistryError("Registry categories must be unique.")

    glyphs = data.get("glyphs")
    if not isinstance(glyphs, list) or not glyphs:
        raise GlyphRegistryError("Registry glyphs must be a non-empty list.")

    seen_ids: set[str] = set()
    seen_tokens: set[str] = set()
    seen_semantics: set[str] = set()

    for entry in glyphs:
        validate_glyph(entry, categories)
        glyph_id = entry["id"]
        semantic_key = entry["semantic_key"]

        if glyph_id in seen_ids:
            raise GlyphRegistryError(f"Duplicate glyph id: {glyph_id}")
        seen_ids.add(glyph_id)

        if semantic_key in seen_semantics:
            raise GlyphRegistryError(
                f"Semantic collision: {semantic_key!r}. Use an alias or a distinct semantic_key."
            )
        seen_semantics.add(semantic_key)

        for token in [entry["glyph"], *entry.get("aliases", [])]:
            if token in seen_tokens:
                raise GlyphRegistryError(f"Duplicate glyph or alias token: {token!r}")
            seen_tokens.add(token)


def _bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise GlyphRegistryError("language_version must use MAJOR.MINOR.PATCH.")
    major, minor, patch = map(int, parts)
    return f"{major}.{minor}.{patch + 1}"


class GlyphRegistry:
    """Validated GLITCH-8 registry with deterministic lookup and rendering."""

    def __init__(self, data: dict[str, Any], *, source: Path | None = None) -> None:
        validate_registry(data)
        self.data = data
        self.source = source
        self._by_id = {entry["id"]: entry for entry in data["glyphs"]}
        self._by_token: dict[str, dict[str, Any]] = {}

        for entry in data["glyphs"]:
            self._by_token[entry["glyph"]] = entry
            for alias in entry.get("aliases", []):
                self._by_token[alias] = entry

    @property
    def language_version(self) -> str:
        return str(self.data["language_version"])

    def get(self, token: str) -> dict[str, Any]:
        try:
            return self._by_token[token]
        except KeyError as exc:
            raise GlyphRegistryError(f"Unknown GLITCH-8 glyph: {token!r}") from exc

    def list(
        self,
        *,
        category: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        values = list(self.data["glyphs"])
        if category is not None:
            values = [entry for entry in values if category in entry["categories"]]
        if status is not None:
            values = [entry for entry in values if entry["status"] == status]
        return sorted(values, key=lambda entry: entry["id"])

    def match_prefix(self, source: str) -> tuple[str, dict[str, Any]]:
        for token in sorted(self._by_token, key=len, reverse=True):
            if (
                source.startswith(token)
                and len(source) > len(token)
                and source[len(token)].isspace()
            ):
                return token, self._by_token[token]
        raise GlyphRegistryError(
            "Statement does not begin with a registered GLITCH-8 glyph."
        )

    def add(self, entry: dict[str, Any]) -> None:
        validate_glyph(entry, set(self.data["categories"]))
        candidate = json.loads(json.dumps(self.data, ensure_ascii=False))
        candidate["glyphs"].append(entry)
        candidate["language_version"] = _bump_patch(candidate["language_version"])
        candidate["updated_at"] = entry["created_at"]
        candidate["glyphs"] = sorted(
            candidate["glyphs"], key=lambda value: value["id"]
        )
        validate_registry(candidate)
        self.__init__(candidate, source=self.source)

    def write(self, path: Path | None = None) -> Path:
        destination = path or self.source
        if destination is None:
            raise GlyphRegistryError("No registry destination was supplied.")

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.source = destination
        return destination

    def render_reference(self) -> str:
        lines = [
            "# GLITCH-8 Glyph Reference",
            "",
            f"Language: {self.data['language']}",
            f"Registry version: {self.language_version}",
            f"Updated: {self.data['updated_at']}",
            "",
            "Generated from the canonical GLITCH-8 registry. Edit the registry, not this file.",
            "",
            "## Core boundary",
            "",
            "~~~text",
            *self.data.get("principles", []),
            "~~~",
            "",
        ]

        for entry in self.list():
            aliases = ", ".join(entry.get("aliases", [])) or "none"
            lines.extend([
                f"## {entry['glyph']} // {entry['name']}",
                "",
                f"ID: {entry['id']}",
                f"Status: {entry['status']}",
                f"Version: {entry['version']}",
                f"Categories: {', '.join(entry['categories'])}",
                f"Aliases: {aliases}",
                f"Semantic key: {entry['semantic_key']}",
                f"CMB invariant: {entry['cmb_invariant']}",
                "",
                entry["definition"],
                "",
                f"Human semantics: {entry['human_semantics']}",
                "",
                f"Machine semantics: {entry['machine_semantics']}",
                "",
                "~~~text",
                entry["example"],
                "~~~",
                "",
            ])

        return "\n".join(lines).rstrip() + "\n"


def load_registry(
    path: Path | str | None = None,
    *,
    writable: bool = False,
) -> GlyphRegistry:
    source = Path(path) if path is not None else canonical_registry_path(writable=writable)
    return GlyphRegistry(_read_json(source), source=source)


def load_entry(path: Path) -> dict[str, Any]:
    value = _read_json(path)
    if "glyph" not in value:
        raise GlyphRegistryError(
            f"{path} must contain one glyph definition object."
        )
    return value


def parse_statement(
    source: str,
    registry: GlyphRegistry | None = None,
) -> Glitch8Statement:
    if not isinstance(source, str) or not source.strip():
        raise GlyphRegistryError("GLITCH-8 statement must be a non-empty string.")

    active = registry or load_registry()
    text_value = source.strip()
    token, entry = active.match_prefix(text_value)
    remainder = text_value[len(token):].lstrip()
    match = _STATEMENT_RE.fullmatch(remainder)

    if match is None:
        raise GlyphRegistryError(
            "Invalid syntax. Expected: GLYPH [RUNTIME] CLAIM :: STATE :: AUTHORITY"
        )

    runtime = match.group("runtime")
    if runtime not in _ALLOWED_RUNTIMES:
        raise GlyphRegistryError(
            f"Unknown runtime {runtime!r}; expected one of "
            f"{', '.join(sorted(_ALLOWED_RUNTIMES))}."
        )

    return Glitch8Statement(
        glyph=entry["glyph"],
        glyph_id=entry["id"],
        runtime=runtime,
        claim=match.group("claim").strip(),
        state=match.group("state").strip(),
        authority=match.group("authority").strip(),
    )
