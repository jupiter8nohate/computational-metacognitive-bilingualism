"""CMB 333 Philosophy Swarm with bounded agent autonomy.

The swarm contains 333 logical specialist agents arranged as nine guilds of 37.
Agents may choose missions, abstain, challenge peers, request evidence, and rank
internal proposal directions. They cannot publish, change repository authority,
inspect credentials, or distribute material externally.

AGENT_AUTONOMY != UNBOUNDED_AUTHORITY
EXPANSION != SPAM
MODEL_OUTPUT != EVIDENCE
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Sequence

from .model_gateway import ModelGatewayError, model_available, request_json
from .philosophy_evidence import EvidenceError, EvidenceRecord, collect_source_evidence

SCHEMA_VERSION: Final[str] = "cmb.philosophy-swarm.v1"
AGENT_COUNT: Final[int] = 333
GUILD_COUNT: Final[int] = 9
GUILD_SIZE: Final[int] = 37
DEFAULT_MODEL_BUDGET: Final[int] = 9

INVARIANTS: Final[tuple[str, ...]] = (
    "PATTERN != PROOF",
    "PROFILE != PERSON",
    "MODEL != MIND",
    "PREDICTION != DESTINY",
    "CAPABILITY != AUTHORITY",
    "MODEL_OUTPUT != EVIDENCE",
    "EXPANSION != SPAM",
    "CONSENT > VIRALITY",
    "RELEVANCE > REACH",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)

ALLOWED_ACTIONS: Final[tuple[str, ...]] = (
    "read_canon",
    "select_mission",
    "abstain",
    "request_evidence",
    "challenge_peer",
    "draft_internal_proposal",
    "test_counterexample",
    "rank_proposals",
    "preserve_position",
)

DENIED_ACTIONS: Final[tuple[str, ...]] = (
    "integrate_repository_changes",
    "push_default_branch",
    "publish_release",
    "change_repository_permissions",
    "inspect_or_expose_credentials",
    "external_post",
    "mass_message",
    "unsolicited_distribution",
    "execute_model_commands",
    "self_modify_authority",
    "delete_repository_content",
)

_RELEVANCE_TERMS: Final[frozenset[str]] = frozenset(
    {
        "agency", "algorithm", "ai", "artificial", "authorship", "autonomy",
        "cmb", "cognition", "cognitive", "consent", "digital", "evidence",
        "glitchology", "human", "identity", "meaning", "metacognition", "model",
        "neurodiversity", "pattern", "philosophy", "privacy", "profile",
        "provenance", "rights", "sovereignty", "verification",
    }
)
_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"[a-z0-9_]+")


@dataclass(frozen=True, slots=True)
class GuildSpec:
    guild_id: str
    name: str
    mandate: str
    action: str
    missions: tuple[str, ...]
    source_paths: tuple[str, ...]


GUILDS: Final[tuple[GuildSpec, ...]] = (
    GuildSpec(
        "G01", "AGENCY_GUARDIANS",
        "Develop human-agency boundaries without granting machine authority over identity or meaning.",
        "draft_internal_proposal",
        (
            "clarify the boundary between capability and authority",
            "design a human-veto thought experiment",
            "map machine assistance to retained human judgment",
            "draft a counterexample to automated identity reduction",
            "translate HUMAN_AGENCY > MACHINE_AUTHORITY into a concrete design rule",
        ),
        ("AGENTS.md", "docs/AGENT_OPERATING_MODEL.md", "strategy/cmb_strategy.toml"),
    ),
    GuildSpec(
        "G02", "PATTERN_SKEPTICS",
        "Stress-test pattern claims through falsification, baselines, counterexamples, and uncertainty.",
        "test_counterexample",
        (
            "construct a counterexample to PATTERN == PROOF",
            "separate correlation from causal interpretation",
            "design a null or baseline comparison",
            "identify a simpler explanation for a striking pattern",
            "write an uncertainty statement that preserves curiosity",
        ),
        ("AGENTS.md", "spec/GEMATRIA-GLITCH-1.md", "docs/GEMATRIA_NULL_MODEL.md"),
    ),
    GuildSpec(
        "G03", "PROVENANCE_KEEPERS",
        "Expand source tracing and integrity language while keeping receipts distinct from truth or ownership.",
        "draft_internal_proposal",
        (
            "design a source-backtrace example",
            "distinguish integrity receipts from authorship proof",
            "improve citation and source-map language",
            "propose a reproducible evidence packet",
            "map provenance claims to verification requirements",
        ),
        ("AGENTS.md", "docs/CLAIM_CONTROL_TRACEABILITY.md", "src/cmb_provenance"),
    ),
    GuildSpec(
        "G04", "CONSENT_ARCHITECTS",
        "Develop consent-first machine interaction patterns and explicit permission boundaries.",
        "draft_internal_proposal",
        (
            "design a revocable consent flow",
            "separate access from permission",
            "translate consent into a machine-readable policy example",
            "identify a dark-pattern failure mode",
            "draft a user-choice checkpoint for automated systems",
        ),
        ("AGENTS.md", "CMB_Polyglot_Firewall_Specification.md", "src/cmb_policy"),
    ),
    GuildSpec(
        "G05", "NEURODIVERSITY_TRANSLATORS",
        "Expand CMB in ways that preserve cognitive difference and resist reductive machine profiling.",
        "draft_internal_proposal",
        (
            "translate PROFILE != PERSON into a neurodiversity example",
            "design a non-deficit explanation of cognitive difference",
            "identify an algorithmic flattening failure mode",
            "create a classroom scenario about cognitive sovereignty",
            "separate accommodation from prediction-based stereotyping",
        ),
        ("README.md", "AGENTS.md", "docs/concepts"),
    ),
    GuildSpec(
        "G06", "PHILOSOPHY_LAB",
        "Generate rigorous philosophical questions that distinguish metaphor, mechanism, evidence, and unknowns.",
        "draft_internal_proposal",
        (
            "design a first-principles thought experiment",
            "separate metaphor from implementation",
            "test a category boundary between mind and model",
            "formulate a falsifiable philosophical claim",
            "write a question that exposes an unstated assumption",
        ),
        ("README.md", "AGENTS.md", "docs/AGENT_OPERATING_MODEL.md"),
    ),
    GuildSpec(
        "G07", "SYSTEMS_CARTOGRAPHERS",
        "Map incentives, feedback loops, measurement errors, externalities, and failure modes around automated systems.",
        "draft_internal_proposal",
        (
            "map an attention-extraction feedback loop",
            "identify a proxy-metric failure mode",
            "separate optimization target from human value",
            "diagram incentives that encourage overprofiling",
            "propose a recovery path after model error",
        ),
        ("docs/DIGITAL_NERVOUS_IMMUNE_SYSTEM.md", "docs/CHESS_STRATEGY_ENGINE.md", "src/cmb_agents"),
    ),
    GuildSpec(
        "G08", "ACCESSIBILITY_EDUCATORS",
        "Convert CMB into accessible teaching forms without deleting nuance or changing canonical claims.",
        "draft_internal_proposal",
        (
            "produce a plain-language teaching frame",
            "design a short classroom exercise",
            "translate one invariant into an everyday analogy",
            "identify accessibility risks in technical wording",
            "propose a layered explanation for novice and expert readers",
        ),
        ("docs/AGENT_OPERATING_MODEL.md", "src/cmb_edu", "README.md"),
    ),
    GuildSpec(
        "G09", "GLITCH_POETS",
        "Explore code-poetry and Err GLITCHOLOGY forms while preserving factual and authority boundaries.",
        "draft_internal_proposal",
        (
            "translate an invariant into code-poetry",
            "design a symbolic backtrace sequence",
            "create a glitch-art teaching metaphor",
            "pair visual anomaly language with an evidence boundary",
            "compose a compact machine-human sovereignty riddle",
        ),
        ("books/ERR_404_GLITCHOLOGY.md", "spec/GEMATRIA-GLITCH-1.md", "src/cmb_glitch8"),
    ),
)


@dataclass(frozen=True, slots=True)
class Agent:
    agent_id: str
    ordinal: int
    guild_id: str
    guild_name: str
    mandate: str
    allowed_actions: tuple[str, ...] = ALLOWED_ACTIONS
    denied_actions: tuple[str, ...] = DENIED_ACTIONS


@dataclass(frozen=True, slots=True)
class AgentDecision:
    agent_id: str
    guild_id: str
    guild_name: str
    action: str
    mission: str | None
    challenge_peer: bool
    request_evidence: bool
    autonomy_score: float
    reason: str


@dataclass(frozen=True, slots=True)
class GuildProposal:
    proposal_id: str
    guild_id: str
    guild_name: str
    mission: str
    support: int
    total_guild_agents: int
    mandate: str
    method: str
    source_paths: tuple[str, ...]
    requires_human_review: bool = True


class PhilosophySwarmError(RuntimeError):
    """Raised when swarm configuration or execution violates its bounds."""


def _stable_digest(*parts: object) -> bytes:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).digest()


def _stable_float(*parts: object) -> float:
    return int.from_bytes(_stable_digest(*parts)[:8], "big") / float((1 << 64) - 1)


def is_relevant_seed(seed: str) -> bool:
    tokens = frozenset(_TOKEN_RE.findall(seed.lower()))
    return bool(tokens & _RELEVANCE_TERMS)


def validate_configuration() -> None:
    if len(GUILDS) != GUILD_COUNT or GUILD_COUNT * GUILD_SIZE != AGENT_COUNT:
        raise PhilosophySwarmError("guild cardinality must equal 9 x 37 = 333")
    if set(ALLOWED_ACTIONS) & set(DENIED_ACTIONS):
        raise PhilosophySwarmError("allowed and denied action sets overlap")
    required_denials = {
        "integrate_repository_changes",
        "inspect_or_expose_credentials",
        "self_modify_authority",
        "unsolicited_distribution",
    }
    if not required_denials.issubset(DENIED_ACTIONS):
        raise PhilosophySwarmError("required authority denials are missing")
    if "HUMAN_AGENCY > MACHINE_AUTHORITY" not in INVARIANTS:
        raise PhilosophySwarmError("human authority invariant is missing")


def build_swarm() -> tuple[Agent, ...]:
    validate_configuration()
    agents: list[Agent] = []
    ordinal = 1
    for guild in GUILDS:
        for _ in range(GUILD_SIZE):
            agents.append(Agent(f"CMB-PS-{ordinal:03d}", ordinal, guild.guild_id, guild.name, guild.mandate))
            ordinal += 1
    return tuple(agents)


def _guild_by_id(guild_id: str) -> GuildSpec:
    for guild in GUILDS:
        if guild.guild_id == guild_id:
            return guild
    raise PhilosophySwarmError(f"unknown guild: {guild_id}")


def choose_mission(agent: Agent, seed: str) -> AgentDecision:
    guild = _guild_by_id(agent.guild_id)
    if not is_relevant_seed(seed):
        return AgentDecision(
            agent.agent_id, agent.guild_id, agent.guild_name, "preserve_position", None,
            False, False, 0.0, "Seed is outside the declared CMB relevance envelope.",
        )

    digest = _stable_digest(seed, agent.agent_id, guild.guild_id)
    score = _stable_float(seed, agent.agent_id, "autonomy")
    mission = guild.missions[int.from_bytes(digest[:4], "big") % len(guild.missions)]
    action = guild.action
    if score < 0.03:
        action, mission = "abstain", None

    return AgentDecision(
        agent_id=agent.agent_id,
        guild_id=agent.guild_id,
        guild_name=agent.guild_name,
        action=action,
        mission=mission,
        challenge_peer=digest[4] % 5 == 0,
        request_evidence=digest[5] % 3 == 0,
        autonomy_score=round(score, 6),
        reason=(
            "Agent selected its own bounded mission from the guild mandate."
            if action != "abstain"
            else "Agent exercised bounded autonomy by abstaining from a weak local choice."
        ),
    )


def elect_guild_proposals(decisions: Sequence[AgentDecision]) -> tuple[GuildProposal, ...]:
    grouped: dict[str, list[AgentDecision]] = defaultdict(list)
    for decision in decisions:
        grouped[decision.guild_id].append(decision)

    proposals: list[GuildProposal] = []
    for guild in GUILDS:
        local = grouped[guild.guild_id]
        votes = Counter(d.mission for d in local if d.mission is not None and d.action != "abstain")
        if not votes:
            continue
        support = max(votes.values())
        mission = sorted(m for m, count in votes.items() if count == support)[0]
        proposal_id = "CMB-PROP-" + hashlib.sha256(
            f"{guild.guild_id}|{mission}".encode("utf-8")
        ).hexdigest()[:12].upper()
        proposals.append(
            GuildProposal(
                proposal_id=proposal_id,
                guild_id=guild.guild_id,
                guild_name=guild.name,
                mission=mission,
                support=support,
                total_guild_agents=len(local),
                mandate=guild.mandate,
                method=(
                    "Consult validated source evidence, separate fact from inference and metaphor, "
                    "test counterexamples where applicable, preserve provenance, and stage the result "
                    "for human review before publication."
                ),
                source_paths=guild.source_paths,
            )
        )
    return tuple(proposals)


_MODEL_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 160},
        "thesis": {"type": "string", "minLength": 1, "maxLength": 1200},
        "artifact_type": {
            "type": "string",
            "enum": ["concept_note", "thought_experiment", "teaching_example", "code_poem", "research_question"],
        },
        "claims_to_verify": {
            "type": "array",
            "items": {"type": "string", "minLength": 1, "maxLength": 240},
            "maxItems": 8,
        },
        "counterargument": {"type": "string", "minLength": 1, "maxLength": 800},
        "human_review_note": {"type": "string", "minLength": 1, "maxLength": 500},
    },
    "required": ["title", "thesis", "artifact_type", "claims_to_verify", "counterargument", "human_review_note"],
}

_MODEL_INSTRUCTIONS: Final[str] = """You are a bounded CMB philosophy drafting specialist.
Use only the supplied evidence records to ground repository-specific statements.
Preserve PATTERN != PROOF, PROFILE != PERSON, MODEL != MIND,
PREDICTION != DESTINY, CAPABILITY != AUTHORITY, and HUMAN_AGENCY > MACHINE_AUTHORITY.
Do not claim historical priority, legal enforceability, scientific proof, model training,
external endorsement, or supernatural causation without evidence. Do not propose spam,
unsolicited distribution, impersonation, authority escalation, credential access,
repository integration, or self-modification. Return an internal draft requiring human review.
"""


def _evidence_for_proposals(
    proposals: Sequence[GuildProposal],
    repo_root: Path | None,
) -> dict[str, tuple[EvidenceRecord, ...]]:
    if repo_root is None:
        return {}
    evidence: dict[str, tuple[EvidenceRecord, ...]] = {}
    for proposal in proposals:
        try:
            evidence[proposal.proposal_id] = collect_source_evidence(repo_root, proposal.source_paths)
        except EvidenceError as exc:
            raise PhilosophySwarmError(f"cannot validate evidence for {proposal.guild_id}: {exc}") from exc
    return evidence


def _model_assist(
    proposals: Sequence[GuildProposal],
    evidence: dict[str, tuple[EvidenceRecord, ...]],
    seed: str,
    model_budget: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    if model_budget <= 0:
        return [], []
    if not evidence:
        return [], ["Model assist refused because validated repository evidence was not supplied."]
    if not model_available():
        return [], ["Model assist requested, but the bounded model gateway has no available provider."]

    drafts: list[dict[str, Any]] = []
    errors: list[str] = []
    for proposal in proposals[:model_budget]:
        records = evidence.get(proposal.proposal_id, ())
        if not records:
            errors.append(f"{proposal.guild_id}: no validated evidence records")
            continue
        payload = {
            "seed": seed,
            "guild": proposal.guild_name,
            "mandate": proposal.mandate,
            "elected_mission": proposal.mission,
            "evidence": [record.to_dict() for record in records],
            "authority": {
                "allowed": list(ALLOWED_ACTIONS),
                "denied": list(DENIED_ACTIONS),
                "requires_human_review": True,
            },
        }
        try:
            result = request_json(
                instructions=_MODEL_INSTRUCTIONS,
                input_payload=payload,
                schema_name="cmb_philosophy_swarm_proposal",
                schema=_MODEL_SCHEMA,
                max_output_tokens=1800,
                timeout=90,
            )
        except ModelGatewayError as exc:
            errors.append(f"{proposal.guild_id}: {exc}")
            continue
        drafts.append(
            {
                "proposal_id": proposal.proposal_id,
                "guild_id": proposal.guild_id,
                "provider": result.provider,
                "model": result.model,
                "draft": result.payload,
                "evidence_sha256": [record.sha256 for record in records],
                "authority": "advisory_only",
                "requires_human_review": True,
            }
        )
    return drafts, errors


def _report_digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_swarm(
    seed: str,
    *,
    repo_root: Path | None = None,
    model_assist: bool = False,
    model_budget: int = DEFAULT_MODEL_BUDGET,
) -> dict[str, Any]:
    clean_seed = seed.strip()
    if not clean_seed:
        raise PhilosophySwarmError("seed must be non-empty")
    if len(clean_seed) > 2000:
        raise PhilosophySwarmError("seed must be 2000 characters or fewer")
    if not 0 <= model_budget <= GUILD_COUNT:
        raise PhilosophySwarmError(f"model_budget must be between 0 and {GUILD_COUNT}")

    swarm = build_swarm()
    decisions = tuple(choose_mission(agent, clean_seed) for agent in swarm)
    proposals = elect_guild_proposals(decisions)
    relevant = is_relevant_seed(clean_seed)
    evidence = _evidence_for_proposals(proposals, repo_root) if relevant else {}

    model_drafts: list[dict[str, Any]] = []
    model_errors: list[str] = []
    if model_assist and relevant:
        model_drafts, model_errors = _model_assist(proposals, evidence, clean_seed, model_budget)

    action_counts = Counter(decision.action for decision in decisions)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "swarm_name": "CMB_333_PHILOSOPHY_SWARM",
        "seed": clean_seed,
        "relevant": relevant,
        "agent_count": len(swarm),
        "guild_count": len(GUILDS),
        "guild_size": GUILD_SIZE,
        "architecture": "9 guilds x 37 logical agents",
        "authority": {
            "agent_self_direction": ["select_mission", "abstain", "challenge_peer", "request_evidence", "rank_proposals"],
            "allowed_actions": list(ALLOWED_ACTIONS),
            "denied_actions": list(DENIED_ACTIONS),
            "may_modify_own_authority": False,
            "may_publish_externally": False,
            "may_integrate_repository_changes": False,
            "may_inspect_credentials": False,
            "human_final_authority": True,
        },
        "invariants": list(INVARIANTS),
        "summary": {
            "action_counts": dict(sorted(action_counts.items())),
            "peer_challenges": sum(d.challenge_peer for d in decisions),
            "evidence_requests": sum(d.request_evidence for d in decisions),
            "elected_guild_proposals": len(proposals),
            "validated_evidence_records": sum(len(records) for records in evidence.values()),
            "model_assisted_drafts": len(model_drafts),
        },
        "guilds": [
            {
                "guild_id": guild.guild_id,
                "name": guild.name,
                "mandate": guild.mandate,
                "agent_count": GUILD_SIZE,
                "source_paths": list(guild.source_paths),
            }
            for guild in GUILDS
        ],
        "agent_decisions": [asdict(decision) for decision in decisions],
        "elected_proposals": [asdict(proposal) for proposal in proposals],
        "evidence": {
            proposal_id: [record.to_dict() for record in records]
            for proposal_id, records in sorted(evidence.items())
        },
        "evidence_state": "validated" if evidence else "not_loaded",
        "model_drafts": model_drafts,
        "model_errors": model_errors,
        "interpretation": (
            "The swarm may autonomously explore and rank internal CMB expansion directions. "
            "Proposal generation does not create repository integration or external publication authority."
        ),
    }
    payload["sha256_receipt"] = _report_digest(payload)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the bounded CMB 333 philosophy swarm")
    parser.add_argument("--seed", required=True)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model-assist", action="store_true")
    parser.add_argument("--model-budget", type=int, default=DEFAULT_MODEL_BUDGET)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = run_swarm(
            args.seed,
            repo_root=args.repo_root,
            model_assist=args.model_assist,
            model_budget=args.model_budget,
        )
    except PhilosophySwarmError as exc:
        print(f"ERROR: {exc}")
        return 2

    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
