package bridge

import (
	"bytes"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"html/template"
	"path"
	"sort"
	"strings"

	"github.com/jupiter8nohate/cmb-google-semantic-bridge/internal/catalog"
)

const LibraryIndexSchemaVersion = "cmb-gsb.library-index.v1"

type LibraryBinding struct {
	SchemaVersion string `json:"schema_version"`
	SHA256        string `json:"sha256"`
}

type PublishedArtifact struct {
	ID              string   `json:"id"`
	Title           string   `json:"title"`
	URL             string   `json:"url"`
	RepositoryPath  string   `json:"repository_path"`
	OutputPath      string   `json:"output_path"`
	SourceSHA256    string   `json:"source_sha256"`
	Format          string   `json:"format"`
	Kind            string   `json:"kind"`
	Status          string   `json:"status"`
	ProvenanceScope string   `json:"provenance_scope"`
	Concepts        []string `json:"concepts"`
	DeclaredMeaning string   `json:"declared_meaning"`
}

type LibraryIndex struct {
	SchemaVersion string              `json:"schema_version"`
	Framework     string              `json:"framework"`
	CanonicalURL  string              `json:"canonical_url"`
	Canon         CanonBinding        `json:"canon"`
	Catalog       LibraryBinding      `json:"catalog"`
	Artifacts     []PublishedArtifact `json:"artifacts"`
}

type CanonLibraryInput struct {
	RepositoryRoot string
	BaseURL        string
	CanonBytes     []byte
	Canon          CanonSemantics
	CatalogBytes   []byte
	CatalogSHA256  string
	Catalog        catalog.Document
}

type librarySemanticEnvelope struct {
	SchemaVersion  string             `json:"schema_version"`
	ArtifactID     string             `json:"artifact_id"`
	CanonicalURL   string             `json:"canonical_url"`
	Canon          CanonBinding       `json:"canon"`
	Catalog        LibraryBinding     `json:"catalog"`
	Invariants     []string           `json:"invariants"`
	Source         librarySource      `json:"source"`
	Interpretation InterpretationRule `json:"interpretation"`
}

type librarySource struct {
	RepositoryPath string `json:"repository_path"`
	SHA256          string `json:"sha256"`
	Format          string `json:"format"`
	ProvenanceScope string `json:"provenance_scope"`
}

type creativeWorkLD struct {
	Type        string            `json:"@type"`
	ID          string            `json:"@id"`
	Name        string            `json:"name"`
	Description string            `json:"description"`
	URL         string            `json:"url"`
	Creator     personLD          `json:"creator"`
	Keywords    []string          `json:"keywords,omitempty"`
	Encoding    string            `json:"encodingFormat,omitempty"`
	Identifier  []propertyValueLD `json:"identifier,omitempty"`
}

type collectionLD struct {
	Context     string           `json:"@context"`
	Type        string           `json:"@type"`
	ID          string           `json:"@id"`
	Name        string           `json:"name"`
	Description string           `json:"description"`
	URL         string           `json:"url"`
	Creator     personLD         `json:"creator"`
	HasPart     []creativeWorkLD `json:"hasPart"`
}

type libraryPageModel struct {
	Title           string
	Description     string
	DeclaredMeaning string
	Author          string
	Status          string
	Kind            string
	Format          string
	ProvenanceScope string
	CanonicalURL    string
	RepositoryPath  string
	SHA256          string
	Source          string
	SourceName      string
	JSONLD          template.JS
}

type libraryIndexModel struct {
	Title       string
	Description string
	Author      string
	Canonical  string
	Count       int
	Artifacts   []PublishedArtifact
	JSONLD      template.JS
}

