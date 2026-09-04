package bridge

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"
	"time"
)

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
	data, err := CMBSemanticJSON(validArtifact(t))
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

func TestRobotsTXT(t *testing.T) {
	got, err := RobotsTXT("https://example.org/cmb/test")
	if err != nil {
		t.Fatal(err)
	}
	want := "User-agent: *\nAllow: /\n\nSitemap: https://example.org/sitemap.xml\n"
	if got != want {
		t.Fatalf("robots = %q, want %q", got, want)
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
