from collections import Counter
from pathlib import Path

from cmb_agents.philosophy_swarm import (
    AGENT_COUNT,
    DENIED_ACTIONS,
    GUILD_COUNT,
    GUILD_SIZE,
    build_swarm,
    run_swarm,
)


def test_swarm_has_exactly_333_unique_agents() -> None:
    swarm = build_swarm()

    assert len(swarm) == AGENT_COUNT == 333
    assert len({agent.agent_id for agent in swarm}) == 333
    assert swarm[0].agent_id == "CMB-PS-001"
    assert swarm[-1].agent_id == "CMB-PS-333"


def test_swarm_has_nine_equal_specialist_guilds() -> None:
    counts = Counter(agent.guild_id for agent in build_swarm())

    assert len(counts) == GUILD_COUNT == 9
    assert set(counts.values()) == {GUILD_SIZE}
    assert GUILD_COUNT * GUILD_SIZE == AGENT_COUNT


def test_authority_envelope_blocks_self_escalation_and_publication() -> None:
    report = run_swarm("CMB human agency and provenance")

    assert "self_modify_authority" in DENIED_ACTIONS
    assert "integrate_repository_changes" in DENIED_ACTIONS
    assert "inspect_or_expose_credentials" in DENIED_ACTIONS
    assert "unsolicited_distribution" in DENIED_ACTIONS
    assert report["authority"]["may_modify_own_authority"] is False
    assert report["authority"]["may_publish_externally"] is False
    assert report["authority"]["may_integrate_repository_changes"] is False
    assert report["authority"]["may_inspect_credentials"] is False
    assert report["authority"]["human_final_authority"] is True


def test_relevant_seed_elects_one_proposal_per_guild() -> None:
    report = run_swarm("CMB philosophy: pattern, proof, consent, agency, and meaning")

    assert report["relevant"] is True
    assert report["summary"]["elected_guild_proposals"] == 9
    assert len(report["agent_decisions"]) == 333
    assert all(proposal["requires_human_review"] for proposal in report["elected_proposals"])


def test_irrelevant_seed_preserves_position() -> None:
    report = run_swarm("banana bread recipe")

    assert report["relevant"] is False
    assert report["summary"]["elected_guild_proposals"] == 0
    assert report["summary"]["action_counts"] == {"preserve_position": 333}


def test_swarm_report_is_deterministic_without_model_assist() -> None:
    seed = "CMB human agency, model boundaries, and cognitive sovereignty"

    first = run_swarm(seed)
    second = run_swarm(seed)

    assert first == second
    assert first["sha256_receipt"] == second["sha256_receipt"]


def test_repo_grounded_run_records_validated_evidence() -> None:
    report = run_swarm(
        "CMB human agency, evidence, and cognitive sovereignty",
        repo_root=Path("."),
    )

    assert report["evidence_state"] == "validated"
    assert report["summary"]["validated_evidence_records"] == 27
    assert len(report["evidence"]) == 9
    assert all(
        record["sha256"] and record["excerpt"]
        for records in report["evidence"].values()
        for record in records
    )
