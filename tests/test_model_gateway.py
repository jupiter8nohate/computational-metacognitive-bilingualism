from __future__ import annotations

import json
import subprocess

import pytest

from cmb_agents import model_gateway


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_resolve_model_config_prefers_explicit_openai() -> None:
    config = model_gateway.resolve_model_config(
        openai_api_key="oa",
        openai_model="gpt-test",
        copilot_token="gh",
        copilot_model="auto",
    )

    assert config.provider == "openai"
    assert config.model == "gpt-test"


def test_resolve_model_config_falls_back_to_copilot() -> None:
    config = model_gateway.resolve_model_config(copilot_token="gh")

    assert config.provider == "copilot"
    assert config.model == model_gateway.DEFAULT_COPILOT_MODEL


def test_resolve_model_config_requires_a_provider() -> None:
    with pytest.raises(model_gateway.ModelGatewayError, match="no model provider"):
        model_gateway.resolve_model_config()


def test_copilot_request_uses_noninteractive_bounded_cli(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command[0] == "copilot"
        assert "-s" in command
        assert "--no-ask-user" in command
        assert "--no-custom-instructions" in command
        assert "--no-auto-update" in command
        assert "--model" in command
        assert command[command.index("--model") + 1] == "auto"
        env = kwargs["env"]
        assert isinstance(env, dict)
        assert env["COPILOT_GITHUB_TOKEN"] == "gh"
        return subprocess.CompletedProcess(command, 0, stdout='{"ok": true}\n', stderr="")

    monkeypatch.setattr(model_gateway.subprocess, "run", fake_run)

    result, config = model_gateway.request_json(
        instructions="Return a bounded result.",
        input_payload={"task": "test"},
        schema_name="test_schema",
        schema={
            "type": "object",
            "required": ["ok"],
            "properties": {"ok": {"type": "boolean"}},
        },
        copilot_token="gh",
        timeout=30,
    )

    assert result == {"ok": True}
    assert config.provider == "copilot"


def test_openai_request_parses_responses_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: object, timeout: int) -> _FakeResponse:
        assert getattr(request, "full_url") == "https://api.openai.com/v1/responses"
        body = json.loads(getattr(request, "data").decode("utf-8"))
        assert body["model"] == "gpt-test"
        assert timeout == 30
        return _FakeResponse(
            {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": "{\"ok\": true}",
                            }
                        ],
                    }
                ]
            }
        )

    monkeypatch.setattr(model_gateway.urllib.request, "urlopen", fake_urlopen)

    result, config = model_gateway.request_json(
        instructions="Return a bounded result.",
        input_payload={"task": "test"},
        schema_name="test_schema",
        schema={
            "type": "object",
            "required": ["ok"],
            "properties": {"ok": {"type": "boolean"}},
        },
        openai_api_key="oa",
        openai_model="gpt-test",
        timeout=30,
    )

    assert result == {"ok": True}
    assert config.provider == "openai"
