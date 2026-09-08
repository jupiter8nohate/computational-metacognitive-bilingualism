"""Deterministic repository collectors for the CMB Glitch Eye engine.

These collectors derive bounded evidence from local Git history and Python AST
imports. They do not call a model, mutate the repository, or assign intent.

PATTERN != PROOF
CORRELATION != DEPENDENCY
CHANGE != DEFECT
PERCEPTION != AUTHORITY
"""

from __future__ import annotations

import ast
import itertools
import json
import math
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .engine import Eye, Perception, build_default_engine


class CollectorError(RuntimeError):
    """Raised when deterministic repository evidence cannot be collected."""


@dataclass(frozen=True, slots=True)
class GitCommit:
    """One bounded Git-history observation."""

    sha: str
    paths: tuple[str, ...]


_SHA_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-fA-F]{40,64}$")
_INVARIANT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b("
    r"PATTERN|PROFILE|MODEL|PREDICTION|CAPABILITY|INTELLIGENCE|"
    r"OPTIMIZATION|HUMAN_AGENCY|MACHINE_AUTHORITY|MACHINE_CAN_READ|"
    r"OBSERVATION|SIGNAL|UNKNOWN|DIFFERENCE|ACCESS|ENGAGEMENT"
    r")\s*(==|!=|>=|<=|>|<)\s*([A-Z][A-Z0-9_]*)\b"
)
_TEXT_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        ".md",
        ".py",
        ".json",
        ".toml",
        ".yaml",
        ".yml",
        ".txt",
        ".go",
        ".rs",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".hs",
        ".lisp",
        ".pl",
        ".cpp",
        ".c",
        ".h",
    }
)
_MAX_TEXT_BYTES: Final[int] = 1_000_000


def _run_git(root: Path, args: list[str], *, timeout: int = 60) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )
    if process.returncode != 0:
        raise CollectorError(
            process.stderr.strip() or f"git command failed: {args!r}"
        )
    return process.stdout


def parse_git_log(output: str) -> tuple[GitCommit, ...]:
    """Parse a git log containing SHA headers followed by changed paths."""

    commits: list[GitCommit] = []
    current_sha: str | None = None
    current_paths: list[str] = []

    def flush() -> None:
        nonlocal current_sha, current_paths
        if current_sha is not None:
            commits.append(
                GitCommit(
                    sha=current_sha,
                    paths=tuple(sorted(set(current_paths))),
                )
            )
        current_sha = None
        current_paths = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _SHA_RE.fullmatch(line):
            flush()
            current_sha = line.lower()
            continue
        if current_sha is not None:
            current_paths.append(Path(line).as_posix())

    flush()
    return tuple(commits)


def collect_git_commits(root: Path, *, max_commits: int = 200) -> tuple[GitCommit, ...]:
    """Collect bounded recent non-merge commit path sets."""

    if max_commits < 1 or max_commits > 2000:
        raise ValueError("max_commits must be between 1 and 2000")

    output = _run_git(
        root,
        [
            "log",
            "--no-merges",
            f"--max-count={max_commits}",
            "--format=%H",
            "--name-only",
            "--",
            ".",
        ],
    )
    return parse_git_log(output)


def _module_name(src_root: Path, path: Path) -> str:
    relative = path.relative_to(src_root).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _resolve_import_module(
    current_module: str,
    *,
    module: str | None,
    level: int,
) -> str:
    if level <= 0:
        return module or ""

    current_parts = current_module.split(".")
    package_parts = current_parts[:-1]
    keep = max(0, len(package_parts) - (level - 1))
    base = package_parts[:keep]

    if module:
        base.extend(module.split("."))
    return ".".join(base)


def _match_module_path(
    module: str,
    module_to_path: dict[str, str],
) -> str | None:
    candidate = module
    while candidate:
        match = module_to_path.get(candidate)
        if match is not None:
            return match
        candidate = candidate.rpartition(".")[0]
    return None


