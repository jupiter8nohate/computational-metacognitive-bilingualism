"""Validate search discovery signals in the exact bundle uploaded to GitHub Pages.

This tests publisher output, not whether Google crawled, indexed, or ranked a URL.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, unquote
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
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
    "JUPITER_HUDSON_BIOGRAPHY/",
    "GLOBAL_AI_WATCH/",
    "FAQ/",
    "story-universe/",
    "spiders-internet/",
    "playground/",
)
UTILITY_HTML = {"search.html", "404.html", VERIFICATION}


class PageMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_head = False
        self.in_title = False
        self.title = ""
        self.title_count = 0
        self.canonicals: list[str] = []
        self.descriptions: list[str] = []
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "head":
            self.in_head = True
        if not self.in_head:
            return
        values = {name.lower(): (value or "") for name, value in attrs}
        if tag == "title":
            self.in_title = True
            self.title_count += 1
        if tag == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonicals.append(values.get("href", ""))
        if tag == "meta":
            name = values.get("name", "").lower()
            if name == "description":
                self.descriptions.append(values.get("content", "").strip())
            if name in {"robots", "googlebot"} and blocks_indexing(
                values.get("content", "")
            ):
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


def blocks_indexing(value: str) -> bool:
    return bool({"noindex", "none"} & set(re.split(r"[\s,:;]+", value.lower())))


def metadata_errors(meta: PageMetadata, url: str) -> list[str]:
    errors = []
    if meta.canonicals != [url]:
        errors.append(
            f"Canonical must point to the one public page URL: {url}; got {meta.canonicals}"
        )
    if meta.noindex:
        errors.append(f"Search landing page has a noindex directive: {url}")
    if meta.title_count != 1 or not meta.title.strip():
        errors.append(
            f"Search landing page must have exactly one nonempty HTML title: {url}"
        )
    if len(meta.descriptions) != 1 or not meta.descriptions[0]:
        errors.append(
            f"Search landing page must have exactly one nonempty meta description: {url}"
        )
    return errors


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
                locations = [
                    node.text or ""
                    for node in root.findall(f"{namespace}url/{namespace}loc")
                ]
                if len(locations) < len(KEY_PAGES):
                    errors.append("sitemap.xml is missing most of the key pages.")
                for loc in locations:
                    if loc in urls:
                        errors.append(f"Duplicate sitemap URL: {loc}")
                    urls.add(loc)
                    parsed = urlsplit(loc)
                    if not loc.startswith(SITE_URL) or parsed.query or parsed.fragment:
                        errors.append(
                            f"Sitemap URL outside canonical origin or contains query/fragment: {loc}"
                        )
                        continue
                    relative = unquote(loc[len(SITE_URL) :])
                    if relative.startswith("/") or ".." in Path(relative).parts:
                        errors.append(f"Unsafe sitemap path: {loc}")
                        continue
                    target = site / relative
                    target = target / "index.html" if loc.endswith("/") else target
                    if not target.is_file():
                        errors.append(
                            f"Sitemap points to missing published HTML: {loc}"
                        )
                    elif target.suffix != ".html" or relative in UTILITY_HTML:
                        errors.append(
                            f"Sitemap includes a non-landing-page resource: {loc}"
                        )
                    else:
                        errors.extend(metadata_errors(inspect_page(target), loc))
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
    # Validate coverage in both directions, including HTML copied outside MkDocs.
    titles: dict[str, str] = {}
    for html in sorted(site.rglob("*.html")):
        relative = html.relative_to(site).as_posix()
        if relative in UTILITY_HTML:
            if relative != VERIFICATION and not inspect_page(html).noindex:
                errors.append(
                    f"Search/error utility needs a noindex directive: {relative}"
                )
            continue
        route = (
            relative.removesuffix("index.html")
            if relative.endswith("index.html")
            else relative
        )
        url = SITE_URL + route
        if url not in urls:
            errors.append(f"Public HTML landing page not listed in sitemap: {url}")
            errors.extend(metadata_errors(inspect_page(html), url))
        meta = inspect_page(html)
        title = " ".join(meta.title.split()).casefold()
        if title in titles:
            errors.append(f"Duplicate search title: {titles[title]} and {url}")
        titles[title] = url
        if not route and "Jupiter Hudson" not in meta.title:
            errors.append("Homepage HTML title does not attribute the creator.")

    compressed = site / "sitemap.xml.gz"
    if compressed.is_file() and sitemap_path.is_file():
        try:
            if gzip.decompress(compressed.read_bytes()) != sitemap_path.read_bytes():
                errors.append("Compressed sitemap differs from sitemap.xml.")
        except (OSError, EOFError) as exc:
            errors.append(f"Compressed sitemap is unreadable: {exc}")

    return errors


def fetch_public_url(url: str) -> tuple[str, dict[str, str], int]:
    """Fetch as a publisher checker; never impersonate Googlebot or claim a Google crawl."""
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "CMB-Publication-Check/1.0"})
            with urlopen(request, timeout=20) as response:
                return (
                    response.read().decode("utf-8"),
                    {key.lower(): value for key, value in response.headers.items()},
                    response.status,
                )
        except HTTPError as exc:
            if 400 <= exc.code < 500 and exc.code != 429:
                return "", {}, exc.code
            if attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2)
    raise RuntimeError("HTTP retry loop exhausted")


def verify_live_publication() -> dict[str, object]:
    """Check published HTTP responses and host-root robots policy, not Google's index."""
    errors: list[str] = []
    sitemap_urls: set[str] = set()
    try:
        text, _, status = fetch_public_url(SITE_URL + "sitemap.xml")
        if status != 200:
            raise ValueError(f"HTTP {status}")
        namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        root = ET.fromstring(text)
        if root.tag != namespace + "urlset":
            raise ValueError("Expected sitemap urlset")
        sitemap_urls = {
            node.text or "" for node in root.findall(f"{namespace}url/{namespace}loc")
        }
    except (OSError, ValueError, ET.ParseError) as exc:
        errors.append(f"Published sitemap could not be read: {exc}")

    robots_url = "https://" + urlsplit(SITE_URL).netloc + "/robots.txt"
    robots_status: int | None = None
    try:
        text, _, robots_status = fetch_public_url(robots_url)
        if robots_status == 200:
            policy = RobotFileParser(robots_url)
            policy.parse(text.splitlines())
            for route in KEY_PAGES:
                if not policy.can_fetch("Googlebot", SITE_URL + route):
                    errors.append(
                        f"Host-root robots.txt blocks Googlebot: {SITE_URL + route}"
                    )
        elif not (400 <= robots_status < 500 and robots_status != 429):
            errors.append(f"Host-root robots.txt returned HTTP {robots_status}")
    except OSError as exc:
        errors.append(f"Host-root robots.txt could not be checked: {exc}")

    def check(relative: str) -> list[str]:
        url = SITE_URL + relative
        try:
            text, headers, status = fetch_public_url(url)
            if status != 200:
                return [f"Published landing page returned HTTP {status}: {url}"]
            metadata = PageMetadata()
            metadata.feed(text)
            failures = metadata_errors(metadata, url)
            if blocks_indexing(headers.get("x-robots-tag", "")):
                failures.append(f"Published X-Robots-Tag blocks indexing: {url}")
            if url not in sitemap_urls:
                failures.append(f"Published landing page missing from sitemap: {url}")
            return failures
        except (OSError, ValueError) as exc:
            return [f"Published landing page could not be checked: {url}: {exc}"]

    with ThreadPoolExecutor(max_workers=4) as workers:
        for failures in workers.map(check, KEY_PAGES):
            errors.extend(failures)
    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "evidence_source": "publisher_http_checks",
        "publication_status": "FAIL" if errors else "PASS",
        "google_index_status": "UNKNOWN",
        "root_robots_url": robots_url,
        "root_robots_http_status": robots_status,
        "checked_urls": [SITE_URL + route for route in KEY_PAGES],
        "failures": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--site-dir", type=Path)
    mode.add_argument("--live", action="store_true")
    parser.add_argument("--report-path", type=Path)
    args = parser.parse_args()
    if args.live:
        report = verify_live_publication()
        if args.report_path:
            args.report_path.write_text(
                json.dumps(report, indent=2) + "\n", encoding="utf-8"
            )
        print(json.dumps(report, indent=2))
        return int(report["publication_status"] != "PASS")
    failures = verify_search_discovery(args.site_dir)
    if failures:
        print("Search discovery validation failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "Search discovery PASS: every public HTML landing page, unique titles, descriptions, canonicals, sitemap coverage and verification file."
    )
    print(
        "Note: Google indexing, live HTTP headers, and host-root robots.txt require external checks."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
