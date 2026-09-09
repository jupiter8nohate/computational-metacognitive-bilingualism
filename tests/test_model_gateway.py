from __future__ import annotations

import json
import subprocess

import pytest

from cmb_agents import model_gateway


def test_parse_json_object_accepts_plain_json() -> None:
    assert model_gateway._parse_json_object('{"ok":true}') == {"ok": True}


def test_parse_json_object_accepts_fenced_json() -> None:
    assert model_gateway._parse_json_object('```json\n{"ok":true}\n```') == {"ok": True}


def test_extract_copilot_message_uses_last_assistant_message() -> None:
    events = [
        {"type": "assistant.message", "data": {"content": '{"step":1}'}},
        {"type": "session.idle", "data": {}},
        {"type": "assistant.message", "data": {"content": '{"step":2}'}},
    ]
    stdout = "\n".join(json.dumps(item) for item in events)

    assert model_gateway._extract_copilot_message(stdout) == '{"step":2}'


def test_copilot_availability_requires_opt_in_token_and_binary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CMB_COPILOT_CLI", "true")
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setattr(model_gateway.shutil, "which", lambda name: "/usr/bin/copilot")

    assert model_gateway.copilot_available() is True

    monkeypatch.delenv("GITHUB_TOKEN")
    assert model_gateway.copilot_available() is False


def test_request_json_uses_copilot_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CMB_COPILOT_CLI", "true")
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("CMB_COPILOT_MODEL", "auto")
    monkeypatch.setattr(model_gateway.shutil, "which", lambda name: "/usr/bin/copilot")

    stdout = json.dumps(
        {
            "type": "assistant.message",
            "data": {"content": '{"answer":"ok"}'},
        }
    )

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=["copilot"],
            returncode=0,
            stdout=stdout,
            stderr="",
        )

    monkeypatch.setattr(model_gateway.subprocess, "run", fake_run)

    result = model_gateway.request_json(
        instructions="Return the answer.",
        input_payload={"question": "health"},
        schema_name="answer",
        schema={
            "type": "object",
            "additionalProperties": False,
            "required": ["answer"],
            "properties": {"answer": {"type": "string"}},
        },
    )

    assert result.payload == {"answer": "ok"}
    assert result.provider == "github_copilot_cli"
    assert result.model == "auto"


def test_request_json_fails_closed_without_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CMB_COPILOT_CLI", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(model_gateway.ModelGatewayError, match="no model provider"):
        model_gateway.request_json(
            instructions="x",
            input_payload={},
            schema_name="empty",
            schema={"type": "object"},
        )
