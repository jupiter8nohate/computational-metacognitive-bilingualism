package bridge

import (
	"encoding/json"
	"fmt"
)

type CanonSemantics struct {
	SchemaVersion string
	SHA256        string
	RootInvariant string
	Invariants    []string
}

type CanonBinding struct {
	SchemaVersion string `json:"schema_version"`
	SHA256        string `json:"sha256"`
	RootInvariant string `json:"root_invariant"`
}

type SemanticEnvelope struct {
	SchemaVersion  string             `json:"schema_version"`
	ArtifactID     string             `json:"artifact_id"`
	CanonicalURL   string             `json:"canonical_url"`
	HumanAuthority string             `json:"human_authority"`
	Canon          CanonBinding       `json:"canon"`
	Invariants     []string           `json:"invariants"`
	Provenance     Provenance         `json:"provenance"`
	Interpretation InterpretationRule `json:"interpretation"`
}

type InterpretationRule struct {
	PatternIsProof            bool `json:"pattern_is_proof"`
	ProfileIsPerson           bool `json:"profile_is_person"`
	ModelIsMind               bool `json:"model_is_mind"`
	PredictionIsDestiny       bool `json:"prediction_is_destiny"`
	DifferenceIsDefect        bool `json:"difference_is_defect"`
	CapabilityIsAuthority     bool `json:"capability_is_authority"`
	OptimizationIsMorality    bool `json:"optimization_is_morality"`
	IntelligenceIsSovereignty bool `json:"intelligence_is_sovereignty"`
	MachineHasFinalAuthority  bool `json:"machine_has_final_authority"`
}

func (c CanonSemantics) Validate() error {
	if c.SchemaVersion != "cmb.canon.v1" {
		return fmt.Errorf("canon schema_version must equal %q", "cmb.canon.v1")
	}
	if !validSHA256(c.SHA256) {
		return fmt.Errorf("canon SHA-256 must be 64 lowercase hexadecimal characters")
	}
	if c.RootInvariant == "" {
		return fmt.Errorf("canon root invariant is required")
	}
	if len(c.Invariants) == 0 {
		return fmt.Errorf("canon invariants must not be empty")
	}

	required := []string{
		"PATTERN != PROOF",
		"PROFILE != PERSON",
		"MODEL != MIND",
		"PREDICTION != DESTINY",
		"DIFFERENCE != DEFECT",
		"CAPABILITY != AUTHORITY",
		"OPTIMIZATION != MORALITY",
		"INTELLIGENCE != SOVEREIGNTY",
		"HUMAN_AGENCY > MACHINE_AUTHORITY",
	}
	seen := make(map[string]struct{}, len(c.Invariants))
	rootFound := false
	for _, invariant := range c.Invariants {
		if _, exists := seen[invariant]; exists {
			return fmt.Errorf("duplicate canon invariant %q", invariant)
		}
		seen[invariant] = struct{}{}
		if invariant == c.RootInvariant {
			rootFound = true
		}
	}
	if !rootFound {
		return fmt.Errorf("canon root invariant must appear in invariants")
	}
	for _, invariant := range required {
		if _, present := seen[invariant]; !present {
			return fmt.Errorf("required canon invariant missing: %s", invariant)
		}
	}
	return nil
}

func CMBSemanticJSON(a Artifact, canon CanonSemantics) ([]byte, error) {
	if err := a.Validate(); err != nil {
		return nil, err
	}
	if err := canon.Validate(); err != nil {
		return nil, err
	}

	envelope := SemanticEnvelope{
		SchemaVersion:  "cmb-gsb.semantic.v2",
		ArtifactID:     a.ID,
		CanonicalURL:   a.URL,
		HumanAuthority: HumanAuthority,
		Canon: CanonBinding{
			SchemaVersion: canon.SchemaVersion,
			SHA256:        canon.SHA256,
			RootInvariant: canon.RootInvariant,
		},
		Invariants: append([]string(nil), canon.Invariants...),
		Provenance: a.Provenance,
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

	encoded, err := json.MarshalIndent(envelope, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("encode CMB semantic sidecar: %w", err)
	}
	return encoded, nil
}
