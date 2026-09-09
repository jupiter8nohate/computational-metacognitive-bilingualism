package main

import (
	"encoding/json"
	"testing"
)

func TestOutOfSampleValidationDeterminism(t *testing.T) {
	discovery := demoCorpusEnvelope()
	validation, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	first, err := runOutOfSampleValidation(discovery, validation)
	if err != nil {
		t.Fatal(err)
	}
	second, err := runOutOfSampleValidation(discovery, validation)
	if err != nil {
		t.Fatal(err)
	}

	firstJSON, err := json.Marshal(first)
	if err != nil {
		t.Fatal(err)
	}
	secondJSON, err := json.Marshal(second)
	if err != nil {
		t.Fatal(err)
	}
	if string(firstJSON) != string(secondJSON) {
		t.Fatal("out-of-sample validation must be deterministic")
	}
}

func TestOutOfSampleSeparatesInstanceReplicationFromClassValidation(t *testing.T) {
	discovery := demoCorpusEnvelope()
	validation, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := runOutOfSampleValidation(discovery, validation)
	if err != nil {
		t.Fatal(err)
	}

	collision := findInstanceValidation(report, "EXACT_COLLISION", "נחש", "משיח")
	if collision == nil {
		t.Fatal("expected exact collision instance")
	}
	if collision.Status != instanceStatusReplicated {
		t.Fatalf("collision status = %q, want %q", collision.Status, instanceStatusReplicated)
	}

	class := findClassValidation(report, "EXACT_COLLISION")
	if class == nil {
		t.Fatal("expected exact collision class validation")
	}
	if class.Status != classStatusNotRecurred {
		t.Fatalf(
			"same repeated collision must not count as independent class recurrence: %q",
			class.Status,
		)
	}
	if class.IndependentExampleCount != 0 {
		t.Fatalf("exact collision independent examples = %d, want 0", class.IndependentExampleCount)
	}
}

func TestOutOfSampleFindsIndependentClassRecurrence(t *testing.T) {
	discovery := demoCorpusEnvelope()
	validation, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := runOutOfSampleValidation(discovery, validation)
	if err != nil {
		t.Fatal(err)
	}

	digitalRoot := findClassValidation(report, "DIGITAL_ROOT")
	if digitalRoot == nil {
		t.Fatal("expected DIGITAL_ROOT class validation")
	}
	if digitalRoot.Status != classStatusRecurred {
		t.Fatalf("digital root class status = %q, want recurrence", digitalRoot.Status)
	}
	if digitalRoot.IndependentExampleCount == 0 {
		t.Fatal("digital root should have independent validation examples on new words")
	}

	palindrome := findClassValidation(report, "PALINDROME")
	if palindrome == nil {
		t.Fatal("expected PALINDROME class validation")
	}
	if palindrome.Status != classStatusNotRecurred {
		t.Fatalf("palindrome class status = %q, want not recurred", palindrome.Status)
	}
}

func TestOutOfSampleMarksMissingVocabularyNotTestable(t *testing.T) {
	discovery := demoCorpusEnvelope()
	validation, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := runOutOfSampleValidation(discovery, validation)
	if err != nil {
		t.Fatal(err)
	}

	prefix := findInstanceValidation(report, "LINGUISTIC_PREFIX_DELTA", "נחש", "הנחש")
	if prefix == nil {
		t.Fatal("expected prefix-delta instance")
	}
	if prefix.Status != instanceStatusNotTestable {
		t.Fatalf("prefix status = %q, want not testable", prefix.Status)
	}
	if prefix.Testable {
		t.Fatal("missing validation vocabulary must not be marked testable")
	}
	if !containsString(prefix.MissingWords, "הנחש") {
		t.Fatalf("missing words = %v, want הנחש", prefix.MissingWords)
	}
}

func TestOutOfSampleRejectsSameCorpusIdentity(t *testing.T) {
	corpus := demoCorpusEnvelope()
	if _, err := runOutOfSampleValidation(corpus, corpus); err == nil {
		t.Fatal("same discovery and validation corpus identity must be rejected")
	}
}

func TestOutOfSampleRejectsRelabeledDuplicateSample(t *testing.T) {
	discovery := demoCorpusEnvelope()
	validation := demoCorpusEnvelope()
	validation.CorpusID = "cmb.gematria.relabel"
	validation.Version = "99.0.0"

	if _, err := runOutOfSampleValidation(discovery, validation); err == nil {
		t.Fatal("same sample contents under different metadata must be rejected")
	}
}

func TestOutOfSampleSampleDigestsDiffer(t *testing.T) {
	discovery := demoCorpusEnvelope()
	validation, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := runOutOfSampleValidation(discovery, validation)
	if err != nil {
		t.Fatal(err)
	}
	if report.Discovery.SampleSHA256 == report.Validation.SampleSHA256 {
		t.Fatal("discovery and validation sample digests must differ")
	}
	if len(report.Discovery.SampleSHA256) != 64 || len(report.Validation.SampleSHA256) != 64 {
		t.Fatal("sample digests must be SHA-256 hex")
	}
}

func TestOutOfSampleLocksCandidateAndHypothesisSets(t *testing.T) {
	discovery := demoCorpusEnvelope()
	validation, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := runOutOfSampleValidation(discovery, validation)
	if err != nil {
		t.Fatal(err)
	}
	if len(report.CandidateSetSHA256) != 64 {
		t.Fatalf("candidate set digest length = %d", len(report.CandidateSetSHA256))
	}
	if len(report.HypothesisSetSHA256) != 64 {
		t.Fatalf("hypothesis set digest length = %d", len(report.HypothesisSetSHA256))
	}
	if report.Summary.CandidateCount != len(report.InstanceReplication) {
		t.Fatalf(
			"candidate count = %d, instance results = %d",
			report.Summary.CandidateCount,
			len(report.InstanceReplication),
		)
	}
	if report.Summary.ClassHypothesisCount != len(report.ClassValidation) {
		t.Fatalf(
			"class hypothesis count = %d, class results = %d",
			report.Summary.ClassHypothesisCount,
			len(report.ClassValidation),
		)
	}
}

func TestOutOfSampleBoundaries(t *testing.T) {
	discovery := demoCorpusEnvelope()
	validation, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := runOutOfSampleValidation(discovery, validation)
	if err != nil {
		t.Fatal(err)
	}

	for _, boundary := range []string{
		"DISCOVERY_SET != VALIDATION_SET",
		"DISCOVERY != CONFIRMATION",
		"INSTANCE_REPLICATION != INDEPENDENT_VALIDATION",
		"CLASS_RECURRED_OUT_OF_SAMPLE != TRUTH",
		"NOT_RECURRED != DISPROVEN",
		"NOT_TESTABLE != FAILED",
		"VALIDATION_CORPUS != UNIVERSE",
		"PATTERN != PROOF",
	} {
		if !containsString(report.Boundary, boundary) {
			t.Errorf("missing validation boundary %q", boundary)
		}
	}
}

func findInstanceValidation(
	report OutOfSampleValidationReport,
	kind string,
	words ...string,
) *InstanceReplicationResult {
	for i := range report.InstanceReplication {
		result := &report.InstanceReplication[i]
		if result.Type != kind {
			continue
		}
		all := true
		for _, word := range words {
			if !containsString(result.Words, word) {
				all = false
				break
			}
		}
		if all {
			return result
		}
	}
	return nil
}

func findClassValidation(
	report OutOfSampleValidationReport,
	kind string,
) *ClassValidationResult {
	for i := range report.ClassValidation {
		if report.ClassValidation[i].Type == kind {
			return &report.ClassValidation[i]
		}
	}
	return nil
}
