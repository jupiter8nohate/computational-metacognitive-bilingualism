"""Small dependency-free operational self-test for installed environments."""

from __future__ import annotations

import tempfile
from pathlib import Path

from .ledger import append_anchor, verify_ledger
from .sealing import load_receipt, save_receipt, seal, verify


def run_selftest() -> None:
    with tempfile.TemporaryDirectory(prefix="cmb-provenance-") as directory:
        root = Path(directory)
        artifact = root / "artifact.txt"
        artifact.write_bytes(b"PATTERN != PROOF\n")
        receipt = seal(
            artifact.name,
            base_dir=root,
            git_commit="0" * 40,
            created_at_utc="1970-01-01T00:00:00Z",
        )
        receipt_path = save_receipt(receipt, root / "receipt.json")
        loaded = load_receipt(receipt_path)
        result = verify(artifact.name, loaded, base_dir=root)
        if not result.ok:
            raise RuntimeError(f"Artifact self-verification failed: {result.failures}")
        ledger = root / "anchors.jsonl"
        append_anchor(
            loaded,
            anchor_type="other",
            location="selftest://receipt",
            description="dependency-free self-test",
            ledger_path=ledger,
            local_recorded_at_utc="1970-01-01T00:00:01Z",
        )
        if verify_ledger(ledger)[0] != 1:
            raise RuntimeError("Ledger self-verification failed.")
