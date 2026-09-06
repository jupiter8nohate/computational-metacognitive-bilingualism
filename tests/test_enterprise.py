from pathlib import Path

from cmb_enterprise import build_trust_report
from cmb_provenance.sealing import save_receipt, seal


def _receipt(tmp_path: Path) -> tuple[Path, Path]:
    asset = tmp_path / "asset.txt"
    asset.write_text("original\n", encoding="utf-8")
    receipt_path = tmp_path / "receipt.json"
    save_receipt(
        seal(
            [asset],
            base_dir=tmp_path,
            git_commit="0" * 40,
            created_at_utc="2026-09-05T00:00:00Z",
        ),
        receipt_path,
    )
    return asset, receipt_path


def test_integrity_only_routes_to_human_review(tmp_path: Path) -> None:
    asset, receipt = _receipt(tmp_path)
    report = build_trust_report([asset], receipt=receipt, base_dir=tmp_path)

    assert report["artifact_integrity"]["status"] == "PASS"
    assert report["enterprise_authority"]["status"] == "NOT_CHECKED"
    assert report["decision"] == "HUMAN_REVIEW"


def test_modified_asset_fails_closed(tmp_path: Path) -> None:
    asset, receipt = _receipt(tmp_path)
    asset.write_text("modified\n", encoding="utf-8")

    report = build_trust_report([asset], receipt=receipt, base_dir=tmp_path)

    assert report["artifact_integrity"]["status"] == "FAIL"
    assert report["decision"] == "DENY"
    codes = {item["code"] for item in report["artifact_integrity"]["failures"]}
    assert "DIGEST_MISMATCH" in codes


def test_required_authority_missing_denies(tmp_path: Path) -> None:
    asset, receipt = _receipt(tmp_path)

    report = build_trust_report(
        [asset],
        receipt=receipt,
        base_dir=tmp_path,
        require_authority=True,
    )

    assert report["enterprise_authority"]["status"] == "FAIL"
    assert report["enterprise_authority"]["failures"] == [
        "ENTERPRISE_AUTHORITY_REQUIRED"
    ]
    assert report["decision"] == "DENY"
