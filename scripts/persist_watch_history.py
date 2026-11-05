"""Preserve each new Global AI Watch collection in a dedicated Git history branch.

Commit the new collection record and the full recovery checkpoint together.
The noncanonical literary witness has its own archive entry.
Requires GITHUB_TOKEN with contents:write in the publishing workflow.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "jupiter8nohate/computational-metacognitive-bilingualism"
API = "https://api.github.com/repos/" + REPOSITORY
BRANCH = "watch-history"
HISTORY = ROOT / "machine/global-ai-watch-history.json"
WATCH = ROOT / "machine/global-ai-watch.json"


def request(
    method: str, url: str, token: str, data: dict | None = None, *,
    accept: str = "application/vnd.github+json",
) -> dict:
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": accept,
            "Content-Type": "application/json",
            "User-Agent": "CMB-Watch-Archive/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def archive_collection(token: str, current_sha: str, checkpoint: dict) -> bool:
    from build_observatory import check_checkpoint

    check_checkpoint(checkpoint)
    record = checkpoint["history"]["entries"][-1]
    ref_url = API + "/git/refs/heads/" + BRANCH
    try:
        ref = request("GET", API + "/git/ref/heads/" + BRANCH, token)
    except HTTPError as exc:
        if exc.code != 404:
            raise
        ref = request(
            "POST", API + "/git/refs", token,
            {"ref": "refs/heads/" + BRANCH, "sha": current_sha},
        )
    head = ref["object"]["sha"]
    checkpoint_path = "archive/watch-checkpoint.json"
    try:
        previous = request(
            "GET", API + "/contents/" + checkpoint_path + "?ref=" + head, token,
            accept="application/vnd.github.raw+json",
        )
    except HTTPError as exc:
        if exc.code != 404:
            raise
    else:
        check_checkpoint(previous)
        previous_tip = previous["history"]["entries"][-1]["hash"]
        if record["hash"] == previous_tip:
            if checkpoint["snapshot_sha256"] != previous["snapshot_sha256"]:
                raise ValueError("Existing collection has a different full snapshot digest")
            return False
        if record["previous_hash"] != previous_tip:
            raise ValueError("New collection does not extend the current Git checkpoint")

    timestamp = record["collected_at"].replace(":", "").replace("-", "")
    timestamp = timestamp.replace("T", "_").replace("Z", "")
    record_path = f"archive/watch-snapshots/{timestamp[:8]}/{timestamp}_{record['hash'][:12]}.json"
    base = request("GET", API + "/git/commits/" + head, token)
    tree = request(
        "POST", API + "/git/trees", token,
        {
            "base_tree": base["tree"]["sha"],
            "tree": [
                {
                    "path": path, "mode": "100644", "type": "blob",
                    "content": json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
                }
                for path, data in ((record_path, record), (checkpoint_path, checkpoint))
            ],
        },
    )
    commit = request(
        "POST", API + "/git/commits", token,
        {
            "message": "archive: preserve Global AI Watch collection and recovery checkpoint",
            "tree": tree["sha"],
            "parents": [head],
        },
    )
    request("PATCH", ref_url, token, {"sha": commit["sha"], "force": False})
    return True


def archive_first_witness(token: str) -> bool:
    """Preserve the latest noncanonical literary artifact in Git separately."""
    path = ROOT / "machine/dna-living-codex.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("human_canon_untouched") is not True:
        raise ValueError("Canon protection invariant was not satisfied")
    chapters = document.get("chapters", [])
    if not chapters:
        return False
    chapter = chapters[0]
    chapter_id = chapter["id"]
    if not chapter_id.startswith("witness-") or not all(
        ch in "0123456789abcdef" for ch in chapter_id.removeprefix("witness-")
    ):
        raise ValueError("Invalid literary chapter identifier")
    remote_path = "archive/dna-witness/" + chapter_id + ".json"
    url = API + "/contents/" + remote_path
    try:
        request("GET", url + "?ref=" + BRANCH, token)
        return False
    except HTTPError as exc:
        if exc.code != 404:
            raise
    content = json.dumps({
        "record_type": "noncanonical_rule_based_allegory",
        "canonical_author": document["canonical_author"],
        "generated_by": document["author"],
        "chapter": chapter,
    }, indent=2, ensure_ascii=False) + "\n"
    request("PUT", url, token, {
        "message": "archive: preserve source-linked noncanonical D.N.A. witness",
        "branch": BRANCH,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    })
    return True


def main() -> int:
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        print("Git archive skipped: untrusted repository context", file=sys.stderr)
        return 2
    token = os.environ.get("GITHUB_TOKEN")
    sha = os.environ.get("GITHUB_SHA")
    if not token or not sha:
        print("Git history branch requires GITHUB_TOKEN and GITHUB_SHA", file=sys.stderr)
        return 2
    from build_observatory import check_history, digest

    try:
        history = json.loads(HISTORY.read_text(encoding="utf-8"))
        check_history(history)
        current = json.loads(WATCH.read_text(encoding="utf-8"))
        if not history["entries"] or history["entries"][-1]["collected_at"] != current["generated_at"]:
            print("No collection matches the history tip; Git history is unchanged")
            return 0
        saved = archive_collection(token, sha, {
            "schema_version": "cmb.watch-checkpoint.v1",
            "snapshot_sha256": digest(current),
            "snapshot": current,
            "history": history,
        })
        witness_saved = archive_first_witness(token)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Git history preservation failed: {exc}", file=sys.stderr)
        return 2
    print("Git collection " + ("preserved" if saved else "already present") + " on " + BRANCH)
    print("Noncanonical witness " + ("preserved" if witness_saved else "already present or unavailable"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
