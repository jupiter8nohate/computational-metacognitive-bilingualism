package canon

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strings"
)

const (
	SchemaVersion = "cmb.canon.v1"
	Framework     = "Computational Metacognitive Bilingualism"
	maxCanonBytes = 4 << 20
)

type Document struct {
	SchemaVersion        string            `json:"schema_version"`
	Framework            string            `json:"framework"`
	Thesis               string            `json:"thesis"`
	RootInvariant        string            `json:"root_invariant"`
	Invariants           []string          `json:"invariants"`
	InterpretationPolicy json.RawMessage   `json:"interpretation_policy"`
	Views                json.RawMessage   `json:"views"`
	Nodes                []json.RawMessage `json:"nodes"`
	Edges                []json.RawMessage `json:"edges"`
}

type Loaded struct {
	Document Document
	SHA256   string
}

func LoadFile(path string) (Loaded, error) {
	info, err := os.Lstat(path)
	if err != nil {
		return Loaded{}, fmt.Errorf("stat canon: %w", err)
	}
	if info.Mode()&os.ModeSymlink != 0 {
		return Loaded{}, fmt.Errorf("canon must not be a symbolic link")
	}
	if !info.Mode().IsRegular() {
		return Loaded{}, fmt.Errorf("canon must be a regular file")
	}
	if info.Size() > maxCanonBytes {
		return Loaded{}, fmt.Errorf("canon exceeds %d bytes", maxCanonBytes)
	}

	file, err := os.Open(path)
	if err != nil {
		return Loaded{}, fmt.Errorf("open canon: %w", err)
	}
	defer file.Close()

	data, err := io.ReadAll(io.LimitReader(file, maxCanonBytes+1))
	if err != nil {
		return Loaded{}, fmt.Errorf("read canon: %w", err)
	}
	if len(data) > maxCanonBytes {
		return Loaded{}, fmt.Errorf("canon exceeds %d bytes", maxCanonBytes)
	}

	document, err := Decode(strings.NewReader(string(data)))
	if err != nil {
		return Loaded{}, err
	}

	sum := sha256.Sum256(data)
	return Loaded{
		Document: document,
		SHA256:   hex.EncodeToString(sum[:]),
	}, nil
}

func Decode(r io.Reader) (Document, error) {
	decoder := json.NewDecoder(r)
	decoder.DisallowUnknownFields()

	var document Document
	if err := decoder.Decode(&document); err != nil {
		return Document{}, fmt.Errorf("decode canon: %w", err)
	}

	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		if err == nil {
			return Document{}, fmt.Errorf("decode canon: trailing JSON value")
		}
		return Document{}, fmt.Errorf("decode canon trailer: %w", err)
	}

	if err := document.Validate(); err != nil {
		return Document{}, fmt.Errorf("validate canon: %w", err)
	}
	return document, nil
}

func (d Document) Validate() error {
	if d.SchemaVersion != SchemaVersion {
		return fmt.Errorf("schema_version must equal %q", SchemaVersion)
	}
	if d.Framework != Framework {
		return fmt.Errorf("framework must equal %q", Framework)
	}
	if strings.TrimSpace(d.Thesis) == "" {
		return fmt.Errorf("thesis is required")
	}
	if strings.TrimSpace(d.RootInvariant) == "" {
		return fmt.Errorf("root_invariant is required")
	}
	if len(d.Invariants) == 0 {
		return fmt.Errorf("invariants must not be empty")
	}

	seen := make(map[string]struct{}, len(d.Invariants))
	rootFound := false
	for i, invariant := range d.Invariants {
		if invariant != strings.TrimSpace(invariant) || invariant == "" {
			return fmt.Errorf("invariants[%d] must be non-empty and already normalized", i)
		}
		if _, exists := seen[invariant]; exists {
			return fmt.Errorf("duplicate invariant %q", invariant)
		}
		seen[invariant] = struct{}{}
		if invariant == d.RootInvariant {
			rootFound = true
		}
	}
	if !rootFound {
		return fmt.Errorf("root_invariant must appear in invariants")
	}
	if len(d.InterpretationPolicy) == 0 || len(d.Views) == 0 || len(d.Nodes) == 0 || len(d.Edges) == 0 {
		return fmt.Errorf("canon graph sections must not be empty")
	}
	return nil
}
