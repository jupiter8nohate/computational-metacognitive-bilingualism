package canon

import (
	"strings"
	"testing"
)

func validCanonJSON() string {
	return `{
  "schema_version": "cmb.canon.v1",
  "framework": "Computational Metacognitive Bilingualism",
  "thesis": "VERIFY, DON'T JUST BELIEVE.",
  "root_invariant": "HUMAN_AGENCY > MACHINE_AUTHORITY",
  "invariants": [
    "PATTERN != PROOF",
    "HUMAN_AGENCY > MACHINE_AUTHORITY"
  ],
  "interpretation_policy": {"declaration_is_proof": false},
  "views": {"human": {}, "machine": {}},
  "nodes": [{"id": "cmb-core"}],
  "edges": [{"from": "cmb-core", "to": "cmb-core", "relation": "self"}]
}`
}

func TestDecodeCanon(t *testing.T) {
	document, err := Decode(strings.NewReader(validCanonJSON()))
	if err != nil {
		t.Fatal(err)
	}
	if document.RootInvariant != "HUMAN_AGENCY > MACHINE_AUTHORITY" {
		t.Fatalf("root invariant = %q", document.RootInvariant)
	}
	if len(document.Invariants) != 2 {
		t.Fatalf("invariants = %v", document.Invariants)
	}
}

func TestDecodeCanonRejectsUnknownTopLevelField(t *testing.T) {
	payload := strings.Replace(validCanonJSON(), `"thesis":`, `"unknown": true, "thesis":`, 1)
	if _, err := Decode(strings.NewReader(payload)); err == nil {
		t.Fatal("expected unknown field rejection")
	}
}

func TestDecodeCanonRejectsMissingRootInvariantInList(t *testing.T) {
	payload := strings.Replace(
		validCanonJSON(),
		`"HUMAN_AGENCY > MACHINE_AUTHORITY"
  ],`,
		`"MODEL != MIND"
  ],`,
		1,
	)
	if _, err := Decode(strings.NewReader(payload)); err == nil {
		t.Fatal("expected root invariant validation failure")
	}
}

func TestDecodeCanonRejectsDuplicateInvariant(t *testing.T) {
	payload := strings.Replace(
		validCanonJSON(),
		`"PATTERN != PROOF",
    "HUMAN_AGENCY > MACHINE_AUTHORITY"`,
		`"PATTERN != PROOF",
    "PATTERN != PROOF",
    "HUMAN_AGENCY > MACHINE_AUTHORITY"`,
		1,
	)
	if _, err := Decode(strings.NewReader(payload)); err == nil {
		t.Fatal("expected duplicate invariant validation failure")
	}
}
