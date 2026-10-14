"""Preserve each new Global AI Watch collection in a dedicated Git history branch.

No human-written canon is modified. The Pages archive is a fast public
checkpoint, while individual source-linked entries are committed to Git.
Requires GITHUB_TOKEN with contents:write in the publishing workflow.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "jupiter8nohate/computational-metacognitive-bilingualism"
API = "https://api.github.com/repos/" + REPOSITORY
BRANCH = "watch-history"
HISTORY = ROOT / "machine/global-ai-watch-history.json"
WATCH = ROOT / "machine/global-ai-watch.json"


def request(method: str, url: str, token: str, data: dict | None = None) -> dict:
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "CMB-Watch-Archive/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def archive_entry(token: str, current_sha: str, record: dict) -> bool:
    try:
        request("GET", API + "/git/ref/heads/" + BRANCH, token)
    except HTTPError as exc:
        if exc.code != 404:
            raise
        request(
            "POST", API + "/git/refs", token,
            {"ref": "refs/heads/" + BRANCH, "sha": current_sha},
        )
    timestamp = record["collected_at"].replace(":", "").replace("-", "")
    timestamp = timestamp.replace("T", "_").replace("Z", "")
    path = "archive/watch-snapshots/" + timestamp[:8] + "/" + timestamp + "_" + record["hash"][:12] + ".json"
    url = API + "/contents/" + quote(path, safe="/")
    try:
        request("GET", url + "?ref=" + BRANCH, token)
        return False
    except HTTPError as exc:
        if exc.code != 404:
            raise
    content = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    request(
        "PUT", url, token,
        {
            "message": "archive: preserve evidence-linked Global AI Watch collection",
            "branch": BRANCH,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        },
    )
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
    from build_observatory import check_history
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    check_history(history)
    if not history["entries"]:
        return 0
    record = history["entries"][-1]
    current = json.loads(WATCH.read_text(encoding="utf-8"))
    if record["collected_at"] != current["generated_at"]:
        print("No new live collection; Git history is unchanged")
        return 0
    try:
        saved = archive_entry(token, sha, record)
    except (HTTPError, OSError, ValueError) as exc:
        print(f"Git history preservation failed: {exc}", file=sys.stderr)
        return 2
    print("Git collection " + ("preserved" if saved else "already present") + " on " + BRANCH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
