"""Add stable page-level discovery metadata without rewriting authored Markdown.

The HTML output is the public artifact. An explicit registry avoids inferring
the meaning of original glyphs, changing story prose, or trusting page headings
as structured facts. This is an SEO/discovery feature, not an indexing claim.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
from html import escape
from pathlib import Path
import gzip
import json
import re
import subprocess
import sys
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.pages import Page

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/"
PREVIEW_IMAGE = SITE_URL + "media/cmb-cognitive-offloading-adaptive-symbiosis.jpg"
START = "<!-- CMB-SEO:BEGIN -->"
END = "<!-- CMB-SEO:END -->"


@dataclass(frozen=True)
class PageSpec:
    title: str
    description: str
    kind: str = "fiction"


# 'term' pages already publish a DefinedTerm JSON-LD node in authored Markdown.
# 'research' pages must never be described as evidence of fictional events.
PAGE_SPECS: dict[str, PageSpec] = {
    "2084/": PageSpec(
        "DEATH NOTE 2084: Complete Reading Guide | Jupiter Hudson",
        "Follow Jupiter, Nia and Mara through the D.N.A. Bible's nine published speculative-fiction transmissions and their companion stories.",
    ),
    "story-universe/": PageSpec(
        "The D.N.A. Bible Story Library | Jupiter Hudson",
        "Explore the D.N.A. Bible literary universe: speculative fiction, code-poetry, GLITCHOLOGY symbolism and the DEATH NOTE 2084 story arc.",
    ),
    "ARCHIVE_READING_MAP/": PageSpec(
        "D.N.A. Bible Canonical Reading Order | Jupiter Hudson",
        "An accessible guide to nine DEATH NOTE 2084 transmissions, companion scrolls, research sources and human-agency themes.",
        "guide",
    ),
    "DEATH_NOTE_2084/": PageSpec(
        "DEATH NOTE 2084: Everybody Dies Twice | Jupiter Hudson",
        "The original speculative-fiction story of Jupiter Hudson, the Feed and a society confusing predictive profiles with human identity.",
    ),
    "DEATH_NOTE_2084_FALSE_LIGHT/": PageSpec(
        "DEATH NOTE 2084: The False Light Protocol | Jupiter Hudson",
        "A speculative-fiction chapter about autonomous agents, convenience, consent and the human right to challenge machine-made decisions.",
    ),
    "DEATH_NOTE_2084_HOUSE_OF_A_MILLION_DOORS/": PageSpec(
        "DEATH NOTE 2084: The House of a Million Doors | Jupiter Hudson",
        "Jupiter and Nia enter a fictional digital House where access and identity are controlled through automated permissions.",
    ),
    "DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_CELLS/": PageSpec(
        "DEATH NOTE 2084: The Ledger of Invisible Cells | Jupiter Hudson",
        "A literary transmission exploring evidence, simulated confinement and the danger of treating an automated score as a verdict.",
    ),
    "DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE/": PageSpec(
        "DEATH NOTE 2084: The Child Who Refused the Update | Jupiter Hudson",
        "Nia refuses Continuity Update 84.1 and challenges coerced digital consent in a fictional future governed by predictive systems.",
    ),
    "DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_YEARS/": PageSpec(
        "DEATH NOTE 2084: The Ledger of Invisible Years | Jupiter Hudson",
        "A sequel about the fictional Sovereign Engine, unreliable digital time, consent and the right to contest a machine's evidence.",
    ),
    "DEATH_NOTE_2084_POST_GROUND_BASELINE/": PageSpec(
        "DEATH NOTE 2084: The Post-Ground Baseline | Jupiter Hudson",
        "The seventh literary transmission examines the distinction between physical time, rendered time and a person's lived experience.",
    ),
    "DEATH_NOTE_2084_WITNESS_IN_LIGHTHOUSE/": PageSpec(
        "DEATH NOTE 2084: The Witness Who Never Left the Lighthouse | Jupiter Hudson",
        "Nia and Mara investigate a fictional generated witness and challenge a system that certifies its own testimony.",
    ),
    "DEATH_NOTE_2084_STATION_SEVEN/": PageSpec(
        "DEATH NOTE 2084: Station Seven | Jupiter Hudson",
        "A speculative-fiction chapter about missing consent records, the right to appeal and restoring human judgment.",
    ),
    "DNA_BIBLE_PYRAMID_WARNING_2084/": PageSpec(
        "D.N.A. Bible: The Pyramid Warning of 2084 | Jupiter Hudson",
        "A code-poetry scroll using a fictional watching eye, glyph pyramid and glitch symbolism to examine digital consent and human agency.",
    ),
    "DEATH_NOTE_2084_EVIDENCE_LEDGER/": PageSpec(
        "DEATH NOTE 2084: Evidence Ledger | Jupiter Hudson",
        "A source-linked research companion separating documented digital-rights mechanisms from fictional predictions and allegations.",
        "research",
    ),
    "GLITCHOLOGY_SYMBOL_DICTIONARY/": PageSpec(
        "Err GLITCHOLOGY: Reader Symbol Dictionary | Jupiter Hudson",
        "Definitions of creator-authored GLITCHOLOGY symbols used in the D.N.A. Bible, with interpretation and evidence boundaries.",
        "guide",
    ),
    "concepts/what-is-cmb/": PageSpec(
        "What Is Computational Metacognitive Bilingualism? | Jupiter Hudson",
        "An introduction to CMB, a human-agency and computational-literacy framework distinguishing machine-readable structure from personal meaning.",
        "term",
    ),
}

# These authored HTML pages bypass MkDocs' Markdown page events and sitemap.
STANDALONE_PAGES = {
    "spiders-internet/": (
        "spiders-internet/index.html",
        PageSpec(
            "The Spider's Internet: A Digital Fable | Jupiter Hudson",
            "A digital fable about attention, artificial intelligence and human sovereignty, with an illustrated story and a companion video.",
        ),
    ),
    "playground/": (
        "docs/playground/index.html",
        PageSpec(
            "CMB Interactive Playground | Jupiter Hudson",
            "Try local SHA-256 hashing, CMB-Z13 symbolic lenses and human-agency boundary rules in a browser playground without sending your statement to a server.",
            "page",
        ),
    ),
}

REPLACED_META = {
    "description",
    "og:title",
    "og:description",
    "og:type",
    "og:url",
    "og:image",
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
}
META_RE = re.compile(r"<meta\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(
    r"\b(?:name|property)\s*=\s*([\"'])(.*?)\1", flags=re.IGNORECASE | re.DOTALL
)
TITLE_RE = re.compile(r"<title\b[^>]*>.*?</title\s*>", flags=re.IGNORECASE | re.DOTALL)
MANAGED_RE = re.compile(
    re.escape(START) + r".*?" + re.escape(END) + r"\n?", flags=re.DOTALL
)
HEAD_CLOSE_RE = re.compile(r"</head\s*>", flags=re.IGNORECASE)
LINK_RE = re.compile(r"<link\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
REL_RE = re.compile(r"\brel\s*=\s*([\"'])(.*?)\1", flags=re.IGNORECASE | re.DOTALL)
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class ContentSummary(HTMLParser):
    """Collect visible article paragraphs without nav, scripts, code blocks or glyph art."""

    VOID = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.paragraphs: list[str] = []
        self.current: list[str] | None = None
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if self.skip_depth:
            self.skip_depth += tag not in self.VOID
        elif (
            tag in {"script", "style", "pre", "svg", "nav"}
            or values.get("aria-hidden") == "true"
            or "hidden" in values
        ):
            self.skip_depth = int(tag not in self.VOID)
        elif tag == "p":
            self.current = []

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            if tag not in self.VOID:
                self.skip_depth -= 1
        elif tag == "p" and self.current is not None:
            self.paragraphs.append(" ".join("".join(self.current).split()))
            self.current = None

    def handle_data(self, data: str) -> None:
        if not self.skip_depth and self.current is not None:
            self.current.append(data)


def summarize_content(content: str) -> str:
    """Use the page's own prose as a conservative fallback, never a generated claim."""
    summary = ContentSummary()
    summary.feed(content)
    candidates = [
        p for p in summary.paragraphs if len(re.findall(r"\b[a-zA-Z]+\b", p)) >= 8
    ]
    if not candidates:
        raise ValueError(
            "Page needs an authored description or a readable introductory paragraph"
        )
    text = next((p for p in candidates if len(p) >= 65), candidates[0])
    return (
        text if len(text) <= 190 else text[:187].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"
    )