def collect_python_import_pairs(root: Path) -> frozenset[frozenset[str]]:
    """Return current explicit Python import relationships under src/."""

    src_root = root / "src"
    if not src_root.is_dir():
        return frozenset()

    python_files = sorted(src_root.rglob("*.py"))
    module_to_path: dict[str, str] = {}
    path_to_module: dict[Path, str] = {}

    for path in python_files:
        module = _module_name(src_root, path)
        if not module:
            continue
        repository_path = path.relative_to(root).as_posix()
        module_to_path[module] = repository_path
        path_to_module[path] = module

    pairs: set[frozenset[str]] = set()

    for path in python_files:
        source_path = path.relative_to(root).as_posix()
        current_module = path_to_module.get(path)
        if current_module is None:
            continue

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=source_path)
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue

        imported_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                resolved = _resolve_import_module(
                    current_module,
                    module=node.module,
                    level=node.level,
                )
                if resolved:
                    imported_modules.add(resolved)

        for imported_module in imported_modules:
            target_path = _match_module_path(imported_module, module_to_path)
            if target_path is None or target_path == source_path:
                continue
            pairs.add(frozenset((source_path, target_path)))

    return frozenset(pairs)


def build_cochange_relations(
    commits: tuple[GitCommit, ...],
    *,
    explicit_pairs: frozenset[frozenset[str]] = frozenset(),
    min_support: int = 3,
    min_score: float = 0.80,
    max_files_per_commit: int = 60,
) -> list[dict[str, object]]:
    """Build conditional co-change relationships from bounded Git history.

    Score is co-change support divided by the lower file occurrence count. This
    asks how often the less-frequently changed file appears with its partner.
    """

    if min_support < 1:
        raise ValueError("min_support must be positive")
    if not 0.0 <= min_score <= 1.0:
        raise ValueError("min_score must be between 0 and 1")
    if max_files_per_commit < 2:
        raise ValueError("max_files_per_commit must be at least 2")

    occurrences: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str]] = Counter()

    for commit in commits:
        paths = tuple(sorted(set(commit.paths)))
        if not paths or len(paths) > max_files_per_commit:
            continue

        occurrences.update(paths)
        for file_a, file_b in itertools.combinations(paths, 2):
            pair_counts[(file_a, file_b)] += 1

    relations: list[dict[str, object]] = []
    for (file_a, file_b), support in pair_counts.items():
        if support < min_support:
            continue

        denominator = min(occurrences[file_a], occurrences[file_b])
        if denominator <= 0:
            continue

        score = support / denominator
        if not math.isfinite(score) or score < min_score:
            continue

        pair = frozenset((file_a, file_b))
        relations.append(
            {
                "file_a": file_a,
                "file_b": file_b,
                "score": round(score, 6),
                "support": support,
                "file_a_occurrences": occurrences[file_a],
                "file_b_occurrences": occurrences[file_b],
                "explicit_dependency": pair in explicit_pairs,
            }
        )

    return sorted(
        relations,
        key=lambda item: (
            -float(item["score"]),
            -int(item["support"]),
            str(item["file_a"]),
            str(item["file_b"]),
        ),
    )


def extract_invariant_signature(text: str) -> tuple[str, ...]:
    """Extract normalized CMB-style invariant expressions from text."""

    expressions = {
        f"{match.group(1)} {match.group(2)} {match.group(3)}"
        for match in _INVARIANT_RE.finditer(text)
    }
    return tuple(sorted(expressions))


def _candidate_invariant_files(root: Path, *, max_files: int) -> tuple[Path, ...]:
    candidates: list[Path] = []

    for path in sorted(root.rglob("*")):
        if len(candidates) >= max_files:
            break
        if not path.is_file() or path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > _MAX_TEXT_BYTES:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if extract_invariant_signature(text):
            candidates.append(path)

    return tuple(candidates)


