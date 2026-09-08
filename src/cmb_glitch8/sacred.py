"""Machine-readable registry for D.N.A. BIBLE://SACRED_ERROR_CODES."""

from __future__ import annotations

import json
import re
from importlib.resources import files
from pathlib import Path
from typing import Any, Final

SACRED_ERROR_SCHEMA_VERSION: Final[str] = "cmb.dna-sacred-error-codes.v1"
_ALLOWED_STATUS: Final[set[str]] = {
    "experimental",
    "proposed",
    "canonical",
    "deprecated",
    "retired",
}
_SEC_ID_RE: Final[re.Pattern[str]] = re.compile(r"^SEC-\d{4}$")
_PRINCIPLE_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9_]+$")
_ALLOWED_EPISTEMIC_TYPES: Final[set[str]] = {
    "theological_interpretation",
    "philosophical_principle",
    "code_poetry",
    "textual_reference",
}
_ALLOWED_MACHINE_PERMISSIONS: Final[set[str]] = {
    "translate",
    "explain",
    "compare",
    "summarize",
    "trace_source",
}
_TRANSLATION_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "plain_language",
    "principle",
    "epistemic_type",
    "machine_permissions",
    "machine_boundaries",
)


class SacredErrorRegistryError(ValueError):
    """Raised when Sacred Error registry validation fails."""


def _package_registry_path() -> Path:
    return Path(str(files("cmb_glitch8").joinpath("sacred_errors.v1.json")))


def _repo_registry_path() -> Path | None:
    candidate = Path.cwd() / "src" / "cmb_glitch8" / "sacred_errors.v1.json"
    return candidate if candidate.is_file() else None


def canonical_sacred_registry_path() -> Path:
    return _repo_registry_path() or _package_registry_path()


