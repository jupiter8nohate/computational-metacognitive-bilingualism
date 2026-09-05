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

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/"
PUBLIC_DIRECTORIES = (
    "assets", "agents", "extensions", "library", "machine", "schemas", "spec",
    "research/case-studies",
)
PUBLIC_FILES = ("AGENTS.md", "llms.txt", "llms-full.txt", "CITATION.cff", "CITATION.bib")
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

    required = (
        *PUBLIC_FILES, "sitemap.xml", "robots.txt", ".well-known/agent-card.json",
        "agents/agent-card.json", "agents/registry.json", "cmb-machine-origin.json",
        "library/catalog.json", "machine/index.json", "machine/discovery-manifest.json",
        "machine/knowledge-graph.jsonld", "machine/generated/manifest.json",
    )
    for path in required:
        check("index.html", path)

    for filename in ("machine/discovery-manifest.json", "machine/index.json"):
        path = site / filename
        if not path.is_file():
            continue
        for value in strings(json.loads(path.read_text(encoding="utf-8"))):
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
    (site / ".well-known").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "agents/agent-card.json", site / ".well-known/agent-card.json")
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
