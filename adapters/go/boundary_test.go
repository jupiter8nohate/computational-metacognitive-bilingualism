package cmbboundary

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type conformanceFile struct {
	SchemaVersion string            `json:"schema_version"`
	Cases         []conformanceCase `json:"cases"`
}

type conformanceCase struct {
	ID       string           `json:"id"`
	Event    json.RawMessage  `json:"event"`
	Expected expectedDecision `json:"expected"`
}

type expectedDecision struct {
	Allowed    bool                `json:"allowed"`
	Authority  string              `json:"authority"`
	Violations []expectedViolation `json:"violations"`
}

type expectedViolation struct {
	Code      BoundaryCode `json:"code"`
	Invariant string       `json:"invariant"`
}

func TestSharedBoundaryConformance(t *testing.T) {
	t.Helper()

	path := filepath.Join("..", "..", "conformance", "boundary.v1.cases.json")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read conformance fixture: %v", err)
	}

	var fixtures conformanceFile
	if err := json.Unmarshal(data, &fixtures); err != nil {
		t.Fatalf("decode conformance fixture: %v", err)
	}
	if fixtures.SchemaVersion != "cmb.boundary-conformance.v1" {
		t.Fatalf("unexpected conformance schema: %s", fixtures.SchemaVersion)
	}

	for _, fixture := range fixtures.Cases {
		fixture := fixture
		t.Run(fixture.ID, func(t *testing.T) {
			event, err := ParseBoundaryEventJSON(fixture.Event)
			if err != nil {
				t.Fatalf("parse event: %v", err)
			}
			decision, err := EvaluateBoundary(event)
			if err != nil {
				t.Fatalf("evaluate event: %v", err)
			}

			if decision.Allowed != fixture.Expected.Allowed {
				t.Fatalf("allowed: got %v want %v", decision.Allowed, fixture.Expected.Allowed)
			}
			if decision.Authority != fixture.Expected.Authority {
				t.Fatalf("authority: got %q want %q", decision.Authority, fixture.Expected.Authority)
			}
			if len(decision.Violations) != len(fixture.Expected.Violations) {
				t.Fatalf("violations: got %d want %d", len(decision.Violations), len(fixture.Expected.Violations))
			}

			for index, expected := range fixture.Expected.Violations {
				actual := decision.Violations[index]
				if actual.Code != expected.Code {
					t.Fatalf("violation[%d].code: got %q want %q", index, actual.Code, expected.Code)
				}
				if actual.Invariant != expected.Invariant {
					t.Fatalf("violation[%d].invariant: got %q want %q", index, actual.Invariant, expected.Invariant)
				}
			}
		})
	}
}

func TestParseBoundaryEventJSONRejectsUnsafeShapes(t *testing.T) {
	valid := `{
		"schema_version":"cmb.boundary-event.v1",
		"event_id":"go-001",
		"consequential_decision":false,
		"ai_involved":false,
		"ai_disclosed":false,
		"human_review_available":false,
		"profile_treated_as_person":false,
		"prediction_treated_as_destiny":false,
		"consent_required":false,
		"consent_present":false
	}`

	tests := map[string]string{
		"unknown field": strings.Replace(valid, `"consent_present":false`, `"consent_present":false,"surprise":true`, 1),
		"duplicate field": strings.Replace(valid, `"ai_involved":false`, `"ai_involved":false,"ai_involved":true`, 1),
		"wrong schema": strings.Replace(valid, "cmb.boundary-event.v1", "cmb.boundary-event.v999", 1),
		"blank event id": strings.Replace(valid, `"go-001"`, `"   "`, 1),
		"trailing value": valid + ` {"extra":true}`,
	}

	for name, input := range tests {
		t.Run(name, func(t *testing.T) {
			if _, err := ParseBoundaryEventJSON([]byte(input)); err == nil {
				t.Fatal("expected strict parser rejection")
			}
		})
	}
}

func TestRequireBoundaryReturnsStructuredRejection(t *testing.T) {
	event := BoundaryEvent{
		SchemaVersion:          SchemaVersion,
		AIInvolved:             true,
		AIDisclosed:            false,
		ConsequentialDecision:  false,
		HumanReviewAvailable:   false,
	}

	decision, err := RequireBoundary(event)
	if err == nil {
		t.Fatal("expected boundary rejection")
	}
	if decision.Allowed {
		t.Fatal("rejected decision must not be allowed")
	}
	if len(decision.Violations) != 1 || decision.Violations[0].Code != AIDisclosureRequired {
		t.Fatalf("unexpected decision: %+v", decision)
	}
}
