package main

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestPublishCommandBuildsCompleteDeterministicSite(t *testing.T) {
	tmp := t.TempDir()
	input := filepath.Join(tmp, "artifact.json")
	source := filepath.Join(tmp, "source.md")
	first := filepath.Join(tmp, "site-a")
	second := filepath.Join(tmp, "site-b")

	artifact := map[string]any{
		"schema_version": "cmb-gsb.artifact.v1",
		"id":             "publisher-test",
		"url":            "https://example.org/original/",
		"title":          "Publisher Test",
		"description":    "A deterministic static publisher test.",
		"author": map[string]any{
			"name": "Human Author",
		},
		"date_published": "2026-09-04T13:00:00Z",
		"date_modified":  "2026-09-04T13:00:00Z",
		"language":       "en",
		"provenance": map[string]any{
			"human_authored":  true,
			"human_authority": "HUMAN_FINAL",
		},
	}

	raw, err := json.MarshalIndent(artifact, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(input, append(raw, '\n'), 0o644); err != nil {
		t.Fatal(err)
	}
	sourceBody := "# Publisher Test\n\n<script>not executable source</script>\n\nPATTERN != PROOF\n"
	if err := os.WriteFile(source, []byte(sourceBody), 0o644); err != nil {
		t.Fatal(err)
	}

	for _, output := range []string{first, second} {
		var stdout bytes.Buffer
		var stderr bytes.Buffer
		err := run([]string{
			"publish",
			"-in", input,
			"-source", source,
			"-out", output,
			"-url", "https://example.org/published/",
		}, &stdout, &stderr)
		if err != nil {
			t.Fatalf("publish failed: %v stderr=%s", err, stderr.String())
		}
		if !strings.Contains(stdout.String(), "published publisher-test") {
			t.Fatalf("unexpected stdout: %s", stdout.String())
		}
	}

	required := []string{
		"index.html",
		"site.css",
		"source.md",
		"article.jsonld",
		"cmb-semantic.json",
		"head.html",
		"sitemap.xml",
		"robots.txt",
		"manifest.json",
	}
	for _, name := range required {
		firstData, err := os.ReadFile(filepath.Join(first, name))
		if err != nil {
			t.Fatalf("read first %s: %v", name, err)
		}
		secondData, err := os.ReadFile(filepath.Join(second, name))
		if err != nil {
			t.Fatalf("read second %s: %v", name, err)
		}
		if !bytes.Equal(firstData, secondData) {
			t.Fatalf("%s differs across deterministic publishes", name)
		}
	}

	index, err := os.ReadFile(filepath.Join(first, "index.html"))
	if err != nil {
		t.Fatal(err)
	}
	indexText := string(index)
	if !strings.Contains(indexText, "https://example.org/published/") {
		t.Fatal("canonical URL override not present in index.html")
	}
	if strings.Contains(indexText, "<pre class=\"source\"><script>") {
		t.Fatal("source was injected as executable HTML")
	}
	if !strings.Contains(indexText, "&lt;script&gt;not executable source&lt;/script&gt;") {
		t.Fatal("escaped source is missing from page")
	}

	copiedSource, err := os.ReadFile(filepath.Join(first, "source.md"))
	if err != nil {
		t.Fatal(err)
	}
	if string(copiedSource) != sourceBody {
		t.Fatal("published source copy differs from human source")
	}
}

func TestPublishRejectsInsecureCanonicalOverride(t *testing.T) {
	tmp := t.TempDir()
	input := filepath.Join(tmp, "artifact.json")
	source := filepath.Join(tmp, "source.md")

	config := `{
  "schema_version": "cmb-gsb.artifact.v1",
  "id": "reject-http",
  "url": "https://example.org/original/",
  "title": "Reject HTTP",
  "description": "Reject insecure canonical URLs.",
  "author": {"name": "Human Author"},
  "date_published": "2026-09-04T13:00:00Z",
  "date_modified": "2026-09-04T13:00:00Z",
  "language": "en",
  "provenance": {
    "human_authored": true,
    "human_authority": "HUMAN_FINAL"
  }
}`
	if err := os.WriteFile(input, []byte(config), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(source, []byte("human source"), 0o644); err != nil {
		t.Fatal(err)
	}

	err := run([]string{
		"publish",
		"-in", input,
		"-source", source,
		"-out", filepath.Join(tmp, "site"),
		"-url", "http://example.org/not-allowed/",
	}, &bytes.Buffer{}, &bytes.Buffer{})
	if err == nil {
		t.Fatal("expected insecure canonical override rejection")
	}
	if !strings.Contains(err.Error(), "absolute https URL") {
		t.Fatalf("unexpected error: %v", err)
	}
}
