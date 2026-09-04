package bridge

import (
	"encoding/json"
	"fmt"
	"io"
)

func DecodeArtifact(r io.Reader) (Artifact, error) {
	decoder := json.NewDecoder(r)
	decoder.DisallowUnknownFields()

	var artifact Artifact
	if err := decoder.Decode(&artifact); err != nil {
		return Artifact{}, fmt.Errorf("decode artifact: %w", err)
	}

	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		if err == nil {
			return Artifact{}, fmt.Errorf("decode artifact: trailing JSON value")
		}
		return Artifact{}, fmt.Errorf("decode artifact trailer: %w", err)
	}

	if err := artifact.Validate(); err != nil {
		return Artifact{}, fmt.Errorf("validate artifact: %w", err)
	}
	return artifact, nil
}
