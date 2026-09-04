package bridge

import (
	"errors"
	"fmt"
	"net/url"
	"strings"
	"time"
)

const (
	ArtifactSchemaVersion = "cmb-gsb.artifact.v1"
	HumanAuthority        = "HUMAN_FINAL"
)

type Author struct {
	Name string `json:"name"`
	URL  string `json:"url,omitempty"`
}

type Provenance struct {
	SHA256         string `json:"sha256,omitempty"`
	Repository     string `json:"repository,omitempty"`
	Commit         string `json:"commit,omitempty"`
	HumanAuthored  bool   `json:"human_authored"`
	HumanAuthority string `json:"human_authority"`
}

type Artifact struct {
	SchemaVersion string     `json:"schema_version"`
	ID            string     `json:"id"`
	URL           string     `json:"url"`
	Title         string     `json:"title"`
	Description   string     `json:"description"`
	Author        Author     `json:"author"`
	DatePublished time.Time  `json:"date_published"`
	DateModified  time.Time  `json:"date_modified"`
	Language      string     `json:"language"`
	Keywords      []string   `json:"keywords,omitempty"`
	Body          string     `json:"body,omitempty"`
	Provenance    Provenance `json:"provenance"`
}

func (a Artifact) Validate() error {
	if a.SchemaVersion != ArtifactSchemaVersion {
		return fmt.Errorf("schema_version must equal %q", ArtifactSchemaVersion)
	}
	if strings.TrimSpace(a.ID) == "" {
		return errors.New("id is required")
	}
	if err := validateHTTPSURL("url", a.URL); err != nil {
		return err
	}
	if strings.TrimSpace(a.Title) == "" {
		return errors.New("title is required")
	}
	if strings.TrimSpace(a.Description) == "" {
		return errors.New("description is required")
	}
	if strings.TrimSpace(a.Author.Name) == "" {
		return errors.New("author.name is required")
	}
	if a.Author.URL != "" {
		if err := validateHTTPSURL("author.url", a.Author.URL); err != nil {
			return err
		}
	}
	if a.DatePublished.IsZero() {
		return errors.New("date_published is required")
	}
	if a.DateModified.IsZero() {
		return errors.New("date_modified is required")
	}
	if a.DateModified.Before(a.DatePublished) {
		return errors.New("date_modified cannot be before date_published")
	}
	if strings.TrimSpace(a.Language) == "" {
		return errors.New("language is required")
	}
	if a.Provenance.HumanAuthority != HumanAuthority {
		return fmt.Errorf("provenance.human_authority must equal %q", HumanAuthority)
	}
	if !a.Provenance.HumanAuthored {
		return errors.New("this bridge only emits human-authored CMB artifacts")
	}
	if a.Provenance.SHA256 != "" && !validSHA256(a.Provenance.SHA256) {
		return errors.New("provenance.sha256 must be 64 lowercase hexadecimal characters")
	}
	return nil
}

func validateHTTPSURL(field, raw string) error {
	parsed, err := url.Parse(raw)
	if err != nil {
		return fmt.Errorf("%s must be a valid URL: %w", field, err)
	}
	if parsed.Scheme != "https" || parsed.Host == "" {
		return fmt.Errorf("%s must be an absolute https URL", field)
	}
	if parsed.User != nil {
		return fmt.Errorf("%s must not contain userinfo", field)
	}
	return nil
}

func validSHA256(value string) bool {
	if len(value) != 64 {
		return false
	}
	for _, r := range value {
		if !((r >= '0' && r <= '9') || (r >= 'a' && r <= 'f')) {
			return false
		}
	}
	return true
}
