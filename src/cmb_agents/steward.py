"""Bounded autonomous maintenance agents for the CMB repository.

The steward intentionally separates observation, model advice, mutation, and merge
authority. Scheduled GitHub Actions may audit the repository, apply deterministic
generated-artifact repairs, ask a configured model for a tightly structured repair
proposal, validate that proposal against a path policy, run fixed verification, and
open a pull request. The steward never merges its own work.

MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

ROOT: Final[Path] = Path(__file__).resolve().parents[2]

ROLE_NAMES: Final[tuple[str, ...]] = (
    "RECOVERY",
    "GLITCH_IR_CONFORMANCE",
    "REGISTRY_SYNC",
    "DOCUMENTATION",
    "STEWARD",
)

_ALLOWED_PREFIXES: Final[tuple[str, ...]] = (
    "src/cmb_glitch8/",
    "src/cmb_agents/",
    "src/cmb_machine/",
    "docs/",
    "books/",
    "examples/",
)
_ALLOWED_EXACT: Final[set[str]] = {"README.md"}
_DENIED_PREFIXES: Final[tuple[str, ...]] = (
    ".github/",
    "tests/",
    "scripts/",
    "schemas/",
    "machine/",
    "agents/",
    "policy/",
    "receipts/",
)
_DENIED_EXACT: Final[set[str]] = {
    "LICENSE",
    "NOTICE",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "pyproject.toml",
    "cmb.toml",
    "src/cmb_agents/steward.py",
}
_MAX_EDITS: Final[int] = 4
_MAX_EDIT_BYTES: Final[int] = 120_000
_MAX_CONTEXT_BYTES: Final[int] = 80_000
_MAX_COMMAND_OUTPUT: Final[int] = 14_000

_PATH_RE: Final[re.Pattern[str]] = re.compile(
    r"(?P<path>(?:src|docs|books|examples)/[A-Za-z0-9_./-]+\.(?:py|md|json|txt|go|rs|ts|hs|lisp|pl|cpp))"
)

_PLAN_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "rationale", "edits"],
    "properties": {
        "summary": {"type": "string", "minLength": 1, "maxLength": 500},
        "rationale": {"type": "string", "minLength": 1, "maxLength": 3000},
        "edits": {
            "type": "array",
            "maxItems": _MAX_EDITS,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["path", "content", "reason"],
                "properties": {
                    "path": {"type": "string", "minLength": 1},
                    "content": {"type": "string"},
                    "reason": {"type": "string", "minLength": 1, "maxLength": 1200},
                },
            },
        },
    },
}


class StewardError(RuntimeError):
    """Raised when a steward boundary or execution invariant is violated."""


@dataclass(frozen=True, slots=True)
class CheckResult:
    role: str
    name: str
    command: list[str]
    returncode: int
    output: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass(frozen=True, slots=True)
class AuditReport:
    roles: tuple[str, ...]
    checks: tuple[CheckResult, ...]
    generated_changes: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "roles": list(self.roles),
            "ok": self.ok,
            "checks": [
                {**asdict(check), "ok": check.ok}
                for check in self.checks
            ],
            "generated_changes": list(self.generated_changes),
        }


def _run(
    command: list[str],
    *,
    cwd: Path = ROOT,
    timeout: int = 900,
) -> CheckResult:
    role, name = "RECOVERY", "command"
    process = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=timeout,
    )
    output = process.stdout[-_MAX_COMMAND_OUTPUT:]
    return CheckResult(role, name, command, process.returncode, output)


def _named_check(role: str, name: str, command: list[str], *, timeout: int = 900) -> CheckResult:
    result = _run(command, timeout=timeout)
    return CheckResult(role, name, result.command, result.returncode, result.output)


def _git_changed_paths() -> tuple[str, ...]:
    process = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    paths: list[str] = []
    for line in process.stdout.splitlines():
        if not line:
            continue
        raw = line[3:]
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.append(raw.strip())
    return tuple(sorted(set(paths)))


def _run_registry_sync() -> CheckResult:
    result = _named_check(
        "REGISTRY_SYNC",
        "regenerate GLITCH-8 public views",
        [sys.executable, "scripts/generate_glitch8_reference.py"],
    )
    return result


def run_audit(*, include_docs: bool = True) -> AuditReport:
    """Run deterministic maintenance agents and normalize generated GLITCH-8 views."""
    checks: list[CheckResult] = []

    checks.append(
        _named_check(
            "RECOVERY",
            "unit and integration tests",
            [sys.executable, "-m", "pytest", "-q"],
            timeout=1200,
        )
    )
    checks.append(
        _named_check(
            "GLITCH_IR_CONFORMANCE",
            "GLT-8101 eight-language conformance",
            [sys.executable, "scripts/check_glitch_ir_conformance.py"],
            timeout=1200,
        )
    )
    checks.append(_run_registry_sync())
    checks.append(
        _named_check(
            "RECOVERY",
            "whitespace and patch integrity",
            ["git", "diff", "--check"],
        )
    )
    if include_docs:
        checks.append(
            _named_check(
                "DOCUMENTATION",
                "strict public documentation build",
                [sys.executable, "scripts/build_docs.py", "--site-dir", "site"],
                timeout=1200,
            )
        )

    return AuditReport(
        roles=ROLE_NAMES,
        checks=tuple(checks),
        generated_changes=_git_changed_paths(),
    )


def _normalize_relative(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise StewardError(f"unsafe path: {path!r}")
    normalized = candidate.as_posix().lstrip("./")
    if not normalized or normalized == ".":
        raise StewardError("empty edit path")
    return normalized


def is_ai_editable_path(path: str) -> bool:
    """Return whether the model may propose an edit to this repository path."""
    try:
        normalized = _normalize_relative(path)
    except StewardError:
        return False

    if normalized in _DENIED_EXACT:
        return False
    if any(normalized.startswith(prefix) for prefix in _DENIED_PREFIXES):
        return False
    return normalized in _ALLOWED_EXACT or any(
        normalized.startswith(prefix) for prefix in _ALLOWED_PREFIXES
    )


def _candidate_paths(report: AuditReport) -> list[str]:
    referenced: list[str] = []
    for check in report.checks:
        if check.ok:
            continue
        for match in _PATH_RE.finditer(check.output):
            path = match.group("path")
            if is_ai_editable_path(path) and path not in referenced:
                referenced.append(path)

    fallbacks = [
        "src/cmb_glitch8/glitch_ir.py",
        "src/cmb_glitch8/registry.py",
        "src/cmb_agents/service.py",
        "docs/GLITCH8_REGISTRY.md",
        "spec/GLITCH-IR-1.md",
        "README.md",
    ]
    for path in fallbacks:
        if is_ai_editable_path(path) and path not in referenced:
            referenced.append(path)
    return referenced


def collect_context(report: AuditReport) -> dict[str, str]:
    """Collect a bounded set of existing, editable files for the repair model."""
    context: dict[str, str] = {}
    budget = _MAX_CONTEXT_BYTES
    for relative in _candidate_paths(report):
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            continue
        raw = path.read_bytes()
        if len(raw) > min(24_000, budget):
            continue
        text = raw.decode("utf-8")
        context[relative] = text
        budget -= len(raw)
        if budget <= 0:
            break
    return context


def _failed_checks(report: AuditReport) -> list[dict[str, Any]]:
    return [
        {
            "role": check.role,
            "name": check.name,
            "command": check.command,
            "returncode": check.returncode,
            "output": check.output,
        }
        for check in report.checks
        if not check.ok
    ]


def _extract_output_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct
    for item in payload.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and content.get("type") == "output_text":
                value = content.get("text")
                if isinstance(value, str) and value.strip():
                    return value
    raise StewardError("model response contained no output_text")


def request_repair_plan(
    report: AuditReport,
    context: dict[str, str],
    *,
    api_key: str,
    model: str,
) -> dict[str, Any]:
    """Ask a configured OpenAI Responses API model for a bounded repair proposal."""
    if not api_key:
        raise StewardError("OPENAI_API_KEY is required for AI repair mode")
    if not model:
        raise StewardError("CMB_AGENT_MODEL is required for AI repair mode")
    if not _failed_checks(report):
        return {"summary": "No repair required.", "rationale": "All checks passed.", "edits": []}

    prompt = {
        "task": (
            "Repair only concrete failures shown in the audit. Return the minimum edits needed. "
            "Do not weaken tests, disable validation, change workflows, change schemas, change "
            "security/authority policy, or invent a success state. If the evidence is insufficient, "
            "return an empty edits array."
        ),
        "invariants": [
            "PATTERN != PROOF",
            "VERIFIED_LABEL != VERIFIED_TRUTH",
            "CAPABILITY != AUTHORITY",
            "MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
        "failed_checks": _failed_checks(report),
        "editable_file_context": context,
    }

    body = {
        "model": model,
        "store": False,
        "instructions": (
            "You are the CMB Recovery Steward. Diagnose repository failures conservatively. "
            "Only propose complete replacement contents for paths supplied in editable_file_context. "
            "Never claim a check passed unless the audit evidence shows it. Keep semantic and "
            "provenance boundaries intact."
        ),
        "input": json.dumps(prompt, ensure_ascii=False),
        "max_output_tokens": 12000,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "cmb_steward_repair_plan",
                "strict": True,
                "schema": _PLAN_SCHEMA,
            }
        },
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise StewardError(f"model request failed with HTTP {exc.code}: {detail[:2000]}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise StewardError(f"model request failed: {exc}") from exc

    plan = json.loads(_extract_output_text(payload))
    if not isinstance(plan, dict):
        raise StewardError("repair plan must be a JSON object")
    return plan


def apply_repair_plan(plan: dict[str, Any], context: dict[str, str]) -> tuple[str, ...]:
    """Apply a structured model proposal only after strict local boundary validation."""
    edits = plan.get("edits")
    if not isinstance(edits, list):
        raise StewardError("repair plan edits must be a list")
    if len(edits) > _MAX_EDITS:
        raise StewardError(f"repair plan exceeds {_MAX_EDITS} edits")

    total = 0
    changed: list[str] = []
    for edit in edits:
        if not isinstance(edit, dict):
            raise StewardError("every repair edit must be an object")
        path = _normalize_relative(str(edit.get("path", "")))
        content = edit.get("content")
        if path not in context:
            raise StewardError(f"model attempted to edit a file outside supplied context: {path}")
        if not is_ai_editable_path(path):
            raise StewardError(f"model attempted a protected path: {path}")
        if not isinstance(content, str):
            raise StewardError(f"replacement content for {path} must be text")

        encoded = content.encode("utf-8")
        total += len(encoded)
        if total > _MAX_EDIT_BYTES:
            raise StewardError("repair plan exceeds total edit byte limit")

        target = ROOT / path
        if target.is_symlink() or not target.is_file():
            raise StewardError(f"model edits require an existing regular file: {path}")
        if target.read_text(encoding="utf-8") == content:
            continue
        target.write_text(content, encoding="utf-8")
        changed.append(path)

    return tuple(changed)


def validate_worktree_changes() -> tuple[str, ...]:
    """Ensure a steward run has not changed protected repository paths."""
    changed = _git_changed_paths()
    for path in changed:
        # Deterministic generated views are allowed even though model edits to some
        # of their source classes are restricted.
        if path in {
            "books/GLITCH8_GLYPH_REFERENCE.md",
            "library/glitch8.glyphs.v1.json",
        }:
            continue
        if not is_ai_editable_path(path):
            raise StewardError(f"steward changed protected path: {path}")
    return changed


def verify() -> tuple[CheckResult, ...]:
    """Run fixed verification after deterministic or AI-assisted changes."""
    checks = (
        _named_check("RECOVERY", "pytest", [sys.executable, "-m", "pytest", "-q"], timeout=1200),
        _named_check(
            "GLITCH_IR_CONFORMANCE",
            "GLT-8101 conformance",
            [sys.executable, "scripts/check_glitch_ir_conformance.py"],
            timeout=1200,
        ),
        _named_check("REGISTRY_SYNC", "registry regeneration", [sys.executable, "scripts/generate_glitch8_reference.py"]),
        _named_check("RECOVERY", "diff check", ["git", "diff", "--check"]),
    )
    return checks


def _write_report(path: Path, report: AuditReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _read_report(path: Path) -> AuditReport:
    data = json.loads(path.read_text(encoding="utf-8"))
    checks = tuple(
        CheckResult(
            role=item["role"],
            name=item["name"],
            command=list(item["command"]),
            returncode=int(item["returncode"]),
            output=item["output"],
        )
        for item in data["checks"]
    )
    return AuditReport(
        roles=tuple(data["roles"]),
        checks=checks,
        generated_changes=tuple(data.get("generated_changes", [])),
    )


def _print_checks(checks: tuple[CheckResult, ...]) -> None:
    for check in checks:
        state = "PASS" if check.ok else "FAIL"
        print(f"[{check.role}] {state}: {check.name}")
        if not check.ok and check.output:
            print(check.output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    audit_parser = sub.add_parser("audit", help="Run deterministic steward audits.")
    audit_parser.add_argument("--report", type=Path, default=Path(".cmb-agent/audit.json"))
    audit_parser.add_argument("--skip-docs", action="store_true")

    repair_parser = sub.add_parser("repair", help="Apply a bounded AI repair proposal.")
    repair_parser.add_argument("--report", type=Path, default=Path(".cmb-agent/audit.json"))

    sub.add_parser("verify", help="Run fixed post-repair verification.")
    sub.add_parser("validate-diff", help="Reject protected-path mutations.")

    args = parser.parse_args(argv)

    try:
        if args.command == "audit":
            report = run_audit(include_docs=not args.skip_docs)
            _write_report(args.report, report)
            _print_checks(report.checks)
            print(f"Generated changes: {len(report.generated_changes)}")
            return 0

        if args.command == "repair":
            report = _read_report(args.report)
            if report.ok:
                print("All audit checks passed; AI repair not required.")
                return 0
            api_key = os.environ.get("OPENAI_API_KEY", "")
            model = os.environ.get("CMB_AGENT_MODEL", "")
            if not api_key or not model:
                print(
                    "AI repair skipped: configure OPENAI_API_KEY secret and "
                    "CMB_AGENT_MODEL repository variable.",
                    file=sys.stderr,
                )
                return 0
            context = collect_context(report)
            plan = request_repair_plan(report, context, api_key=api_key, model=model)
            changed = apply_repair_plan(plan, context)
            print(plan.get("summary", "Repair proposal applied."))
            print(f"AI-edited files: {len(changed)}")
            return 0

        if args.command == "verify":
            checks = verify()
            _print_checks(checks)
            validate_worktree_changes()
            return 0 if all(check.ok for check in checks) else 1

        if args.command == "validate-diff":
            changed = validate_worktree_changes()
            print(f"Validated steward worktree: {len(changed)} changed path(s).")
            return 0

    except (OSError, StewardError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"CMB Steward failed: {exc}", file=sys.stderr)
        return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
