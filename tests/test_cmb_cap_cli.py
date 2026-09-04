from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from cmb_cap import issue_from_sdl
from cmb_cap.cli import main
from cmb_policy.authorization import generate_ed25519_keypair


SOURCE = """cmb/1
HUMAN "Jupiter Hudson"
AGENT research_bot
ALLOW web.search
SCOPE project cmb
PURPOSE "public research"
EXPIRES 2099-01-01T00:00:00Z
DELEGABLE false
RETURN receipt
"""


def _credential(tmp_path: Path) -> Path:
    private_key, _ = generate_ed25519_keypair()
    credential = issue_from_sdl(
        SOURCE,
        private_key_b64=private_key,
        now=datetime.now(timezone.utc),
    )
    path = tmp_path / "credential.json"
    path.write_text(json.dumps(credential), encoding="utf-8")
    return path


def test_export_vc_requires_valid_credential(tmp_path: Path, capsys) -> None:
    credential_path = _credential(tmp_path)
    payload = json.loads(credential_path.read_text(encoding="utf-8"))
    payload["authority"]["purpose"] = "tampered"
    credential_path.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "credential.vc.json"

    assert main(["export-vc", str(credential_path), "--output", str(output)]) == 2
    assert not output.exists()
    assert "Refusing VC projection of unverified credential" in capsys.readouterr().out


def test_export_vc_accepts_verified_credential(tmp_path: Path) -> None:
    credential_path = _credential(tmp_path)
    output = tmp_path / "credential.vc.json"

    assert main(["export-vc", str(credential_path), "--output", str(output)]) == 0
    projection = json.loads(output.read_text(encoding="utf-8"))
    assert projection["cmb:standardsStatus"] == (
        "VC_2_0_projection_only_not_W3C_Data_Integrity_proof"
    )
