package bridge

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func validCanonSemantics() CanonSemantics {
	return CanonSemantics{
		SchemaVersion: "cmb.canon.v1",
		SHA256:        strings.Repeat("0", 64),
		RootInvariant: "HUMAN_AGENCY > MACHINE_AUTHORITY",
		Invariants: []string{
			"PATTERN != PROOF",
			"PROFILE != PERSON",
			"MODEL != MIND",
			"PREDICTION != DESTINY",
			"DIFFERENCE != DEFECT",
			"CAPABILITY != AUTHORITY",
			"OPTIMIZATION != MORALITY",
			"INTELLIGENCE != SOVEREIGNTY",
			"HUMAN_AGENCY > MACHINE_AUTHORITY",
		},
	}
}

func validArtifact(t *testing.T) Artifact {
	t.Helper()
	published := time.Date(2026, 9, 4, 13, 0, 0, 0, time.UTC)
	return Artifact{
		SchemaVersion: ArtifactSchemaVersion,
		ID:            "cmb-test",
		URL:           "https://example.org/cmb/test",
		Title:         "CMB Test Artifact",
		Description:   "A test artifact.",
		Author: Author{
			Name: "Jupiter Hudson",
			URL:  "https://example.org/authors/jupiter-hudson",
		},
		DatePublished: published,
		DateModified:  published.Add(time.Hour),
		Language:      "en",
		Keywords:      []string{"CMB", "cmb", " human agency "},
		Body:          "PATTERN != PROOF",
		Provenance: Provenance{
			SHA256:         SHA256Bytes([]byte("PATTERN != PROOF")),
			Repository:     "https://github.com/example/repo",
			Commit:         "abc123",
			HumanAuthored:  true,
			HumanAuthority: HumanAuthority,
		},
	}
}

func TestArticleJSONLD(t *testing.T) {
	data, err := ArticleJSONLD(validArtifact(t))
	if err != nil {
		t.Fatal(err)
	}

	var doc map[string]any
	if err := json.Unmarshal(data, &doc); err != nil {
		t.Fatal(err)
	}

	if got := doc["@context"]; got != "https://schema.org" {
		t.Fatalf("@context = %v", got)
	}
	if got := doc["@type"]; got != "Article" {
		t.Fatalf("@type = %v", got)
	}
	if got := doc["headline"]; got != "CMB Test Artifact" {
		t.Fatalf("headline = %v", got)
	}
	if got := doc["mainEntityOfPage"]; got != "https://example.org/cmb/test" {
		t.Fatalf("mainEntityOfPage = %v", got)
	}

	keywords, ok := doc["keywords"].([]any)
	if !ok {
		t.Fatal("keywords missing")
	}
	if len(keywords) != 2 {
		t.Fatalf("keywords len = %d, want 2", len(keywords))
	}
}

func TestArticleJSONLDDoesNotLeakCMBPolicyMetadata(t *testing.T) {
	data, err := ArticleJSONLD(validArtifact(t))
	if err != nil {
		t.Fatal(err)
	}

	var doc map[string]any
	if err := json.Unmarshal(data, &doc); err != nil {
		t.Fatal(err)
	}

	for _, forbiddenKey := range []string{
		"human_authority",
		"machine_has_final_authority",
		"additionalProperty",
		"cmb:invariants",
	} {
		if _, exists := doc[forbiddenKey]; exists {
			t.Fatalf("Google-facing JSON-LD leaked CMB metadata key %q", forbiddenKey)
		}
	}

	if got := doc["articleBody"]; got != "PATTERN != PROOF" {
		t.Fatalf("articleBody = %v; human-authored source text should remain visible", got)
	}
}

func TestCMBSemanticJSONPreservesHumanAuthority(t *testing.T) {
	data, err := CMBSemanticJSON(validArtifact(t), validCanonSemantics())
	if err != nil {
		t.Fatal(err)
	}

	var doc map[string]any
	if err := json.Unmarshal(data, &doc); err != nil {
		t.Fatal(err)
	}
	if got := doc["human_authority"]; got != HumanAuthority {
		t.Fatalf("human_authority = %v", got)
	}
	interpretation, ok := doc["interpretation"].(map[string]any)
	if !ok {
		t.Fatal("interpretation missing")
	}
	if got := interpretation["machine_has_final_authority"]; got != false {
		t.Fatalf("machine_has_final_authority = %v", got)
	}
}

