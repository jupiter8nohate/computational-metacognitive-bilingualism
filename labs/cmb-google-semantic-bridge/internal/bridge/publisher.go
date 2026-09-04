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
  --bg: #080a0d;
  --panel: #11151b;
  --text: #edf2f7;
  --muted: #9aa7b4;
  --line: #26313d;
  --accent: #f3c969;
  --code: #d7f7e8;
}
* { box-sizing: border-box; }
html { background: var(--bg); }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  line-height: 1.65;
}
main {
  width: min(980px, calc(100% - 32px));
  margin: 0 auto;
  padding: 56px 0 80px;
}
header, article, footer {
  border: 1px solid var(--line);
  background: var(--panel);
  padding: clamp(20px, 4vw, 40px);
}
header { margin-bottom: 20px; }
article { overflow: hidden; }
h1 {
  margin: 0 0 12px;
  color: var(--accent);
  font-size: clamp(2rem, 7vw, 4.5rem);
  line-height: 1;
  overflow-wrap: anywhere;
}
.meta, footer { color: var(--muted); }
.meta span { display: inline-block; margin-right: 18px; }
.source {
  margin: 0;
  color: var(--code);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font: inherit;
}
a { color: var(--accent); }
footer { margin-top: 20px; font-size: 0.9rem; }
.hash { overflow-wrap: anywhere; }
.invariant {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  color: var(--accent);
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
  <title>{{.Title}}</title>
  <link rel="canonical" href="{{.CanonicalURL}}">
  <link rel="stylesheet" href="site.css">
  <script type="application/ld+json">
{{.JSONLD}}
  </script>
</head>
<body>
<main>
  <header>
    <h1>{{.Title}}</h1>
    <p>{{.Description}}</p>
    <p class="meta">
      <span>Author: {{.Author}}</span>
      <span>Published: {{.DatePublished}}</span>
      <span>Modified: {{.DateModified}}</span>
    </p>
  </header>
  <article aria-label="Human-authored source">
    <pre class="source">{{.Source}}</pre>
  </article>
  <footer>
    <div>SHA-256: <span class="hash">{{.SHA256}}</span></div>
    <div><a href="source.md">Source</a> · <a href="article.jsonld">JSON-LD</a> · <a href="cmb-semantic.json">CMB semantic sidecar</a> · <a href="manifest.json">Build manifest</a></div>
    <div class="invariant">HUMAN_AGENCY &gt; MACHINE_AUTHORITY · PATTERN != PROOF</div>
  </footer>
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