def _required_string(value: dict[str, Any], field: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or not item.strip():
        raise SacredErrorRegistryError(f"Field {field!r} must be a non-empty string.")
    return item.strip()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SacredErrorRegistryError(f"Cannot read Sacred Error registry {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SacredErrorRegistryError("Sacred Error registry root must be a JSON object.")
    return value


def validate_sacred_registry(data: dict[str, Any]) -> None:
    if data.get("schema_version") != SACRED_ERROR_SCHEMA_VERSION:
        raise SacredErrorRegistryError(
            f"Expected {SACRED_ERROR_SCHEMA_VERSION!r}; got {data.get('schema_version')!r}."
        )

    for field in ("registry_version", "framework", "work", "author", "updated_at", "status"):
        _required_string(data, field)

    if data["status"] not in _ALLOWED_STATUS:
        raise SacredErrorRegistryError(f"Invalid registry status: {data['status']!r}")

    boundaries = data.get("boundaries")
    if (
        not isinstance(boundaries, list)
        or not boundaries
        or any(not isinstance(item, str) or not item.strip() for item in boundaries)
    ):
        raise SacredErrorRegistryError("Registry boundaries must be a non-empty string list.")
    if len(boundaries) != len(set(boundaries)):
        raise SacredErrorRegistryError("Registry boundaries must be unique.")

    translation = data.get("translation_conformance")
    if not isinstance(translation, dict):
        raise SacredErrorRegistryError("translation_conformance must be an object.")
    if _required_string(translation, "set") != "sacred_translation_v1":
        raise SacredErrorRegistryError("Unsupported Sacred Translation conformance set.")

    conformance_ids = translation.get("entry_ids")
    if (
        not isinstance(conformance_ids, list)
        or not conformance_ids
        or any(not isinstance(item, str) or not _SEC_ID_RE.fullmatch(item) for item in conformance_ids)
    ):
        raise SacredErrorRegistryError(
            "translation_conformance.entry_ids must be a non-empty SEC id list."
        )
    if len(conformance_ids) != len(set(conformance_ids)):
        raise SacredErrorRegistryError("translation_conformance.entry_ids must be unique.")

    required_fields = translation.get("required_fields")
    if (
        not isinstance(required_fields, list)
        or set(required_fields) != set(_TRANSLATION_REQUIRED_FIELDS)
        or len(required_fields) != len(_TRANSLATION_REQUIRED_FIELDS)
    ):
        raise SacredErrorRegistryError(
            "translation_conformance.required_fields must match the Sacred Translation contract."
        )

    conformance_id_set = set(conformance_ids)

    errors = data.get("errors")
    if not isinstance(errors, list) or not errors:
        raise SacredErrorRegistryError("Registry errors must be a non-empty list.")

    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for entry in errors:
        if not isinstance(entry, dict):
            raise SacredErrorRegistryError("Each Sacred Error must be an object.")

        error_id = _required_string(entry, "id")
        name = _required_string(entry, "name")
        _required_string(entry, "theme")
        _required_string(entry, "trigger")
        _required_string(entry, "recovery")
        _required_string(entry, "interpretation")
        status = _required_string(entry, "status")

        if not _SEC_ID_RE.fullmatch(error_id):
            raise SacredErrorRegistryError(f"Invalid Sacred Error id: {error_id!r}")
        if error_id in seen_ids:
            raise SacredErrorRegistryError(f"Duplicate Sacred Error id: {error_id}")
        if name in seen_names:
            raise SacredErrorRegistryError(f"Duplicate Sacred Error name: {name}")
        if status not in _ALLOWED_STATUS:
            raise SacredErrorRegistryError(f"Invalid Sacred Error status: {status!r}")

        source = entry.get("source")
        if not isinstance(source, dict):
            raise SacredErrorRegistryError(f"{error_id} source must be an object.")
        _required_string(source, "book")
        _required_string(source, "verses")
        _required_string(source, "mode")
        chapter = source.get("chapter")
        if not isinstance(chapter, int) or isinstance(chapter, bool) or chapter < 1:
            raise SacredErrorRegistryError(f"{error_id} source chapter must be a positive integer.")

        invariants = entry.get("invariants")
        if (
            not isinstance(invariants, list)
            or not invariants
            or any(not isinstance(item, str) or not item.strip() for item in invariants)
        ):
            raise SacredErrorRegistryError(f"{error_id} invariants must be a non-empty string list.")
        if len(invariants) != len(set(invariants)):
            raise SacredErrorRegistryError(f"{error_id} invariants must be unique.")

        if error_id in conformance_id_set:
            plain_language = _required_string(entry, "plain_language")
            principle = _required_string(entry, "principle")
            epistemic_type = _required_string(entry, "epistemic_type")
            if not _PRINCIPLE_RE.fullmatch(principle):
                raise SacredErrorRegistryError(
                    f"{error_id} principle must use lowercase snake_case."
                )
            if epistemic_type not in _ALLOWED_EPISTEMIC_TYPES:
                raise SacredErrorRegistryError(
                    f"{error_id} has invalid epistemic_type: {epistemic_type!r}"
                )
            if not plain_language:
                raise SacredErrorRegistryError(f"{error_id} plain_language must not be empty.")

            permissions = entry.get("machine_permissions")
            if (
                not isinstance(permissions, list)
                or not permissions
                or any(item not in _ALLOWED_MACHINE_PERMISSIONS for item in permissions)
            ):
                raise SacredErrorRegistryError(
                    f"{error_id} machine_permissions contains unsupported values."
                )
            if len(permissions) != len(set(permissions)):
                raise SacredErrorRegistryError(
                    f"{error_id} machine_permissions must be unique."
                )

            machine_boundaries = entry.get("machine_boundaries")
            if (
                not isinstance(machine_boundaries, list)
                or not machine_boundaries
                or any(
                    not isinstance(item, str) or not _PRINCIPLE_RE.fullmatch(item)
                    for item in machine_boundaries
                )
            ):
                raise SacredErrorRegistryError(
                    f"{error_id} machine_boundaries must use lowercase snake_case."
                )
            if len(machine_boundaries) != len(set(machine_boundaries)):
                raise SacredErrorRegistryError(
                    f"{error_id} machine_boundaries must be unique."
                )

        seen_ids.add(error_id)
        seen_names.add(name)

    missing_conformance_ids = conformance_id_set - seen_ids
    if missing_conformance_ids:
        missing = ", ".join(sorted(missing_conformance_ids))
        raise SacredErrorRegistryError(
            f"Sacred Translation conformance entries are missing: {missing}"
        )


class SacredErrorRegistry:
    """Validated Sacred Error registry with deterministic lookup."""

    def __init__(self, data: dict[str, Any], *, source: Path | None = None) -> None:
        validate_sacred_registry(data)
        self.data = data
        self.source = source
        self._by_id = {entry["id"]: entry for entry in data["errors"]}
        self._by_name = {entry["name"]: entry for entry in data["errors"]}

    def get(self, token: str) -> dict[str, Any]:
        key = token.strip().upper()
        entry = self._by_id.get(key) or self._by_name.get(key)
        if entry is None:
            raise SacredErrorRegistryError(f"Unknown Sacred Error: {token!r}")
        return entry

    def list(
        self,
        *,
        book: str | None = None,
        theme: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        values = list(self.data["errors"])
        if book is not None:
            target = book.casefold()
            values = [entry for entry in values if entry["source"]["book"].casefold() == target]
        if theme is not None:
            values = [entry for entry in values if entry["theme"] == theme]
        if status is not None:
            values = [entry for entry in values if entry["status"] == status]
        return sorted(values, key=lambda entry: entry["id"])

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search Sacred Errors by biblical reference, CMB invariant, or human concept."""
        raw = query.strip()
        if not raw:
            raise SacredErrorRegistryError("Sacred Error search query must not be empty.")

        target = raw.casefold()
        normalized_target = target.replace(" ", "_")
        ranked: list[tuple[int, str, dict[str, Any]]] = []

        for entry in self.data["errors"]:
            source = entry["source"]
            reference = f"{source['book']} {source['chapter']}:{source['verses']}"
            exact_fields = [
                entry["id"],
                entry["name"],
                entry.get("principle", ""),
                reference,
                *entry["invariants"],
            ]
            structured_fields = [
                entry["theme"],
                entry["trigger"],
                entry["recovery"],
                entry.get("principle", ""),
                *entry["invariants"],
            ]
            prose_fields = [
                entry["interpretation"],
                entry.get("plain_language", ""),
                reference,
            ]

            score: int | None = None
            if any(target == value.casefold() for value in exact_fields if value):
                score = 0
            elif any(
                target in value.casefold()
                or normalized_target in value.casefold()
                or target in value.casefold().replace("_", " ")
                for value in structured_fields
                if value
            ):
                score = 1
            elif any(target in value.casefold() for value in prose_fields if value):
                score = 2

            if score is not None:
                ranked.append((score, entry["id"], entry))

        return [entry for _, _, entry in sorted(ranked, key=lambda item: (item[0], item[1]))]


def load_sacred_registry(path: Path | str | None = None) -> SacredErrorRegistry:
    source = Path(path) if path is not None else canonical_sacred_registry_path()
    return SacredErrorRegistry(_read_json(source), source=source)
