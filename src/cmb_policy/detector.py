"""Deterministic path- and AST-aware change detection for CMB-SRP-2."""

from __future__ import annotations

import ast
import fnmatch
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

from .runtime import RuntimePolicy, RuntimePolicyError, required_controls_for

SCAN_SCHEMA = "cmb.scan-report.v1"


@dataclass(frozen=True, slots=True)
class PathRule:
    rule_id: str
    glob: str
    operation: str


@dataclass(frozen=True, slots=True)
class PythonCallRule:
    rule_id: str
    names: tuple[str, ...]
    operation: str


@dataclass(frozen=True, slots=True)
class DetectorConfig:
    python_ast: bool
    fail_closed_on_python_parse_error: bool
    max_file_bytes: int
    path_rules: tuple[PathRule, ...]
    python_call_rules: tuple[PythonCallRule, ...]

    @classmethod
    def load(cls, policy_path: Path, runtime_policy: RuntimePolicy) -> "DetectorConfig":
        payload = tomllib.loads(policy_path.read_text(encoding="utf-8"))
        raw = payload.get("detectors")
        if not isinstance(raw, dict):
            raise RuntimePolicyError("CMB-SRP-2 requires a [detectors] section")

        max_file_bytes = raw.get("max_file_bytes", 1_048_576)
        if isinstance(max_file_bytes, bool) or not isinstance(max_file_bytes, int):
            raise RuntimePolicyError("detectors.max_file_bytes must be an integer")
        if max_file_bytes <= 0:
            raise RuntimePolicyError("detectors.max_file_bytes must be positive")

        path_rules = tuple(
            _path_rule(item, runtime_policy)
            for item in _table_array(raw.get("path_rules", []), "detectors.path_rules")
        )
        call_rules = tuple(
            _call_rule(item, runtime_policy)
            for item in _table_array(
                raw.get("python_call_rules", []),
                "detectors.python_call_rules",
            )
        )
        return cls(
            python_ast=bool(raw.get("python_ast", True)),
            fail_closed_on_python_parse_error=bool(
                raw.get("fail_closed_on_python_parse_error", True)
            ),
            max_file_bytes=max_file_bytes,
            path_rules=path_rules,
            python_call_rules=call_rules,
        )


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    operation: str
    rule_id: str
    detector: str
    line: int | None = None
    column: int | None = None
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "operation": self.operation,
            "rule_id": self.rule_id,
            "detector": self.detector,
            "line": self.line,
            "column": self.column,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class ScanError:
    path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class ScanReport:
    policy_digest: str
    files: tuple[str, ...]
    findings: tuple[Finding, ...]
    errors: tuple[ScanError, ...]
    base: str | None = None
    head: str | None = None

    @property
    def operations(self) -> tuple[str, ...]:
        return tuple(sorted({item.operation for item in self.findings}))

    def payload(self) -> dict[str, Any]:
        return {
            "schema": SCAN_SCHEMA,
            "policy_digest": self.policy_digest,
            "base": self.base,
            "head": self.head,
            "files": list(self.files),
            "findings": [item.to_dict() for item in self.findings],
            "errors": [item.to_dict() for item in self.errors],
            "operations": list(self.operations),
        }

    @property
    def digest(self) -> str:
        encoded = json.dumps(
            self.payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {**self.payload(), "report_digest": self.digest}


def scan_paths(
    paths: Iterable[Path],
    *,
    policy_path: Path,
    repo_root: Path | None = None,
    base: str | None = None,
    head: str | None = None,
) -> ScanReport:
    root = (repo_root or Path.cwd()).resolve()
    policy = RuntimePolicy.load(policy_path)
    config = DetectorConfig.load(policy_path, policy)

    normalized = _expand_paths(paths, root)
    findings: list[Finding] = []
    errors: list[ScanError] = []

    for relative in normalized:
        findings.extend(_path_findings(relative, config))
        target = root / relative
        if not target.exists():
            continue
        if not target.is_file():
            continue
        try:
            size = target.stat().st_size
        except OSError as exc:
            errors.append(ScanError(relative, "STAT_ERROR", str(exc)))
            continue
        if size > config.max_file_bytes:
            errors.append(
                ScanError(
                    relative,
                    "FILE_TOO_LARGE",
                    f"{size} bytes exceeds detector limit {config.max_file_bytes}",
                )
            )
            continue
        if config.python_ast and target.suffix.lower() == ".py":
            ast_findings, ast_errors = _scan_python(target, relative, config)
            findings.extend(ast_findings)
            errors.extend(ast_errors)

    findings.sort(
        key=lambda item: (
            item.path,
            item.line if item.line is not None else -1,
            item.column if item.column is not None else -1,
            item.operation,
            item.rule_id,
        )
    )
    errors.sort(key=lambda item: (item.path, item.code, item.message))
    return ScanReport(
        policy_digest=policy.digest,
        files=tuple(normalized),
        findings=tuple(findings),
        errors=tuple(errors),
        base=base,
        head=head,
    )


def scan_git(
    *,
    base: str,
    head: str,
    policy_path: Path,
    repo_root: Path | None = None,
) -> ScanReport:
    root = (repo_root or Path.cwd()).resolve()
    completed = subprocess.run(
        ["git", "diff", "--name-only", "-z", f"{base}...{head}"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimePolicyError(f"git diff failed: {message or completed.returncode}")
    names = [
        Path(item.decode("utf-8", errors="strict"))
        for item in completed.stdout.split(b"\0")
        if item
    ]
    return scan_paths(
        names,
        policy_path=policy_path,
        repo_root=root,
        base=base,
        head=head,
    )


def load_scan_report(path: Path) -> ScanReport:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != SCAN_SCHEMA:
        raise RuntimePolicyError("unsupported or malformed scan report")
    findings = tuple(
        Finding(
            path=item["path"],
            operation=item["operation"],
            rule_id=item["rule_id"],
            detector=item["detector"],
            line=item.get("line"),
            column=item.get("column"),
            evidence=item.get("evidence", ""),
        )
        for item in payload.get("findings", [])
    )
    errors = tuple(
        ScanError(path=item["path"], code=item["code"], message=item["message"])
        for item in payload.get("errors", [])
    )
    report = ScanReport(
        policy_digest=payload["policy_digest"],
        files=tuple(payload.get("files", [])),
        findings=findings,
        errors=errors,
        base=payload.get("base"),
        head=payload.get("head"),
    )
    expected = payload.get("report_digest")
    if expected is not None and expected != report.digest:
        raise RuntimePolicyError("scan report digest mismatch")
    return report


def summarize_report(report: ScanReport, policy: RuntimePolicy) -> dict[str, Any]:
    operations = []
    for operation in report.operations:
        rule = policy.operations.get(operation)
        if rule is None:
            criticality = 1.0
            controls = ("human_signature", "isolated_verification", "two_party_review")
        else:
            criticality = rule.criticality
            controls = required_controls_for(policy, operation)
        operations.append(
            {
                "operation": operation,
                "criticality": criticality,
                "required_controls": list(controls),
            }
        )
    return {
        "report_digest": report.digest,
        "finding_count": len(report.findings),
        "error_count": len(report.errors),
        "operations": operations,
        "highest_criticality": max(
            (item["criticality"] for item in operations),
            default=0.0,
        ),
    }


def _path_findings(path: str, config: DetectorConfig) -> list[Finding]:
    return [
        Finding(
            path=path,
            operation=rule.operation,
            rule_id=rule.rule_id,
            detector="path",
            evidence=f"path_glob:{rule.glob}",
        )
        for rule in config.path_rules
        if fnmatch.fnmatchcase(path, rule.glob)
    ]


def _scan_python(
    path: Path,
    relative: str,
    config: DetectorConfig,
) -> tuple[list[Finding], list[ScanError]]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [], [ScanError(relative, "PYTHON_READ_ERROR", str(exc))]
    try:
        tree = ast.parse(source, filename=relative)
    except SyntaxError as exc:
        error = ScanError(
            relative,
            "PYTHON_PARSE_ERROR",
            f"{exc.msg} at line {exc.lineno or 0}",
        )
        return [], [error]

    aliases = _import_aliases(tree)
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _qualified_name(node.func, aliases)
        if not name:
            continue
        for rule in config.python_call_rules:
            if name in rule.names:
                findings.append(
                    Finding(
                        path=relative,
                        operation=rule.operation,
                        rule_id=rule.rule_id,
                        detector="python_ast_call",
                        line=getattr(node, "lineno", None),
                        column=getattr(node, "col_offset", None),
                        evidence=f"call:{name}",
                    )
                )
    return findings, []


def _import_aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split(".")[0]] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                aliases[item.asname or item.name] = f"{node.module}.{item.name}"
    return aliases


def _qualified_name(node: ast.AST, aliases: Mapping[str, str]) -> str:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        prefix = _qualified_name(node.value, aliases)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    if isinstance(node, ast.Call):
        return _qualified_name(node.func, aliases)
    return ""


def _expand_paths(paths: Iterable[Path], root: Path) -> list[str]:
    collected: set[str] = set()
    for raw in paths:
        candidate = raw if raw.is_absolute() else root / raw
        try:
            resolved = candidate.resolve(strict=False)
            relative = resolved.relative_to(root)
        except ValueError as exc:
            raise RuntimePolicyError(f"path escapes repository root: {raw}") from exc

        if candidate.exists() and candidate.is_dir():
            for child in candidate.rglob("*"):
                if child.is_file() and ".git" not in child.parts:
                    collected.add(child.resolve().relative_to(root).as_posix())
        else:
            collected.add(relative.as_posix())
    return sorted(collected)


def _path_rule(item: Mapping[str, Any], policy: RuntimePolicy) -> PathRule:
    rule_id = _text(item.get("id"), "path rule id")
    glob = _text(item.get("glob"), f"{rule_id}.glob")
    operation = _operation(item.get("operation"), policy, rule_id)
    return PathRule(rule_id=rule_id, glob=glob, operation=operation)


def _call_rule(item: Mapping[str, Any], policy: RuntimePolicy) -> PythonCallRule:
    rule_id = _text(item.get("id"), "python call rule id")
    names = item.get("names")
    if not isinstance(names, list) or not names:
        raise RuntimePolicyError(f"{rule_id}.names must be a non-empty array")
    normalized = tuple(sorted({_text(name, f"{rule_id}.names") for name in names}))
    operation = _operation(item.get("operation"), policy, rule_id)
    return PythonCallRule(rule_id=rule_id, names=normalized, operation=operation)


def _operation(value: Any, policy: RuntimePolicy, rule_id: str) -> str:
    operation = _text(value, f"{rule_id}.operation")
    if operation not in policy.operations:
        raise RuntimePolicyError(f"{rule_id}: unknown operation {operation}")
    return operation


def _table_array(value: Any, field: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise RuntimePolicyError(f"{field} must be an array of tables")
    if any(not isinstance(item, dict) for item in value):
        raise RuntimePolicyError(f"{field} entries must be tables")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimePolicyError(f"{field} must be non-empty text")
    return value.strip()
