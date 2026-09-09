package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

const (
	validationStatusValidated   = "VALIDATED_OUT_OF_SAMPLE"
	validationStatusFailed      = "NOT_VALIDATED_OUT_OF_SAMPLE"
	validationStatusNotTestable = "NOT_TESTABLE_IN_VALIDATION"
)

type ValidationCorpusRef struct {
	CorpusID      string `json:"corpus_id"`
	CorpusVersion string `json:"corpus_version"`
	CorpusSHA256  string `json:"corpus_sha256"`
	RecordCount   int    `json:"record_count"`
}

type OutOfSampleValidationResult struct {
	SignatureID        string   `json:"signature_id"`
	Type               string   `json:"type"`
	Words              []string `json:"words"`
	Values             []int    `json:"values"`
	DiscoveryEvidence  string   `json:"discovery_evidence"`
	RequiredWords      []string `json:"required_words"`
	MissingWords       []string `json:"missing_words"`
	Testable           bool     `json:"testable"`
	Status             string   `json:"status"`
	ValidationEvidence string   `json:"validation_evidence,omitempty"`
}

type OutOfSampleValidationSummary struct {
	CandidateCount   int `json:"candidate_count"`
	TestableCount    int `json:"testable_count"`
	ValidatedCount   int `json:"validated_count"`
	FailedCount      int `json:"failed_count"`
	NotTestableCount int `json:"not_testable_count"`
}

type OutOfSampleValidationReport struct {
	SchemaVersion      string                       `json:"schema_version"`
	Protocol           string                       `json:"protocol"`
	GematriaSystem     string                       `json:"gematria_system"`
	Discovery          ValidationCorpusRef          `json:"discovery"`
	Validation         ValidationCorpusRef          `json:"validation"`
	CandidateSetSHA256 string                       `json:"candidate_set_sha256"`
	Summary            OutOfSampleValidationSummary `json:"summary"`
	Results            []OutOfSampleValidationResult `json:"results"`
	Boundary           []string                     `json:"boundary"`
}

func runOutOfSampleValidation(
	discovery Corpus,
	validation Corpus,
) (OutOfSampleValidationReport, error) {
	if err := validateCorpus(discovery); err != nil {
		return OutOfSampleValidationReport{}, fmt.Errorf("discovery corpus: %w", err)
	}
	if err := validateCorpus(validation); err != nil {
		return OutOfSampleValidationReport{}, fmt.Errorf("validation corpus: %w", err)
	}
	if discovery.GematriaSystem != validation.GematriaSystem {
		return OutOfSampleValidationReport{}, fmt.Errorf(
			"gematria systems differ: discovery=%q validation=%q",
			discovery.GematriaSystem,
			validation.GematriaSystem,
		)
	}

	discoverySHA, err := corpusDigest(discovery)
	if err != nil {
		return OutOfSampleValidationReport{}, err
	}
	validationSHA, err := corpusDigest(validation)
	if err != nil {
		return OutOfSampleValidationReport{}, err
	}
	if corpusRef(discovery) == corpusRef(validation) {
		return OutOfSampleValidationReport{}, fmt.Errorf(
			"discovery and validation corpus identities must differ: %s",
			corpusRef(discovery),
		)
	}
	if discoverySHA == validationSHA {
		return OutOfSampleValidationReport{}, fmt.Errorf(
			"discovery and validation corpus contents must differ",
		)
	}

	discoveryFindings := Analyze(discovery.Records)
	validationFindings := Analyze(validation.Records)

	validationBySignature := make(map[string]Finding, len(validationFindings))
	for _, finding := range validationFindings {
		signatureID, err := findingSignatureID(canonicalFindingSignature(finding))
		if err != nil {
			return OutOfSampleValidationReport{}, err
		}
		validationBySignature[signatureID] = finding
	}

	validationWords := make(map[string]struct{}, len(validation.Records))
	for _, entry := range validation.Records {
		validationWords[entry.Word] = struct{}{}
	}

	results := make([]OutOfSampleValidationResult, 0, len(discoveryFindings))
	signatureIDs := make([]string, 0, len(discoveryFindings))
	summary := OutOfSampleValidationSummary{
		CandidateCount: len(discoveryFindings),
	}

	for _, finding := range discoveryFindings {
		signatureID, err := findingSignatureID(canonicalFindingSignature(finding))
		if err != nil {
			return OutOfSampleValidationReport{}, err
		}
		signatureIDs = append(signatureIDs, signatureID)

		requiredWords := requiredWordsForValidation(finding)
		missingWords := make([]string, 0)
		for _, word := range requiredWords {
			if _, ok := validationWords[word]; !ok {
				missingWords = append(missingWords, word)
			}
		}
		sort.Strings(missingWords)

		result := OutOfSampleValidationResult{
			SignatureID:       signatureID,
			Type:              finding.Type,
			Words:             append([]string(nil), finding.Words...),
			Values:            append([]int(nil), finding.Values...),
			DiscoveryEvidence: finding.Evidence,
			RequiredWords:     requiredWords,
			MissingWords:      missingWords,
		}

		if len(missingWords) > 0 {
			result.Status = validationStatusNotTestable
			summary.NotTestableCount++
			results = append(results, result)
			continue
		}

		result.Testable = true
		summary.TestableCount++
		if matched, ok := validationBySignature[signatureID]; ok {
			result.Status = validationStatusValidated
			result.ValidationEvidence = matched.Evidence
			summary.ValidatedCount++
		} else {
			result.Status = validationStatusFailed
			summary.FailedCount++
		}
		results = append(results, result)
	}

	sort.Slice(results, func(i, j int) bool {
		left := results[i]
		right := results[j]
		if validationStatusRank(left.Status) != validationStatusRank(right.Status) {
			return validationStatusRank(left.Status) < validationStatusRank(right.Status)
		}
		if left.Type != right.Type {
			return left.Type < right.Type
		}
		return left.SignatureID < right.SignatureID
	})

	candidateSetSHA, err := candidateSetDigest(signatureIDs)
	if err != nil {
		return OutOfSampleValidationReport{}, err
	}

	return OutOfSampleValidationReport{
		SchemaVersion:  "gematria-glitch.out-of-sample.v1",
		Protocol:       "GEMATRIA-GLITCH-1",
		GematriaSystem: discovery.GematriaSystem,
		Discovery: ValidationCorpusRef{
			CorpusID:      discovery.CorpusID,
			CorpusVersion: discovery.Version,
			CorpusSHA256:  discoverySHA,
			RecordCount:   len(discovery.Records),
		},
		Validation: ValidationCorpusRef{
			CorpusID:      validation.CorpusID,
			CorpusVersion: validation.Version,
			CorpusSHA256:  validationSHA,
			RecordCount:   len(validation.Records),
		},
		CandidateSetSHA256: candidateSetSHA,
		Summary:            summary,
		Results:            results,
		Boundary: []string{
			"DISCOVERY_SET != VALIDATION_SET",
			"DISCOVERY != CONFIRMATION",
			"VALIDATED_OUT_OF_SAMPLE != TRUTH",
			"NOT_VALIDATED != DISPROVEN",
			"NOT_TESTABLE != FAILED",
			"VALIDATION_CORPUS != UNIVERSE",
			"PATTERN != PROOF",
		},
	}, nil
}

