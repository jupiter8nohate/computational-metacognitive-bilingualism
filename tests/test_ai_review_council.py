from __future__ import annotations

import pytest

from cmb_agents.ai_review_council import (
    _MAX_DIFF_CHARS,
    _bounded_diff,
    _extract_output_text,
    _validate_result,
)
from cmb_agents.review_council import ReviewChange


def test_bounded_diff_marks_truncated_input() -> None:
    diff, truncated = _bounded_diff((
        ReviewChange(
            path="src/large.py",
            patch="+" + ("x" * (_MAX_DIFF_CHARS + 200)),
            additions=1,
        ),
    ))

    assert truncated is True
    assert "REVIEW_INPUT_TRUNCATED" in diff
    assert len(diff) <= _MAX_DIFF_CHARS + 300


def test_bounded_diff_reports_complete_input() -> None:
    diff, truncated = _bounded_diff((
        ReviewChange(
            path="src/small.py",
            patch="+VALUE = 1\n",
            additions=1,
        ),
    ))

    assert truncated is False
    assert "PATH: src/small.py" in diff
    assert "REVIEW_INPUT_TRUNCATED" not in diff


def test_extract_output_text_accepts_nested_response_shape() -> None:
    payload = {
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": '{"summary":"ok"}',
                    }
                ],
            }
        ]
    }

    assert _extract_output_text(payload) == '{"summary":"ok"}'


def test_validate_result_accepts_bounded_shape() -> None:
    result = _validate_result({
        "summary": "No blocking issue found.",
        "verdict": "APPROVE",
        "confidence": 0.8,
        "findings": [],
    })

    assert result["verdict"] == "APPROVE"


def test_validate_result_rejects_unknown_verdict() -> None:
    with pytest.raises(RuntimeError, match="verdict"):
        _validate_result({
            "summary": "bad",
            "verdict": "AUTO_MERGE",
            "confidence": 1.0,
            "findings": [],
        })
