"""Validate search discovery signals in the exact bundle uploaded to GitHub Pages.

This tests publisher output, not whether Google crawled, indexed, or ranked a URL.
"""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

SITE_URL = "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/"
VERIFICATION = "google57d4128d590e83d8.html"
KEY_PAGES = (
    "",
    "concepts/what-is-cmb/",
    "concepts/human-agency-machine-authority/",
    "concepts/cognitive-sovereignty/",
    "fables/",
    "RESEARCHERS/",
)


class PageMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_head = False
        self.in_title = False
        self.title = ""
        self.canonicals: list[str] = []
        self.description = ""
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "head":
            self.in_head = True
        if not self.in_head:
            return
        values = {name.lower(): (value or "") for name, value in attrs}
        if tag == "title":
            self.in_title = True
        if tag == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonicals.append(values.get("href", ""))
        if tag == "meta":
            name = values.get("name", "").lower()
            if name == "description":
                self.description = values.get("content", "").strip()
            if name in {"robots", "googlebot"} and "noindex" in values.get("content", "").lower():
                self.noindex = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "head":
            self.in_head = False

    def handle_data(self, data: str) -> None:
        if self.in_head and self.in_title:
            self.title += data


def inspect_page(path: Path) -> PageMetadata:
    metadata = PageMetadata()
    metadata.feed(path.read_text(encoding="utf-8"))
    return metadata


def verify_search_discovery(site: Path) -> list[str]:
    """Return actionable failures, not unverifiable claims about Google's index."""
    errors: list[str] = []
    sitemap_path = site / "sitemap.xml"
    verification_path = site / VERIFICATION
    if not verification_path.is_file() or (
        verification_path.read_text(encoding="utf-8").strip()
        != f"google-site-verification: {VERIFICATION}"
    ):
        errors.append("Google ownership verification file is missing or incorrect.")

    urls: set[str] = set()
    if not sitemap_path.is_file():
        errors.append("Generated sitemap.xml is missing.")
    else:
        try:
            root = ET.parse(sitemap_path).getroot()
            namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
            if root.tag != namespace + "urlset":
                errors.append("sitemap.xml does not contain a standard sitemap urlset.")
            else:
                locations = [node.text or "" for node in root.findall(f"{namespace}url/{namespace}loc")]
                if len(locations) < len(KEY_PAGES):
                    errors.append("sitemap.xml is missing most of the key pages.")
                for loc in locations:
                    if loc in urls:
                        errors.append(f"Duplicate sitemap URL: {loc}")
                    urls.add(loc)
                    parsed = urlsplit(loc)
                    if not loc.startswith(SITE_URL) or parsed.query or parsed.fragment:
                        errors.append(f"Sitemap URL outside canonical origin or contains query/fragment: {loc}")
                        continue
                    relative = unquote(loc[len(SITE_URL):])
                    if relative.startswith("/") or ".." in Path(relative).parts:
                        errors.append(f"Unsafe sitemap path: {loc}")
                        continue
                    target = site / relative
                    target = target / "index.html" if loc.endswith("/") else target
                    if not target.is_file():
                        errors.append(f"Sitemap points to missing published HTML: {loc}")
        except (OSError, ET.ParseError) as exc:
            errors.append(f"sitemap.xml is unreadable or invalid XML: {exc}")

    for relative in KEY_PAGES:
        url = SITE_URL + relative
        html = site / relative / "index.html"
        if not html.is_file():
            errors.append(f"Key search landing page missing: {relative or '(home)'}")
            continue
        if url not in urls:
            errors.append(f"Key landing page not listed in sitemap: {url}")
        meta = inspect_page(html)
        if meta.canonicals != [url]:
            errors.append(f"Canonical must point to the one public page URL: {url}; got {meta.canonicals}")
        if meta.noindex:
            errors.append(f"Key landing page has a noindex directive: {url}")
        if not meta.title.strip():
            errors.append(f"Key landing page has no HTML title: {url}")
        if not relative and not meta.description:
            errors.append("Homepage is missing HTML meta description.")
        if not relative and "Jupiter Hudson" not in meta.title:
            errors.append("Homepage HTML title does not attribute the creator.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, required=True)
    args = parser.parse_args()
    failures = verify_search_discovery(args.site_dir)
    if failures:
        print("Search discovery validation failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("Search discovery PASS: canonical pages, sitemap targets, homepage metadata, and verification file.")
    print("Note: Google indexing, live HTTP headers, and host-root robots.txt require external checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