func requiredWordsForValidation(finding Finding) []string {
	limit := len(finding.Words)
	if finding.Type == "LINGUISTIC_PREFIX_DELTA" && limit > 2 {
		limit = 2
	}
	seen := make(map[string]struct{}, limit)
	out := make([]string, 0, limit)
	for _, word := range finding.Words[:limit] {
		if _, exists := seen[word]; exists {
			continue
		}
		seen[word] = struct{}{}
		out = append(out, word)
	}
	sort.Strings(out)
	return out
}

func candidateSetDigest(signatureIDs []string) (string, error) {
	ids := append([]string(nil), signatureIDs...)
	sort.Strings(ids)
	data, err := json.Marshal(ids)
	if err != nil {
		return "", fmt.Errorf("marshal candidate signature set: %w", err)
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func validationStatusRank(status string) int {
	switch status {
	case validationStatusValidated:
		return 0
	case validationStatusFailed:
		return 1
	case validationStatusNotTestable:
		return 2
	default:
		return 3
	}
}

func renderOutOfSampleGlitch(report OutOfSampleValidationReport) string {
	var b strings.Builder
	b.WriteString("𓁹 Err ⃝or⃟⃤://OUT_OF_SAMPLE_VALIDATION\n")
	fmt.Fprintf(
		&b,
		"DISCOVERY://%s@%s\n",
		report.Discovery.CorpusID,
		report.Discovery.CorpusVersion,
	)
	fmt.Fprintf(
		&b,
		"VALIDATION://%s@%s\n",
		report.Validation.CorpusID,
		report.Validation.CorpusVersion,
	)
	fmt.Fprintf(&b, "CANDIDATE_SET_SHA256://%s\n", report.CandidateSetSHA256)
	fmt.Fprintf(&b, "CANDIDATES://%d\n", report.Summary.CandidateCount)
	fmt.Fprintf(&b, "TESTABLE://%d\n", report.Summary.TestableCount)
	fmt.Fprintf(&b, "VALIDATED://%d\n", report.Summary.ValidatedCount)
	fmt.Fprintf(&b, "FAILED://%d\n", report.Summary.FailedCount)
	fmt.Fprintf(&b, "NOT_TESTABLE://%d\n\n", report.Summary.NotTestableCount)

	for _, result := range report.Results {
		fmt.Fprintf(&b, "꩜ STATUS://%s\n", result.Status)
		fmt.Fprintf(&b, "TYPE://%s\n", result.Type)
		fmt.Fprintf(&b, "WORDS://%s\n", strings.Join(result.Words, " | "))
		fmt.Fprintf(&b, "VALUES://%v\n", result.Values)
		fmt.Fprintf(&b, "SIGNATURE://%s\n", result.SignatureID)
		if len(result.MissingWords) > 0 {
			fmt.Fprintf(&b, "MISSING_WORDS://%s\n", strings.Join(result.MissingWords, " | "))
		}
		if result.ValidationEvidence != "" {
			fmt.Fprintf(&b, "VALIDATION_EVIDENCE://%s\n", result.ValidationEvidence)
		}
		b.WriteString("VALIDATED_OUT_OF_SAMPLE != TRUTH\n\n")
	}

	b.WriteString("DISCOVERY_SET != VALIDATION_SET\n")
	b.WriteString("NOT_VALIDATED != DISPROVEN\n")
	b.WriteString("NOT_TESTABLE != FAILED\n")
	b.WriteString("PATTERN != PROOF\n")
	b.WriteString("♡⃟ INTERPRETATION://HUMAN\n")
	return b.String()
}
