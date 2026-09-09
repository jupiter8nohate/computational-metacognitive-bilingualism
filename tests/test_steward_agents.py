from __future__ import annotations

from pathlib import Path

import pytest

from cmb_agents import steward


def test_ai_edit_policy_blocks_authority_and_workflow_paths() -> None:
    assert steward.is_ai_editable_path("src/cmb_glitch8/glitch_ir.py")
    assert steward.is_ai_editable_path("docs/GLITCH8_REGISTRY.md")
    assert steward.is_ai_editable_path("README.md")

    assert not steward.is_ai_editable_path(".github/workflows/ci.yml")
    assert not steward.is_ai_editable_path("tests/test_glitch8.py")
    assert not steward.is_ai_editable_path("schemas/glitch-ir.v1.schema.json")
    assert not steward.is_ai_editable_path("machine/glitch-ir.json")
    assert not steward.is_ai_editable_path("SECURITY.md")
    assert not steward.is_ai_editable_path("pyproject.toml")
    assert not steward.is_ai_editable_path("src/cmb_agents/steward.py")
    assert not steward.is_ai_editable_path("../outside.txt")


def test_extract_output_text_accepts_responses_output_shape() -> None:
    payload = {
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": '{"summary":"ok","rationale":"test","edits":[]}',
                    }
                ],
            }
        ]
    }
    assert steward._extract_output_text(payload).startswith('{"summary"')


def test_apply_repair_plan_requires_supplied_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    target = root / "src" / "cmb_glitch8" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("OLD = True\n", encoding="utf-8")

    monkeypatch.setattr(steward, "ROOT", root)

    plan = {
        "summary": "repair",
        "rationale": "test",
        "edits": [
            {
                "path": "src/cmb_glitch8/example.py",
                "content": "OLD = False\n",
                "reason": "test repair",
            }
        ],
    }

    changed = steward.apply_repair_plan(
        plan,
        {"src/cmb_glitch8/example.py": "OLD = True\n"},
    )

    assert changed == ("src/cmb_glitch8/example.py",)
    assert target.read_text(encoding="utf-8") == "OLD = False\n"


def test_apply_repair_plan_rejects_protected_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    target = root / "tests" / "test_example.py"
    target.parent.mkdir(parents=True)
    target.write_text("assert True\n", encoding="utf-8")
    monkeypatch.setattr(steward, "ROOT", root)

    with pytest.raises(steward.StewardError, match="protected path|outside supplied context"):
        steward.apply_repair_plan(
            {
                "summary": "bad",
                "rationale": "bad",
                "edits": [
                    {
                        "path": "tests/test_example.py",
                        "content": "assert False\n",
                        "reason": "weaken test",
                    }
                ],
            },
            {"tests/test_example.py": "assert True\n"},
        )


def test_plan_edit_count_is_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    monkeypatch.setattr(steward, "ROOT", root)

    edits = []
    context = {}
    for index in range(steward._MAX_EDITS + 1):
        relative = f"docs/file-{index}.md"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("old\n", encoding="utf-8")
        context[relative] = "old\n"
        edits.append({"path": relative, "content": "new\n", "reason": "test"})

    with pytest.raises(steward.StewardError, match="exceeds"):
        steward.apply_repair_plan(
            {"summary": "too many", "rationale": "test", "edits": edits},
            context,
        )


def test_public_status_writer_emits_machine_and_human_views(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(steward, "ROOT", tmp_path)
    report = steward.AuditReport(
        roles=("CANON",),
        checks=(
            steward.CheckResult(
                role="CANON",
                name="glitch8_semantic_consistency",
                command=[],
                returncode=0,
                output="ok",
            ),
        ),
        generated_changes=(),
        evidence_packets=(
            {
                "agent": "CANON",
                "task": "glitch8_semantic_consistency",
                "observed": {"mirror_matches": True},
                "evidence": ["source", "mirror"],
                "confidence": 1.0,
                "recommended_action": "none",
                "authority": "read_only",
                "severity": "info",
            },
        ),
    )

    steward._write_public_status(report)

    human = (tmp_path / "docs/generated/CMB_SYSTEM_STATUS.md").read_text(encoding="utf-8")
    machine = (tmp_path / "docs/generated/cmb-system-status.json").read_text(encoding="utf-8")
    assert "| CANON | glitch8_semantic_consistency | PASS |" in human
    assert "\\n" not in human
    assert '"overall_ok": true' in machine
    assert "\\n" not in machine


def _make_repository_root(root: Path) -> None:
    (root / "src/cmb_agents").mkdir(parents=True)
    (root / "src/cmb_glitch8").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"test\"\n", encoding="utf-8")
    (root / "src/cmb_agents/steward.py").write_text("# steward\n", encoding="utf-8")
    (root / "src/cmb_glitch8/glyphs.v1.json").write_text("{}\n", encoding="utf-8")


def test_resolve_repository_root_prefers_explicit_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "checkout"
    _make_repository_root(root)
    monkeypatch.setenv("CMB_REPOSITORY_ROOT", str(root))
    monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path / "wrong"))

    assert steward._resolve_repository_root() == root.resolve()


def test_resolve_repository_root_uses_current_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "checkout"
    _make_repository_root(root)
    monkeypatch.delenv("CMB_REPOSITORY_ROOT", raising=False)
    monkeypatch.delenv("GITHUB_WORKSPACE", raising=False)
    monkeypatch.chdir(root)

    assert steward._resolve_repository_root() == root.resolve()


def test_role_registry_includes_autonomy_arbiter() -> None:
    assert "AUTONOMY_ARBITER" in steward.ROLE_NAMES
