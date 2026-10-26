"""Add stable page-level discovery metadata without rewriting authored Markdown.

The HTML output is the public artifact. An explicit registry avoids inferring
the meaning of original glyphs, changing story prose, or trusting page headings
as structured facts. This is an SEO/discovery feature, not an indexing claim.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path
import json
import re
import sys

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

REPLACED_META = {
    "description", "og:title", "og:description", "og:type", "og:url",
    "og:image", "twitter:card", "twitter:title",
    "twitter:description", "twitter:image",
}
META_RE = re.compile(r"<meta\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(r"\b(?:name|property)\s*=\s*([\"'])(.*?)\1", flags=re.IGNORECASE | re.DOTALL)
TITLE_RE = re.compile(r"<title\b[^>]*>.*?</title\s*>", flags=re.IGNORECASE | re.DOTALL)
MANAGED_RE = re.compile(re.escape(START) + r".*?" + re.escape(END), flags=re.DOTALL)
HEAD_CLOSE_RE = re.compile(r"</head\s*>", flags=re.IGNORECASE)


def _metadata(spec: PageSpec, url: str) -> str:
    title = escape(spec.title, quote=True)
    description = escape(spec.description, quote=True)
    image = escape(PREVIEW_IMAGE, quote=True)
    canonical = escape(url, quote=True)
    lines = [
        '<meta name="description" content="' + description + '">',
        '<meta property="og:type" content="article">',
        '<meta property="og:title" content="' + title + '">',
        '<meta property="og:description" content="' + description + '">',
        '<meta property="og:url" content="' + canonical + '">',
        '<meta property="og:image" content="' + image + '">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="' + title + '">',
        '<meta name="twitter:description" content="' + description + '">',
        '<meta name="twitter:image" content="' + image + '">',
    ]
    if spec.kind != "term":
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
        lines.extend([
            '<script type="application/ld+json">',
            json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
            "</script>",
        ])
    return START + "\n" + "\n".join(lines) + "\n" + END


def enrich_html(source: str, relative: str, spec: PageSpec) -> str:
    """Replace only HTML-head metadata, preserving body and authored glyphs."""
    match = HEAD_CLOSE_RE.search(source)
    if match is None:
        raise ValueError(f"{relative}: rendered HTML has no closing head tag")
    head, body = source[:match.start()], source[match.start():]
    if not re.search(r"<head\b", head, flags=re.IGNORECASE):
        raise ValueError(f"{relative}: rendered HTML has no opening head tag")
    head = MANAGED_RE.sub("", head)

    def keep_nonmanaged(match: re.Match[str]) -> str:
        attr = ATTR_RE.search(match.group())
        return "" if attr and attr.group(2).lower() in REPLACED_META else match.group()

    head = META_RE.sub(keep_nonmanaged, head)
    page_title = "<title>" + escape(spec.title) + "</title>"
    if TITLE_RE.search(head) is None:
        raise ValueError(f"{relative}: rendered HTML has no title tag")
    head = TITLE_RE.sub(lambda _: page_title, head, count=1)
    return head + _metadata(spec, SITE_URL + relative) + "\n" + body


def enrich_site(site: Path) -> int:
    """Reject missing canonical pages; never silently publish partial metadata."""
    missing = [
        relative for relative in PAGE_SPECS
        if not (site / relative / "index.html").is_file()
    ]
    if missing:
        raise ValueError("Cannot enrich absent published pages: " + ", ".join(missing))
    for relative, spec in PAGE_SPECS.items():
        file = site / relative / "index.html"
        original = file.read_text(encoding="utf-8")
        updated = enrich_html(original, relative, spec)
        if updated != original:
            file.write_text(updated, encoding="utf-8")
    return len(PAGE_SPECS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        count = enrich_site(args.site_dir)
    except (OSError, ValueError) as exc:
        print(f"CMB semantic metadata failed: {exc}", file=sys.stderr)
        return 1
    print(f"Enriched {count} canonical pages with human-readable social metadata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
