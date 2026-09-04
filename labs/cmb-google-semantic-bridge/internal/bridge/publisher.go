package bridge

import (
	"bytes"
	"fmt"
	"html/template"
	"strings"
	"unicode/utf8"
)

const siteCSS = `:root {
  color-scheme: dark;
  --bg: #07080c;
  --bg-deep: #030407;
  --panel: rgba(15, 18, 27, 0.88);
  --panel-strong: rgba(10, 13, 20, 0.96);
  --text: #f4f0e8;
  --text-soft: #d9d3c8;
  --muted: #a9a39a;
  --line: rgba(244, 204, 117, 0.18);
  --line-strong: rgba(244, 204, 117, 0.42);
  --gold: #f4cc75;
  --violet: #d7a5ff;
  --sky: #9bdcff;
  --mint: #c8f7dc;
  --danger: #ffb4b4;
  --shadow: 0 28px 90px rgba(0, 0, 0, 0.48);
  --radius-lg: 26px;
  --radius-md: 18px;
  --radius-sm: 12px;
  --max: 1080px;
}

* {
  box-sizing: border-box;
}

html {
  min-height: 100%;
  background:
    radial-gradient(circle at 12% -4%, rgba(215, 165, 255, 0.16), transparent 30%),
    radial-gradient(circle at 88% 4%, rgba(155, 220, 255, 0.12), transparent 26%),
    radial-gradient(circle at 50% 115%, rgba(244, 204, 117, 0.08), transparent 36%),
    linear-gradient(180deg, #0a0d14 0%, var(--bg) 48%, var(--bg-deep) 100%);
}

body {
  margin: 0;
  min-height: 100vh;
  background: transparent;
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  line-height: 1.72;
  letter-spacing: 0.008em;
  text-rendering: optimizeLegibility;
}

body::before,
body::after {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

body::before {
  background:
    linear-gradient(rgba(255, 255, 255, 0.018), rgba(255, 255, 255, 0)),
    repeating-linear-gradient(
      to bottom,
      rgba(255, 255, 255, 0.012) 0,
      rgba(255, 255, 255, 0.012) 1px,
      transparent 1px,
      transparent 5px
    );
  opacity: 0.38;
}

body::after {
  background-image:
    radial-gradient(circle at 10% 20%, rgba(244, 204, 117, 0.32) 0 1px, transparent 1.5px),
    radial-gradient(circle at 76% 14%, rgba(155, 220, 255, 0.28) 0 1px, transparent 1.5px),
    radial-gradient(circle at 42% 74%, rgba(215, 165, 255, 0.22) 0 1px, transparent 1.5px),
    radial-gradient(circle at 90% 82%, rgba(244, 204, 117, 0.22) 0 1px, transparent 1.5px);
  background-size: 240px 240px, 310px 310px, 370px 370px, 430px 430px;
  opacity: 0.45;
}

::selection {
  background: rgba(244, 204, 117, 0.24);
  color: #fff8e8;
}

a {
  color: inherit;
}

a:focus-visible {
  outline: 2px solid var(--sky);
  outline-offset: 4px;
}

.skip-link {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 20;
  transform: translateY(-160%);
  padding: 10px 14px;
  border-radius: 999px;
  background: var(--gold);
  color: #161006;
  font-weight: 800;
  text-decoration: none;
}

.skip-link:focus {
  transform: translateY(0);
}

.site-shell {
  position: relative;
  z-index: 1;
  width: min(var(--max), calc(100% - 28px));
  margin: 0 auto;
  padding: 30px 0 72px;
}

.ornament {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 4px 0 18px;
  color: rgba(244, 204, 117, 0.72);
  letter-spacing: 0.22em;
  user-select: none;
}

.ornament::before,
.ornament::after {
  content: "";
  width: min(120px, 18vw);
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--line-strong));
}

.ornament::after {
  background: linear-gradient(90deg, var(--line-strong), transparent);
}

.panel {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.022), rgba(255, 255, 255, 0)),
    var(--panel);
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}

.panel + .panel {
  margin-top: 18px;
}

.hero {
  padding: clamp(26px, 5vw, 50px);
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 14% 0%, rgba(244, 204, 117, 0.12), transparent 30%),
    radial-gradient(circle at 88% 4%, rgba(215, 165, 255, 0.10), transparent 24%);
}

.hero-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 28px;
  align-items: start;
}

.kicker {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  padding: 8px 13px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(244, 204, 117, 0.055);
  color: var(--gold);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}

.title {
  max-width: 900px;
  margin: 0;
  color: var(--gold);
  font-size: clamp(2.15rem, 7vw, 5rem);
  line-height: 0.98;
  letter-spacing: 0.02em;
  text-wrap: balance;
  overflow-wrap: anywhere;
}

.subtitle {
  max-width: 74ch;
  margin: 20px 0 0;
  color: var(--text-soft);
  font-size: clamp(0.98rem, 1.6vw, 1.08rem);
}

.sigil {
  display: grid;
  place-items: center;
  width: 110px;
  aspect-ratio: 1;
  border: 1px solid var(--line-strong);
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(244, 204, 117, 0.12), transparent 60%),
    rgba(255, 255, 255, 0.018);
  box-shadow:
    0 0 0 8px rgba(244, 204, 117, 0.025),
    0 0 56px rgba(215, 165, 255, 0.08);
  color: var(--gold);
  font-size: 2.2rem;
  line-height: 1;
}

.meta-row {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 26px;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 9px 13px;
  border: 1px solid rgba(244, 204, 117, 0.14);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.022);
  color: var(--muted);
  font-size: 0.86rem;
}

.meta-chip strong {
  color: var(--text);
  font-weight: 700;
}

.separator {
  color: var(--gold);
  opacity: 0.82;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 11px;
  margin: 0;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(244, 204, 117, 0.055), rgba(244, 204, 117, 0.012));
  color: var(--gold);
  font-size: 0.86rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.section-heading .glyph {
  color: var(--violet);
  font-size: 1.08rem;
}

.panel-body {
  padding: clamp(20px, 3.4vw, 34px);
}

.transmission-frame {
  position: relative;
  border: 1px solid rgba(200, 247, 220, 0.12);
  border-radius: var(--radius-md);
  background:
    linear-gradient(180deg, rgba(200, 247, 220, 0.025), rgba(200, 247, 220, 0)),
    rgba(3, 6, 8, 0.66);
  overflow: hidden;
}

.transmission-frame::before {
  content: "HUMAN SOURCE · EXACT BYTES · UTF-8";
  display: block;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(200, 247, 220, 0.10);
  color: rgba(200, 247, 220, 0.64);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.source {
  margin: 0;
  padding: clamp(20px, 4vw, 36px);
  color: var(--mint);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font: inherit;
  font-size: clamp(0.86rem, 1.6vw, 0.98rem);
  line-height: 1.76;
}

.provenance-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.info-card {
  min-width: 0;
  padding: 17px 18px;
  border: 1px solid rgba(244, 204, 117, 0.13);
  border-radius: var(--radius-md);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.022), rgba(255, 255, 255, 0)),
    var(--panel-strong);
}

.info-card.wide {
  grid-column: 1 / -1;
}

.info-label {
  margin: 0 0 8px;
  color: var(--gold);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.info-value {
  margin: 0;
  color: var(--text-soft);
  overflow-wrap: anywhere;
}

.machine-boundary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.boundary-card {
  padding: 17px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.018);
}

.boundary-card strong {
  display: block;
  margin-bottom: 6px;
  color: var(--sky);
  font-size: 0.84rem;
}

.boundary-card span {
  color: var(--muted);
  font-size: 0.88rem;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.resource-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-height: 48px;
  padding: 11px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.02);
  color: var(--text);
  text-decoration: none;
  transition:
    transform 140ms ease,
    border-color 140ms ease,
    background 140ms ease;
}

.resource-link::after {
  content: "✦";
  color: var(--gold);
  opacity: 0.72;
}

.resource-link:hover {
  transform: translateY(-2px);
  border-color: var(--line-strong);
  background: rgba(244, 204, 117, 0.055);
}

.final-gate {
  padding: clamp(24px, 4vw, 38px);
  text-align: center;
}

.final-gate .axiom {
  margin: 0;
  color: var(--gold);
  font-size: clamp(1rem, 2.4vw, 1.34rem);
  font-weight: 900;
  letter-spacing: 0.08em;
}

.final-gate .subaxiom {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 0.88rem;
}

.footer-mark {
  margin: 22px 0 0;
  color: rgba(215, 165, 255, 0.74);
  font-size: 0.78rem;
  letter-spacing: 0.12em;
}

@media (max-width: 780px) {
  .site-shell {
    width: min(var(--max), calc(100% - 18px));
    padding-top: 18px;
  }

  .hero-grid {
    grid-template-columns: 1fr;
  }

  .sigil {
    width: 78px;
    grid-row: 1;
  }

  .provenance-grid,
  .machine-boundary,
  .resource-grid {
    grid-template-columns: 1fr;
  }

  .info-card.wide {
    grid-column: auto;
  }

  .meta-chip,
  .resource-link {
    width: 100%;
  }

  .panel {
    border-radius: 20px;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition-duration: 0.001ms !important;
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
  }
}

@media print {
  :root {
    color-scheme: light;
  }

  body,
  html {
    background: white;
    color: black;
  }

  body::before,
  body::after,
  .ornament,
  .sigil {
    display: none;
  }

  .site-shell {
    width: 100%;
    padding: 0;
  }

  .panel {
    border: 1px solid #bbb;
    box-shadow: none;
    background: white;
    color: black;
  }

  .source,
  .title,
  .section-heading,
  .info-label,
  .final-gate .axiom {
    color: black;
  }
}
`