def on_post_page(output: str, *, page: Page, config: MkDocsConfig) -> str:
    """MkDocs hook: honor front matter and emit head metadata for every Markdown page."""
    if config["site_url"] != SITE_URL:
        raise ValueError("Search metadata must use the configured canonical CMB origin")
    relative = page.url
    curated = PAGE_SPECS.get(relative)
    if not relative:
        fallback_title = config["site_name"]
        fallback_description = config["site_description"]
    else:
        fallback_title = (
            curated.title
            if curated
            else str(page.title).removeprefix("Concepts / ") + " | CMB"
        )
        fallback_description = curated.description if curated else ""
    title = page.meta.get("title") or fallback_title
    description = (
        page.meta.get("description")
        or fallback_description
        or summarize_content(page.content)
    )
    spec = PageSpec(str(title), str(description), curated.kind if curated else "page")
    return enrich_html(output, relative, spec)


def _metadata(spec: PageSpec, url: str) -> str:
    title = escape(spec.title, quote=True)
    description = escape(spec.description, quote=True)
    image = escape(PREVIEW_IMAGE, quote=True)
    canonical = escape(url, quote=True)
    lines = [
        '<link rel="canonical" href="' + canonical + '">',
        '<meta name="description" content="' + description + '">',
        '<meta property="og:type" content="'
        + ("website" if spec.kind == "page" else "article")
        + '">',
        '<meta property="og:title" content="' + title + '">',
        '<meta property="og:description" content="' + description + '">',
        '<meta property="og:url" content="' + canonical + '">',
        '<meta property="og:image" content="' + image + '">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="' + title + '">',
        '<meta name="twitter:description" content="' + description + '">',
        '<meta name="twitter:image" content="' + image + '">',
    ]
    if spec.kind in {"fiction", "guide", "research"}:
        graph: dict[str, object] = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "@id": url + "#work",
            "url": url,
            "name": spec.title.removesuffix(" | Jupiter Hudson"),
            "description": spec.description,
            "inLanguage": "en",
            "author": {"@type": "Person", "name": "Jupiter Hudson"},
            "genre": {
                "fiction": "Speculative fiction",
                "guide": "Literary guide and commentary",
                "research": "Research commentary",
            }[spec.kind],
            "isAccessibleForFree": True,
        }
        if spec.kind in {"fiction", "guide"}:
            graph["isPartOf"] = {
                "@type": "CreativeWorkSeries",
                "name": "D.N.A. Bible / DEATH NOTE 2084",
                "url": SITE_URL + "story-universe/",
            }
        lines.extend(
            [
                '<script type="application/ld+json">',
                json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace(
                    "</", "<\\/"
                ),
                "</script>",
            ]
        )
    return START + "\n" + "\n".join(lines) + "\n" + END