def _file_versions(
    root: Path,
    repository_path: str,
    *,
    versions_per_file: int,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    history = _run_git(
        root,
        [
            "log",
            f"--max-count={versions_per_file}",
            "--format=%H",
            "--",
            repository_path,
        ],
    )

    versions: list[tuple[str, tuple[str, ...]]] = []
    for sha in (
        line.strip().lower()
        for line in history.splitlines()
        if _SHA_RE.fullmatch(line.strip())
    ):
        try:
            content = _run_git(
                root,
                ["show", f"{sha}:{repository_path}"],
                timeout=30,
            )
        except CollectorError:
            continue
        versions.append((sha, extract_invariant_signature(content)))

    return tuple(versions)


def collect_provenance_drift(
    root: Path,
    *,
    max_files: int = 25,
    versions_per_file: int = 8,
    max_records: int = 100,
) -> list[dict[str, object]]:
    """Detect exact invariant-signature changes across file history."""

    if max_files < 1 or versions_per_file < 2 or max_records < 1:
        raise ValueError("collector limits must be positive and versions_per_file >= 2")

    records: list[dict[str, object]] = []

    for path in _candidate_invariant_files(root, max_files=max_files):
        repository_path = path.relative_to(root).as_posix()
        versions = _file_versions(
            root,
            repository_path,
            versions_per_file=versions_per_file,
        )

        for newer, older in zip(versions, versions[1:]):
            newer_sha, newer_signature = newer
            older_sha, older_signature = older
            if newer_signature == older_signature:
                continue

            removed = sorted(set(older_signature) - set(newer_signature))
            added = sorted(set(newer_signature) - set(older_signature))
            if not removed and not added:
                continue

            exact_replacement = bool(removed and added)
            confidence = 1.0 if exact_replacement else 0.85
            description = (
                f"Invariant signature changed in {repository_path}: "
                f"removed={removed!r}; added={added!r}."
            )
            records.append(
                {
                    "artifacts": [
                        f"path:{repository_path}",
                        f"commit:{older_sha}",
                        f"commit:{newer_sha}",
                    ],
                    "confidence": confidence,
                    "description": description,
                    "removed": removed,
                    "added": added,
                }
            )
            if len(records) >= max_records:
                return records

    return records


def collect_repository_state(
    root: Path,
    *,
    max_commits: int = 200,
    min_support: int = 3,
    min_score: float = 0.80,
) -> dict[str, object]:
    """Collect normalized state consumed by the default Glitch Eyes."""

    root = root.resolve()
    _run_git(root, ["rev-parse", "--is-inside-work-tree"])

    commits = collect_git_commits(root, max_commits=max_commits)
    explicit_pairs = collect_python_import_pairs(root)
    cochange = build_cochange_relations(
        commits,
        explicit_pairs=explicit_pairs,
        min_support=min_support,
        min_score=min_score,
    )
    drift = collect_provenance_drift(root)

    return {
        "collector": {
            "schema_version": "cmb.glitch-eye-state.v1",
            "commits_analyzed": len(commits),
            "explicit_python_dependency_pairs": len(explicit_pairs),
            "min_support": min_support,
            "min_score": min_score,
        },
        "cochange_relations": cochange,
        "provenance_drift": drift,
    }


def perception_to_dict(perception: Perception) -> dict[str, object]:
    """Serialize a perception without exposing internal Python Enum objects."""

    return {
        "eye": perception.eye.value,
        "detector": perception.detector,
        "evidence": list(perception.evidence),
        "confidence": perception.confidence,
        "hypothesis": perception.hypothesis,
    }


def observe_repository(
    root: Path,
    *,
    max_commits: int = 200,
    min_support: int = 3,
    min_score: float = 0.80,
) -> dict[str, object]:
    """Collect repository evidence and run deterministic Glitch Eye fusion."""

    state = collect_repository_state(
        root,
        max_commits=max_commits,
        min_support=min_support,
        min_score=min_score,
    )
    engine = build_default_engine()
    perceptions = engine.fusion(
        (Eye.HIDDEN_CONTEXT, Eye.TEMPORAL),
        state,
    )

    return {
        "schema_version": "cmb.glitch-eye-observation.v1",
        "root": str(root.resolve()),
        "state": state,
        "perceptions": [perception_to_dict(item) for item in perceptions],
        "boundaries": [
            "PATTERN != PROOF",
            "CORRELATION != DEPENDENCY",
            "CHANGE != DEFECT",
            "PERCEPTION != AUTHORITY",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
    }


def main() -> int:
    """Allow direct read-only execution with python -m cmb_agents.eyes.collectors."""

    payload = observe_repository(Path.cwd())
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
