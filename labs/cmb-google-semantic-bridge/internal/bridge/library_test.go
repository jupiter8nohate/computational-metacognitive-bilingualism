package bridge

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/jupiter8nohate/cmb-google-semantic-bridge/internal/catalog"
)

func TestBuildCanonLibraryPublishesDeclaredCorpusDeterministically(t *testing.T) {
	root := t.TempDir()
	if err := os.MkdirAll(filepath.Join(root, "docs"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(root, "agents"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "docs", "ONE.md"), []byte("# One\n\nPATTERN != PROOF\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "agents", "agent-card.json"), []byte("{\"name\":\"CMB\"}\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	catalogDoc := catalog.Document{
		SchemaVersion:      catalog.SchemaVersion,
		Framework:          catalog.Framework,
		DeclaredOriginator: "Human Author",
		Purpose:            "Publish declared works.",
		Invariants:         []string{"PATTERN != PROOF"},
		InterpretationPolicy: catalog.InterpretationPolicy{
			CatalogIsIdentity:              false,
			ClassificationIsTruth:          false,
			UncertaintyIsAllowed:           true,
			HumanSelfDefinitionHasPriority: true,
			ProvenanceNote:                 "Evidence is bounded.",
		},
		Artifacts: []catalog.Artifact{
			{
				ID: "one", Title: "One", Path: "docs/ONE.md", Format: "markdown", Kind: "manifesto",
				Status: "canonical", ProvenanceScope: "canonical_public_artifact",
				HumanReadable: true, Indexable: true, Concepts: []string{"human agency"},
				DeclaredMeaning: "First work.",
			},
			{
				ID: "cmb-agent-card", Title: "Agent Card", Path: "agents/agent-card.json", Format: "json", Kind: "discovery",
				Status: "canonical", ProvenanceScope: "canonical_public_artifact",
				HumanReadable: true, Indexable: true, Concepts: []string{"discovery"},
				DeclaredMeaning: "Agent discovery metadata.",
			},
		},
	}
	canon := validCanonSemantics()
	canonBytes := []byte("{\"schema_version\":\"cmb.canon.v1\"}\n")
	catalogBytes := []byte("{\"schema_version\":\"cmb.library.catalog.v1\"}\n")

	input := CanonLibraryInput{
		RepositoryRoot: root,
		BaseURL:        "https://example.org/cmb/",
		CanonBytes:     canonBytes,
		Canon:          canon,
		CatalogBytes:   catalogBytes,
		CatalogSHA256:  strings.Repeat("1", 64),
		Catalog:        catalogDoc,
	}
	first, index, err := BuildCanonLibrary(input)
	if err != nil {
		t.Fatal(err)
	}
	second, secondIndex, err := BuildCanonLibrary(input)
	if err != nil {
		t.Fatal(err)
	}
	if len(index.Artifacts) != 2 || len(secondIndex.Artifacts) != 2 {
		t.Fatalf("artifact counts = %d %d", len(index.Artifacts), len(secondIndex.Artifacts))
	}
	if !bytes.Equal(first["index.html"], second["index.html"]) {
		t.Fatal("index output is not deterministic")
	}
	for _, required := range []string{
		"index.html",
		"library-index.json",
		"collection.jsonld",
		"cmb-canon.json",
		"catalog.json",
		"site.css",
		"sitemap.xml",
		"robots.txt",
		"artifacts/one/index.html",
		"artifacts/one/source.md",
		"artifacts/one/work.jsonld",
		"artifacts/one/cmb-semantic.json",
		".well-known/agent-card.json",
	} {
		if len(first[required]) == 0 {
			t.Fatalf("missing %s", required)
		}
	}
	var machine LibraryIndex
	if err := json.Unmarshal(first["library-index.json"], &machine); err != nil {
		t.Fatal(err)
	}
	if machine.CanonicalURL != "https://example.org/cmb/" {
		t.Fatalf("canonical URL = %q", machine.CanonicalURL)
	}
}

func TestBuildCanonLibraryRejectsCatalogPathSymlink(t *testing.T) {
	root := t.TempDir()
	outside := filepath.Join(t.TempDir(), "outside.md")
	if err := os.WriteFile(outside, []byte("outside"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(outside, filepath.Join(root, "escape.md")); err != nil {
		t.Skipf("symlink unavailable: %v", err)
	}
	doc := catalog.Document{
		SchemaVersion: catalog.SchemaVersion, Framework: catalog.Framework, DeclaredOriginator: "Human",
		Purpose: "Test", Invariants: []string{"PATTERN != PROOF"},
		InterpretationPolicy: catalog.InterpretationPolicy{
			UncertaintyIsAllowed: true, HumanSelfDefinitionHasPriority: true, ProvenanceNote: "Bounded.",
		},
		Artifacts: []catalog.Artifact{{
			ID: "escape", Title: "Escape", Path: "escape.md", Format: "markdown", Kind: "test",
			Status: "canonical", ProvenanceScope: "repository_artifact", HumanReadable: true, Indexable: true,
			Concepts: []string{"safety"}, DeclaredMeaning: "Must fail.",
		}},
	}
	_, _, err := BuildCanonLibrary(CanonLibraryInput{
		RepositoryRoot: root, BaseURL: "https://example.org/cmb", CanonBytes: []byte("x"),
		Canon: validCanonSemantics(), CatalogBytes: []byte("y"), CatalogSHA256: strings.Repeat("1", 64), Catalog: doc,
	})
	if err == nil || !strings.Contains(err.Error(), "symbolic link") {
		t.Fatalf("expected symlink rejection, got %v", err)
	}
}

func TestWriteBundleAtomicSupportsNestedTree(t *testing.T) {
	output := filepath.Join(t.TempDir(), "site")
	outputs := map[string][]byte{"index.html": []byte("root")}
	outputs["artifacts/one/index.html"] = []byte("one")
	outputs[".well-known/agent-card.json"] = []byte("{}")
	err := WriteBundleAtomic(output, "library", "0.5.0", outputs)
	if err != nil {
		t.Fatal(err)
	}
	for _, name := range []string{"index.html", "artifacts/one/index.html", ".well-known/agent-card.json", "manifest.json"} {
		if _, err := os.Stat(filepath.Join(output, filepath.FromSlash(name))); err != nil {
			t.Fatalf("missing %s: %v", name, err)
		}
	}
}
