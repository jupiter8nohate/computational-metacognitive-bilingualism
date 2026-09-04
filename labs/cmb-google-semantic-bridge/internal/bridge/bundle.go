package bridge

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

type OutputManifest struct {
	SchemaVersion string            `json:"schema_version"`
	ToolVersion   string            `json:"tool_version"`
	ArtifactID    string            `json:"artifact_id"`
	Files         map[string]string `json:"files_sha256"`
}

func WriteBundleAtomic(outputDir, artifactID, toolVersion string, outputs map[string][]byte) error {
	if len(outputs) == 0 {
		return fmt.Errorf("publication outputs must not be empty")
	}
	cleanOutput := filepath.Clean(outputDir)
	base := filepath.Base(cleanOutput)
	if base == "." || base == string(filepath.Separator) || base == "" {
		return fmt.Errorf("unsafe output directory %q", outputDir)
	}

	parent := filepath.Dir(cleanOutput)
	if err := os.MkdirAll(parent, 0o755); err != nil {
		return fmt.Errorf("create output parent: %w", err)
	}

	stage, err := os.MkdirTemp(parent, "."+base+".stage-*")
	if err != nil {
		return fmt.Errorf("create publication stage: %w", err)
	}
	defer os.RemoveAll(stage)

	names := make([]string, 0, len(outputs))
	for name := range outputs {
		clean, err := safeBundlePath(name)
		if err != nil {
			return err
		}
		names = append(names, clean)
	}
	sort.Strings(names)

	manifest := OutputManifest{
		SchemaVersion: "cmb-gsb.output-manifest.v1",
		ToolVersion:   toolVersion,
		ArtifactID:    artifactID,
		Files:         make(map[string]string, len(outputs)),
	}
	for _, name := range names {
		path := filepath.Join(stage, filepath.FromSlash(name))
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			return fmt.Errorf("create output directory for %s: %w", name, err)
		}
		if err := writeSyncedFile(path, outputs[name], 0o644); err != nil {
			return fmt.Errorf("write %s: %w", name, err)
		}
		manifest.Files[name] = SHA256Bytes(outputs[name])
	}

	manifestJSON, err := json.MarshalIndent(manifest, "", "  ")
	if err != nil {
		return fmt.Errorf("encode output manifest: %w", err)
	}
	manifestJSON = append(manifestJSON, '\n')
	if err := writeSyncedFile(filepath.Join(stage, "manifest.json"), manifestJSON, 0o644); err != nil {
		return fmt.Errorf("write manifest.json: %w", err)
	}

	if err := replaceDirectory(stage, cleanOutput); err != nil {
		return err
	}
	return nil
}

func writeSyncedFile(path string, data []byte, mode os.FileMode) error {
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, mode)
	if err != nil {
		return err
	}
	ok := false
	defer func() {
		if !ok {
			_ = file.Close()
		}
	}()
	if _, err := file.Write(data); err != nil {
		return err
	}
	if err := file.Sync(); err != nil {
		return err
	}
	if err := file.Close(); err != nil {
		return err
	}
	ok = true
	return nil
}

func replaceDirectory(stage, destination string) error {
	info, err := os.Lstat(destination)
	if errors.Is(err, os.ErrNotExist) {
		if err := os.Rename(stage, destination); err != nil {
			return fmt.Errorf("activate publication: %w", err)
		}
		return nil
	}
	if err != nil {
		return fmt.Errorf("inspect publication destination: %w", err)
	}
	if info.Mode()&os.ModeSymlink != 0 {
		return fmt.Errorf("publication destination must not be a symbolic link")
	}
	if !info.IsDir() {
		return fmt.Errorf("publication destination must be a directory")
	}

	backup := stage + ".previous"
	if err := os.Rename(destination, backup); err != nil {
		return fmt.Errorf("stage previous publication: %w", err)
	}
	if err := os.Rename(stage, destination); err != nil {
		rollbackErr := os.Rename(backup, destination)
		if rollbackErr != nil {
			return fmt.Errorf("activate publication: %v; rollback failed: %w", err, rollbackErr)
		}
		return fmt.Errorf("activate publication: %w", err)
	}
	if err := os.RemoveAll(backup); err != nil {
		return fmt.Errorf("remove previous publication: %w", err)
	}
	return nil
}


func safeBundlePath(name string) (string, error) {
	if name == "" {
		return "", fmt.Errorf("unsafe output name %q", name)
	}
	slash := filepath.ToSlash(name)
	clean := filepath.ToSlash(filepath.Clean(slash))
	if clean != slash || clean == "." || strings.HasPrefix(clean, "/") {
		return "", fmt.Errorf("unsafe output name %q", name)
	}
	for _, part := range strings.Split(clean, "/") {
		if part == "" || part == "." || part == ".." {
			return "", fmt.Errorf("unsafe output name %q", name)
		}
	}
	if clean == "manifest.json" {
		return "", fmt.Errorf("manifest.json is reserved for the bundle manifest")
	}
	return clean, nil
}
