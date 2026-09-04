package bridge

import (
	"encoding/json"
	"fmt"
)

type SemanticEnvelope struct {
	SchemaVersion  string             `json:"schema_version"`
	ArtifactID     string             `json:"artifact_id"`
	CanonicalURL   string             `json:"canonical_url"`
	HumanAuthority string             `json:"human_authority"`
	Invariants     []string           `json:"invariants"`
	Provenance     Provenance         `json:"provenance"`
	Interpretation InterpretationRule `json:"interpretation"`
}

type InterpretationRule struct {
	PatternIsProof           bool `json:"pattern_is_proof"`
	ProfileIsPerson          bool `json:"profile_is_person"`
	ModelIsMind              bool `json:"model_is_mind"`
	PredictionIsDestiny      bool `json:"prediction_is_destiny"`
	MachineHasFinalAuthority bool `json:"machine_has_final_authority"`
}

func CMBSemanticJSON(a Artifact) ([]byte, error) {
	if err := a.Validate(); err != nil {
		return nil, err
	}

	envelope := SemanticEnvelope{
		SchemaVersion:  "cmb-gsb.semantic.v1",
		ArtifactID:     a.ID,
		CanonicalURL:   a.URL,
		HumanAuthority: HumanAuthority,
		Invariants: []string{
			"PATTERN != PROOF",
			"PROFILE != PERSON",
			"MODEL != MIND",
			"PREDICTION != DESTINY",
			"HUMAN_AGENCY > MACHINE_AUTHORITY",
		},
		Provenance: a.Provenance,
		Interpretation: InterpretationRule{
			PatternIsProof:           false,
			ProfileIsPerson:          false,
			ModelIsMind:              false,
			PredictionIsDestiny:      false,
			MachineHasFinalAuthority: false,
		},
	}

	encoded, err := json.MarshalIndent(envelope, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("encode CMB semantic sidecar: %w", err)
	}
	return encoded, nil
}