func BuildCanonLibrary(input CanonLibraryInput) (map[string][]byte, LibraryIndex, error) {
	if err := input.Canon.Validate(); err != nil {
		return nil, LibraryIndex{}, fmt.Errorf("validate canon: %w", err)
	}
	if err := input.Catalog.Validate(); err != nil {
		return nil, LibraryIndex{}, fmt.Errorf("validate catalog: %w", err)
	}
	if !validSHA256(input.CatalogSHA256) {
		return nil, LibraryIndex{}, fmt.Errorf("catalog SHA-256 must be 64 lowercase hexadecimal characters")
	}
	if len(input.CanonBytes) == 0 || len(input.CatalogBytes) == 0 {
		return nil, LibraryIndex{}, fmt.Errorf("exact canon and catalog bytes are required")
	}
	base, err := NormalizeBaseURL(input.BaseURL)
	if err != nil {
		return nil, LibraryIndex{}, err
	}
	rootURL := base + "/"

	outputs := map[string][]byte{
		"cmb-canon.json": append([]byte(nil), input.CanonBytes...),
		"catalog.json":   append([]byte(nil), input.CatalogBytes...),
		"site.css":       CanonLibraryCSS(),
	}
	published := make([]PublishedArtifact, 0, len(input.Catalog.Artifacts))

	for _, entry := range input.Catalog.Artifacts {
		if !entry.HumanReadable || !entry.MachineIndexable {
			continue
		}
		source, err := ReadRepositoryUTF8File(input.RepositoryRoot, entry.Path)
		if err != nil {
			return nil, LibraryIndex{}, fmt.Errorf("artifact %s: %w", entry.ID, err)
		}
		digest := SHA256Bytes(source)
		artifactURL := base + "/artifacts/" + entry.ID + "/"
		sourceName := "source." + sourceExtension(entry.Format)
		outputBase := path.Join("artifacts", entry.ID)

		workJSONLD, err := libraryCreativeWorkJSONLD(entry, input.Catalog.DeclaredOriginator, artifactURL, digest)
		if err != nil {
			return nil, LibraryIndex{}, fmt.Errorf("artifact %s JSON-LD: %w", entry.ID, err)
		}
		semantic, err := librarySemanticJSON(entry, artifactURL, digest, input)
		if err != nil {
			return nil, LibraryIndex{}, fmt.Errorf("artifact %s semantic sidecar: %w", entry.ID, err)
		}
		pageHTML, err := libraryArtifactHTML(entry, input.Catalog.DeclaredOriginator, artifactURL, digest, sourceName, source, workJSONLD)
		if err != nil {
			return nil, LibraryIndex{}, fmt.Errorf("artifact %s page: %w", entry.ID, err)
		}

		outputs[path.Join(outputBase, "index.html")] = pageHTML
		outputs[path.Join(outputBase, sourceName)] = append([]byte(nil), source...)
		outputs[path.Join(outputBase, "work.jsonld")] = workJSONLD
		outputs[path.Join(outputBase, "cmb-semantic.json")] = semantic

		switch entry.ID {
		case "cmb-agent-card":
			outputs[".well-known/agent-card.json"] = append([]byte(nil), source...)
		case "cmb-agent-registry":
			outputs["agents/registry.json"] = append([]byte(nil), source...)
		}

		published = append(published, PublishedArtifact{
			ID:              entry.ID,
			Title:           entry.Title,
			URL:             artifactURL,
			RepositoryPath:  entry.Path,
			OutputPath:      outputBase + "/",
			SourceSHA256:    digest,
			Format:          entry.Format,
			Kind:            entry.Kind,
			Status:          entry.Status,
			ProvenanceScope: entry.ProvenanceScope,
			Concepts:        append([]string(nil), entry.Concepts...),
			DeclaredMeaning: entry.DeclaredMeaning,
		})
	}

	sort.Slice(published, func(i, j int) bool {
		return published[i].ID < published[j].ID
	})

	index := LibraryIndex{
		SchemaVersion: LibraryIndexSchemaVersion,
		Framework:     catalog.Framework,
		CanonicalURL:  rootURL,
		Canon: CanonBinding{
			SchemaVersion: input.Canon.SchemaVersion,
			SHA256:        input.Canon.SHA256,
			RootInvariant: input.Canon.RootInvariant,
		},
		Catalog: LibraryBinding{
			SchemaVersion: input.Catalog.SchemaVersion,
			SHA256:        input.CatalogSHA256,
		},
		Artifacts: published,
	}
	indexJSON, err := json.MarshalIndent(index, "", "  ")
	if err != nil {
		return nil, LibraryIndex{}, fmt.Errorf("encode library index: %w", err)
	}
	outputs["library-index.json"] = append(indexJSON, '\n')

	collectionJSONLD, err := libraryCollectionJSONLD(index, input.Catalog)
	if err != nil {
		return nil, LibraryIndex{}, err
	}
	indexHTML, err := libraryIndexHTML(index, input.Catalog, collectionJSONLD)
	if err != nil {
		return nil, LibraryIndex{}, err
	}
	outputs["index.html"] = indexHTML
	outputs["collection.jsonld"] = collectionJSONLD

	urls := make([]string, 0, len(published)+1)
	urls = append(urls, rootURL)
	for _, artifact := range published {
		urls = append(urls, artifact.URL)
	}
	sitemap, err := URLSitemapXML(urls)
	if err != nil {
		return nil, LibraryIndex{}, err
	}
	outputs["sitemap.xml"] = sitemap
	robots, err := RobotsTXT(base)
	if err != nil {
		return nil, LibraryIndex{}, err
	}
	outputs["robots.txt"] = []byte(robots)
	return outputs, index, nil
}

