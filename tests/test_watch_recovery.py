import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    spec = spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


observatory = load_script("build_observatory")
archive = load_script("persist_watch_history")
collector = load_script("update_global_ai_watch")


def sample(hours_old: int) -> dict:
    fixture = ROOT / "tests/fixtures/global-ai-watch-static-snapshot.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    data["generated_at"] = (datetime.now(timezone.utc) - timedelta(hours=hours_old)).isoformat()
    return data


def make_checkpoint(history: dict, snapshot: dict) -> dict:
    return {
        "schema_version": "cmb.watch-checkpoint.v1",
        "snapshot_sha256": observatory.digest(snapshot),
        "history": history,
        "snapshot": snapshot,
    }


class WatchRecoveryTests(unittest.TestCase):
    def test_pages_failure_recovers_legacy_git_chain_and_archives_fresh_collection(self):
        history = observatory.new_history()
        for hours in (3, 2):
            observatory.record_snapshot(history, sample(hours), stale=False)

        with tempfile.TemporaryDirectory() as folder:
            prior = Path(folder) / "watch-snapshots" / "legacy"
            for record in history["entries"]:
                observatory.save_json(prior / f"{record['hash']}.json", record)
            with patch.object(observatory, "urlopen", side_effect=URLError("DNS failure")):
                recovered = observatory.load_recovery_history(Path(folder))

        self.assertEqual(recovered, history)
        fresh = sample(0)
        self.assertTrue(observatory.record_snapshot(recovered, fresh, stale=False))
        checkpoint = make_checkpoint(recovered, fresh)
        missing = HTTPError("https://api.github.com/", 404, "missing checkpoint", {}, None)
        responses = [
            {"object": {"sha": "old"}}, missing, {"tree": {"sha": "base"}},
            {"sha": "updated-tree"}, {"sha": "new"}, {},
        ]
        with patch.dict(sys.modules, {"build_observatory": observatory}), patch.object(
            archive, "request", side_effect=responses
        ) as request:
            self.assertTrue(archive.archive_collection("test-token", "main", checkpoint))

        tree = request.call_args_list[3].args[3]
        blobs = {entry["path"]: json.loads(entry["content"]) for entry in tree["tree"]}
        self.assertEqual(blobs.pop("archive/watch-checkpoint.json"), checkpoint)
        self.assertEqual(list(blobs.values()), [recovered["entries"][-1]])
        self.assertEqual(request.call_args.args[3], {"sha": "new", "force": False})

    def test_migration_keeps_newer_git_collection_when_pages_is_behind(self):
        published = observatory.new_history()
        observatory.record_snapshot(published, sample(3), stale=False)
        published["total_collections"] = 15
        history = {**published, "entries": published["entries"].copy()}
        observatory.record_snapshot(history, sample(2), stale=False)
        with tempfile.TemporaryDirectory() as folder:
            checkout = Path(folder)
            git_record = history["entries"][-1]
            observatory.save_json(checkout / "watch-snapshots" / "legacy" / "new.json", git_record)
            with patch.object(observatory, "load_prior", return_value=published):
                self.assertEqual(observatory.load_recovery_history(checkout), history)

    def test_source_failure_reuses_git_snapshot_without_contacting_pages(self):
        saved = sample(8)
        history = observatory.new_history()
        observatory.record_snapshot(history, saved, stale=False)
        with tempfile.TemporaryDirectory() as folder:
            checkout = Path(folder)
            checkpoint = checkout / "watch-checkpoint.json"
            observatory.save_json(checkpoint, make_checkpoint(history, saved))
            document = checkout / "watch.md"
            document.write_text(
                f"{collector.START_MARKER}\n{collector.END_MARKER}\n", encoding="utf-8"
            )
            output = checkout / "snapshot.json"
            arguments = [
                "update_global_ai_watch.py", "--allow-stale", "--recovery-checkpoint", str(checkpoint),
                "--output-doc", str(document), "--output-json", str(output),
            ]
            with patch.object(
                collector, "fetch_gdelt", side_effect=collector.WatchError("GDELT down")
            ), patch.object(
                collector, "fetch_rss_articles", side_effect=collector.WatchError("RSS down")
            ), patch.object(
                collector, "urlopen", side_effect=AssertionError("Pages lookup during Git recovery")
            ), patch.object(sys, "argv", arguments):
                self.assertEqual(collector.main(), 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), saved)
            self.assertIn("STALE - LIVE SOURCES UNAVAILABLE", document.read_text(encoding="utf-8"))
            with patch.object(observatory, "load_prior", side_effect=AssertionError("Pages lookup")):
                recovered = observatory.load_recovery_history(checkout)
            self.assertFalse(observatory.record_snapshot(recovered, saved, stale=True))
            self.assertEqual(recovered, history)

    def test_tampered_checkpoint_is_rejected(self):
        saved = sample(2)
        history = observatory.new_history()
        observatory.record_snapshot(history, saved, stale=False)
        checkpoint = make_checkpoint(history, saved)
        saved["articles"][0]["title"] = "tampered"
        with self.assertRaisesRegex(observatory.ObservatoryError, "digest mismatch"):
            observatory.check_checkpoint(checkpoint)

    def test_retry_is_idempotent_and_forked_collection_is_rejected(self):
        saved = sample(2)
        history = observatory.new_history()
        observatory.record_snapshot(history, saved, stale=False)
        previous = make_checkpoint(history, saved)
        fork = observatory.new_history()
        newer = sample(1)
        observatory.record_snapshot(fork, newer, stale=False)

        responses = [{"object": {"sha": "old"}}, previous]
        with patch.dict(sys.modules, {"build_observatory": observatory}), patch.object(
            archive, "request", side_effect=responses + responses
        ) as request:
            self.assertFalse(archive.archive_collection("test-token", "main", previous))
            with self.assertRaisesRegex(ValueError, "does not extend"):
                archive.archive_collection("test-token", "main", make_checkpoint(fork, newer))
            self.assertEqual(request.call_count, 4)
