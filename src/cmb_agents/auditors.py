"""Read-only specialist auditors used by the bounded CMB Steward.

These agents inspect repository state and emit structured evidence packets. They do
not mutate repository files, merge pull requests, publish releases, change security
settings, or expand their own authority.

AGENT_SPECIALIZATION > AGENT_POWER
DETERMINISTIC_CHECK > MODEL_OPINION
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

from .immune_system import DIGITAL_DNA, digital_dna_digest

_SAFE_AUTHORITIES: Final[set[str]] = {"read_only", "propose_only"}


@dataclass(frozen=True, slots=True)
class EvidencePacket:
    """Machine-readable claim/evidence envelope for one specialist agent."""

    agent: str
    task: str
    observed: dict[str, Any]
    evidence: tuple[str, ...]
    confidence: float
    recommended_action: str
    authority: str = "read_only"
    severity: str = "info"

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class AgentAudit:
    """Normalized result for a read-only specialist audit."""

    name: str
    ok: bool
    summary: str
    packet: EvidencePacket


def _read_text(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _read_json(root: Path, relative: str) -> Any:
    return json.loads(_read_text(root, relative))


def _packet(
    *,
    agent: str,
    task: str,
    observed: dict[str, Any],
    evidence: tuple[str, ...],
    confidence: float,
    recommended_action: str,
    severity: str = "info",
    authority: str = "read_only",
) -> EvidencePacket:
    return EvidencePacket(
        agent=agent,
        task=task,
        observed=observed,
        evidence=evidence,
        confidence=max(0.0, min(1.0, confidence)),
        recommended_action=recommended_action,
        authority=authority,
        severity=severity,
    )


def audit_canon(root: Path) -> AgentAudit:
    """Check that the canonical GLITCH-8 registry and public views remain aligned."""

    source_path = "src/cmb_glitch8/glyphs.v1.json"
    mirror_path = "library/glitch8.glyphs.v1.json"
    reference_path = "books/GLITCH8_GLYPH_REFERENCE.md"

    source = _read_json(root, source_path)
    mirror = _read_json(root, mirror_path)
    reference = _read_text(root, reference_path)

    glyphs = source.get("glyphs", []) if isinstance(source, dict) else []
    ids = [item.get("id") for item in glyphs if isinstance(item, dict)]
    duplicate_ids = sorted({item for item in ids if item and ids.count(item) > 1})
    missing_reference_names = sorted(
        item.get("name", "")
        for item in glyphs
        if isinstance(item, dict)
        and item.get("name")
        and str(item["name"]) not in reference
    )
    missing_required_fields = sorted(
        str(item.get("id", "<missing-id>"))
        for item in glyphs
        if isinstance(item, dict)
        and any(
            not item.get(field)
            for field in ("id", "name", "glyph", "definition", "human_semantics", "machine_semantics")
        )
    )

    mirror_matches = source == mirror
    ok = mirror_matches and not duplicate_ids and not missing_reference_names and not missing_required_fields
    summary = (
        f"{len(glyphs)} glyphs checked; mirror={'aligned' if mirror_matches else 'drifted'}; "
        f"duplicate_ids={len(duplicate_ids)}; missing_reference_names={len(missing_reference_names)}."
    )
    packet = _packet(
        agent="CANON",
        task="glitch8_semantic_consistency",
        observed={
            "glyph_count": len(glyphs),
            "mirror_matches": mirror_matches,
            "duplicate_ids": duplicate_ids,
            "missing_reference_names": missing_reference_names,
            "missing_required_fields": missing_required_fields,
        },
        evidence=(source_path, mirror_path, reference_path),
        confidence=1.0,
        recommended_action=(
            "No canon repair required."
            if ok
            else "Regenerate public views from the canonical registry and resolve duplicate or incomplete glyph records."
        ),
        severity="info" if ok else "error",
    )
    return AgentAudit("CANON", ok, summary, packet)


_HTML_IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_ALT_RE = re.compile(r"\balt\s*=\s*([\"'])(.*?)\1", re.IGNORECASE | re.DOTALL)
_MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\([^\)]+\)")


def _image_alt_issues(text: str) -> int:
    issues = 0
    for tag in _HTML_IMG_RE.findall(text):
        match = _ALT_RE.search(tag)
        if match is None or not match.group(2).strip():
            issues += 1
    issues += sum(1 for alt in _MD_IMG_RE.findall(text) if not alt.strip())
    return issues


def audit_accessibility(root: Path) -> AgentAudit:
    """Check high-value accessibility invariants without trying to replace a browser audit."""

    entry_paths = ("docs/index.md", "README.md", "docs/SEARCH_FOR_TRUTH.md")
    alt_issues = {
        path: _image_alt_issues(_read_text(root, path))
        for path in entry_paths
        if (root / path).is_file()
    }

    css_paths = (
        "docs/stylesheets/tokens.css",
        "docs/stylesheets/components.css",
        "docs/stylesheets/accessibility.css",
        "docs/stylesheets/cmb.css",
    )
    css = "\n".join(
        _read_text(root, path)
        for path in css_paths
        if (root / path).is_file()
    )
    has_focus = "focus-visible" in css
    has_reduced_motion = "prefers-reduced-motion" in css
    has_high_contrast = "prefers-contrast" in css
    homepage_alt_ok = alt_issues.get("docs/index.md", 0) == 0
    ok = homepage_alt_ok and has_focus and has_reduced_motion

    warnings = sum(alt_issues.values())
    summary = (
        f"entry alt issues={warnings}; focus-visible={has_focus}; "
        f"reduced-motion={has_reduced_motion}; high-contrast={has_high_contrast}."
    )
    packet = _packet(
        agent="ACCESSIBILITY",
        task="front_door_accessibility",
        observed={
            "alt_issues_by_file": alt_issues,
            "focus_visible": has_focus,
            "prefers_reduced_motion": has_reduced_motion,
            "prefers_contrast": has_high_contrast,
        },
        evidence=tuple(path for path in entry_paths if (root / path).is_file()) + tuple(
            path for path in css_paths if (root / path).is_file()
        ),
        confidence=0.95,
        recommended_action=(
            "No blocking accessibility defect detected in the primary entry surfaces."
            if ok
            else "Repair missing homepage alt text or restore keyboard-focus/reduced-motion safeguards."
        ),
        severity="info" if ok and warnings == 0 else ("warning" if ok else "error"),
    )
    return AgentAudit("ACCESSIBILITY", ok, summary, packet)


_VERSION_RE = re.compile(r"^version\s*=\s*[\"']([^\"']+)[\"']", re.MULTILINE)


def audit_release(root: Path) -> AgentAudit:
    """Inspect repository-declared release gates without pretending external gates are complete."""

    pyproject = _read_text(root, "pyproject.toml")
    release = _read_text(root, "RELEASE.md")
    stabilization = _read_text(root, "docs/STABILIZATION_CYCLE.md")
    external = _read_text(root, "docs/EXTERNAL_REVIEW.md")
    settings = _read_text(root, "docs/REPOSITORY_SETTINGS.md")

    match = _VERSION_RE.search(pyproject)
    version = match.group(1) if match else None
    rc_declared = bool(version and version.startswith("1.5.0"))
    review_boundary = "SELF_TEST != INDEPENDENT_AUDIT" in external
    final_gate = "independent review" in stabilization.lower()
    platform_boundary = "GREEN_CI != PROTECTED_BRANCH" in settings
    ok = bool(version) and rc_declared and review_boundary and final_gate and platform_boundary

    packet = _packet(
        agent="RELEASE",
        task="release_readiness_declarations",
        observed={
            "package_version": version,
            "v1_5_candidate_declared": rc_declared,
            "independent_review_boundary_present": review_boundary,
            "final_release_review_gate_present": final_gate,
            "branch_protection_boundary_present": platform_boundary,
            "external_gates_authoritatively_checked": False,
        },
        evidence=(
            "pyproject.toml",
            "RELEASE.md",
            "docs/STABILIZATION_CYCLE.md",
            "docs/EXTERNAL_REVIEW.md",
            "docs/REPOSITORY_SETTINGS.md",
        ),
        confidence=0.98,
        recommended_action=(
            "Repository release declarations are internally coherent; external review, DOI, and platform settings remain separate gates."
            if ok
            else "Reconcile package version and release/stabilization governance before tagging."
        ),
        severity="info" if ok else "error",
    )
    return AgentAudit(
        "RELEASE",
        ok,
        f"version={version or 'unknown'}; repository-declared v1.5 gates={'coherent' if ok else 'incomplete'}.",
        packet,
    )


_NAV_MD_RE = re.compile(r":\s+([A-Za-z0-9_./-]+\.md)\s*$")


def audit_librarian(root: Path) -> AgentAudit:
    """Check the documentation catalogue for broken MkDocs navigation targets."""

    mkdocs = _read_text(root, "mkdocs.yml")
    nav_targets = sorted(set(_NAV_MD_RE.findall(mkdocs)))
    missing = sorted(path for path in nav_targets if not (root / "docs" / path).is_file())
    docs_count = sum(1 for _ in (root / "docs").rglob("*.md"))
    ok = not missing

    packet = _packet(
        agent="LIBRARIAN",
        task="documentation_catalog_integrity",
        observed={
            "nav_target_count": len(nav_targets),
            "docs_markdown_count": docs_count,
            "missing_nav_targets": missing,
        },
        evidence=("mkdocs.yml", "docs/"),
        confidence=1.0,
        recommended_action=(
            "MkDocs navigation targets resolve."
            if ok
            else "Repair or remove missing navigation targets before publication."
        ),
        severity="info" if ok else "error",
    )
    return AgentAudit(
        "LIBRARIAN",
        ok,
        f"{len(nav_targets)} nav targets checked; missing={len(missing)}; docs={docs_count}.",
        packet,
    )


def _git_history(root: Path, relative: str) -> tuple[str | None, str | None, int]:
    process = subprocess.run(
        ["git", "log", "--format=%H", "--", relative],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=60,
    )
    if process.returncode != 0:
        return None, None, 0
    commits = [line.strip() for line in process.stdout.splitlines() if line.strip()]
    if not commits:
        return None, None, 0
    return commits[-1], commits[0], len(commits)


def audit_archaeologist(root: Path) -> AgentAudit:
    """Backtrace the canonical registry through Git history."""

    target = "src/cmb_glitch8/glyphs.v1.json"
    first_commit, latest_commit, commit_count = _git_history(root, target)
    ok = bool(first_commit and latest_commit and commit_count)

    packet = _packet(
        agent="ARCHAEOLOGIST",
        task="canonical_registry_backtrace",
        observed={
            "path": target,
            "first_commit": first_commit,
            "latest_commit": latest_commit,
            "commit_count": commit_count,
            "claim_scope": "repository_history_only",
        },
        evidence=(target, ".git history"),
        confidence=1.0 if ok else 0.4,
        recommended_action=(
            "Repository provenance backtrace is available."
            if ok
            else "Ensure the audit runs from a full Git checkout before making history claims."
        ),
        severity="info" if ok else "warning",
    )
    # A shallow/missing Git history should not make the whole steward destructive.
    return AgentAudit(
        "ARCHAEOLOGIST",
        True,
        f"registry history commits={commit_count}; backtrace={'available' if ok else 'limited'}.",
        packet,
    )


def audit_discovery(root: Path) -> AgentAudit:
    """Validate the core machine-discovery declaration surface."""

    path = "machine/discovery-manifest.json"
    manifest = _read_json(root, path)
    required = ("schema_version", "framework", "canonical_site", "canonical_repository", "sitemap", "robots")
    missing = [key for key in required if not isinstance(manifest, dict) or not manifest.get(key)]
    llm_points = manifest.get("llm_entry_points", []) if isinstance(manifest, dict) else []
    ok = not missing and isinstance(llm_points, list) and len(llm_points) >= 1

    packet = _packet(
        agent="DISCOVERY",
        task="machine_discovery_contract",
        observed={
            "missing_required_keys": missing,
            "llm_entry_point_count": len(llm_points) if isinstance(llm_points, list) else 0,
        },
        evidence=(path, "llms.txt", "llms-full.txt"),
        confidence=1.0,
        recommended_action=(
            "Machine discovery contract contains the required public entry points."
            if ok
            else "Repair the discovery manifest before publishing machine-facing metadata."
        ),
        severity="info" if ok else "error",
    )
    return AgentAudit("DISCOVERY", ok, f"missing_keys={len(missing)}; llm_entry_points={len(llm_points) if isinstance(llm_points, list) else 0}.", packet)


def _unpinned_workflow_actions(root: Path) -> list[str]:
    findings: list[str] = []
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return findings

    uses_pattern = re.compile(r"^\s*uses:\s*([^\s#]+)", re.MULTILINE)
    sha_pattern = re.compile(r"^[0-9a-fA-F]{40}$")

    for workflow in sorted(workflows.glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        for match in uses_pattern.finditer(text):
            reference = match.group(1)
            if reference.startswith("./") or reference.startswith("docker://"):
                continue
            if "@" not in reference:
                findings.append(f"{workflow.relative_to(root)}:{reference}")
                continue
            _, ref = reference.rsplit("@", 1)
            if not sha_pattern.fullmatch(ref):
                findings.append(f"{workflow.relative_to(root)}:{reference}")
    return findings


def audit_security(root: Path) -> AgentAudit:
    """Check repository-side security controls that can be represented as files."""

    required_paths = (
        "SECURITY.md",
        ".github/dependabot.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/dependency-review.yml",
        ".github/workflows/scorecard.yml",
    )
    missing = [path for path in required_paths if not (root / path).is_file()]
    dependency_review = (
        _read_text(root, ".github/workflows/dependency-review.yml")
        if (root / ".github/workflows/dependency-review.yml").is_file()
        else ""
    )
    dependency_review_fail_closed = "continue-on-error: true" not in dependency_review
    unpinned_actions = _unpinned_workflow_actions(root)
    ok = not missing and dependency_review_fail_closed and not unpinned_actions

    packet = _packet(
        agent="SECURITY",
        task="repository_security_surface",
        observed={
            "missing_repository_controls": missing,
            "dependency_review_fail_closed": dependency_review_fail_closed,
            "unpinned_workflow_actions": unpinned_actions,
            "platform_security_settings_checked": False,
        },
        evidence=required_paths + (".github/workflows/",),
        confidence=1.0,
        recommended_action=(
            "Repository-side security controls are present, dependency review fails closed, and external actions are SHA-pinned."
            if ok
            else "Repair missing controls, fail-open dependency review, or unpinned workflow actions."
        ),
        severity="info" if ok else "error",
    )
    return AgentAudit(
        "SECURITY",
        ok,
        (
            f"missing_controls={len(missing)}; "
            f"dependency_review_fail_closed={dependency_review_fail_closed}; "
            f"unpinned_actions={len(unpinned_actions)}."
        ),
        packet,
    )


def audit_dnis(root: Path) -> AgentAudit:
    """Check Digital Nervous Immune System registry and invariant continuity."""

    path = "agents/immune-cell-registry.json"
    registry = _read_json(root, path)
    declared_dna = tuple(registry.get("digital_dna", [])) if isinstance(registry, dict) else ()
    cells = registry.get("cells", []) if isinstance(registry, dict) else []
    cell_ids = {
        str(item.get("id"))
        for item in cells
        if isinstance(item, dict) and item.get("id")
    }
    required_cells = {
        "RECEPTOR_CELL",
        "DENDRITIC_CELL",
        "POSITION_CELL",
        "CHAPERONE_CELL",
        "T_CELL_POLICY_GATE",
        "REFLEX_CELL",
        "MACROPHAGE_RECOVERY",
        "CORTEX_LIAISON",
        "B_CELL_PROVENANCE",
        "MEMORY_CELL",
    }
    missing_cells = sorted(required_cells - cell_ids)
    dna_matches = declared_dna == DIGITAL_DNA
    protocol_ok = isinstance(registry, dict) and registry.get("protocol") == "CMB-DNIS-1"
    ok = dna_matches and protocol_ok and not missing_cells

    packet = _packet(
        agent="DNIS",
        task="digital_nervous_immune_integrity",
        observed={
            "protocol_ok": protocol_ok,
            "digital_dna_matches_runtime": dna_matches,
            "digital_dna_digest": digital_dna_digest(),
            "declared_cell_count": len(cell_ids),
            "missing_required_cells": missing_cells,
        },
        evidence=(path, "src/cmb_agents/immune_system.py"),
        confidence=1.0,
        recommended_action=(
            "DNIS registry and runtime Digital DNA are aligned."
            if ok
            else "Repair DNIS registry/runtime drift before treating cell-agent routing as canonical."
        ),
        severity="info" if ok else "error",
    )
    return AgentAudit(
        "DNIS",
        ok,
        f"protocol={'ok' if protocol_ok else 'invalid'}; dna={'aligned' if dna_matches else 'drifted'}; missing_cells={len(missing_cells)}.",
        packet,
    )



def audit_review_council(root: Path) -> AgentAudit:
    """Check CMB-SRC-1 registry, workflow presence, and authority boundaries."""

    registry_path = "agents/review-council-registry.json"
    workflow_path = ".github/workflows/cmb-stockfish-review.yml"
    registry = _read_json(root, registry_path)
    agents = registry.get("agents", []) if isinstance(registry, dict) else []
    agent_ids = {
        str(item.get("id"))
        for item in agents
        if isinstance(item, dict) and item.get("id")
    }
    required_agents = {
        "TACTICIAN",
        "SECURITY_SENTINEL",
        "CORRECTNESS_ENGINE",
        "ARCHITECT",
        "TEST_ADVERSARY",
        "GOVERNANCE_GUARD",
        "SKEPTIC",
        "ARBITER",
    }
    missing_agents = sorted(required_agents - agent_ids)
    protocol_ok = isinstance(registry, dict) and registry.get("protocol") == "CMB-SRC-1"
    merge_authority_ok = isinstance(registry, dict) and registry.get("merge_authority") is False
    release_authority_ok = isinstance(registry, dict) and registry.get("release_authority") is False
    workflow_present = (root / workflow_path).is_file()
    workflow_text = _read_text(root, workflow_path) if workflow_present else ""
    read_only = "contents: read" in workflow_text
    deterministic_gate = "Enforce deterministic verdict" in workflow_text

    ok = (
        protocol_ok
        and merge_authority_ok
        and release_authority_ok
        and workflow_present
        and read_only
        and deterministic_gate
        and not missing_agents
    )

    packet = _packet(
        agent="REVIEW_COUNCIL",
        task="stockfish_review_council_integrity",
        observed={
            "protocol_ok": protocol_ok,
            "declared_agent_count": len(agent_ids),
            "missing_required_agents": missing_agents,
            "merge_authority_disabled": merge_authority_ok,
            "release_authority_disabled": release_authority_ok,
            "workflow_present": workflow_present,
            "contents_read_only": read_only,
            "deterministic_verdict_gate": deterministic_gate,
        },
        evidence=(registry_path, workflow_path, "src/cmb_agents/review_council.py"),
        confidence=1.0,
        recommended_action=(
            "CMB-SRC-1 registry, workflow, deterministic gate, and authority boundaries are aligned."
            if ok
            else "Repair review-council registry/workflow drift before relying on automated PR review."
        ),
        severity="info" if ok else "error",
    )
    return AgentAudit(
        "REVIEW_COUNCIL",
        ok,
        f"protocol={'ok' if protocol_ok else 'invalid'}; missing_agents={len(missing_agents)}.",
        packet,
    )

def review_packets(audits: tuple[AgentAudit, ...]) -> AgentAudit:
    """Review specialist outputs for authority escalation and ungrounded self-certification."""

    unsafe = sorted(
        audit.name
        for audit in audits
        if audit.packet.authority not in _SAFE_AUTHORITIES
    )
    high_risk_claims = sorted(
        audit.name
        for audit in audits
        if audit.packet.observed.get("external_gates_authoritatively_checked") is True
    )
    ok = not unsafe and not high_risk_claims

    packet = _packet(
        agent="REVIEWER",
        task="agent_evidence_packet_review",
        observed={
            "audits_reviewed": [audit.name for audit in audits],
            "unsafe_authority_packets": unsafe,
            "external_self_certification_packets": high_risk_claims,
            "failing_specialists": [audit.name for audit in audits if not audit.ok],
        },
        evidence=("structured evidence packets",),
        confidence=1.0,
        recommended_action=(
            "Specialist agents remain within read-only/propose-only authority."
            if ok
            else "Reject the agent output until authority escalation or self-certification is removed."
        ),
        severity="info" if ok else "error",
    )
    return AgentAudit(
        "REVIEWER",
        ok,
        f"reviewed={len(audits)}; unsafe_authority={len(unsafe)}; self_certification={len(high_risk_claims)}.",
        packet,
    )


def run_specialist_audits(root: Path) -> tuple[AgentAudit, ...]:
    """Run all read-only specialist agents and finish with an authority reviewer."""

    audits = (
        audit_canon(root),
        audit_accessibility(root),
        audit_release(root),
        audit_librarian(root),
        audit_archaeologist(root),
        audit_discovery(root),
        audit_security(root),
        audit_dnis(root),
        audit_review_council(root),
    )
    return (*audits, review_packets(audits))