func librarySemanticJSON(entry catalog.Artifact, canonicalURL, sourceSHA string, input CanonLibraryInput) ([]byte, error) {
	envelope := librarySemanticEnvelope{
		SchemaVersion: "cmb-gsb.library-semantic.v1",
		ArtifactID:    entry.ID,
		CanonicalURL:  canonicalURL,
		Canon: CanonBinding{
			SchemaVersion: input.Canon.SchemaVersion,
			SHA256:        input.Canon.SHA256,
			RootInvariant: input.Canon.RootInvariant,
		},
		Catalog: LibraryBinding{
			SchemaVersion: input.Catalog.SchemaVersion,
			SHA256:        input.CatalogSHA256,
		},
		Invariants: append([]string(nil), input.Canon.Invariants...),
		Source: librarySource{
			RepositoryPath: entry.Path,
			SHA256:          sourceSHA,
			Format:          entry.Format,
			ProvenanceScope: entry.ProvenanceScope,
		},
		Interpretation: InterpretationRule{
			PatternIsProof:            false,
			ProfileIsPerson:           false,
			ModelIsMind:               false,
			PredictionIsDestiny:       false,
			DifferenceIsDefect:        false,
			CapabilityIsAuthority:     false,
			OptimizationIsMorality:    false,
			IntelligenceIsSovereignty: false,
			MachineHasFinalAuthority:  false,
		},
	}
	data, err := json.MarshalIndent(envelope, "", "  ")
	if err != nil {
		return nil, err
	}
	return data, nil
}

func libraryCreativeWorkJSONLD(entry catalog.Artifact, author, canonicalURL, sourceSHA string) ([]byte, error) {
	work := creativeWorkLD{
		Type:        "CreativeWork",
		ID:          canonicalURL + "#work",
		Name:        entry.Title,
		Description: entry.DeclaredMeaning,
		URL:         canonicalURL,
		Creator: personLD{
			Type: "Person",
			Name: author,
		},
		Keywords: cleanStrings(entry.Concepts),
		Encoding: encodingFormat(entry.Format),
		Identifier: []propertyValueLD{
			{Type: "PropertyValue", Name: "CMB Artifact ID", Value: entry.ID, PropertyID: "cmb:artifact-id"},
			{Type: "PropertyValue", Name: "SHA-256", Value: sourceSHA, PropertyID: "sha256"},
		},
	}
	document := struct {
		Context string `json:"@context"`
		creativeWorkLD
	}{
		Context:        "https://schema.org",
		creativeWorkLD: work,
	}
	data, err := json.MarshalIndent(document, "", "  ")
	if err != nil {
		return nil, err
	}
	return data, nil
}

func libraryCollectionJSONLD(index LibraryIndex, document catalog.Document) ([]byte, error) {
	parts := make([]creativeWorkLD, 0, len(index.Artifacts))
	for _, artifact := range index.Artifacts {
		parts = append(parts, creativeWorkLD{
			Type:        "CreativeWork",
			ID:          artifact.URL + "#work",
			Name:        artifact.Title,
			Description: artifact.DeclaredMeaning,
			URL:         artifact.URL,
			Creator: personLD{Type: "Person", Name: document.DeclaredOriginator},
			Keywords: cleanStrings(artifact.Concepts),
			Encoding: encodingFormat(artifact.Format),
		})
	}
	collection := collectionLD{
		Context:     "https://schema.org",
		Type:        "CollectionPage",
		ID:          index.CanonicalURL + "#collection",
		Name:        "CMB Digital Library",
		Description: document.Purpose,
		URL:         index.CanonicalURL,
		Creator:     personLD{Type: "Person", Name: document.DeclaredOriginator},
		HasPart:     parts,
	}
	data, err := json.MarshalIndent(collection, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("encode library collection JSON-LD: %w", err)
	}
	return data, nil
}

func libraryIndexHTML(index LibraryIndex, document catalog.Document, jsonLD []byte) ([]byte, error) {
	model := libraryIndexModel{
		Title:       "CMB Digital Library",
		Description: document.Purpose,
		Author:      document.DeclaredOriginator,
		Canonical:   index.CanonicalURL,
		Count:       len(index.Artifacts),
		Artifacts:   index.Artifacts,
		JSONLD:      template.JS(jsonLD),
	}
	tmpl, err := template.New("library-index").Parse(libraryIndexTemplate)
	if err != nil {
		return nil, fmt.Errorf("parse library index template: %w", err)
	}
	var out bytes.Buffer
	if err := tmpl.Execute(&out, model); err != nil {
		return nil, fmt.Errorf("render library index: %w", err)
	}
	return out.Bytes(), nil
}