func TestArtifactRejectsMachineAuthority(t *testing.T) {
	artifact := validArtifact(t)
	artifact.Provenance.HumanAuthority = "MACHINE_FINAL"
	if err := artifact.Validate(); err == nil {
		t.Fatal("expected machine authority rejection")
	}
}

func TestArtifactRejectsHTTPURL(t *testing.T) {
	artifact := validArtifact(t)
	artifact.URL = "http://example.org/insecure"
	if err := artifact.Validate(); err == nil {
		t.Fatal("expected non-HTTPS URL rejection")
	}
}

func TestDecodeArtifactRejectsUnknownField(t *testing.T) {
	payload := `{
		"schema_version":"cmb-gsb.artifact.v1",
		"id":"x",
		"url":"https://example.org/x",
		"title":"X",
		"description":"X",
		"author":{"name":"Human"},
		"date_published":"2026-09-04T13:00:00Z",
		"date_modified":"2026-09-04T13:00:00Z",
		"language":"en",
		"provenance":{"human_authored":true,"human_authority":"HUMAN_FINAL"},
		"ranking_override":true
	}`

	if _, err := DecodeArtifact(strings.NewReader(payload)); err == nil {
		t.Fatal("expected unknown field rejection")
	}
}

func TestCanonicalLinkEscapesHTML(t *testing.T) {
	got, err := CanonicalLink("https://example.org/a?x=1&y=2")
	if err != nil {
		t.Fatal(err)
	}
	want := `<link rel="canonical" href="https://example.org/a?x=1&amp;y=2">`
	if got != want {
		t.Fatalf("canonical = %q, want %q", got, want)
	}
}

func TestSitemapXML(t *testing.T) {
	data, err := SitemapXML([]Artifact{validArtifact(t)})
	if err != nil {
		t.Fatal(err)
	}
	text := string(data)
	for _, expected := range []string{
		`<?xml version="1.0" encoding="UTF-8"?>`,
		`xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"`,
		`<loc>https://example.org/cmb/test</loc>`,
		`<lastmod>2026-09-04</lastmod>`,
	} {
		if !strings.Contains(text, expected) {
			t.Fatalf("sitemap missing %q:\n%s", expected, text)
		}
	}
}

func TestSitemapRejectsDuplicateURL(t *testing.T) {
	artifact := validArtifact(t)
	if _, err := SitemapXML([]Artifact{artifact, artifact}); err == nil {
		t.Fatal("expected duplicate URL rejection")
	}
}

func TestRobotsTXTPreservesProjectBasePath(t *testing.T) {
	got, err := RobotsTXT("https://example.org/project/")
	if err != nil {
		t.Fatal(err)
	}
	want := "User-agent: *\nAllow: /\n\nSitemap: https://example.org/project/sitemap.xml\n"
	if got != want {
		t.Fatalf("robots = %q, want %q", got, want)
	}
}

func TestOriginURL(t *testing.T) {
	got, err := OriginURL("https://example.org/project/page/")
	if err != nil {
		t.Fatal(err)
	}
	if got != "https://example.org" {
		t.Fatalf("origin = %q", got)
	}
}

func TestHeadBlockContainsCanonicalAndJSONLD(t *testing.T) {
	data, err := HeadBlock(validArtifact(t))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Contains(data, []byte(`rel="canonical"`)) {
		t.Fatal("head block missing canonical link")
	}
	if !bytes.Contains(data, []byte(`type="application/ld+json"`)) {
		t.Fatal("head block missing JSON-LD script")
	}
}

func TestSHA256Bytes(t *testing.T) {
	got := SHA256Bytes([]byte("abc"))
	want := "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
	if got != want {
		t.Fatalf("sha256 = %s, want %s", got, want)
	}
}

