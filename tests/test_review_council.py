from __future__ import annotations

from cmb_agents.review_council import ReviewChange, Severity, Verdict, load_changes, review_changes


def test_safe_change_can_be_approved() -> None:
    packet = review_changes((
        ReviewChange(
            path="docs/example.md",
            patch="@@ -0,0 +1,2 @@\n+# Example\n+Safe documentation.\n",
            additions=2,
        ),
    ))

    assert packet.verdict is Verdict.APPROVE
    assert packet.score >= 90
    assert packet.digest.startswith("sha256:")


def test_secret_exposure_requests_changes() -> None:
    packet = review_changes((
        ReviewChange(
            path="src/example.py",
            patch="@@ -0,0 +1 @@\n+api_key = \"super-secret-value\"\n",
            additions=1,
        ),
    ))

    assert packet.verdict is Verdict.REQUEST_CHANGES
    assert any(f.severity is Severity.CRITICAL for f in packet.findings)


def test_dangerous_execution_is_blocking() -> None:
    packet = review_changes((
        ReviewChange(
            path="src/example.py",
            patch="@@ -0,0 +1,2 @@\n+import os\n+os.system(user_input)\n",
            additions=2,
        ),
    ))

    assert packet.verdict is Verdict.REQUEST_CHANGES
    assert any(f.category == "unsafe_execution" for f in packet.findings)


def test_governance_surface_escalates_to_human() -> None:
    packet = review_changes((
        ReviewChange(
            path="cmb.toml",
            patch="@@ -1 +1 @@\n-default_friction = 0.20\n+default_friction = 0.30\n",
            additions=1,
            deletions=1,
        ),
    ))

    assert packet.verdict is Verdict.HUMAN_REVIEW
    assert packet.council_votes["GOVERNANCE_GUARD"] is Verdict.HUMAN_REVIEW


def test_authority_expansion_requests_changes() -> None:
    packet = review_changes((
        ReviewChange(
            path=".github/workflows/agent.yml",
            patch="@@ -1 +1,2 @@\n+permissions: write-all\n+pull-requests: write\n",
            additions=2,
        ),
    ))

    assert packet.verdict is Verdict.REQUEST_CHANGES
    assert any(f.category == "authority_expansion" for f in packet.findings)


def test_unfinished_work_reduces_score() -> None:
    packet = review_changes((
        ReviewChange(
            path="src/example.py",
            patch="@@ -0,0 +1 @@\n+# TODO finish edge case\n",
            additions=1,
        ),
    ))

    assert packet.score < 100
    assert any(f.category == "unfinished_work" for f in packet.findings)


def test_detector_patterns_inside_python_strings_do_not_self_trigger() -> None:
    packet = review_changes((
        ReviewChange(
            path="src/cmb_agents/review_council.py",
            patch=(
                "@@ -0,0 +1,3 @@\n"
                "+danger = re.compile(r\"\\bos\\.system\\(\")\n"
                "+authority = re.compile(r\"merge_pull_request|permissions:\\s*write-all\")\n"
                "+unfinished = re.compile(r\"\\b(?:TODO|FIXME)\\b\")\n"
            ),
            additions=3,
        ),
    ))

    blocking = {
        finding.category
        for finding in packet.findings
        if finding.severity in {Severity.ERROR, Severity.CRITICAL}
    }
    assert blocking == set()


def test_test_fixture_strings_do_not_trigger_blocking_findings() -> None:
    packet = review_changes((
        ReviewChange(
            path="tests/test_fixture.py",
            patch=(
                "@@ -0,0 +1,3 @@\n"
                "+danger_patch = \"@@ -0,0 +1 @@\\n+os.system(user_input)\\n\"\n"
                "+authority_patch = \"permissions: write-all\\npull-requests: write\\n\"\n"
                "+todo_patch = \"# TODO fixture text\"\n"
            ),
            additions=3,
        ),
    ))

    assert not any(
        finding.severity in {Severity.ERROR, Severity.CRITICAL}
        for finding in packet.findings
    )
    assert not any(finding.category == "unfinished_work" for finding in packet.findings)


def test_real_python_secret_assignment_still_blocks() -> None:
    packet = review_changes((
        ReviewChange(
            path="src/runtime.py",
            patch='@@ -0,0 +1 @@\n+token = "actual-secret-material"\n',
            additions=1,
        ),
    ))

    assert packet.verdict is Verdict.REQUEST_CHANGES
    assert any(f.category == "secret_exposure" for f in packet.findings)


def test_load_changes_rejects_negative_counts() -> None:
    try:
        load_changes([
            {
                "path": "src/example.py",
                "patch": "",
                "additions": -1,
                "deletions": 0,
            }
        ])
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:
        raise AssertionError("negative change counts must be rejected")


def test_many_governance_warnings_escalate_without_blocking() -> None:
    changes = tuple(
        ReviewChange(
            path=f".github/workflows/governance-{index}.yml",
            patch="@@ -0,0 +1 @@\n+name: governance check\n",
            additions=1,
        )
        for index in range(12)
    )

    packet = review_changes(changes)

    assert packet.verdict is Verdict.HUMAN_REVIEW
    assert not any(
        finding.severity in {Severity.ERROR, Severity.CRITICAL}
        for finding in packet.findings
    )
