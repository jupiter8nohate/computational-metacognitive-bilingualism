"""Stockfish-style bounded review council for CMB pull requests.

The engine borrows search ideas from chess engines: position evaluation, candidate
lines, pruning, adversarial re-evaluation, and a final principal variation. It does
not claim to be Stockfish and it does not merge pull requests.

REVIEW != MERGE
SCORE != TRUTH
MODEL_OPINION != EVIDENCE
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import tokenize
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence


class Verdict(str, Enum):
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class ReviewChange:
    path: str
    patch: str
    additions: int = 0
    deletions: int = 0


@dataclass(frozen=True, slots=True)
class Finding:
    agent: str
    severity: Severity
    category: str
    path: str
    message: str
    evidence: str
    score_delta: float

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["severity"] = self.severity.value
        return payload


@dataclass(frozen=True, slots=True)
class CandidateLine:
    name: str
    score: float
    rationale: str
    finding_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ReviewPacket:
    schema_version: str
    verdict: Verdict
    score: float
    confidence: float
    principal_variation: tuple[str, ...]
    findings: tuple[Finding, ...]
    council_votes: Mapping[str, Verdict]
    reviewed_paths: tuple[str, ...]
    digest: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "verdict": self.verdict.value,
            "score": self.score,
            "confidence": self.confidence,
            "principal_variation": list(self.principal_variation),
            "findings": [finding.to_dict() for finding in self.findings],
            "council_votes": {key: value.value for key, value in self.council_votes.items()},
            "reviewed_paths": list(self.reviewed_paths),
            "digest": self.digest,
        }


_CRITICAL_PATHS = (
    ".github/workflows/",
    "SECURITY.md",
    "cmb.toml",
    "policy/",
    "schemas/",
    "src/cmb_policy/",
    "src/cmb_agents/steward.py",
    "src/cmb_agents/autonomy.py",
    "src/cmb_agents/strategy.py",
)

_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)

_DANGEROUS_PATTERNS = (
    (re.compile(r"\bsubprocess\.(?:run|Popen|call)\([^\n]*shell\s*=\s*True"), "shell=True execution"),
    (re.compile(r"\bos\.system\("), "os.system execution"),
    (re.compile(r"\beval\("), "eval execution"),
    (re.compile(r"\bexec\("), "exec execution"),
    (re.compile(r"verify\s*=\s*False"), "TLS verification disabled"),
)

_WEAKENING_PATTERNS = (
    (re.compile(r"pytest\.skip|@pytest\.mark\.skip"), "test skip introduced"),
    (re.compile(r"continue-on-error:\s*true", re.IGNORECASE), "CI failure tolerance introduced"),
    (re.compile(r"fail-fast:\s*false", re.IGNORECASE), "matrix fail-fast disabled"),
)

_AUTHORITY_PATTERNS = (
    (re.compile(r"(?i)auto.?merge|merge_pull_request|pull-requests:\s*write"), "merge or PR write authority"),
    (re.compile(r"(?i)permissions:\s*write-all"), "write-all workflow authority"),
    (re.compile(r"(?i)secrets:\s*inherit"), "broad secret inheritance"),
)

_TODO_PATTERN = re.compile(r"\b(?:TODO|FIXME)\b")
_ASSERT_FALSE_PATTERN = re.compile(r"\bassert\s+False\b")
_BROAD_EXCEPTION_PATTERN = re.compile(r"\bexcept\s+Exception\s*:")


def _added_lines(patch: str) -> str:
    return "\n".join(
        line[1:]
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def _python_ignored_spans(
    line: str,
    *,
    ignore_strings: bool,
    ignore_comments: bool,
) -> tuple[tuple[int, int], ...]:
    spans: list[tuple[int, int]] = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(line + "\n").readline)
        for token in tokens:
            if token.start[0] != 1 or token.end[0] != 1:
                continue
            if ignore_strings and token.type == tokenize.STRING:
                spans.append((token.start[1], token.end[1]))
            elif ignore_comments and token.type == tokenize.COMMENT:
                spans.append((token.start[1], token.end[1]))
    except (IndentationError, tokenize.TokenError):
        return ()
    return tuple(spans)


def _first_contextual_match(
    change: ReviewChange,
    pattern: re.Pattern[str],
    *,
    ignore_strings: bool = True,
    ignore_comments: bool = True,
) -> str | None:
    is_python = change.path.endswith(".py")
    for line in _added_lines(change.patch).splitlines():
        spans = (
            _python_ignored_spans(
                line,
                ignore_strings=ignore_strings,
                ignore_comments=ignore_comments,
            )
            if is_python
            else ()
        )
        for match in pattern.finditer(line):
            if any(start <= match.start() < end for start, end in spans):
                continue
            return match.group(0)
    return None


def _finding(
    agent: str,
    severity: Severity,
    category: str,
    change: ReviewChange,
    message: str,
    evidence: str,
    score_delta: float,
) -> Finding:
    return Finding(agent, severity, category, change.path, message, evidence[:400], score_delta)


def _security_review(change: ReviewChange) -> list[Finding]:
    findings: list[Finding] = []
    for pattern in _SECRET_PATTERNS:
        match = _first_contextual_match(change, pattern)
        if match:
            findings.append(_finding(
                "SECURITY_SENTINEL", Severity.CRITICAL, "secret_exposure", change,
                "Possible credential or private key material added.", match, -100.0,
            ))
    for pattern, label in _DANGEROUS_PATTERNS:
        match = _first_contextual_match(change, pattern)
        if match:
            findings.append(_finding(
                "SECURITY_SENTINEL", Severity.ERROR, "unsafe_execution", change,
                f"Potentially unsafe execution primitive: {label}.", match, -35.0,
            ))
    return findings


def _correctness_review(change: ReviewChange) -> list[Finding]:
    findings: list[Finding] = []
    if change.path.endswith(".py"):
        broad_exception = _first_contextual_match(change, _BROAD_EXCEPTION_PATTERN)
        if broad_exception and not _first_contextual_match(change, re.compile(r"\braise\b")):
            findings.append(_finding(
                "CORRECTNESS_ENGINE", Severity.WARNING, "broad_exception", change,
                "Broad exception handling may hide a real failure path.", broad_exception, -8.0,
            ))
        forced_failure = _first_contextual_match(change, _ASSERT_FALSE_PATTERN)
        if forced_failure:
            findings.append(_finding(
                "CORRECTNESS_ENGINE", Severity.ERROR, "forced_failure", change,
                "Unconditional assertion failure introduced.", forced_failure, -30.0,
            ))
    unfinished = _first_contextual_match(
        change,
        _TODO_PATTERN,
        ignore_strings=True,
        ignore_comments=False,
    )
    if unfinished:
        findings.append(_finding(
            "CORRECTNESS_ENGINE", Severity.WARNING, "unfinished_work", change,
            "Unresolved TODO or FIXME added to production change.", unfinished, -5.0,
        ))
    return findings


def _architecture_review(change: ReviewChange) -> list[Finding]:
    findings: list[Finding] = []
    if change.additions > 700 and not change.path.startswith("tests/"):
        findings.append(_finding(
            "ARCHITECT", Severity.WARNING, "change_size", change,
            "Large single-file addition increases review and recovery risk.",
            f"additions={change.additions}", -6.0,
        ))
    if change.path.startswith("src/") and "/__init__.py" not in change.path and change.additions > 0:
        if "class " in _added_lines(change.patch) and change.additions > 450:
            findings.append(_finding(
                "ARCHITECT", Severity.WARNING, "module_cohesion", change,
                "Large module with new classes may deserve decomposition after stabilization.",
                f"path={change.path}", -4.0,
            ))
    return findings


def _test_review(change: ReviewChange) -> list[Finding]:
    findings: list[Finding] = []
    for pattern, label in _WEAKENING_PATTERNS:
        match = _first_contextual_match(change, pattern)
        if match:
            findings.append(_finding(
                "TEST_ADVERSARY", Severity.ERROR, "test_weakening", change,
                f"Potential verification weakening: {label}.", match, -25.0,
            ))
    if change.path.startswith("src/") and change.additions >= 120:
        findings.append(_finding(
            "TEST_ADVERSARY", Severity.INFO, "coverage_prompt", change,
            "Substantial implementation change should have focused tests in the same PR.",
            f"source_additions={change.additions}", -1.0,
        ))
    return findings


def _governance_review(change: ReviewChange) -> list[Finding]:
    findings: list[Finding] = []
    critical = any(change.path == prefix or change.path.startswith(prefix) for prefix in _CRITICAL_PATHS)
    if critical:
        findings.append(_finding(
            "GOVERNANCE_GUARD", Severity.WARNING, "critical_surface", change,
            "Change touches a high-authority or governance-sensitive surface.",
            change.path, -7.0,
        ))
    for pattern, label in _AUTHORITY_PATTERNS:
        match = _first_contextual_match(change, pattern)
        if match:
            findings.append(_finding(
                "GOVERNANCE_GUARD", Severity.ERROR, "authority_expansion", change,
                f"Review authority expansion carefully: {label}.", match, -28.0,
            ))
    return findings


def _run_base_agents(changes: Sequence[ReviewChange]) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    for change in changes:
        findings.extend(_security_review(change))
        findings.extend(_correctness_review(change))
        findings.extend(_architecture_review(change))
        findings.extend(_test_review(change))
        findings.extend(_governance_review(change))
    return tuple(findings)


def _score(findings: Iterable[Finding], changes: Sequence[ReviewChange]) -> float:
    base = 100.0
    base -= min(20.0, max(0, len(changes) - 12) * 1.25)
    base += sum(finding.score_delta for finding in findings)
    return round(max(0.0, min(100.0, base)), 2)


def _candidate_lines(findings: tuple[Finding, ...], score: float) -> tuple[CandidateLine, ...]:
    critical = tuple(i for i, f in enumerate(findings) if f.severity is Severity.CRITICAL)
    errors = tuple(i for i, f in enumerate(findings) if f.severity is Severity.ERROR)
    warnings = tuple(i for i, f in enumerate(findings) if f.severity is Severity.WARNING)
    return (
        CandidateLine("safe_merge", score + (4.0 if not critical and not errors else -40.0), "No blocking evidence found.", warnings[:4]),
        CandidateLine(
            "request_changes",
            100.0 - score + (45.0 if critical else 20.0) if critical or errors else -1.0,
            "Blocking defects dominate." if critical or errors else "No blocking evidence supports this line.",
            critical + errors,
        ),
        CandidateLine("human_escalation", 35.0 + len(warnings) * 3.0, "Ambiguity or governance-sensitive changes justify human review.", warnings),
    )


def _select_principal_line(lines: Sequence[CandidateLine]) -> CandidateLine:
    """Select the highest-scoring legal candidate line deterministically."""

    if not lines:
        raise ValueError("at least one candidate line is required")
    return max(lines, key=lambda line: (line.score, line.name))


def _skeptic(findings: tuple[Finding, ...], principal: CandidateLine, changes: Sequence[ReviewChange]) -> CandidateLine:
    """Challenge the current principal variation before the arbiter accepts it."""

    high_authority = any(any(c.path == p or c.path.startswith(p) for p in _CRITICAL_PATHS) for c in changes)
    error_count = sum(1 for finding in findings if finding.severity in {Severity.ERROR, Severity.CRITICAL})
    if principal.name == "safe_merge" and high_authority:
        return CandidateLine(
            "human_escalation",
            principal.score + 6.0,
            "Skeptic rejects automatic comfort on a governance-sensitive surface.",
            principal.finding_ids,
        )
    if principal.name == "safe_merge" and error_count:
        return CandidateLine(
            "request_changes",
            principal.score + 50.0,
            "Skeptic found blocking evidence inconsistent with a safe-merge line.",
            tuple(i for i, f in enumerate(findings) if f.severity in {Severity.ERROR, Severity.CRITICAL}),
        )
    return principal


def _vote(agent: str, findings: tuple[Finding, ...], score: float, changes: Sequence[ReviewChange]) -> Verdict:
    owned = [finding for finding in findings if finding.agent == agent]
    if any(f.severity in {Severity.ERROR, Severity.CRITICAL} for f in owned):
        return Verdict.REQUEST_CHANGES
    if agent == "GOVERNANCE_GUARD" and any(
        any(change.path == p or change.path.startswith(p) for p in _CRITICAL_PATHS)
        for change in changes
    ):
        return Verdict.HUMAN_REVIEW
    if score < 70.0:
        return Verdict.HUMAN_REVIEW
    return Verdict.APPROVE


def review_changes(changes: Sequence[ReviewChange]) -> ReviewPacket:
    if not changes:
        raise ValueError("at least one changed file is required")
    if len(changes) > 500:
        raise ValueError("review is bounded to 500 changed files")

    findings = _run_base_agents(changes)
    score = _score(findings, changes)
    candidates = _candidate_lines(findings, score)
    principal = _skeptic(findings, _select_principal_line(candidates), changes)

    votes = {
        agent: _vote(agent, findings, score, changes)
        for agent in (
            "SECURITY_SENTINEL",
            "CORRECTNESS_ENGINE",
            "ARCHITECT",
            "TEST_ADVERSARY",
            "GOVERNANCE_GUARD",
        )
    }

    if any(f.severity is Severity.CRITICAL for f in findings):
        verdict = Verdict.REQUEST_CHANGES
    elif sum(v is Verdict.REQUEST_CHANGES for v in votes.values()) >= 2:
        verdict = Verdict.REQUEST_CHANGES
    elif principal.name == "request_changes":
        verdict = Verdict.REQUEST_CHANGES
    elif principal.name == "human_escalation" or any(v is Verdict.HUMAN_REVIEW for v in votes.values()):
        verdict = Verdict.HUMAN_REVIEW
    else:
        verdict = Verdict.APPROVE

    confidence = 0.99 if any(f.severity is Severity.CRITICAL for f in findings) else 0.90
    confidence -= min(0.25, sum(1 for f in findings if f.severity is Severity.WARNING) * 0.02)
    confidence = round(max(0.5, confidence), 3)

    principal_variation = (
        "POSITION_EVALUATION",
        principal.name.upper(),
        "SKEPTIC_CHALLENGE",
        "COUNCIL_VOTE",
        f"ARBITER:{verdict.value}",
    )
    payload = {
        "verdict": verdict.value,
        "score": score,
        "confidence": confidence,
        "principal_variation": principal_variation,
        "findings": [f.to_dict() for f in findings],
        "council_votes": {k: v.value for k, v in votes.items()},
        "reviewed_paths": sorted(change.path for change in changes),
    }
    digest = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    return ReviewPacket(
        schema_version="cmb.stockfish-review.v1",
        verdict=verdict,
        score=score,
        confidence=confidence,
        principal_variation=principal_variation,
        findings=findings,
        council_votes=votes,
        reviewed_paths=tuple(sorted(change.path for change in changes)),
        digest=digest,
    )


def load_changes(payload: Sequence[Mapping[str, object]]) -> tuple[ReviewChange, ...]:
    changes: list[ReviewChange] = []
    for item in payload:
        path = str(item.get("path", "")).strip()
        patch = str(item.get("patch", ""))
        if not path:
            raise ValueError("every change requires a path")
        additions = int(item.get("additions", 0))
        deletions = int(item.get("deletions", 0))
        if additions < 0 or deletions < 0:
            raise ValueError("change counts must be non-negative")
        changes.append(
            ReviewChange(
                path=path,
                patch=patch,
                additions=additions,
                deletions=deletions,
            )
        )
    return tuple(changes)


def render_markdown(packet: ReviewPacket) -> str:
    lines = [
        "# CMB Stockfish Review Council",
        "",
        f"Verdict: **{packet.verdict.value}**",
        f"Position score: **{packet.score:.2f}/100**",
        f"Confidence: **{packet.confidence:.3f}**",
        f"Receipt: `{packet.digest}`",
        "",
        "## Principal variation",
        "",
        " -> ".join(packet.principal_variation),
        "",
        "## Council votes",
        "",
        "| Agent | Vote |",
        "| --- | --- |",
    ]
    lines.extend(f"| {agent} | {vote.value} |" for agent, vote in packet.council_votes.items())
    lines.extend(["", "## Findings", ""])
    if not packet.findings:
        lines.append("No heuristic findings were produced. This is not proof of correctness.")
    else:
        for finding in packet.findings:
            lines.append(
                f"- **{finding.severity.value.upper()}** `{finding.agent}` `{finding.path}`: {finding.message}"
            )
    lines.extend([
        "",
        "SCORE != TRUTH  ",
        "REVIEW != MERGE  ",
        "MODEL_OPINION != EVIDENCE  ",
        "HUMAN_AGENCY > MACHINE_AUTHORITY",
        "",
    ])
    return "\n".join(lines)
