"""Build and verify the same public bundle locally, in CI, and for Pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterator
from urllib.parse import unquote, urljoin, urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/"
PUBLIC_DIRECTORIES = (
    "assets", "agents", "datasets", "extensions", "library", "machine", "schemas", "spec",
    "conformance/glitch-ir", "research/case-studies",
    "examples/polyglot/jupiter_glitchology_runtime",
    "examples/polyglot/glitchology_registry_3d_runtime",
)
PUBLIC_FILES = ("AGENTS.md", "llms.txt", "llms-full.txt", "CITATION.cff", "CITATION.bib")
REQUIRED_PUBLIC_PATHS = (
    *PUBLIC_FILES,
    "sitemap.xml",
    "robots.txt",
    "agents/agent-card.json",
    "agents/registry.json",
    "cmb-machine-origin.json",
    "library/catalog.json",
    "library/cmb-conversation-atlas.v1.json",
    "schemas/cmb.conversation-atlas.v1.schema.json",
    "schemas/cmb.stewardship-status.v1.schema.json",
    "schemas/cmb.discovery.v1.schema.json",
    "machine/index.json",
    "machine/discovery-manifest.json",
    "machine/recovery-map.json",
    "machine/stewardship-status.json",
    "machine/knowledge-graph.jsonld",
    "machine/generated/manifest.json",
    "machine/glitch-ir.json",
    "schemas/glitch-ir.v1.schema.json",
    "conformance/glitch-ir/v1/GLT-8101-V001.json",
    "machine/glitch-3d.json",
    "schemas/glitch-3d.v1.schema.json",
    "spec/GLITCH-3D-1.md",
    "examples/polyglot/glitchology_registry_3d_runtime/GLITCH_3D_SOURCE_FRACTURE.g3d",
    "datasets/cmb-canonical-corpus/manifest.json",
    "datasets/cmb-canonical-corpus/corpus.jsonl",
    "schemas/cmb.recovery-map.v1.schema.json",
    "schemas/cmb.canonical-corpus-manifest.v1.schema.json",
    "schemas/cmb.canonical-corpus-record.v1.schema.json",
    "examples/polyglot/jupiter_glitchology_runtime/README.md",
    "examples/polyglot/jupiter_glitchology_runtime/main.go",
    "examples/polyglot/jupiter_glitchology_runtime/mirror.py",
)
BUILD_MARKER = ".cmb-docs-build"


class PageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()
        self.headings = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h1":
            self.headings += 1
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.add(value)


def strings(value: object) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def validate_discovery_manifest(site: Path, errors: set[str]) -> None:
    """Validate the published discovery manifest against its declared Draft 2020-12 schema."""
    manifest_path = site / "machine/discovery-manifest.json"
    schema_path = site / "schemas/cmb.discovery.v1.schema.json"
    if not manifest_path.is_file() or not schema_path.is_file():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, SchemaError) as exc:
        errors.add(f"Discovery schema setup failed: {exc}")
        return
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.add(f"Discovery manifest schema violation at {location}: {error.message}")


def local_target(site: Path, source: str, link: str) -> Path | None:
    """Resolve links with browser URL rules, including the Pages project prefix."""
    url = urlsplit(urljoin(urljoin(SITE_URL, source), link))
    origin = urlsplit(SITE_URL)
    if url.scheme not in {"http", "https"} or url.netloc != origin.netloc:
        return None
    if not url.path.startswith(origin.path):
        raise ValueError(f"URL leaves the project path: {link}")
    target = (site / unquote(url.path[len(origin.path):])).resolve()
    if not target.is_relative_to(site.resolve()):
        raise ValueError(f"URL escapes the build directory: {link}")
    return target / "index.html" if target.is_dir() or url.path.endswith("/") else target


def check_site(site: Path) -> tuple[int, int]:
    """Reject missing local assets, discovery endpoints, and damaged bundles."""
    errors: set[str] = set()
    link_count = 0
    pages = sorted(site.rglob("*.html"))

    def check(source: str, link: str) -> None:
        nonlocal link_count
        try:
            target = local_target(site, source, link)
        except ValueError as exc:
            errors.add(f"{source}: {exc}")
            return
        if target is not None:
            link_count += 1
            if not target.is_file():
                errors.add(f"{source} -> {link}")

    if not (site / "index.html").is_file():
        errors.add("Missing homepage: index.html")
    for page in pages:
        source = page.relative_to(site).as_posix()
        parser = PageLinks()
        parser.feed(page.read_text(encoding="utf-8"))
        for link in parser.links:
            check(source, link)
        if source == "index.html" and parser.headings != 1:
            errors.add("Homepage must render exactly one h1 heading.")

    for path in REQUIRED_PUBLIC_PATHS:
        check("index.html", path)

    validate_discovery_manifest(site, errors)

    for filename in ("machine/discovery-manifest.json", "machine/index.json", "machine/recovery-map.json", "machine/knowledge-graph.jsonld"):
        path = site / filename
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if filename == "machine/knowledge-graph.jsonld" and isinstance(payload, dict):
            # JSON-LD @context values are vocabulary namespaces, not fetchable
            # publication targets. Validate graph content, not namespace IRIs.
            payload = {key: value for key, value in payload.items() if key != "@context"}
        for value in strings(payload):
            if value.startswith(SITE_URL) or (not value.endswith("/") and value.startswith(
                tuple(f"{directory}/" for directory in PUBLIC_DIRECTORIES)
            )):
                # The machine index declares repository-root paths, not paths
                # relative to the JSON document's own directory.
                check(filename, urljoin(SITE_URL, value))

    for filename in ("llms.txt", "llms-full.txt"):
        path = site / filename
        if path.is_file():
            for link in re.findall(r"\[[^\]]+\]\((https?://[^\s)]+)\)", path.read_text(encoding="utf-8")):
                check(filename, link)

    manifest_path = site / "machine/generated/manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("path_base") != "manifest_directory":
            errors.add("Generated bundle must declare paths relative to its manifest.")
        for item in manifest["artifacts"]:
            target = (manifest_path.parent / item["path"]).resolve()
            if not target.is_relative_to(manifest_path.parent.resolve()) or not target.is_file():
                errors.add(f"Generated artifact is missing or escapes its bundle: {item['path']}")
            elif hashlib.sha256(target.read_bytes()).hexdigest() != item["sha256"]:
                errors.add(f"Generated artifact checksum mismatch: {item['path']}")

    if errors:
        raise ValueError("Public site integrity check failed:\n" + "\n".join(sorted(errors)))
    return len(pages), link_count


def stage_public_assets(site: Path) -> None:
    # Only tracked files from explicit public directories enter the upload.
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", *PUBLIC_DIRECTORIES], cwd=ROOT,
    ).decode("utf-8").split("\0")
    for relative in filter(None, tracked):
        source = ROOT / relative
        if source.is_symlink():
            raise ValueError(f"Public assets must not be symlinks: {relative}")
        target = site / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for filename in PUBLIC_FILES:
        shutil.copyfile(ROOT / filename, site / filename)
    shutil.copyfile(ROOT / "machine/fgc-origin-mark.json", site / "cmb-machine-origin.json")
    subprocess.run(
        [sys.executable, "-m", "cmb_machine.cli", "compile-core", "--output-dir",
         str(site / "machine/generated")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL,
    )


def build_site(destination: Path) -> tuple[int, int]:
    destination = destination.absolute()
    resolved = destination.resolve()
    if destination.is_symlink() or resolved == ROOT or resolved in ROOT.parents:
        raise ValueError("Build output cannot replace a source directory or symlink.")
    if resolved.is_relative_to(ROOT) and resolved != ROOT / "site":
        raise ValueError("Inside the repository, build output must be the ignored site/ directory.")
    if destination.exists() and (
        not destination.is_dir() or (
            any(destination.iterdir()) and not (destination / BUILD_MARKER).is_file()
        )
    ):
        raise ValueError("Output is not empty or a previous CMB docs build; choose a new directory.")

    with tempfile.TemporaryDirectory(prefix="cmb-docs-") as temporary:
        stage = Path(temporary) / "site"
        subprocess.run(
            [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", str(stage)],
            cwd=ROOT, check=True,
        )
        stage_public_assets(stage)
        counts = check_site(stage)
        (stage / BUILD_MARKER).write_text("CMB documentation build\n", encoding="utf-8")
        # The previous local build survives until the new bundle passes validation.
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(stage, destination)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=ROOT / "site")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        pages, links = check_site(args.site_dir) if args.check_only else build_site(args.site_dir)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"Documentation build failed: {exc}", file=sys.stderr)
        return 1
    print(f"Public site verified: {pages} HTML pages, {links} local references, discovery and bundle checksums.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
