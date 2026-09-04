"""Artifact-level sealing and verification APIs."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, TypeAlias

from .canonical import canonical_json_bytes, sha256_bytes, sha256_file
from .constants import (
    GIT_COMMIT_CALLER_SUPPLIED,
    GIT_COMMIT_VERIFIED,
    HASH_ALGORITHM,
    MANIFEST_SCHEMA_VERSION,
    RECEIPT_SCHEMA_VERSION,
    TOOL_VERSION,
)
from .errors import SchemaValidationError, SealError
from .models import (
    ArtifactDigest,
    ArtifactManifest,
    Coverage,
    SealReceipt,
    VerificationFailure,
    VerificationResult,
)
from .schemas import (
    load_json_strict,
    validate_git_commit,
    validate_receipt,
    validate_relative_path,
)
from .timeutil import normalize_timestamp, utc_now_iso

PathInput: TypeAlias = str | os.PathLike[str]
PathsInput: TypeAlias = PathInput | Iterable[PathInput]
ReceiptInput: TypeAlias = SealReceipt | Mapping[str, Any] | PathInput
_GIT_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def _path_list(paths: PathsInput) -> list[Path]:
    if isinstance(paths, (str, os.PathLike)):
        result = [Path(paths)]
    else:
        result = [Path(path) for path in paths]
    if not result:
        raise SealError("At least one protected path is required.")
    return result


def _base_path(base_dir: PathInput | None) -> Path:
    candidate = Path.cwd() if base_dir is None else Path(base_dir)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise SealError(f"Unable to resolve sealing root {candidate}: {exc}") from exc
    if not resolved.is_dir():
        raise SealError(f"Sealing root is not a directory: {resolved}")
    return resolved


def _protected_file(base: Path, supplied: Path) -> tuple[Path, str]:
    candidate = supplied if supplied.is_absolute() else base / supplied
    try:
        if candidate.is_symlink():
            raise SealError(f"Refusing to seal symbolic link: {candidate}")
        resolved = candidate.resolve(strict=True)
        relative = resolved.relative_to(base)
    except SealError:
        raise
    except ValueError as exc:
        raise SealError(
            f"Protected path is outside sealing root {base}: {candidate}"
        ) from exc
    except OSError as exc:
        raise SealError(f"Unable to resolve protected path {candidate}: {exc}") from exc
    canonical_path = validate_relative_path(relative.as_posix())
    return resolved, canonical_path


def resolve_git_commit(base_dir: PathInput) -> str:
    base = Path(base_dir)
    try:
        completed = subprocess.run(
            ["git", "-C", str(base), "rev-parse", "--verify", "HEAD^{commit}"],
            check=False,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SealError(f"Unable to resolve Git commit: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "not inside a Git worktree"
        raise SealError(f"Unable to resolve Git commit for {base}: {detail}")
    commit = completed.stdout.strip().lower()
    try:
        return validate_git_commit(commit)
    except SchemaValidationError as exc:
        raise SealError(f"Git returned an invalid full commit ID: {commit!r}") from exc


def _run_git(base: Path, arguments: list[str], *, operation: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(base), *arguments],
            check=False,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SealError(f"Unable to {operation}: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "Git failed"
        raise SealError(f"Unable to {operation}: {detail}")
    return completed.stdout.strip()


def verify_worktree_artifacts_match_commit(
    base: Path, commit: str, artifacts: Iterable[tuple[Path, ArtifactDigest]]
) -> None:
    """Require every captured artifact digest to equal its committed Git blob."""

    root_text = _run_git(
        base, ["rev-parse", "--show-toplevel"], operation="resolve Git worktree root"
    )
    try:
        root = Path(root_text).resolve(strict=True)
    except OSError as exc:
        raise SealError(
            f"Unable to resolve Git worktree root {root_text!r}: {exc}"
        ) from exc

    for resolved, artifact in artifacts:
        try:
            repository_path = resolved.relative_to(root).as_posix()
        except ValueError as exc:
            raise SealError(
                f"Protected path is outside the Git worktree: {artifact.path}"
            ) from exc

        committed_object = _run_git(
            root,
            ["rev-parse", "--verify", f"{commit}:{repository_path}"],
            operation=f"find {artifact.path!r} in Git commit {commit}",
        ).lower()
        if not _GIT_OBJECT_ID_RE.fullmatch(committed_object):
            raise SealError(f"Git returned an invalid object ID for {artifact.path!r}.")
        committed_digest, committed_size = _hash_git_blob(root, committed_object)
        if committed_size != artifact.size_bytes or not hmac.compare_digest(
            committed_digest, artifact.sha256
        ):
            raise SealError(
                f"Protected file differs byte-for-byte from Git commit {commit}: "
                f"{artifact.path}"
            )


def _hash_git_blob(root: Path, object_id: str) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    try:
        with tempfile.TemporaryFile() as error_output:
            process = subprocess.Popen(
                ["git", "-C", str(root), "cat-file", "blob", object_id],
                stdout=subprocess.PIPE,
                stderr=error_output,
            )
            if process.stdout is None:  # pragma: no cover - guaranteed by PIPE
                process.kill()
                raise SealError("Unable to read committed Git blob output.")
            with process.stdout:
                while chunk := process.stdout.read(1024 * 1024):
                    digest.update(chunk)
                    size += len(chunk)
            return_code = process.wait(timeout=10)
            if return_code != 0:
                error_output.seek(0)
                detail = error_output.read().decode("utf-8", errors="replace").strip()
                raise SealError(
                    f"Unable to read committed Git blob {object_id}: "
                    f"{detail or 'Git failed'}"
                )
    except SealError:
        raise
    except subprocess.TimeoutExpired as exc:
        process.kill()
        process.wait()
        raise SealError(f"Timed out reading committed Git blob {object_id}.") from exc
    except OSError as exc:
        raise SealError(
            f"Unable to read committed Git blob {object_id}: {exc}"
        ) from exc
    return digest.hexdigest(), size


def _receipt_from_mapping(raw: Mapping[str, Any]) -> SealReceipt:
    validated = validate_receipt(raw)
    manifest_data = validated["manifest"]
    manifest = ArtifactManifest(
        schema_version=manifest_data["schema_version"],
        tool_version=manifest_data["tool_version"],
        hash_algorithm=manifest_data["hash_algorithm"],
        git_commit=manifest_data["git_commit"],
        git_commit_status=manifest_data["git_commit_status"],
        artifacts=tuple(
            ArtifactDigest(**artifact) for artifact in manifest_data["artifacts"]
        ),
    )
    coverage_data = validated["coverage"]
    return SealReceipt(
        schema_version=validated["schema_version"],
        tool_version=validated["tool_version"],
        created_at_utc=validated["created_at_utc"],
        coverage=Coverage(
            type=coverage_data["type"],
            paths=tuple(coverage_data["paths"]),
            excludes_unlisted=coverage_data["excludes_unlisted"],
        ),
        manifest=manifest,
        manifest_sha256=validated["manifest_sha256"],
    )


def coerce_receipt(receipt: ReceiptInput) -> SealReceipt:
    if isinstance(receipt, SealReceipt):
        return _receipt_from_mapping(receipt.to_dict())
    if isinstance(receipt, Mapping):
        return _receipt_from_mapping(receipt)
    return load_receipt(receipt)


def seal(
    paths: PathsInput,
    *,
    base_dir: PathInput | None = None,
    git_commit: str | None = None,
    created_at_utc: str | None = None,
) -> SealReceipt:
    """Seal an explicit set of files and return a self-describing receipt."""

    supplied_paths = _path_list(paths)
    base = _base_path(base_dir)
    artifacts: list[ArtifactDigest] = []
    resolved_artifacts: list[tuple[Path, ArtifactDigest]] = []
    seen: set[str] = set()
    for supplied in supplied_paths:
        resolved, canonical_path = _protected_file(base, supplied)
        if canonical_path in seen:
            raise SealError(
                f"Protected path was supplied more than once: {canonical_path}"
            )
        seen.add(canonical_path)
        digest, size = sha256_file(resolved)
        artifact = ArtifactDigest(path=canonical_path, sha256=digest, size_bytes=size)
        resolved_artifacts.append((resolved, artifact))
        artifacts.append(artifact)
    artifacts.sort(key=lambda artifact: artifact.path)

    if git_commit is None:
        commit = resolve_git_commit(base)
        verify_worktree_artifacts_match_commit(base, commit, resolved_artifacts)
        git_commit_status = GIT_COMMIT_VERIFIED
    else:
        commit = validate_git_commit(git_commit.lower())
        git_commit_status = GIT_COMMIT_CALLER_SUPPLIED
    manifest = ArtifactManifest(
        schema_version=MANIFEST_SCHEMA_VERSION,
        tool_version=TOOL_VERSION,
        hash_algorithm=HASH_ALGORITHM,
        git_commit=commit,
        git_commit_status=git_commit_status,
        artifacts=tuple(artifacts),
    )
    manifest_sha256 = sha256_bytes(canonical_json_bytes(manifest.to_dict()))
    timestamp = (
        utc_now_iso() if created_at_utc is None else normalize_timestamp(created_at_utc)
    )
    receipt = SealReceipt(
        schema_version=RECEIPT_SCHEMA_VERSION,
        tool_version=TOOL_VERSION,
        created_at_utc=timestamp,
        coverage=Coverage(
            type="explicit_file_set",
            paths=tuple(artifact.path for artifact in artifacts),
            excludes_unlisted=True,
        ),
        manifest=manifest,
        manifest_sha256=manifest_sha256,
    )
    return _receipt_from_mapping(receipt.to_dict())


def save_receipt(receipt: ReceiptInput, path: PathInput) -> Path:
    """Atomically write a validated receipt, replacing only the target file."""

    validated = coerce_receipt(receipt)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(validated.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n"
    )
    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
        )
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
        temporary_name = None
        if os.name != "nt":
            directory_fd = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    except OSError as exc:
        raise SealError(f"Unable to write receipt {destination}: {exc}") from exc
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
    return destination


def load_receipt(path: PathInput) -> SealReceipt:
    source = Path(path)
    try:
        if source.stat().st_size > 16 * 1024 * 1024:
            raise SealError(f"Receipt exceeds the 16 MiB safety limit: {source}")
        raw = load_json_strict(source.read_text(encoding="utf-8"))
    except SealError:
        raise
    except (OSError, UnicodeError) as exc:
        raise SealError(f"Unable to read receipt {source}: {exc}") from exc
    return _receipt_from_mapping(raw)


def _verification_paths(
    base: Path, paths: PathsInput
) -> tuple[dict[str, Path], list[VerificationFailure]]:
    mapped: dict[str, Path] = {}
    failures: list[VerificationFailure] = []
    for supplied in _path_list(paths):
        candidate = supplied if supplied.is_absolute() else base / supplied
        try:
            resolved = candidate.resolve(strict=False)
            relative = resolved.relative_to(base).as_posix()
            canonical_path = validate_relative_path(relative)
        except (OSError, ValueError, SchemaValidationError) as exc:
            failures.append(
                VerificationFailure(
                    str(supplied),
                    "INVALID_PATH",
                    f"Path is outside the verification root: {exc}",
                )
            )
            continue
        if canonical_path in mapped:
            failures.append(
                VerificationFailure(
                    canonical_path,
                    "DUPLICATE_PATH",
                    "Path was supplied more than once.",
                )
            )
            continue
        mapped[canonical_path] = candidate
    return mapped, failures


def verify(
    paths: PathsInput,
    receipt: ReceiptInput,
    *,
    base_dir: PathInput | None = None,
    check_git_commit: bool = False,
) -> VerificationResult:
    """Verify the exact declared coverage and byte digests in a seal receipt."""

    sealed = coerce_receipt(receipt)
    base = _base_path(base_dir)
    supplied, failures = _verification_paths(base, paths)
    expected = {artifact.path: artifact for artifact in sealed.manifest.artifacts}

    for extra in sorted(set(supplied) - set(expected)):
        failures.append(
            VerificationFailure(
                extra, "UNSEALED_PATH", "Path is not covered by this receipt."
            )
        )
    for missing in sorted(set(expected) - set(supplied)):
        failures.append(
            VerificationFailure(
                missing,
                "MISSING_COVERAGE",
                "Receipt covers this path, but it was not supplied.",
            )
        )

    checked: list[str] = []
    for path in sorted(set(expected) & set(supplied)):
        artifact = expected[path]
        try:
            digest, size = sha256_file(supplied[path])
        except SealError as exc:
            failures.append(VerificationFailure(path, "READ_ERROR", str(exc)))
            continue
        checked.append(path)
        if size != artifact.size_bytes:
            failures.append(
                VerificationFailure(
                    path,
                    "SIZE_MISMATCH",
                    f"Expected {artifact.size_bytes} bytes; found {size} bytes.",
                )
            )
        if not hmac.compare_digest(digest, artifact.sha256):
            failures.append(
                VerificationFailure(
                    path, "DIGEST_MISMATCH", "Byte-level SHA-256 digest does not match."
                )
            )

    git_matches: bool | None = None
    if check_git_commit:
        try:
            git_matches = hmac.compare_digest(
                resolve_git_commit(base), sealed.manifest.git_commit
            )
        except SealError as exc:
            failures.append(VerificationFailure(None, "GIT_ERROR", str(exc)))
            git_matches = False
        else:
            if not git_matches:
                failures.append(
                    VerificationFailure(
                        None,
                        "GIT_COMMIT_MISMATCH",
                        "Current Git commit is not the commit recorded by the receipt.",
                    )
                )

    return VerificationResult(
        ok=not failures,
        manifest_sha256=sealed.manifest_sha256,
        checked_paths=tuple(checked),
        git_commit_matches=git_matches,
        failures=tuple(failures),
    )
