package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/jupiter8nohate/cmb-google-semantic-bridge/internal/bridge"
	"github.com/jupiter8nohate/cmb-google-semantic-bridge/internal/canon"
	"github.com/jupiter8nohate/cmb-google-semantic-bridge/internal/catalog"
)

const (
	version            = "0.5.0"
	defaultCanonPath   = "../../library/canon.json"
	defaultCatalogPath = "../../library/catalog.json"
	defaultRepoRoot    = "../.."
)

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
	case "publish-canon":
		return publishCanonCommand(args[1:], stdout)
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
	canonPath := fs.String("canon", defaultCanonPath, "CMB canon JSON file")
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
	loadedCanon, semantics, err := loadCanonSemantics(*canonPath)
	if err != nil {
		return err
	}

	outputs, err := metadataOutputs(artifact, *siteBase, semantics)
	if err != nil {
		return err
	}
	outputs["cmb-canon.json"] = append([]byte(nil), loadedCanon.Bytes...)

	if err := bridge.WriteBundleAtomic(*output, artifact.ID, version, outputs); err != nil {
		return err
	}

	fmt.Fprintf(
		stdout,
		"rendered %s to %s canon=%s\n",
		artifact.ID,
		*output,
		loadedCanon.SHA256,
	)
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
	canonPath := fs.String("canon", defaultCanonPath, "CMB canon JSON file")
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

	source, err := bridge.ReadUTF8Source(*sourcePath)
	if err != nil {
		return fmt.Errorf("read source: %w", err)
	}
	artifact, err = bridge.BindSource(artifact, source)
	if err != nil {
		return fmt.Errorf("bind source: %w", err)
	}

	loadedCanon, semantics, err := loadCanonSemantics(*canonPath)
	if err != nil {
		return err
	}
	outputs, err := metadataOutputs(artifact, *siteBase, semantics)
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
	outputs["cmb-canon.json"] = append([]byte(nil), loadedCanon.Bytes...)

	if err := bridge.WriteBundleAtomic(*output, artifact.ID, version, outputs); err != nil {
		return err
	}

	fmt.Fprintf(
		stdout,
		"published %s to %s source=%s canon=%s\n",
		artifact.ID,
		*output,
		artifact.Provenance.SHA256,
		loadedCanon.SHA256,
	)
	return nil
}

func publishCanonCommand(args []string, stdout io.Writer) error {
	fs := flag.NewFlagSet("publish-canon", flag.ContinueOnError)
	fs.SetOutput(io.Discard)
	root := fs.String("root", defaultRepoRoot, "repository root containing catalog-declared source files")
	canonPath := fs.String("canon", defaultCanonPath, "CMB canon JSON file")
	catalogPath := fs.String("catalog", defaultCatalogPath, "CMB digital-library catalog JSON file")
	output := fs.String("out", "", "publication output directory")
	baseURL := fs.String("base-url", "", "absolute HTTPS base URL for the published library")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *output == "" || *baseURL == "" {
		return errors.New("publish-canon requires -out and -base-url")
	}

	loadedCanon, semantics, err := loadCanonSemantics(*canonPath)
	if err != nil {
		return err
	}
	loadedCatalog, err := catalog.LoadFile(*catalogPath)
	if err != nil {
		return fmt.Errorf("load catalog: %w", err)
	}

	outputs, index, err := bridge.BuildCanonLibrary(bridge.CanonLibraryInput{
		RepositoryRoot: *root,
		BaseURL:        *baseURL,
		CanonBytes:     loadedCanon.Bytes,
		Canon:          semantics,
		CatalogBytes:   loadedCatalog.Bytes,
		CatalogSHA256:  loadedCatalog.SHA256,
		Catalog:        loadedCatalog.Document,
	})
	if err != nil {
		return err
	}
	if err := bridge.WriteBundleAtomic(*output, "cmb-canon-library", version, outputs); err != nil {
		return err
	}

	fmt.Fprintf(
		stdout,
		"published-canon artifacts=%d out=%s canon=%s catalog=%s\n",
		len(index.Artifacts),
		*output,
		loadedCanon.SHA256,
		loadedCatalog.SHA256,
	)
	return nil
}

func metadataOutputs(
	artifact bridge.Artifact,
	siteBase string,
	semantics bridge.CanonSemantics,
) (map[string][]byte, error) {
	jsonLD, err := bridge.ArticleJSONLD(artifact)
	if err != nil {
		return nil, err
	}
	semantic, err := bridge.CMBSemanticJSON(artifact, semantics)
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

func loadCanonSemantics(path string) (canon.Loaded, bridge.CanonSemantics, error) {
	loaded, err := canon.LoadFile(path)
	if err != nil {
		return canon.Loaded{}, bridge.CanonSemantics{}, fmt.Errorf("load canon: %w", err)
	}
	semantics := bridge.CanonSemantics{
		SchemaVersion: loaded.Document.SchemaVersion,
		SHA256:        loaded.SHA256,
		RootInvariant: loaded.Document.RootInvariant,
		Invariants:    append([]string(nil), loaded.Document.Invariants...),
	}
	if err := semantics.Validate(); err != nil {
		return canon.Loaded{}, bridge.CanonSemantics{}, fmt.Errorf("validate canon semantics: %w", err)
	}
	return loaded, semantics, nil
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
	data, err := bridge.ReadRegularFile(*input, bridge.MaxHashBytes)
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
	fmt.Fprintln(w, "  cmb-gsb render -in artifact.json -out build/ [-canon ../../library/canon.json] [-site-base https://example.org/project/]")
	fmt.Fprintln(w, "  cmb-gsb publish -in artifact.json -source MANIFESTO.md -out public/ [-canon ../../library/canon.json] [-url https://example.org/cmb/] [-site-base https://example.org/project/]")
	fmt.Fprintln(w, "  cmb-gsb publish-canon -out public/ -base-url https://example.org/cmb/ [-root ../..] [-canon ../../library/canon.json] [-catalog ../../library/catalog.json]")
	fmt.Fprintln(w, "  cmb-gsb hash -file MANIFESTO.md")
}
