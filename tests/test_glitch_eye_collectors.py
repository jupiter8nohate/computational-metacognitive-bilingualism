from __future__ import annotations

import subprocess
from pathlib import Path

from cmb_agents.eyes import Eye
from cmb_agents.eyes.collectors import (
    GitCommit,
    build_cochange_relations,
    collect_python_import_pairs,
    extract_invariant_signature,
    observe_repository,
    parse_git_log,
)


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _commit(root: Path, message: str) -> None:
    _git(root, "add", ".")
    _git(root, "commit", "-m", message)


def test_parse_git_log_builds_commit_path_sets() -> None:
    sha_a = "a" * 40
    sha_b = "b" * 40
    commits = parse_git_log(
        f"{sha_a}\nREADME.md\ndocs/a.md\n\n{sha_b}\nsrc/a.py\n"
    )

    assert commits == (
        GitCommit(sha=sha_a, paths=("README.md", "docs/a.md")),
        GitCommit(sha=sha_b, paths=("src/a.py",)),
    )


def test_cochange_score_uses_lower_frequency_file() -> None:
    commits = (
        GitCommit("a" * 40, ("a.md", "b.md")),
        GitCommit("b" * 40, ("a.md", "b.md")),
        GitCommit("c" * 40, ("a.md",)),
    )

    relations = build_cochange_relations(
        commits,
        min_support=2,
        min_score=0.90,
    )

    assert len(relations) == 1
    assert relations[0]["score"] == 1.0
    assert relations[0]["support"] == 2


def test_python_import_pairs_mark_explicit_dependencies(tmp_path: Path) -> None:
    package = tmp_path / "src" / "demo"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "a.py").write_text("import demo.b\n", encoding="utf-8")
    (package / "b.py").write_text("VALUE = 1\n", encoding="utf-8")

    pairs = collect_python_import_pairs(tmp_path)

    assert frozenset(("src/demo/a.py", "src/demo/b.py")) in pairs



def test_python_import_pairs_resolve_relative_package_imports(tmp_path: Path) -> None:
    package = tmp_path / "src" / "demo"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(
        "from .worker import VALUE\n",
        encoding="utf-8",
    )
    (package / "worker.py").write_text("VALUE = 1\n", encoding="utf-8")

    pairs = collect_python_import_pairs(tmp_path)

    assert frozenset(
        ("src/demo/__init__.py", "src/demo/worker.py")
    ) in pairs


def test_extract_invariant_signature_is_normalized() -> None:
    signature = extract_invariant_signature(
        "PATTERN!=PROOF\nPROFILE != PERSON\nordinary text\n"
    )

    assert signature == (
        "PATTERN != PROOF",
        "PROFILE != PERSON",
    )


def test_observe_repository_uses_real_git_history(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "eyes@example.test")
    _git(tmp_path, "config", "user.name", "Glitch Eye Test")

    docs = tmp_path / "docs"
    docs.mkdir()
    file_a = docs / "a.md"
    file_b = docs / "b.md"
    policy = docs / "policy.md"

    file_a.write_text("alpha 1\n", encoding="utf-8")
    file_b.write_text("beta 1\n", encoding="utf-8")
    policy.write_text("PATTERN != PROOF\n", encoding="utf-8")
    _commit(tmp_path, "initial evidence")

    file_a.write_text("alpha 2\n", encoding="utf-8")
    file_b.write_text("beta 2\n", encoding="utf-8")
    _commit(tmp_path, "paired change one")

    file_a.write_text("alpha 3\n", encoding="utf-8")
    file_b.write_text("beta 3\n", encoding="utf-8")
    policy.write_text("PATTERN == PROOF\n", encoding="utf-8")
    _commit(tmp_path, "paired change and invariant mutation")

    payload = observe_repository(
        tmp_path,
        max_commits=20,
        min_support=3,
        min_score=0.90,
    )

    perceptions = payload["perceptions"]
    eyes = {item["eye"] for item in perceptions}

    assert Eye.HIDDEN_CONTEXT.value in eyes
    assert Eye.TEMPORAL.value in eyes

    hidden = [
        item
        for item in perceptions
        if item["eye"] == Eye.HIDDEN_CONTEXT.value
    ]
    assert any(
        set(item["evidence"]) == {"docs/a.md", "docs/b.md"}
        for item in hidden
    )

    temporal = [
        item
        for item in perceptions
        if item["eye"] == Eye.TEMPORAL.value
    ]
    assert any("docs/policy.md" in item["hypothesis"] for item in temporal)