type pageModel struct {
	Language      string
	Title         string
	Description   string
	Author        string
	DatePublished string
	DateModified  string
	CanonicalURL  string
	Source        string
	SHA256        string
	JSONLD        template.JS
}

const pageTemplate = `<!doctype html>
<html lang="{{.Language}}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{{.Description}}">
  <meta name="author" content="{{.Author}}">
  <meta name="generator" content="CMB Google Semantic Bridge">
  <meta name="robots" content="index,follow">
  <meta name="theme-color" content="#07080c">
  <title>{{.Title}}</title>
  <link rel="canonical" href="{{.CanonicalURL}}">
  <link rel="stylesheet" href="site.css">
  <script type="application/ld+json">
{{.JSONLD}}
  </script>
</head>
<body>
  <a class="skip-link" href="#human-source">Skip to human source</a>

  <main class="site-shell">
    <div class="ornament" aria-hidden="true">⚯ ✦ ♃ ✦ 🪐 ✦ 🦩</div>

    <header class="panel hero">
      <div class="hero-grid">
        <div>
          <div class="kicker">
            <span>𓁻 Sovereign Transmission</span>
            <span class="separator">✦</span>
            <span>Human Authored</span>
          </div>

          <h1 class="title">{{.Title}}</h1>
          <p class="subtitle">{{.Description}}</p>
        </div>

        <div class="sigil" aria-hidden="true">♃</div>
      </div>

      <div class="meta-row" aria-label="Publication metadata">
        <div class="meta-chip"><strong>Author</strong><span class="separator">│</span>{{.Author}}</div>
        <div class="meta-chip"><strong>Published</strong><span class="separator">│</span>{{.DatePublished}}</div>
        <div class="meta-chip"><strong>Modified</strong><span class="separator">│</span>{{.DateModified}}</div>
      </div>
    </header>

    <section class="panel" id="human-source" aria-labelledby="source-title">
      <h2 class="section-heading" id="source-title"><span class="glyph">⚯</span> Human Source Transmission</h2>
      <div class="panel-body">
        <div class="transmission-frame">
          <pre class="source">{{.Source}}</pre>
        </div>
      </div>
    </section>

    <section class="panel" aria-labelledby="provenance-title">
      <h2 class="section-heading" id="provenance-title"><span class="glyph">𓅓</span> Provenance Ledger</h2>
      <div class="panel-body">
        <div class="provenance-grid">
          <div class="info-card wide">
            <p class="info-label">Canonical Publication</p>
            <p class="info-value">{{.CanonicalURL}}</p>
          </div>

          <div class="info-card wide">
            <p class="info-label">SHA-256 Source Integrity</p>
            <p class="info-value">{{.SHA256}}</p>
          </div>

          <div class="info-card">
            <p class="info-label">Authority Boundary</p>
            <p class="info-value">HUMAN_FINAL</p>
          </div>

          <div class="info-card">
            <p class="info-label">Publication Mode</p>
            <p class="info-value">Static · deterministic · machine-readable</p>
          </div>
        </div>
      </div>
    </section>

    <section class="panel" aria-labelledby="boundary-title">
      <h2 class="section-heading" id="boundary-title"><span class="glyph">⃤</span> Human ↔ Machine Boundary</h2>
      <div class="panel-body">
        <div class="machine-boundary">
          <div class="boundary-card">
            <strong>Human Source</strong>
            <span>Meaning · authorship · context · judgment</span>
          </div>
          <div class="boundary-card">
            <strong>Semantic Bridge</strong>
            <span>Structure · metadata · integrity · discovery</span>
          </div>
          <div class="boundary-card">
            <strong>Machine Reader</strong>
            <span>Parse · index · describe · never define the person</span>
          </div>
        </div>
      </div>
    </section>

    <nav class="panel" aria-labelledby="resources-title">
      <h2 class="section-heading" id="resources-title"><span class="glyph">✦</span> Publication Surfaces</h2>
      <div class="panel-body">
        <div class="resource-grid">
          <a class="resource-link" href="source.md"><span>Source</span></a>
          <a class="resource-link" href="article.jsonld"><span>JSON-LD</span></a>
          <a class="resource-link" href="cmb-semantic.json"><span>CMB Semantic</span></a>
          <a class="resource-link" href="manifest.json"><span>Build Manifest</span></a>
          <a class="resource-link" href="sitemap.xml"><span>Sitemap</span></a>
          <a class="resource-link" href="robots.txt"><span>Robots Artifact</span></a>
        </div>
      </div>
    </nav>

    <footer class="panel final-gate">
      <p class="axiom">HUMAN_AGENCY &gt; MACHINE_AUTHORITY <span class="separator">✦</span> PATTERN != PROOF</p>
      <p class="subaxiom">Visibility · structure · provenance · human meaning preserved</p>
      <p class="footer-mark" aria-hidden="true">⚯ 𓁻 ✦ ♃ ✦ 🪐 ✦ 🦩 ✦ 𓅓 ⃤</p>
    </footer>

    <div class="ornament" aria-hidden="true">🦩 ✦ 🪐 ✦ ♃ ✦ ⚯</div>
  </main>
</body>
</html>
`

