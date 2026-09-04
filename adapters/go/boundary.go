// Package cmbboundary implements the CMB boundary-event.v1 contract in Go.
//
// The evaluator consumes explicit application facts. It does not infer identity,
// diagnosis, intent, mental state, or moral status from human expression.
package cmbboundary

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"strings"
)

const (
	SchemaVersion = "cmb.boundary-event.v1"
	Authority     = "HUMAN_FINAL"
)

type BoundaryCode string

const (
	AIDisclosureRequired   BoundaryCode = "AI_DISCLOSURE_REQUIRED"
	HumanReviewRequired    BoundaryCode = "HUMAN_REVIEW_REQUIRED"
	ProfileIsNotPerson     BoundaryCode = "PROFILE_IS_NOT_PERSON"
	PredictionIsNotDestiny BoundaryCode = "PREDICTION_IS_NOT_DESTINY"
	ConsentRequired        BoundaryCode = "CONSENT_REQUIRED"
)

type BoundaryEvent struct {
	SchemaVersion               string  `json:"schema_version"`
	EventID                     *string `json:"event_id"`
	ConsequentialDecision       bool    `json:"consequential_decision"`
	AIInvolved                  bool    `json:"ai_involved"`
	AIDisclosed                 bool    `json:"ai_disclosed"`
	HumanReviewAvailable        bool    `json:"human_review_available"`
	ProfileTreatedAsPerson      bool    `json:"profile_treated_as_person"`
	PredictionTreatedAsDestiny  bool    `json:"prediction_treated_as_destiny"`
	ConsentRequired             bool    `json:"consent_required"`
	ConsentPresent              bool    `json:"consent_present"`
}

func (event BoundaryEvent) Validate() error {
	if event.SchemaVersion != SchemaVersion {
		return fmt.Errorf("schema_version must equal %s", SchemaVersion)
	}
	if event.EventID != nil && strings.TrimSpace(*event.EventID) == "" {
		return errors.New("event_id must be non-empty when supplied")
	}
	return nil
}

type BoundaryViolation struct {
	Code      BoundaryCode `json:"code"`
	Invariant string       `json:"invariant"`
	Message   string       `json:"message"`
}

type BoundaryDecision struct {
	Allowed    bool                `json:"allowed"`
	Authority  string              `json:"authority"`
	Violations []BoundaryViolation `json:"violations"`
}

type BoundaryRejectedError struct {
	Decision BoundaryDecision
}

func (err *BoundaryRejectedError) Error() string {
	codes := make([]string, 0, len(err.Decision.Violations))
	for _, violation := range err.Decision.Violations {
		codes = append(codes, string(violation.Code))
	}
	return "CMB boundary rejected event: " + strings.Join(codes, ", ")
}

// ParseBoundaryEventJSON validates the transport shape before semantic evaluation.
// Unknown fields, duplicate top-level keys, trailing values, invalid versions, and
// blank event IDs fail closed.
func ParseBoundaryEventJSON(data []byte) (BoundaryEvent, error) {
	if err := rejectDuplicateTopLevelKeys(data); err != nil {
		return BoundaryEvent{}, err
	}

	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.DisallowUnknownFields()

	var event BoundaryEvent
	if err := decoder.Decode(&event); err != nil {
		return BoundaryEvent{}, fmt.Errorf("invalid boundary event: %w", err)
	}
	if err := requireJSONEOF(decoder); err != nil {
		return BoundaryEvent{}, err
	}
	if err := event.Validate(); err != nil {
		return BoundaryEvent{}, err
	}
	return event, nil
}

func requireJSONEOF(decoder *json.Decoder) error {
	var extra json.RawMessage
	if err := decoder.Decode(&extra); err == io.EOF {
		return nil
	} else if err != nil {
		return fmt.Errorf("invalid trailing JSON: %w", err)
	}
	return errors.New("boundary event must contain exactly one JSON value")
}

func rejectDuplicateTopLevelKeys(data []byte) error {
	decoder := json.NewDecoder(bytes.NewReader(data))

	token, err := decoder.Token()
	if err != nil {
		return fmt.Errorf("invalid boundary event: %w", err)
	}
	delim, ok := token.(json.Delim)
	if !ok || delim != '{' {
		return errors.New("boundary event must be a JSON object")
	}

	seen := make(map[string]struct{})
	for decoder.More() {
		token, err = decoder.Token()
		if err != nil {
			return fmt.Errorf("invalid boundary event key: %w", err)
		}
		key, ok := token.(string)
		if !ok {
			return errors.New("boundary event object key must be a string")
		}
		if _, exists := seen[key]; exists {
			return fmt.Errorf("duplicate boundary event field: %s", key)
		}
		seen[key] = struct{}{}

		var raw json.RawMessage
		if err := decoder.Decode(&raw); err != nil {
			return fmt.Errorf("invalid value for %s: %w", key, err)
		}
	}

	token, err = decoder.Token()
	if err != nil {
		return fmt.Errorf("invalid boundary event: %w", err)
	}
	delim, ok = token.(json.Delim)
	if !ok || delim != '}' {
		return errors.New("boundary event object did not terminate correctly")
	}
	return requireJSONEOF(decoder)
}

func EvaluateBoundary(event BoundaryEvent) (BoundaryDecision, error) {
	if err := event.Validate(); err != nil {
		return BoundaryDecision{}, err
	}

	violations := make([]BoundaryViolation, 0, 5)

	if event.AIInvolved && !event.AIDisclosed {
		violations = append(violations, BoundaryViolation{
			Code:      AIDisclosureRequired,
			Invariant: "CAPABILITY != AUTHORITY",
			Message:   "AI involvement must be disclosed when this boundary policy requires transparency.",
		})
	}

	if event.ConsequentialDecision && !event.HumanReviewAvailable {
		violations = append(violations, BoundaryViolation{
			Code:      HumanReviewRequired,
			Invariant: "HUMAN_AGENCY > MACHINE_AUTHORITY",
			Message:   "Consequential automated decisions require an available human review path.",
		})
	}

	if event.ProfileTreatedAsPerson {
		violations = append(violations, BoundaryViolation{
			Code:      ProfileIsNotPerson,
			Invariant: "PROFILE != PERSON",
			Message:   "A profile may inform a workflow but must not be treated as the person itself.",
		})
	}

	if event.PredictionTreatedAsDestiny {
		violations = append(violations, BoundaryViolation{
			Code:      PredictionIsNotDestiny,
			Invariant: "PREDICTION != DESTINY",
			Message:   "A prediction must not be treated as an inevitable human outcome.",
		})
	}

	if event.ConsentRequired && !event.ConsentPresent {
		violations = append(violations, BoundaryViolation{
			Code:      ConsentRequired,
			Invariant: "ATTENTION != CONSENT",
			Message:   "The declared operation requires consent before it may proceed.",
		})
	}

	return BoundaryDecision{
		Allowed:    len(violations) == 0,
		Authority:  Authority,
		Violations: violations,
	}, nil
}

func RequireBoundary(event BoundaryEvent) (BoundaryDecision, error) {
	decision, err := EvaluateBoundary(event)
	if err != nil {
		return BoundaryDecision{}, err
	}
	if !decision.Allowed {
		return decision, &BoundaryRejectedError{Decision: decision}
	}
	return decision, nil
}
