package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"github.com/jupiter8nohate/cmb-google-semantic-bridge/internal/bridge"
)

const version = "0.1.0"

func main() {
	if err := run(os.Args[1:], os.Stdout, os.Stderr); err != nil {
		fmt.Fprintln(os.Stderr, "cmb-gsb:", err)
		os.Exit(1)
	}
}

func run(args []string, stdout, stderr io.Writer) error {
	if len(args) == 0 {
		printUsage(stderr)
		return errors.New("command required")
	}

	switch args[0] {
	case "version":
		fmt.Fprintln(stdout, version)
		return nil
	case "validate":
		return validateCommand(args[1:], stdout)
	case "render":
		return renderCommand(args[1:], stdout)
	case "hash":
		return hashCommand(args[1:], stdout)
	case "help", "-h", "--help":
		printUsage(stdout)
		return nil
	default:
		printUsage(stderr)
		return fmt.Errorf("unknown command %q", args[0])
	}
}

func validateCommand(args []string, stdout io.Writer) error {
	fs := flag.NewFlagSet("validate", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	input := fs.String("in", "", "artifact JSON file")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *input == "" {
		return errors.New("validate requires -in")
	}

	file, err := os.Open(*input)
	if err != nil {
		return fmt.Errorf("open input: %w", err)
	}
	defer file.Close()

	artifact, err := bridge.DecodeArtifact(file)
	if err != nil {
		return err
	}
	fmt.Fprintf(stdout, "valid %s %s\n", artifact.SchemaVersion, artifact.ID)
	return nil
}

func renderCommand(args []string, stdout io.Writer) error {
	fs := flag.NewFlagSet("render", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	input := fs.String("in", "", "artifact JSON file")
	output := fs.String("out", "", "output directory")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *input == "" || *output == "" {
		return errors.New("render requires -in and -out")
	}

	file, err := os.Open(*input)
	if err != nil {
		return fmt.Errorf("open input: %w", err)
	}
	defer file.Close()

	artifact, err := bridge.DecodeArtifact(file)
	if err != nil {
		return err
	}

	if artifact.Provenance.SHA256 == "" && artifact.Body != "" {
		artifact.Provenance.SHA256 = bridge.SHA256Bytes([]byte(artifact.Body))
	}

	jsonLD, err := bridge.ArticleJSONLD(artifact)
	if err != nil {
		return err
	}
	semantic, err := bridge.CMBSemanticJSON(artifact)
	if err != nil {
		return err
	}
	head, err := bridge.HeadBlock(artifact)
	if err != nil {
		return err
	}
	sitemap, err := bridge.SitemapXML([]bridge.Artifact{artifact})
	if err != nil {
		return err
	}
	robots, err := bridge.RobotsTXT(artifact.URL)
	if err != nil {
		return err
	}

	if err := os.MkdirAll(*output, 0o755); err != nil {
		return fmt.Errorf("create output directory: %w", err)
	}

	outputs := map[string][]byte{
		"article.jsonld":    jsonLD,
		"cmb-semantic.json": semantic,
		"head.html":         head,
		"sitemap.xml":       sitemap,
		"robots.txt":        []byte(robots),
	}
	for name, data := range outputs {
		path := filepath.Join(*output, name)
		if err := os.WriteFile(path, data, 0o644); err != nil {
			return fmt.Errorf("write %s: %w", name, err)
		}
	}

	manifest := struct {
		ToolVersion string            `json:"tool_version"`
		ArtifactID  string            `json:"artifact_id"`
		Files       map[string]string `json:"files_sha256"`
	}{
		ToolVersion: version,
		ArtifactID:  artifact.ID,
		Files:       make(map[string]string, len(outputs)),
	}
	for name, data := range outputs {
		manifest.Files[name] = bridge.SHA256Bytes(data)
	}
	manifestJSON, err := json.MarshalIndent(manifest, "", "  ")
	if err != nil {
		return fmt.Errorf("encode output manifest: %w", err)
	}
	manifestJSON = append(manifestJSON, '\n')
	if err := os.WriteFile(filepath.Join(*output, "manifest.json"), manifestJSON, 0o644); err != nil {
		return fmt.Errorf("write manifest.json: %w", err)
	}

	fmt.Fprintf(stdout, "rendered %s to %s\n", artifact.ID, *output)
	return nil
}

func hashCommand(args []string, stdout io.Writer) error {
	fs := flag.NewFlagSet("hash", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	input := fs.String("file", "", "file to hash")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *input == "" {
		return errors.New("hash requires -file")
	}
	data, err := os.ReadFile(*input)
	if err != nil {
		return fmt.Errorf("read file: %w", err)
	}
	fmt.Fprintln(stdout, bridge.SHA256Bytes(data))
	return nil
}

func printUsage(w io.Writer) {
	fmt.Fprintln(w, "CMB Google Semantic Bridge")
	fmt.Fprintln(w, "")
	fmt.Fprintln(w, "Usage:")
	fmt.Fprintln(w, "  cmb-gsb version")
	fmt.Fprintln(w, "  cmb-gsb validate -in artifact.json")
	fmt.Fprintln(w, "  cmb-gsb render -in artifact.json -out build/")
	fmt.Fprintln(w, "  cmb-gsb hash -file MANIFESTO.md")
}
