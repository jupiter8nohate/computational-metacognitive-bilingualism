package catalog

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

const (
	SchemaVersion   = "cmb.library.catalog.v1"
	Framework       = "Computational Metacognitive Bilingualism"
	maxCatalogBytes = 8 << 20
)

type InterpretationPolicy struct {
	CatalogIsIdentity              bool   `json:"catalog_is_identity"`
	ClassificationIsTruth          bool   `json:"classification_is_truth"`
	UncertaintyIsAllowed           bool   `json:"uncertainty_is_allowed"`
	HumanSelfDefinitionHasPriority bool   `json:"human_self_definition_has_priority"`
	ProvenanceNote                 string `json:"provenance_note"`
}

type Artifact struct {
	ID              string   `json:"id"`
	Title           string   `json:"title"`
	Path            string   `json:"path"`
	Format          string   `json:"format"`
	Kind            string   `json:"kind"`
	Status          string   `json:"status"`
	ProvenanceScope string   `json:"provenance_scope"`
	HumanReadable    bool     `json:"human_readable"`
	Indexable        bool     `json:"machine_indexable"`
	Concepts         []string `json:"concepts"`
	DeclaredMeaning  string   `json:"declared_meaning"`
}

type Document struct {
	SchemaVersion        string               `json:"schema_version"`
	Framework            string               `json:"framework"`
	DeclaredOriginator   string               `json:"declared_originator"`
	Purpose              string               `json:"purpose"`
	Invariants           []string             `json:"invariants"`
	InterpretationPolicy InterpretationPolicy `json:"interpretation_policy"`
	Artifacts            []Artifact           `json:"artifacts"`
}

type Loaded struct {
	Document Document
	SHA256   string
	Bytes    []byte
}

func LoadFile(path string) (Loaded, error) {
	info, err := os.Lstat(path)
	if err != nil {
		return Loaded{}, fmt.Errorf("stat catalog: %w", err)
	}
	if info.Mode()&os.ModeSymlink != 0 {
		return Loaded{}, fmt.Errorf("catalog must not be a symbolic link")
	}
	if !info.Mode().IsRegular() {
		return Loaded{}, fmt.Errorf("catalog must be a regular file")
	}
	if info.Size() > maxCatalogBytes {
		return Loaded{}, fmt.Errorf("catalog exceeds %d bytes", maxCatalogBytes)
	}

	file, err := os.Open(path)
	if err != nil {
		return Loaded{}, fmt.Errorf("open catalog: %w", err)
	}
	defer file.Close()

	data, err := io.ReadAll(io.LimitReader(file, maxCatalogBytes+1))
	if err != nil {
		return Loaded{}, fmt.Errorf("read catalog: %w", err)
	}
	if len(data) > maxCatalogBytes {
		return Loaded{}, fmt.Errorf("catalog exceeds %d bytes", maxCatalogBytes)
	}

	document, err := Decode(strings.NewReader(string(data)))
	if err != nil {
		return Loaded{}, err
	}
	sum := sha256.Sum256(data)
	return Loaded{
		Document: document,
		SHA256:   hex.EncodeToString(sum[:]),
		Bytes:    append([]byte(nil), data...),
	}, nil
}