func libraryArtifactHTML(entry catalog.Artifact, author, canonicalURL, sourceSHA, sourceName string, source []byte, jsonLD []byte) ([]byte, error) {
	model := libraryPageModel{
		Title:           entry.Title,
		Description:     entry.Kind,
		DeclaredMeaning: entry.DeclaredMeaning,
		Author:          author,
		Status:          entry.Status,
		Kind:            entry.Kind,
		Format:          entry.Format,
		ProvenanceScope: entry.ProvenanceScope,
		CanonicalURL:    canonicalURL,
		RepositoryPath:  entry.Path,
		SHA256:          sourceSHA,
		Source:          string(source),
		SourceName:      sourceName,
		JSONLD:          template.JS(jsonLD),
	}
	tmpl, err := template.New("library-artifact").Parse(libraryArtifactTemplate)
	if err != nil {
		return nil, err
	}
	var out bytes.Buffer
	if err := tmpl.Execute(&out, model); err != nil {
		return nil, err
	}
	return out.Bytes(), nil
}

func URLSitemapXML(urls []string) ([]byte, error) {
	if len(urls) == 0 {
		return nil, fmt.Errorf("at least one URL is required")
	}
	seen := make(map[string]struct{}, len(urls))
	items := make([]sitemapURL, 0, len(urls))
	for _, raw := range urls {
		if err := validateHTTPSURL("sitemap URL", raw); err != nil {
			return nil, err
		}
		if _, exists := seen[raw]; exists {
			return nil, fmt.Errorf("duplicate sitemap URL %q", raw)
		}
		seen[raw] = struct{}{}
		items = append(items, sitemapURL{Loc: raw})
	}
	document := sitemapDocument{
		Xmlns: "http://www.sitemaps.org/schemas/sitemap/0.9",
		URLs:  items,
	}
	body, err := xml.MarshalIndent(document, "", "  ")
	if err != nil {
		return nil, err
	}
	return append([]byte(xml.Header), append(body, '\n')...), nil
}

func sourceExtension(format string) string {
	switch strings.ToLower(strings.TrimSpace(format)) {
	case "markdown":
		return "md"
	case "json":
		return "json"
	default:
		return "txt"
	}
}

func encodingFormat(format string) string {
	switch strings.ToLower(strings.TrimSpace(format)) {
	case "markdown":
		return "text/markdown"
	case "json":
		return "application/json"
	default:
		return "text/plain"
	}
}

func CanonLibraryCSS() []byte {
	return append(SiteCSS(), []byte(libraryCSS)...)
}

const libraryCSS = `
.library-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.library-item {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: rgba(255,255,255,0.018);
}
.library-item h2 {
  margin: 0 0 8px;
  color: var(--gold);
  font-size: 1rem;
}
.library-item p {
  margin: 0;
  color: var(--muted);
}
.library-item a {
  text-decoration: none;
}
.library-meta {
  margin-top: 10px;
  color: var(--sky);
  font-size: 0.78rem;
}
`

const libraryIndexTemplate = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{{.Description}}">
  <meta name="author" content="{{.Author}}">
  <meta name="generator" content="CMB Google Semantic Bridge">
  <title>{{.Title}}</title>
  <link rel="canonical" href="{{.Canonical}}">
  <link rel="stylesheet" href="site.css">
  <script type="application/ld+json">
{{.JSONLD}}
  </script>