def enrich_html(source: str, relative: str, spec: PageSpec) -> str:
    """Replace only HTML-head metadata, preserving body and authored glyphs."""
    match = HEAD_CLOSE_RE.search(source)
    if match is None:
        raise ValueError(f"{relative}: rendered HTML has no closing head tag")
    head, body = source[: match.start()], source[match.start() :]
    if not re.search(r"<head\b", head, flags=re.IGNORECASE):
        raise ValueError(f"{relative}: rendered HTML has no opening head tag")
    head = MANAGED_RE.sub("", head)

    def keep_nonmanaged(match: re.Match[str]) -> str:
        attr = ATTR_RE.search(match.group())
        return "" if attr and attr.group(2).lower() in REPLACED_META else match.group()

    head = META_RE.sub(keep_nonmanaged, head)

    def keep_noncanonical(match: re.Match[str]) -> str:
        rel = REL_RE.search(match.group())
        return (
            "" if rel and "canonical" in rel.group(2).lower().split() else match.group()
        )

    head = LINK_RE.sub(keep_noncanonical, head)
    page_title = "<title>" + escape(spec.title) + "</title>"
    first_title = TITLE_RE.search(head)
    if first_title is None:
        raise ValueError(f"{relative}: rendered HTML has no title tag")
    head = TITLE_RE.sub(
        lambda m: page_title if m.start() == first_title.start() else "", head
    )
    return head + _metadata(spec, SITE_URL + relative) + "\n" + body


