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
	instanceStatusReplicated   = "INSTANCE_REPLICATED_IN_VALIDATION"
	instanceStatusFailed       = "INSTANCE_NOT_REPLICATED_IN_VALIDATION"
	instanceStatusNotTestable  = "INSTANCE_NOT_TESTABLE_IN_VALIDATION"
	classStatusRecurred        = "CLASS_RECURRED_OUT_OF_SAMPLE"
	classStatusNotRecurred     = "CLASS_NOT_RECURRED_OUT_OF_SAMPLE"
)

type ValidationCorpusRef struct {
	CorpusID      string `json:"corpus_id"`
	CorpusVersion string `json:"corpus_version"`
	CorpusSHA256  string `json:"corpus_sha256"`
	RecordCount   int    `json:"record_count"`
}

type InstanceReplicationResult struct {
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

type IndependentValidationExample struct {
	SignatureID string   `json:"signature_id"`
	Words       []string `json:"words"`
	Values      []int    `json:"values"`
	Evidence    string   `json:"evidence"`
}

type ClassValidationResult struct {
	Type                       string                         `json:"type"`
	DiscoverySignatureCount    int                            `json:"discovery_signature_count"`
	ValidationSignatureCount   int                            `json:"validation_signature_count"`
	IndependentExampleCount    int                            `json:"independent_example_count"`
	Status                     string                         `json:"status"`
	IndependentExamples        []IndependentValidationExample `json:"independent_examples"`
}

type OutOfSampleValidationSummary struct {
	CandidateCount             int `json:"candidate_count"`
	InstanceTestableCount      int `json:"instance_testable_count"`
	InstanceReplicatedCount    int `json:"instance_replicated_count"`
	InstanceFailedCount        int `json:"instance_failed_count"`
	InstanceNotTestableCount   int `json:"instance_not_testable_count"`
	ClassHypothesisCount       int `json:"class_hypothesis_count"`
	ClassRecurredCount         int `json:"class_recurred_count"`
	ClassNotRecurredCount      int `json:"class_not_recurred_count"`
}

type OutOfSampleValidationReport struct {
	SchemaVersion        string                       `json:"schema_version"`
	Protocol             string                       `json:"protocol"`
	GematriaSystem       string                       `json:"gematria_system"`
	Discovery            ValidationCorpusRef          `json:"discovery"`
	Validation           ValidationCorpusRef          `json:"validation"`
	CandidateSetSHA256   string                       `json:"candidate_set_sha256"`
	HypothesisSetSHA256  string                       `json:"hypothesis_set_sha256"`
	Summary              OutOfSampleValidationSummary `json:"summary"`
	InstanceReplication []InstanceReplicationResult   `json:"instance_replication"`
	ClassValidation     []ClassValidationResult       `json:"class_validation"`
	Boundary             []string                     `json:"boundary"`
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
	validationByType := make(map[string][]Finding)
	for _, finding := range validationFindings {
		signatureID, err := findingSignatureID(canonicalFindingSignature(finding))
		if err != nil {
			return OutOfSampleValidationReport{}, err
		}
		validationBySignature[signatureID] = finding
		validationByType[finding.Type] = append(validationByType[finding.Type], finding)
	}

	validationWords := make(map[string]struct{}, len(validation.Records))
	for _, entry := range validation.Records {
		validationWords[entry.Word] = struct{}{}
	}

	discoverySignaturesByType := make(map[string]map[string]struct{})
	candidateSignatureIDs := make([]string, 0, len(discoveryFindings))
	typeHypotheses := make(map[string]struct{})
	instanceResults := make([]InstanceReplicationResult, 0, len(discoveryFindings))
	summary := OutOfSampleValidationSummary{
		CandidateCount: len(discoveryFindings),
	}

	for _, finding := range discoveryFindings {
		signatureID, err := findingSignatureID(canonicalFindingSignature(finding))
		if err != nil {
			return OutOfSampleValidationReport{}, err
		}
		candidateSignatureIDs = append(candidateSignatureIDs, signatureID)
		typeHypotheses[finding.Type] = struct{}{}
		if discoverySignaturesByType[finding.Type] == nil {
			discoverySignaturesByType[finding.Type] = make(map[string]struct{})
		}
		discoverySignaturesByType[finding.Type][signatureID] = struct{}{}

		requiredWords := requiredWordsForValidation(finding)
		missingWords := make([]string, 0)
		for _, word := range requiredWords {
			if _, ok := validationWords[word]; !ok {
				missingWords = append(missingWords, word)
			}
		}
		sort.Strings(missingWords)

		result := InstanceReplicationResult{
			SignatureID:       signatureID,
			Type:              finding.Type,
			Words:             append([]string(nil), finding.Words...),
			Values:            append([]int(nil), finding.Values...),
			DiscoveryEvidence: finding.Evidence,
			RequiredWords:     requiredWords,
			MissingWords:      missingWords,
		}

		if len(missingWords) > 0 {
			result.Status = instanceStatusNotTestable
			summary.InstanceNotTestableCount++
			instanceResults = append(instanceResults, result)
			continue
		}

		result.Testable = true
		summary.InstanceTestableCount++
		if matched, ok := validationBySignature[signatureID]; ok {
			result.Status = instanceStatusReplicated
			result.ValidationEvidence = matched.Evidence
			summary.InstanceReplicatedCount++
		} else {
			result.Status = instanceStatusFailed
			summary.InstanceFailedCount++
		}
		instanceResults = append(instanceResults, result)
	}

	sort.Slice(instanceResults, func(i, j int) bool {
		left := instanceResults[i]
		right := instanceResults[j]
		if instanceStatusRank(left.Status) != instanceStatusRank(right.Status) {
			return instanceStatusRank(left.Status) < instanceStatusRank(right.Status)
		}
		if left.Type != right.Type {
			return left.Type < right.Type
		}
		return left.SignatureID < right.SignatureID
	})

	classResults := make([]ClassValidationResult, 0, len(typeHypotheses))
	for kind := range typeHypotheses {
		discoverySet := discoverySignaturesByType[kind]
		examples := make([]IndependentValidationExample, 0)
		seenValidationSignatures := make(map[string]struct{})

		for _, finding := range validationByType[kind] {
			signatureID, err := findingSignatureID(canonicalFindingSignature(finding))
			if err != nil {
				return OutOfSampleValidationReport{}, err
			}
			seenValidationSignatures[signatureID] = struct{}{}
			if _, seenInDiscovery := discoverySet[signatureID]; seenInDiscovery {
				continue
			}
			examples = append(examples, IndependentValidationExample{
				SignatureID: signatureID,
				Words:       append([]string(nil), finding.Words...),
				Values:      append([]int(nil), finding.Values...),
				Evidence:    finding.Evidence,
			})
		}

		sort.Slice(examples, func(i, j int) bool {
			return examples[i].SignatureID < examples[j].SignatureID
		})

		status := classStatusNotRecurred
		if len(examples) > 0 {
			status = classStatusRecurred
			summary.ClassRecurredCount++
		} else {
			summary.ClassNotRecurredCount++
		}

		classResults = append(classResults, ClassValidationResult{
			Type:                     kind,
			DiscoverySignatureCount:  len(discoverySet),
			ValidationSignatureCount: len(seenValidationSignatures),
			IndependentExampleCount:  len(examples),
			Status:                   status,
			IndependentExamples:      examples,
		})
	}

	sort.Slice(classResults, func(i, j int) bool {
		if classResults[i].Status != classResults[j].Status {
			return classResults[i].Status < classResults[j].Status
		}
		return classResults[i].Type < classResults[j].Type
	})
	summary.ClassHypothesisCount = len(classResults)

	candidateSetSHA, err := stringSetDigest(candidateSignatureIDs)
	if err != nil {
		return OutOfSampleValidationReport{}, err
	}
	hypothesisTypes := make([]string, 0, len(typeHypotheses))
	for kind := range typeHypotheses {
		hypothesisTypes = append(hypothesisTypes, kind)
	}
	hypothesisSetSHA, err := stringSetDigest(hypothesisTypes)
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
		CandidateSetSHA256:  candidateSetSHA,
		HypothesisSetSHA256: hypothesisSetSHA,
		Summary:              summary,
		InstanceReplication: instanceResults,
		ClassValidation:     classResults,
		Boundary: []string{
			"DISCOVERY_SET != VALIDATION_SET",
			"DISCOVERY != CONFIRMATION",
			"INSTANCE_REPLICATION != INDEPENDENT_VALIDATION",
			"CLASS_RECURRED_OUT_OF_SAMPLE != TRUTH",
			"NOT_RECURRED != DISPROVEN",
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

func stringSetDigest(values []string) (string, error) {
	items := append([]string(nil), values...)
	sort.Strings(items)
	data, err := json.Marshal(items)
	if err != nil {
		return "", fmt.Errorf("marshal string set: %w", err)
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func instanceStatusRank(status string) int {
	switch status {
	case instanceStatusReplicated:
		return 0
	case instanceStatusFailed:
		return 1
	case instanceStatusNotTestable:
		return 2
	default:
		return 3
	}
}

func renderOutOfSampleGlitch(report OutOfSampleValidationReport) string {
	var b strings.Builder
	b.WriteString("𓁹 Err ⃝or⃟⃤://OUT_OF_SAMPLE_VALIDATION\n")
	fmt.Fprintf(&b, "DISCOVERY://%s@%s\n", report.Discovery.CorpusID, report.Discovery.CorpusVersion)
	fmt.Fprintf(&b, "VALIDATION://%s@%s\n", report.Validation.CorpusID, report.Validation.CorpusVersion)
	fmt.Fprintf(&b, "CANDIDATE_SET_SHA256://%s\n", report.CandidateSetSHA256)
	fmt.Fprintf(&b, "HYPOTHESIS_SET_SHA256://%s\n", report.HypothesisSetSHA256)
	fmt.Fprintf(&b, "CANDIDATES://%d\n", report.Summary.CandidateCount)
	fmt.Fprintf(&b, "INSTANCE_TESTABLE://%d\n", report.Summary.InstanceTestableCount)
	fmt.Fprintf(&b, "INSTANCE_REPLICATED://%d\n", report.Summary.InstanceReplicatedCount)
	fmt.Fprintf(&b, "INSTANCE_NOT_TESTABLE://%d\n", report.Summary.InstanceNotTestableCount)
	fmt.Fprintf(&b, "CLASS_HYPOTHESES://%d\n", report.Summary.ClassHypothesisCount)
	fmt.Fprintf(&b, "CLASS_RECURRED://%d\n\n", report.Summary.ClassRecurredCount)

	b.WriteString("𓂀 CLASS_VALIDATION\n")
	for _, result := range report.ClassValidation {
		fmt.Fprintf(&b, "TYPE://%s\n", result.Type)
		fmt.Fprintf(&b, "STATUS://%s\n", result.Status)
		fmt.Fprintf(&b, "INDEPENDENT_EXAMPLES://%d\n", result.IndependentExampleCount)
		for _, example := range result.IndependentExamples {
			fmt.Fprintf(
				&b,
				"  ꩜ %s | WORDS=%s | VALUES=%v\n",
				example.SignatureID,
				strings.Join(example.Words, " | "),
				example.Values,
			)
		}
		b.WriteString("CLASS_RECURRED_OUT_OF_SAMPLE != TRUTH\n\n")
	}

	b.WriteString("𓁹 INSTANCE_REPLICATION\n")
	for _, result := range report.InstanceReplication {
		fmt.Fprintf(&b, "STATUS://%s\n", result.Status)
		fmt.Fprintf(&b, "TYPE://%s\n", result.Type)
		fmt.Fprintf(&b, "WORDS://%s\n", strings.Join(result.Words, " | "))
		fmt.Fprintf(&b, "SIGNATURE://%s\n", result.SignatureID)
		if len(result.MissingWords) > 0 {
			fmt.Fprintf(&b, "MISSING_WORDS://%s\n", strings.Join(result.MissingWords, " | "))
		}
		b.WriteString("INSTANCE_REPLICATION != INDEPENDENT_VALIDATION\n\n")
	}

	b.WriteString("DISCOVERY_SET != VALIDATION_SET\n")
	b.WriteString("NOT_RECURRED != DISPROVEN\n")
	b.WriteString("NOT_TESTABLE != FAILED\n")
	b.WriteString("PATTERN != PROOF\n")
	b.WriteString("♡⃟ INTERPRETATION://HUMAN\n")
	return b.String()
}
