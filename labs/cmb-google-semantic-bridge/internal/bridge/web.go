package bridge

import (
	"bytes"
	"encoding/xml"
	"fmt"
	"html/template"
	"strings"
	"time"
)

type sitemapURL struct {
	Loc     string `xml:"loc"`
	LastMod string `xml:"lastmod,omitempty"`
}

type sitemapDocument struct {
	XMLName xml.Name     `xml:"urlset"`
	Xmlns   string       `xml:"xmlns,attr"`
	URLs    []sitemapURL `xml:"url"`
}

func CanonicalLink(rawURL string) (string, error) {
	if err := validateHTTPSURL("canonical URL", rawURL); err != nil {
		return "", err
	}
	return `<link rel="canonical" href="` + template.HTMLEscapeString(rawURL) + `">`, nil
}

func RobotsTXT(siteBaseURL string) (string, error) {
	base, err := NormalizeBaseURL(siteBaseURL)
	if err != nil {
		return "", err
	}
	return "User-agent: *\nAllow: /\n\nSitemap: " + base + "/sitemap.xml\n", nil
}

func OriginURL(raw string) (string, error) {
	parsed, err := parseHTTPSURL("URL", raw)
	if err != nil {
		return "", err
	}
	return parsed.Scheme + "://" + parsed.Host, nil
}

func SitemapXML(artifacts []Artifact) ([]byte, error) {
	if len(artifacts) == 0 {
		return nil, fmt.Errorf("at least one artifact is required")
	}

	seen := make(map[string]struct{}, len(artifacts))
	urls := make([]sitemapURL, 0, len(artifacts))
	for _, artifact := range artifacts {
		if err := artifact.Validate(); err != nil {
			return nil, fmt.Errorf("artifact %q: %w", artifact.ID, err)
		}
		if _, exists := seen[artifact.URL]; exists {
			return nil, fmt.Errorf("duplicate sitemap URL %q", artifact.URL)
		}
		seen[artifact.URL] = struct{}{}
		urls = append(urls, sitemapURL{
			Loc:     artifact.URL,
			LastMod: artifact.DateModified.UTC().Format(time.DateOnly),
		})
	}

	document := sitemapDocument{
		Xmlns: "http://www.sitemaps.org/schemas/sitemap/0.9",
		URLs:  urls,
	}
	body, err := xml.MarshalIndent(document, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("encode sitemap: %w", err)
	}
	return append([]byte(xml.Header), append(body, '\n')...), nil
}

func HeadBlock(a Artifact) ([]byte, error) {
	jsonLD, err := ArticleJSONLD(a)
	if err != nil {
		return nil, err
	}
	canonical, err := CanonicalLink(a.URL)
	if err != nil {
		return nil, err
	}

	var out bytes.Buffer
	out.WriteString(canonical)
	out.WriteByte('\n')
	out.WriteString(`<script type="application/ld+json">`)
	out.WriteByte('\n')
	out.Write(jsonLD)
	out.WriteByte('\n')
	out.WriteString(`</script>`)
	out.WriteByte('\n')
	return out.Bytes(), nil
}

func NormalizeBaseURL(raw string) (string, error) {
	parsed, err := parseHTTPSURL("base URL", raw)
	if err != nil {
		return "", err
	}
	parsed.RawQuery = ""
	parsed.Path = strings.TrimRight(parsed.Path, "/")
	return parsed.String(), nil
}
