package bridge

import (
	"encoding/json"
	"fmt"
	"strings"
)

type personLD struct {
	Type string `json:"@type"`
	Name string `json:"name"`
	URL  string `json:"url,omitempty"`
}

type propertyValueLD struct {
	Type       string `json:"@type"`
	Name       string `json:"name"`
	Value      any    `json:"value"`
	PropertyID string `json:"propertyID,omitempty"`
}

type articleLD struct {
	Context          string            `json:"@context"`
	Type             string            `json:"@type"`
	ID               string            `json:"@id"`
	Headline         string            `json:"headline"`
	Description      string            `json:"description"`
	URL              string            `json:"url"`
	MainEntityOfPage string            `json:"mainEntityOfPage"`
	InLanguage       string            `json:"inLanguage"`
	DatePublished    string            `json:"datePublished"`
	DateModified     string            `json:"dateModified"`
	Author           personLD          `json:"author"`
	Keywords         []string          `json:"keywords,omitempty"`
	ArticleBody      string            `json:"articleBody,omitempty"`
	Identifier       []propertyValueLD `json:"identifier,omitempty"`
}

func ArticleJSONLD(a Artifact) ([]byte, error) {
	if err := a.Validate(); err != nil {
		return nil, err
	}

	identifiers := []propertyValueLD{
		{
			Type:       "PropertyValue",
			Name:       "CMB Artifact ID",
			Value:      a.ID,
			PropertyID: "cmb:artifact-id",
		},
	}
	if a.Provenance.SHA256 != "" {
		identifiers = append(identifiers, propertyValueLD{
			Type:       "PropertyValue",
			Name:       "SHA-256",
			Value:      a.Provenance.SHA256,
			PropertyID: "sha256",
		})
	}

	document := articleLD{
		Context:          "https://schema.org",
		Type:             "Article",
		ID:               a.URL + "#article",
		Headline:         a.Title,
		Description:      a.Description,
		URL:              a.URL,
		MainEntityOfPage: a.URL,
		InLanguage:       a.Language,
		DatePublished:    a.DatePublished.Format("2006-01-02T15:04:05Z07:00"),
		DateModified:     a.DateModified.Format("2006-01-02T15:04:05Z07:00"),
		Author: personLD{
			Type: "Person",
			Name: a.Author.Name,
			URL:  a.Author.URL,
		},
		Keywords:    cleanStrings(a.Keywords),
		ArticleBody: a.Body,
		Identifier:  identifiers,
	}

	encoded, err := json.MarshalIndent(document, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("encode JSON-LD: %w", err)
	}
	return encoded, nil
}

func cleanStrings(values []string) []string {
	seen := make(map[string]struct{}, len(values))
	out := make([]string, 0, len(values))
	for _, value := range values {
		value = strings.TrimSpace(value)
		if value == "" {
			continue
		}
		key := strings.ToLower(value)
		if _, exists := seen[key]; exists {
			continue
		}
		seen[key] = struct{}{}
		out = append(out, value)
	}
	return out
}