func TestBindSourcePopulatesBodyAndHash(t *testing.T) {
	artifact := validArtifact(t)
	artifact.Body = ""
	artifact.Provenance.SHA256 = ""
	source := []byte("# Human source\n\nPATTERN != PROOF\n")

	bound, err := BindSource(artifact, source)
	if err != nil {
		t.Fatal(err)
	}
	if bound.Body != string(source) {
		t.Fatalf("body = %q", bound.Body)
	}
	if bound.Provenance.SHA256 != SHA256Bytes(source) {
		t.Fatalf("sha256 = %s", bound.Provenance.SHA256)
	}
}

func TestBindSourceRejectsDeclaredHashMismatch(t *testing.T) {
	artifact := validArtifact(t)
	artifact.Body = ""
	artifact.Provenance.SHA256 = SHA256Bytes([]byte("different source"))

	_, err := BindSource(artifact, []byte("actual source"))
	if err == nil {
		t.Fatal("expected source hash mismatch")
	}
	if !strings.Contains(err.Error(), "source SHA-256 mismatch") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestBindSourceRejectsInvalidUTF8(t *testing.T) {
	artifact := validArtifact(t)
	artifact.Body = ""
	artifact.Provenance.SHA256 = ""

	if _, err := BindSource(artifact, []byte{0xff, 0xfe}); err == nil {
		t.Fatal("expected invalid UTF-8 rejection")
	}
}

func TestPageHTMLEscapesSourceButEmbedsArticleJSONLD(t *testing.T) {
	artifact := validArtifact(t)
	artifact.Body = "<script>alert('x')</script>\nPATTERN != PROOF"
	artifact.Provenance.SHA256 = SHA256Bytes([]byte(artifact.Body))

	page, err := PageHTML(artifact)
	if err != nil {
		t.Fatal(err)
	}
	text := string(page)

	if strings.Contains(text, "<pre class=\"source\"><script>") {
		t.Fatal("human source was inserted as raw HTML")
	}
	if !strings.Contains(text, "&lt;script&gt;alert") {
		t.Fatal("escaped human source not found")
	}
	if !strings.Contains(text, `<script type="application/ld+json">`) {
		t.Fatal("embedded Article JSON-LD missing")
	}
	if !strings.Contains(text, `rel="canonical" href="https://example.org/cmb/test"`) {
		t.Fatal("canonical URL missing")
	}
	if !strings.Contains(text, HumanAuthority) && strings.Contains(text, "machine_has_final_authority") {
		t.Fatal("CMB sidecar semantics leaked into page JSON-LD")
	}
}

func TestSiteCSSHasNoExternalImports(t *testing.T) {
	css := string(SiteCSS())
	if strings.Contains(css, "@import") || strings.Contains(css, "url(http") {
		t.Fatal("site CSS must remain zero-dependency")
	}
}

func TestDecorativePublicationFrame(t *testing.T) {
	artifact := validArtifact(t)
	page, err := PageHTML(artifact)
	if err != nil {
		t.Fatal(err)
	}
	text := string(page)

	for _, required := range []string{
		"Human Source Transmission",
		"Provenance Ledger",
		"Human ↔ Machine Boundary",
		"Publication Surfaces",
		"HUMAN_AGENCY &gt; MACHINE_AUTHORITY",
		"class=\"skip-link\"",
		`@media (prefers-reduced-motion: reduce)`,
	} {
		target := text
		if strings.HasPrefix(required, "@media") {
			target = string(SiteCSS())
		}
		if !strings.Contains(target, required) {
			t.Fatalf("decorative publication missing %q", required)
		}
	}
}

func TestPublicationFrameAvoidsEmDash(t *testing.T) {
	artifact := validArtifact(t)
	page, err := PageHTML(artifact)
	if err != nil {
		t.Fatal(err)
	}

	if strings.Contains(string(page), "—") {
		t.Fatal("publication HTML contains an em dash")
	}
	if strings.Contains(string(SiteCSS()), "—") {
		t.Fatal("publication CSS contains an em dash")
	}
}

func TestSiteCSSPreservesAccessibilityModes(t *testing.T) {
	css := string(SiteCSS())
	for _, required := range []string{
		":focus-visible",
		"prefers-reduced-motion",
		"@media print",
		".skip-link",
	} {
		if !strings.Contains(css, required) {
			t.Fatalf("site CSS missing accessibility rule %q", required)
		}
	}
}


func TestCMBSemanticJSONBindsCanonDigest(t *testing.T) {
	data, err := CMBSemanticJSON(validArtifact(t), validCanonSemantics())
	if err != nil {
		t.Fatal(err)
	}

	var doc map[string]any
	if err := json.Unmarshal(data, &doc); err != nil {
		t.Fatal(err)
	}
	if got := doc["schema_version"]; got != "cmb-gsb.semantic.v2" {
		t.Fatalf("schema_version = %v", got)
	}
	canonDoc, ok := doc["canon"].(map[string]any)
	if !ok {
		t.Fatal("canon binding missing")
	}
	if got := canonDoc["sha256"]; got != strings.Repeat("0", 64) {
		t.Fatalf("canon sha256 = %v", got)
	}
	invariants, ok := doc["invariants"].([]any)
	if !ok || len(invariants) != 9 {
		t.Fatalf("invariants = %v", doc["invariants"])
	}
}

func TestCMBSemanticJSONRejectsIncompleteCanon(t *testing.T) {
	canon := validCanonSemantics()
	canon.Invariants = canon.Invariants[:4]
	if _, err := CMBSemanticJSON(validArtifact(t), canon); err == nil {
		t.Fatal("expected incomplete canon rejection")
	}
}

func TestArticleJSONLDPreservesExactBodyText(t *testing.T) {
	artifact := validArtifact(t)
	artifact.Body = "\n  PATTERN != PROOF  \n"
	artifact.Provenance.SHA256 = SHA256Bytes([]byte(artifact.Body))

	data, err := ArticleJSONLD(artifact)
	if err != nil {
		t.Fatal(err)
	}
	var doc map[string]any
	if err := json.Unmarshal(data, &doc); err != nil {
		t.Fatal(err)
	}
	if got := doc["articleBody"]; got != artifact.Body {
		t.Fatalf("articleBody = %q, want exact %q", got, artifact.Body)
	}
}

func TestArtifactRejectsURLFragment(t *testing.T) {
	artifact := validArtifact(t)
	artifact.URL = "https://example.org/cmb/test#fragment"
	if err := artifact.Validate(); err == nil {
		t.Fatal("expected URL fragment rejection")
	}
}

func TestNormalizeBaseURLRejectsUserinfo(t *testing.T) {
	if _, err := NormalizeBaseURL("https://user:pass@example.org/project/"); err == nil {
		t.Fatal("expected userinfo rejection")
	}
}

func TestReadRegularFileRejectsSymlink(t *testing.T) {
	tmp := t.TempDir()
	target := filepath.Join(tmp, "target.txt")
	link := filepath.Join(tmp, "link.txt")
	if err := os.WriteFile(target, []byte("source"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(target, link); err != nil {
		t.Skipf("symlink unavailable: %v", err)
	}
	if _, err := ReadRegularFile(link, 1024); err == nil {
		t.Fatal("expected symlink rejection")
	}
}

func TestWriteBundleAtomicReplacesCompleteGeneration(t *testing.T) {
	output := filepath.Join(t.TempDir(), "site")
	first := map[string][]byte{
		"index.html":   []byte("first"),
		"obsolete.txt": []byte("old"),
	}
	if err := WriteBundleAtomic(output, "artifact", "0.4.0", first); err != nil {
		t.Fatal(err)
	}

	second := map[string][]byte{
		"index.html": []byte("second"),
	}
	if err := WriteBundleAtomic(output, "artifact", "0.4.0", second); err != nil {
		t.Fatal(err)
	}

	data, err := os.ReadFile(filepath.Join(output, "index.html"))
	if err != nil {
		t.Fatal(err)
	}
	if string(data) != "second" {
		t.Fatalf("index.html = %q", data)
	}
	if _, err := os.Stat(filepath.Join(output, "obsolete.txt")); !os.IsNotExist(err) {
		t.Fatalf("obsolete output survived atomic replacement: %v", err)
	}
	if _, err := os.Stat(filepath.Join(output, "manifest.json")); err != nil {
		t.Fatalf("manifest missing: %v", err)
	}
}
