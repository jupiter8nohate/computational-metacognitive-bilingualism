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
