from __future__ import annotations

import json
from pathlib import Path

from cmb_policy.attestation import (
    CMB_SRP2_PREDICATE_V1,
    IN_TOTO_STATEMENT_V1,
    build_scan_statement,
)
from cmb_policy.detector import (
    DetectorConfig,
    load_scan_report,
    scan_paths,
    summarize_report,
)
from cmb_policy.runtime import RuntimePolicy, required_controls_for


POLICY = """
[cmb]
protocol = "cmb.sovereignty-runtime.v2"
default_friction = 0.20
high_friction_threshold = 0.75
critical_threshold = 0.90

[principles]
pattern_is_proof = false
profile_is_person = false
model_is_mind = false
prediction_is_destiny = false
human_agency_over_machine_authority = true

[operations.code_change]
criticality = 0.55
reversible = true
controls = []

[operations.manage_authentication]
criticality = 0.85
reversible = true
controls = []

[operations.deploy_production]
criticality = 0.95
reversible = false
controls = ["reproducible_build"]

[operations.modify_permissions]
criticality = 1.00
reversible = false
controls = []

[operations.collect_tracking_data]
criticality = 1.00
reversible = false
controls = ["explicit_consent"]

[detectors]
python_ast = true
fail_closed_on_python_parse_error = true
max_file_bytes = 1048576

[[detectors.path_rules]]
id = "deploy"
glob = ".github/workflows/*deploy*.yml"
operation = "deploy_production"

[[detectors.python_call_rules]]
id = "permission"
operation = "modify_permissions"
names = ["os.chmod", "Path.chmod", "pathlib.Path.chmod"]

[[detectors.python_call_rules]]
id = "tracking"
operation = "collect_tracking_data"
names = ["posthog.capture", "analytics.track"]

[[detectors.python_call_rules]]
id = "auth"
operation = "manage_authentication"
names = ["login_user"]
"""


def _policy(tmp_path: Path) -> tuple[Path, RuntimePolicy]:
    path = tmp_path / "cmb.toml"
    path.write_text(POLICY, encoding="utf-8")
    return path, RuntimePolicy.load(path)


def test_v2_detector_config_loads(tmp_path: Path) -> None:
    path, policy = _policy(tmp_path)
    config = DetectorConfig.load(path, policy)
    assert len(config.path_rules) == 1
    assert len(config.python_call_rules) == 3


def test_python_ast_detects_permission_mutation(tmp_path: Path) -> None:
    policy_path, _ = _policy(tmp_path)
    source = tmp_path / "permissions.py"
    source.write_text(
        "import os\nos.chmod('artifact', 0o600)\n",
        encoding="utf-8",
    )
    report = scan_paths([source], policy_path=policy_path, repo_root=tmp_path)
    assert report.operations == ("modify_permissions",)
    assert report.findings[0].detector == "python_ast_call"
    assert report.findings[0].line == 2


def test_python_ast_resolves_import_alias(tmp_path: Path) -> None:
    policy_path, _ = _policy(tmp_path)
    source = tmp_path / "tracking.py"
    source.write_text(
        "import posthog as ph\nph.capture('user', 'opened')\n",
        encoding="utf-8",
    )
    report = scan_paths([source], policy_path=policy_path, repo_root=tmp_path)
    assert report.operations == ("collect_tracking_data",)
    assert report.findings[0].evidence == "call:posthog.capture"


def test_string_mentions_do_not_trigger_ast_rule(tmp_path: Path) -> None:
    policy_path, _ = _policy(tmp_path)
    source = tmp_path / "notes.py"
    source.write_text(
        "example = 'posthog.capture() and os.chmod()'\n",
        encoding="utf-8",
    )
    report = scan_paths([source], policy_path=policy_path, repo_root=tmp_path)
    assert report.findings == ()


def test_path_sensitive_deployment_detection(tmp_path: Path) -> None:
    policy_path, policy = _policy(tmp_path)
    workflow = tmp_path / ".github" / "workflows" / "deploy-prod.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: deploy\n", encoding="utf-8")
    report = scan_paths([workflow], policy_path=policy_path, repo_root=tmp_path)
    assert report.operations == ("deploy_production",)
    summary = summarize_report(report, policy)
    assert summary["highest_criticality"] == 0.95
    assert "human_signature" in required_controls_for(policy, "deploy_production")
    assert "two_party_review" in required_controls_for(policy, "deploy_production")


def test_python_parse_error_is_recorded_without_source_leak(tmp_path: Path) -> None:
    policy_path, _ = _policy(tmp_path)
    source = tmp_path / "broken.py"
    source.write_text("def broken(:\n    secret = 'do-not-copy'\n", encoding="utf-8")
    report = scan_paths([source], policy_path=policy_path, repo_root=tmp_path)
    assert report.errors[0].code == "PYTHON_PARSE_ERROR"
    assert "do-not-copy" not in report.errors[0].message


def test_report_digest_is_deterministic_and_verified(tmp_path: Path) -> None:
    policy_path, _ = _policy(tmp_path)
    source = tmp_path / "permissions.py"
    source.write_text("import os\nos.chmod('x', 0o600)\n", encoding="utf-8")
    first = scan_paths([source], policy_path=policy_path, repo_root=tmp_path)
    second = scan_paths([source], policy_path=policy_path, repo_root=tmp_path)
    assert first.digest == second.digest
    serialized = tmp_path / "report.json"
    serialized.write_text(json.dumps(first.to_dict()), encoding="utf-8")
    loaded = load_scan_report(serialized)
    assert loaded.digest == first.digest


def test_in_toto_statement_is_explicitly_unsigned_evidence(tmp_path: Path) -> None:
    policy_path, policy = _policy(tmp_path)
    source = tmp_path / "clean.py"
    source.write_text("print('hello')\n", encoding="utf-8")
    report = scan_paths([source], policy_path=policy_path, repo_root=tmp_path)
    statement = build_scan_statement(report, policy)
    assert statement["_type"] == IN_TOTO_STATEMENT_V1
    assert statement["predicateType"] == CMB_SRP2_PREDICATE_V1
    assert statement["subject"][0]["digest"]["sha256"] == report.digest[7:]
    boundaries = statement["predicate"]["epistemicBoundaries"]
    assert "UNSIGNED_STATEMENT != ATTESTATION" in boundaries
    assert "ATTESTATION != CORRECTNESS" in boundaries