func Decode(r io.Reader) (Document, error) {
	decoder := json.NewDecoder(r)
	decoder.DisallowUnknownFields()

	var document Document
	if err := decoder.Decode(&document); err != nil {
		return Document{}, fmt.Errorf("decode catalog: %w", err)
	}
	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		if err == nil {
			return Document{}, fmt.Errorf("decode catalog: trailing JSON value")
		}
		return Document{}, fmt.Errorf("decode catalog trailer: %w", err)
	}
	if err := document.Validate(); err != nil {
		return Document{}, fmt.Errorf("validate catalog: %w", err)
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
	if strings.TrimSpace(d.DeclaredOriginator) == "" {
		return fmt.Errorf("declared_originator is required")
	}
	if strings.TrimSpace(d.Purpose) == "" {
		return fmt.Errorf("purpose is required")
	}
	if len(d.Invariants) == 0 {
		return fmt.Errorf("invariants must not be empty")
	}
	if d.InterpretationPolicy.CatalogIsIdentity {
		return fmt.Errorf("catalog_is_identity must be false")
	}
	if d.InterpretationPolicy.ClassificationIsTruth {
		return fmt.Errorf("classification_is_truth must be false")
	}
	if !d.InterpretationPolicy.UncertaintyIsAllowed {
		return fmt.Errorf("uncertainty_is_allowed must be true")
	}
	if !d.InterpretationPolicy.HumanSelfDefinitionHasPriority {
		return fmt.Errorf("human_self_definition_has_priority must be true")
	}
	if strings.TrimSpace(d.InterpretationPolicy.ProvenanceNote) == "" {
		return fmt.Errorf("provenance_note is required")
	}
	if len(d.Artifacts) == 0 {
		return fmt.Errorf("artifacts must not be empty")
	}

	invariants := make(map[string]struct{}, len(d.Invariants))
	for i, invariant := range d.Invariants {
		if invariant == "" || invariant != strings.TrimSpace(invariant) {
			return fmt.Errorf("invariants[%d] must be non-empty and normalized", i)
		}
		if _, exists := invariants[invariant]; exists {
			return fmt.Errorf("duplicate invariant %q", invariant)
		}
		invariants[invariant] = struct{}{}
	}

	ids := make(map[string]struct{}, len(d.Artifacts))
	for i, artifact := range d.Artifacts {
		if err := artifact.Validate(); err != nil {
			return fmt.Errorf("artifacts[%d]: %w", i, err)
		}
		if _, exists := ids[artifact.ID]; exists {
			return fmt.Errorf("duplicate artifact id %q", artifact.ID)
		}
		ids[artifact.ID] = struct{}{}
	}
	return nil
}

func (a Artifact) Validate() error {
	if strings.TrimSpace(a.ID) == "" {
		return fmt.Errorf("id is required")
	}
	if strings.TrimSpace(a.Title) == "" {
		return fmt.Errorf("title is required")
	}
	if err := validateRelativePath(a.Path); err != nil {
		return fmt.Errorf("path: %w", err)
	}
	if strings.TrimSpace(a.Format) == "" {
		return fmt.Errorf("format is required")
	}
	if strings.TrimSpace(a.Kind) == "" {
		return fmt.Errorf("kind is required")
	}
	switch a.Status {
	case "canonical", "derived", "planned", "open":
	default:
		return fmt.Errorf("unsupported status %q", a.Status)
	}
	switch a.ProvenanceScope {
	case "canonical_public_artifact", "repository_artifact":
	default:
		return fmt.Errorf("unsupported provenance_scope %q", a.ProvenanceScope)
	}
	if len(a.Concepts) == 0 {
		return fmt.Errorf("concepts must not be empty")
	}
	seen := make(map[string]struct{}, len(a.Concepts))
	for i, concept := range a.Concepts {
		if concept == "" || concept != strings.TrimSpace(concept) {
			return fmt.Errorf("concepts[%d] must be non-empty and normalized", i)
		}
		key := strings.ToLower(concept)
		if _, exists := seen[key]; exists {
			return fmt.Errorf("duplicate concept %q", concept)
		}
		seen[key] = struct{}{}
	}
	if strings.TrimSpace(a.DeclaredMeaning) == "" {
		return fmt.Errorf("declared_meaning is required")
	}
	return nil
}

func validateRelativePath(path string) error {
	if path == "" || path != filepath.Clean(path) {
		return fmt.Errorf("must be a normalized relative path")
	}
	if filepath.IsAbs(path) || path == "." {
		return fmt.Errorf("must be a repository-relative file path")
	}
	for _, part := range strings.Split(filepath.ToSlash(path), "/") {
		if part == ".." || part == "" {
			return fmt.Errorf("must not escape the repository root")
		}
	}
	return nil
}