func BindSource(a Artifact, source []byte) (Artifact, error) {
	if len(source) == 0 {
		return Artifact{}, fmt.Errorf("source must not be empty")
	}
	if !utf8.Valid(source) {
		return Artifact{}, fmt.Errorf("source must be valid UTF-8")
	}

	digest := SHA256Bytes(source)
	if a.Provenance.SHA256 != "" && a.Provenance.SHA256 != digest {
		return Artifact{}, fmt.Errorf(
			"source SHA-256 mismatch: artifact declares %s but source is %s",
			a.Provenance.SHA256,
			digest,
		)
	}

	a.Body = string(source)
	a.Provenance.SHA256 = digest
	if err := a.Validate(); err != nil {
		return Artifact{}, err
	}
	return a, nil
}

func PageHTML(a Artifact) ([]byte, error) {
	if err := a.Validate(); err != nil {
		return nil, err
	}
	if strings.TrimSpace(a.Body) == "" {
		return nil, fmt.Errorf("artifact body is required for a published page")
	}

	jsonLD, err := ArticleJSONLD(a)
	if err != nil {
		return nil, err
	}

	model := pageModel{
		Language:      a.Language,
		Title:         a.Title,
		Description:   a.Description,
		Author:        a.Author.Name,
		DatePublished: a.DatePublished.Format("2006-01-02"),
		DateModified:  a.DateModified.Format("2006-01-02"),
		CanonicalURL:  a.URL,
		Source:        a.Body,
		SHA256:        a.Provenance.SHA256,
		JSONLD:        template.JS(jsonLD),
	}

	tmpl, err := template.New("page").Parse(pageTemplate)
	if err != nil {
		return nil, fmt.Errorf("parse page template: %w", err)
	}

	var out bytes.Buffer
	if err := tmpl.Execute(&out, model); err != nil {
		return nil, fmt.Errorf("render page template: %w", err)
	}
	return out.Bytes(), nil
}

func SiteCSS() []byte {
	return []byte(siteCSS)
}
