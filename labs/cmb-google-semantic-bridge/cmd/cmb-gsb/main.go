package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/jupiter8nohate/cmb-google-semantic-bridge/internal/bridge"
)

const version = "0.3.0"

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
	case "publish":
		return publishCommand(args[1:], stdout)
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

	artifact, err := loadArtifact(*input)
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
	siteBase := fs.String("site-base", "", "optional HTTPS site base for sitemap discovery")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *input == "" || *output == "" {
		return errors.New("render requires -in and -out")
	}

	artifact, err := loadArtifact(*input)
	if err != nil {
		return err
	}

	if artifact.Provenance.SHA256 == "" && artifact.Body != "" {
		artifact.Provenance.SHA256 = bridge.SHA256Bytes([]byte(artifact.Body))
	}

	outputs, err := metadataOutputs(artifact, *siteBase)
	if err != nil {
		return err
	}
	if err := writeBundle(*output, artifact.ID, outputs); err != nil {
		return err
	}

	fmt.Fprintf(stdout, "rendered %s to %s\n", artifact.ID, *output)
	return nil
}

func publishCommand(args []string, stdout io.Writer) error {
	fs := flag.NewFlagSet("publish", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	input := fs.String("in", "", "artifact JSON file")
	sourcePath := fs.String("source", "", "human-authored source file")
	output := fs.String("out", "", "publication output directory")
	urlOverride := fs.String("url", "", "optional HTTPS canonical URL override")
	siteBase := fs.String("site-base", "", "optional HTTPS site base for sitemap discovery")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *input == "" || *sourcePath == "" || *output == "" {
		return errors.New("publish requires -in, -source, and -out")
	}

	artifact, err := loadArtifact(*input)
	if err != nil {
		return err
	}
	if strings.TrimSpace(*urlOverride) != "" {
		artifact.URL = strings.TrimSpace(*urlOverride)
	}

	source, err := os.ReadFile(*sourcePath)
	if err != nil {
		return fmt.Errorf("read source: %w", err)
	}
	artifact, err = bridge.BindSource(artifact, source)
	if err != nil {
		return fmt.Errorf("bind source: %w", err)
	}

	outputs, err := metadataOutputs(artifact, *siteBase)
	if err != nil {
		return err
	}
	page, err := bridge.PageHTML(artifact)
	if err != nil {
		return err
	}
	outputs["index.html"] = page
	outputs["site.css"] = bridge.SiteCSS()
	outputs["source.md"] = append([]byte(nil), source...)

	if err := writeBundle(*output, artifact.ID, outputs); err != nil {
		return err
	}

	fmt.Fprintf(
		stdout,
		"published %s to %s (%s)\n",
		artifact.ID,
		*output,
		artifact.Provenance.SHA256,
	)
	return nil
}

func metadataOutputs(artifact bridge.Artifact, siteBase string) (map[string][]byte, error) {
	jsonLD, err := bridge.ArticleJSONLD(artifact)
	if err != nil {
		return nil, err
	}
	semantic, err := bridge.CMBSemanticJSON(artifact)
	if err != nil {
		return nil, err
	}
	head, err := bridge.HeadBlock(artifact)
	if err != nil {
		return nil, err
	}
	sitemap, err := bridge.SitemapXML([]bridge.Artifact{artifact})
	if err != nil {
		return nil, err
	}
	if strings.TrimSpace(siteBase) == "" {
		siteBase, err = bridge.OriginURL(artifact.URL)
		if err != nil {
			return nil, err
		}
	}
	robots, err := bridge.RobotsTXT(siteBase)
	if err != nil {
		return nil, err
	}

	return map[string][]byte{
		"article.jsonld":    jsonLD,
		"cmb-semantic.json": semantic,
		"head.html":         head,
		"sitemap.xml":       sitemap,
		"robots.txt":        []byte(robots),
	}, nil
}

func writeBundle(outputDir, artifactID string, outputs map[string][]byte) error {
	if err := os.MkdirAll(outputDir, 0o755); err != nil {
		return fmt.Errorf("create output directory: %w", err)
	}

	names := make([]string, 0, len(outputs))
	for name := range outputs {
		names = append(names, name)
	}
	sort.Strings(names)

	for _, name := range names {
		path := filepath.Join(outputDir, name)
		if err := os.WriteFile(path, outputs[name], 0o644); err != nil {
			return fmt.Errorf("write %s: %w", name, err)
		}
	}

	manifest := struct {
		SchemaVersion string            `json:"schema_version"`
		ToolVersion   string            `json:"tool_version"`
		ArtifactID    string            `json:"artifact_id"`
		Files         map[string]string `json:"files_sha256"`
	}{
		SchemaVersion: "cmb-gsb.output-manifest.v1",
		ToolVersion:   version,
		ArtifactID:    artifactID,
		Files:         make(map[string]string, len(outputs)),
	}
	for _, name := range names {
		manifest.Files[name] = bridge.SHA256Bytes(outputs[name])
	}

	manifestJSON, err := json.MarshalIndent(manifest, "", "  ")
	if err != nil {
		return fmt.Errorf("encode output manifest: %w", err)
	}
	manifestJSON = append(manifestJSON, '\n')
	if err := os.WriteFile(filepath.Join(outputDir, "manifest.json"), manifestJSON, 0o644); err != nil {
		return fmt.Errorf("write manifest.json: %w", err)
	}
	return nil
}

func loadArtifact(path string) (bridge.Artifact, error) {
	file, err := os.Open(path)
	if err != nil {
		return bridge.Artifact{}, fmt.Errorf("open input: %w", err)
	}
	defer file.Close()

	artifact, err := bridge.DecodeArtifact(file)
	if err != nil {
		return bridge.Artifact{}, err
	}
	return artifact, nil
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
	fmt.Fprintln(w, "  cmb-gsb render -in artifact.json -out build/ [-site-base https://example.org/project/]")
	fmt.Fprintln(w, "  cmb-gsb publish -in artifact.json -source MANIFESTO.md -out site/ [-url https://example.org/work/] [-site-base https://example.org/project/]")
	fmt.Fprintln(w, "  cmb-gsb hash -file MANIFESTO.md")
}
