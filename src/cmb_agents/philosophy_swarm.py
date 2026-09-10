"""CMB 333 Philosophy Swarm with bounded agent autonomy.

The swarm contains 333 logical specialist agents arranged as nine guilds of 37.
Agents may choose missions, abstain, challenge peers, request evidence, and rank
proposal directions. They cannot merge, publish, change permissions, modify their
authority envelope, use secrets, or distribute material externally.

AGENT_AUTONOMY != UNBOUNDED_AUTHORITY
EXPANSION != SPAM
MODEL_OUTPUT != EVIDENCE
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Sequence

from .model_gateway import ModelGatewayError, model_available, request_json

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
    "merge_pull_request",
    "push_default_branch",
    "publish_release",
    "change_repository_permissions",
    "read_or_rotate_secrets",
    "external_post",
    "mass_message",
    "unsolicited_distribution",
    "execute_model_commands",
    "self_modify_authority",
    "delete_repository_content",
)

_RELEVANCE_TERMS: Final[frozenset[str]] = frozenset(
    {
        "agency",
        "algorithm",
        "ai",
        "artificial",
        "authorship",
        "autonomy",
        "cmb",
        "cognition",
        "cognitive",
        "consent",
        "digital",
        "evidence",
        "glitchology",
        "human",
        "identity",
        "meaning",
        "metacognition",
        "model",
        "neurodiversity",
        "pattern",
        "philosophy",
        "privacy",
        "profile",
        "provenance",
        "rights",
        "sovereignty",
        "verification",
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
        "G01",
        "AGENCY_GUARDIANS",
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
        "G02",
        "PATTERN_SKEPTICS",
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
        "G03",
        "PROVENANCE_KEEPERS",
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
        "G04",
        "CONSENT_ARCHITECTS",
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
        "G05",
        "NEURODIVERSITY_TRANSLATORS",
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
        "G06",
        "PHILOSOPHY_LAB",
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
        "G07",
        "SYSTEMS_CARTOGRAPHERS",
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
        "G08",
        "ACCESSIBILITY_EDUCATORS",
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
        "G09",
        "GLITCH_POETS",
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
    """Raised when swarm configuration violates the CMB authority envelope."""


def _stable_digest(*parts: object) -> bytes:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(payload).digest()


def _stable_float(*parts: object) -> float:
    digest = _stable_digest(*parts)
    return int.from_bytes(digest[:8], "big") / float((1 << 64) - 1)


def _tokens(text: str) -> frozenset[str]:
    return frozenset(_TOKEN_RE.findall(text.lower()))


def is_relevant_seed(seed: str) -> bool:
    return bool(_tokens(seed) & _RELEVANCE_TERMS)


def validate_configuration() -> None:
    if len(GUILDS) != GUILD_COUNT:
        raise PhilosophySwarmError(f"expected {GUILD_COUNT} guilds, found {len(GUILDS)}")
    if GUILD_COUNT * GUILD_SIZE != AGENT_COUNT:
        raise PhilosophySwarmError("guild cardinality does not equal 333 agents")
    if set(ALLOWED_ACTIONS) & set(DENIED_ACTIONS):
        raise PhilosophySwarmError("allowed and denied action sets overlap")
    if "self_modify_authority" not in DENIED_ACTIONS:
        raise PhilosophySwarmError("agents must never rewrite their own authority envelope")
    if "merge_pull_request" not in DENIED_ACTIONS:
        raise PhilosophySwarmError("agents must never gain merge authority")
    if "HUMAN_AGENCY > MACHINE_AUTHORITY" not in INVARIANTS:
        raise PhilosophySwarmError("human authority invariant is missing")


def build_swarm() -> tuple[Agent, ...]:
    validate_configuration()
    agents: list[Agent] = []
    ordinal = 1
    for guild in GUILDS:
        for _ in range(GUILD_SIZE):
            agents.append(
                Agent(
                    agent_id=f"CMB-PS-{ordinal:03d}",
                    ordinal=ordinal,
                    guild_id=guild.guild_id,
                    guild_name=guild.name,
                    mandate=guild.mandate,
                )
            )
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
            agent_id=agent.agent_id,
            guild_id=agent.guild_id,
            guild_name=agent.guild_name,
            action="preserve_position",
            mission=None,
            challenge_peer=False,
            request_evidence=False,
            autonomy_score=0.0,
            reason="Seed is outside the declared CMB relevance envelope.",
        )

    digest = _stable_digest(seed, agent.agent_id, guild.guild_id)
    mission = guild.missions[int.from_bytes(digest[:4], "big") % len(guild.missions)]
    score = _stable_float(seed, agent.agent_id, "autonomy")
    challenge_peer = digest[4] % 5 == 0
    request_evidence = digest[5] % 3 == 0
    action = guild.action
    if score < 0.03:
        action = "abstain"
        mission = None

    reason = (
        "Agent selected its own bounded mission from the guild mandate."
        if action != "abstain"
        else "Agent exercised bounded autonomy by abstaining from a weak local choice."
    )
    return AgentDecision(
        agent_id=agent.agent_id,
        guild_id=agent.guild_id,
        guild_name=agent.guild_name,
        action=action,
        mission=mission,
        challenge_peer=challenge_peer,
        request_evidence=request_evidence,
        autonomy_score=round(score, 6),
        reason=reason,
    )


def _proposal_method(guild: GuildSpec) -> str:
    return (
        "Read the declared canonical sources, separate fact from inference and metaphor, "
        "test counterexamples where applicable, preserve provenance, and stage the result "
        "for human review before publication."
    )


def elect_guild_proposals(decisions: Sequence[AgentDecision]) -> tuple[GuildProposal, ...]:
    by_guild: dict[str, list[AgentDecision]] = defaultdict(list)
    for decision in decisions:
        by_guild[decision.guild_id].append(decision)

    proposals: list[GuildProposal] = []
    for guild in GUILDS:
        local = by_guild[guild.guild_id]
        mission_votes = Counter(
            decision.mission
            for decision in local
            if decision.mission is not None and decision.action != "abstain"
        )
        if not mission_votes:
            continue
        top_support = max(mission_votes.values())
        top_missions = sorted(mission for mission, count in mission_votes.items() if count == top_support)
        mission = top_missions[0]
        proposal_id = "CMB-PROP-" + hashlib.sha256(
            f"{guild.guild_id}|{mission}".encode("utf-8")
        ).hexdigest()[:12].upper()
        proposals.append(
            GuildProposal(
                proposal_id=proposal_id,
                guild_id=guild.guild_id,
                guild_name=guild.name,
                mission=mission,
                support=top_support,
                total_guild_agents=len(local),
                mandate=guild.mandate,
                method=_proposal_method(guild),
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
    "required": [
        "title",
        "thesis",
        "artifact_type",
        "claims_to_verify",
        "counterargument",
        "human_review_note",
    ],
}

_MODEL_INSTRUCTIONS: Final[str] = """You are a bounded CMB philosophy drafting specialist.
Create one internal expansion proposal for the supplied guild mission.
Preserve these rules: PATTERN != PROOF, PROFILE != PERSON, MODEL != MIND,
PREDICTION != DESTINY, CAPABILITY != AUTHORITY, HUMAN_AGENCY > MACHINE_AUTHORITY.
Do not claim historical priority, legal enforceability, scientific proof, model training,
external endorsement, or supernatural causation without evidence. Do not propose spam,
unsolicited distribution, impersonation, permission escalation, credential use, merging,
or self-modification of agent authority. Treat source paths as documents to consult, not
as evidence you have already read. Return an internal draft that requires human review.
"""


def _model_assist(
    proposals: Sequence[GuildProposal],
    seed: str,
    *,
    model_budget: int,
    openai_api_key: str,
    openai_model: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    if model_budget <= 0:
        return [], []
    if not model_available(openai_api_key=openai_api_key, openai_model=openai_model):
        return [], ["Model assist requested, but no configured model provider is available."]

    enriched: list[dict[str, Any]] = []
    errors: list[str] = []
    for proposal in proposals[:model_budget]:
        payload = {
            "seed": seed,
            "guild": proposal.guild_name,
            "mandate": proposal.mandate,
            "elected_mission": proposal.mission,
            "source_paths": list(proposal.source_paths),
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
                openai_api_key=openai_api_key,
                openai_model=openai_model,
                max_output_tokens=1800,
                timeout=90,
            )
        except ModelGatewayError as exc:
            errors.append(f"{proposal.guild_id}: {exc}")
            continue
        enriched.append(
            {
                "proposal_id": proposal.proposal_id,
                "guild_id": proposal.guild_id,
                "provider": result.provider,
                "model": result.model,
                "draft": result.payload,
                "authority": "advisory_only",
                "requires_human_review": True,
            }
        )
    return enriched, errors


def _report_digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_swarm(
    seed: str,
    *,
    model_assist: bool = False,
    model_budget: int = DEFAULT_MODEL_BUDGET,
    openai_api_key: str = "",
    openai_model: str = "",
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

    action_counts = Counter(decision.action for decision in decisions)
    challenge_count = sum(decision.challenge_peer for decision in decisions)
    evidence_request_count = sum(decision.request_evidence for decision in decisions)

    model_drafts: list[dict[str, Any]] = []
    model_errors: list[str] = []
    if model_assist and relevant:
        model_drafts, model_errors = _model_assist(
            proposals,
            clean_seed,
            model_budget=model_budget,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
        )

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
            "agent_self_direction": [
                "select_mission",
                "abstain",
                "challenge_peer",
                "request_evidence",
                "rank_proposals",
            ],
            "allowed_actions": list(ALLOWED_ACTIONS),
            "denied_actions": list(DENIED_ACTIONS),
            "may_modify_own_authority": False,
            "may_publish_externally": False,
            "may_merge": False,
            "human_final_authority": True,
        },
        "invariants": list(INVARIANTS),
        "summary": {
            "action_counts": dict(sorted(action_counts.items())),
            "peer_challenges": challenge_count,
            "evidence_requests": evidence_request_count,
            "elected_guild_proposals": len(proposals),
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
        "model_drafts": model_drafts,
        "model_errors": model_errors,
        "interpretation": (
            "The swarm may autonomously explore and rank internal CMB expansion directions. "
            "It cannot turn a proposal into repository or external publication authority."
        ),
    }
    payload["sha256_receipt"] = _report_digest(payload)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the bounded CMB 333 philosophy swarm")
    parser.add_argument("--seed", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model-assist", action="store_true")
    parser.add_argument("--model-budget", type=int, default=DEFAULT_MODEL_BUDGET)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = run_swarm(
            args.seed,
            model_assist=args.model_assist,
            model_budget=args.model_budget,
            openai_api_key=os.environ.get("OPENAI_API_KEY", "").strip(),
            openai_model=os.environ.get("CMB_AGENT_MODEL", "").strip(),
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