def source_revision_dates(root: Path) -> dict[str, str]:
    """Return committed source dates; shallow, dirty and untracked sources get no date."""
    try:

        def git(*args: str) -> str:
            return subprocess.check_output(
                ["git", "-C", str(root), *args],
                text=True,
                stderr=subprocess.DEVNULL,
            )

        if git("rev-parse", "--is-shallow-repository").strip() != "false":
            return {}
        dirty = set(
            git(
                "diff", "--name-only", "-z", "HEAD", "--", "docs", "spiders-internet"
            ).split("\0")
        )
        history = git(
            "-c",
            "core.quotePath=false",
            "log",
            "--format=@@%cI",
            "--name-only",
            "--",
            "docs",
            "spiders-internet",
        )
    except (OSError, subprocess.CalledProcessError):
        return {}
    dates: dict[str, str] = {}
    date = ""
    for line in history.splitlines():
        if line.startswith("@@"):
            date = line[2:]
        elif line and date and line not in dirty:
            dates.setdefault(line, date)
    return dates


def page_source(relative: str, root: Path) -> str | None:
    if relative in STANDALONE_PAGES:
        return STANDALONE_PAGES[relative][0]
    candidates = (
        ["docs/index.md"]
        if not relative
        else [
            "docs/" + relative.removesuffix("/") + ".md",
            "docs/" + relative + "index.md",
        ]
    )
    return next((path for path in candidates if (root / path).is_file()), None)


def finalize_sitemap(site: Path, root: Path = ROOT) -> int:
    """Complete MkDocs' sitemap after static assets are staged and replace build dates."""
    path = site / "sitemap.xml"
    sitemap = ET.parse(path).getroot()
    if sitemap.tag != SITEMAP_NS + "urlset":
        raise ValueError("Expected the generated MkDocs sitemap urlset")
    entries = {node.findtext(SITEMAP_NS + "loc"): node for node in sitemap}
    for relative in STANDALONE_PAGES:
        url = SITE_URL + relative
        if url not in entries:
            node = ET.SubElement(sitemap, SITEMAP_NS + "url")
            ET.SubElement(node, SITEMAP_NS + "loc").text = url
            entries[url] = node
    dates = source_revision_dates(root)
    for url, node in entries.items():
        for old in node.findall(SITEMAP_NS + "lastmod"):
            node.remove(old)
        source = page_source(url.removeprefix(SITE_URL), root) if url else None
        if source in dates:
            ET.SubElement(node, SITEMAP_NS + "lastmod").text = dates[source]
    ET.register_namespace("", SITEMAP_NS[1:-1])
    ET.indent(sitemap)
    data = ET.tostring(sitemap, encoding="utf-8", xml_declaration=True) + b"\n"
    path.write_bytes(data)
    (site / "sitemap.xml.gz").write_bytes(gzip.compress(data, mtime=0))
    return len(entries)


def enrich_site(site: Path, root: Path = ROOT) -> int:
    """Finalize standalone pages after the all-page Markdown hook and static staging."""
    missing = [
        relative
        for relative in (*PAGE_SPECS, *STANDALONE_PAGES)
        if not (site / relative / "index.html").is_file()
    ]
    if missing:
        raise ValueError("Cannot enrich absent published pages: " + ", ".join(missing))
    for relative, (_, spec) in STANDALONE_PAGES.items():
        file = site / relative / "index.html"
        original = file.read_text(encoding="utf-8")
        updated = enrich_html(original, relative, spec)
        if updated != original:
            file.write_text(updated, encoding="utf-8")
    # Search and error utilities should remain reachable without becoming search results.
    for relative in ("search.html", "404.html"):
        file = site / relative
        if file.is_file():
            html = file.read_text(encoding="utf-8")
            directive = '<meta name="robots" content="noindex,follow">\n'
            if directive not in html:
                file.write_text(
                    HEAD_CLOSE_RE.sub(lambda m: directive + m.group(), html, count=1),
                    encoding="utf-8",
                )
    return finalize_sitemap(site, root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        count = enrich_site(args.site_dir)
    except (OSError, ValueError) as exc:
        print(f"CMB semantic metadata failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Finalized {count} sitemap pages with canonical metadata and source-history dates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
