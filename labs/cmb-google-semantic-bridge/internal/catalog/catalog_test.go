package catalog

import (
	"strings"
	"testing"
)

func validCatalog() string {
	return `{
  "schema_version":"cmb.library.catalog.v1",
  "framework":"Computational Metacognitive Bilingualism",
  "declared_originator":"Human Author",
  "purpose":"Index public artifacts.",
  "invariants":["PATTERN != PROOF"],
  "interpretation_policy":{
    "catalog_is_identity":false,
    "classification_is_truth":false,
    "uncertainty_is_allowed":true,
    "human_self_definition_has_priority":true,
    "provenance_note":"Integrity is evidence, not ownership."
  },
  "artifacts":[{
    "id":"artifact-one",
    "title":"Artifact One",
    "path":"docs/ONE.md",
    "format":"markdown",
    "kind":"manifesto",
    "status":"canonical",
    "provenance_scope":"canonical_public_artifact",
    "human_readable":true,
    "machine_indexable":true,
    "concepts":["human agency"],
    "declared_meaning":"A declared public artifact."
  }]
}`
}

func TestDecodeCatalog(t *testing.T) {
	doc, err := Decode(strings.NewReader(validCatalog()))
	if err != nil {
		t.Fatal(err)
	}
	if len(doc.Artifacts) != 1 || doc.Artifacts[0].ID != "artifact-one" {
		t.Fatalf("artifacts = %#v", doc.Artifacts)
	}
}

func TestDecodeCatalogRejectsUnknownField(t *testing.T) {
	payload := strings.Replace(validCatalog(), `"purpose":`, `"ranking_override":true,"purpose":`, 1)
	if _, err := Decode(strings.NewReader(payload)); err == nil {
		t.Fatal("expected unknown field rejection")
	}
}

func TestDecodeCatalogRejectsTraversal(t *testing.T) {
	payload := strings.Replace(validCatalog(), `"docs/ONE.md"`, `"../ONE.md"`, 1)
	if _, err := Decode(strings.NewReader(payload)); err == nil {
		t.Fatal("expected traversal rejection")
	}
}

func TestDecodeCatalogRejectsDuplicateArtifactID(t *testing.T) {
	artifact := `{
    "id":"artifact-one",
    "title":"Artifact Two",
    "path":"docs/TWO.md",
    "format":"markdown",
    "kind":"manifesto",
    "status":"derived",
    "provenance_scope":"repository_artifact",
    "human_readable":true,
    "machine_indexable":true,
    "concepts":["verification"],
    "declared_meaning":"Second artifact."
  }`
	payload := strings.Replace(validCatalog(), "\n  }]\n}", ",\n  "+artifact+"]\n}", 1)
	if _, err := Decode(strings.NewReader(payload)); err == nil {
		t.Fatal("expected duplicate artifact id rejection")
	}
}