</head>
<body>
  <a class="skip-link" href="#library">Skip to library</a>
  <main class="site-shell">
    <div class="ornament" aria-hidden="true">🦩 ✦ 🪐 ✦ ♃ ✦ ⚯</div>
    <header class="panel hero">
      <div class="kicker">CMB Canon Library <span class="separator">✦</span> Verify, Don't Just Believe</div>
      <h1 class="title">{{.Title}}</h1>
      <p class="subtitle">{{.Description}}</p>
      <div class="meta-row">
        <div class="meta-chip"><strong>Declared originator</strong><span class="separator">│</span>{{.Author}}</div>
        <div class="meta-chip"><strong>Published artifacts</strong><span class="separator">│</span>{{.Count}}</div>
      </div>
    </header>
    <section class="panel" id="library">
      <h2 class="section-heading"><span class="glyph">✦</span> Canonical Artifact Index</h2>
      <div class="panel-body library-grid">
        {{range .Artifacts}}
        <article class="library-item">
          <h2><a href="{{.URL}}">{{.Title}}</a></h2>
          <p>{{.DeclaredMeaning}}</p>
          <div class="library-meta">{{.Status}} · {{.Kind}} · {{.Format}} · SHA-256 {{.SourceSHA256}}</div>
        </article>
        {{end}}
      </div>
    </section>
    <nav class="panel" aria-labelledby="machine-title">
      <h2 class="section-heading" id="machine-title"><span class="glyph">⃤</span> Machine Surfaces</h2>
      <div class="panel-body resource-grid">
        <a class="resource-link" href="library-index.json"><span>Library Index</span></a>
        <a class="resource-link" href="cmb-canon.json"><span>Canon Graph</span></a>
        <a class="resource-link" href="catalog.json"><span>Artifact Catalog</span></a>
        <a class="resource-link" href="collection.jsonld"><span>Collection JSON-LD</span></a>
        <a class="resource-link" href="sitemap.xml"><span>Sitemap</span></a>
        <a class="resource-link" href="manifest.json"><span>Build Manifest</span></a>
      </div>
    </nav>
    <footer class="panel final-gate">
      <p class="axiom">HUMAN_AGENCY &gt; MACHINE_AUTHORITY <span class="separator">✦</span> VERIFY, DON'T JUST BELIEVE</p>
      <p class="subaxiom">Catalog != identity · Hash != authorship · Discoverability != ownership</p>
    </footer>
  </main>
</body>
</html>
`

const libraryArtifactTemplate = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{{.DeclaredMeaning}}">
  <meta name="author" content="{{.Author}}">
  <meta name="generator" content="CMB Google Semantic Bridge">
  <title>{{.Title}}</title>
  <link rel="canonical" href="{{.CanonicalURL}}">
  <link rel="stylesheet" href="../../site.css">
  <script type="application/ld+json">
{{.JSONLD}}
  </script>
</head>
<body>
  <a class="skip-link" href="#source">Skip to source</a>
  <main class="site-shell">
    <div class="ornament" aria-hidden="true">⚯ ✦ ♃ ✦ 🪐 ✦ 🦩</div>
    <header class="panel hero">
      <div class="kicker">{{.Status}} <span class="separator">✦</span> {{.Kind}}</div>
      <h1 class="title">{{.Title}}</h1>
      <p class="subtitle">{{.DeclaredMeaning}}</p>
      <div class="meta-row">
        <div class="meta-chip"><strong>Declared originator</strong><span class="separator">│</span>{{.Author}}</div>
        <div class="meta-chip"><strong>Format</strong><span class="separator">│</span>{{.Format}}</div>
        <div class="meta-chip"><strong>Scope</strong><span class="separator">│</span>{{.ProvenanceScope}}</div>
      </div>
    </header>
    <section class="panel">
      <h2 class="section-heading"><span class="glyph">𓅓</span> Integrity Binding</h2>
      <div class="panel-body provenance-grid">
        <div class="info-card wide"><p class="info-label">Repository path</p><p class="info-value">{{.RepositoryPath}}</p></div>
        <div class="info-card wide"><p class="info-label">SHA-256</p><p class="info-value">{{.SHA256}}</p></div>
      </div>
    </section>
    <section class="panel" id="source">
      <h2 class="section-heading"><span class="glyph">⚯</span> Exact Repository Source</h2>
      <div class="panel-body">
        <div class="transmission-frame"><pre class="source">{{.Source}}</pre></div>
      </div>
    </section>
    <nav class="panel">
      <h2 class="section-heading"><span class="glyph">✦</span> Artifact Surfaces</h2>
      <div class="panel-body resource-grid">
        <a class="resource-link" href="{{.SourceName}}"><span>Exact Source</span></a>
        <a class="resource-link" href="work.jsonld"><span>CreativeWork JSON-LD</span></a>
        <a class="resource-link" href="cmb-semantic.json"><span>CMB Semantic</span></a>
        <a class="resource-link" href="../../index.html"><span>Library Home</span></a>
      </div>
    </nav>
    <footer class="panel final-gate">
      <p class="axiom">SOURCE HASH != AUTHORSHIP <span class="separator">✦</span> HUMAN_AGENCY &gt; MACHINE_AUTHORITY</p>
    </footer>
  </main>
</body>
</html>
`
