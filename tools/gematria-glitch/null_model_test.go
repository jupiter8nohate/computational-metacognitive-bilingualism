package main

import (
	"encoding/json"
	"sort"
	"testing"
)

func TestNullModelDeterminism(t *testing.T) {
	corpus := demoCorpusEnvelope()

	first, err := runNullModel(corpus, 5000, 369)
	if err != nil {
		t.Fatal(err)
	}
	second, err := runNullModel(corpus, 5000, 369)
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
		t.Fatal("null-model output must be deterministic for the same corpus, seed, and simulation count")
	}
}

func TestPermutationPreservesExactValueMultiset(t *testing.T) {
	corpus := demoCorpusEnvelope()
	original := make([]int, len(corpus.Records))
	for i, entry := range corpus.Records {
		original[i] = Gematria(entry.Word)
	}
	permuted := append([]int(nil), original...)

	rng := &splitMix64{state: 369}
	fisherYates(permuted, rng)

	sort.Ints(original)
	sort.Ints(permuted)

	if len(original) != len(permuted) {
		t.Fatalf("value multiset lengths differ: %d != %d", len(original), len(permuted))
	}
	for i := range original {
		if original[i] != permuted[i] {
			t.Fatalf("value multiset changed at index %d: %d != %d", i, original[i], permuted[i])
		}
	}
}

func TestNullModelCollisionIsNotGuaranteed(t *testing.T) {
	report, err := runNullModel(demoCorpusEnvelope(), 10000, 369)
	if err != nil {
		t.Fatal(err)
	}

	collision := findNullFinding(report, "EXACT_COLLISION", "נחש", "משיח")
	if collision == nil {
		t.Fatal("expected null-model result for נחש and משיח collision")
	}
	if collision.NullHits <= 0 {
		t.Fatal("expected collision to occur sometimes under permutation")
	}
	if collision.NullHits >= collision.Simulations {
		t.Fatal("collision must not be guaranteed under permutation")
	}
	if collision.EmpiricalPValue >= 0.10 {
		t.Fatalf("collision null p-value = %f, expected below 0.10 for this demonstration corpus", collision.EmpiricalPValue)
	}
}

func TestNullModelSingleWordStructureUsesObservedValueDistribution(t *testing.T) {
	report, err := runNullModel(demoCorpusEnvelope(), 10000, 369)
	if err != nil {
		t.Fatal(err)
	}

	square := findNullFinding(report, "PERFECT_SQUARE", "אמת")
	if square == nil {
		t.Fatal("expected null-model result for אמת perfect square")
	}
	if square.EmpiricalPValue <= 0 || square.EmpiricalPValue >= 0.20 {
		t.Fatalf("unexpected square empirical p-value %f", square.EmpiricalPValue)
	}

	palindrome := findNullFinding(report, "PALINDROME", "הנחש")
	if palindrome == nil {
		t.Fatal("expected null-model result for הנחש palindrome")
	}
	if palindrome.EmpiricalPValue <= 0 || palindrome.EmpiricalPValue >= 0.20 {
		t.Fatalf("unexpected palindrome empirical p-value %f", palindrome.EmpiricalPValue)
	}
}

func TestNullModelBounds(t *testing.T) {
	corpus := demoCorpusEnvelope()

	if _, err := runNullModel(corpus, minNullSimulations-1, 1); err == nil {
		t.Fatal("simulation count below lower bound must fail")
	}
	if _, err := runNullModel(corpus, maxNullSimulations+1, 1); err == nil {
		t.Fatal("simulation count above upper bound must fail")
	}
}

func TestNullModelValueDigestDeterminism(t *testing.T) {
	corpus := demoCorpusEnvelope()
	first, err := valueMultisetDigest(corpus)
	if err != nil {
		t.Fatal(err)
	}
	second, err := valueMultisetDigest(corpus)
	if err != nil {
		t.Fatal(err)
	}
	if first != second {
		t.Fatalf("value multiset digest drift: %s != %s", first, second)
	}
	if len(first) != 64 {
		t.Fatalf("value multiset digest length = %d, want 64", len(first))
	}
}

func TestNullModelBoundaries(t *testing.T) {
	report, err := runNullModel(demoCorpusEnvelope(), 1000, 369)
	if err != nil {
		t.Fatal(err)
	}

	for _, boundary := range []string{
		"NULL_MODEL != REALITY",
		"EMPIRICAL_P_VALUE != TRUTH_PROBABILITY",
		"BH_Q_VALUE != TRUTH_PROBABILITY",
		"MULTIPLE_TESTING_CORRECTION != SEMANTIC_PROOF",
		"SURPRISE != SIGNIFICANCE",
		"RARE_UNDER_NULL != SUPERNATURAL",
		"REPLICATION != PROOF",
		"PATTERN != PROOF",
	} {
		if !containsString(report.Boundary, boundary) {
			t.Errorf("missing null-model boundary %q", boundary)
		}
	}
}

func TestNullModelSummaryIsStable(t *testing.T) {
	report, err := runNullModel(demoCorpusEnvelope(), 1000, 369)
	if err != nil {
		t.Fatal(err)
	}
	first := nullModelSummary(report)
	second := nullModelSummary(report)
	if first == "" || first == "NO_FINDINGS" {
		t.Fatalf("unexpected summary %q", first)
	}
	if first != second {
		t.Fatalf("summary drift: %q != %q", first, second)
	}
}

func findNullFinding(report NullModelReport, kind string, words ...string) *NullModelFinding {
	for i := range report.Findings {
		finding := &report.Findings[i]
		if finding.Type != kind {
			continue
		}
		all := true
		for _, word := range words {
			if !containsString(finding.Words, word) {
				all = false
				break
			}
		}
		if all {
			return finding
		}
	}
	return nil
}

func TestBenjaminiHochbergAdjustment(t *testing.T) {
	results := []NullModelFinding{
		{SignatureID: "sig:a", EmpiricalPValue: 0.01},
		{SignatureID: "sig:b", EmpiricalPValue: 0.03},
		{SignatureID: "sig:c", EmpiricalPValue: 0.04},
	}

	applyBenjaminiHochberg(results)

	want := []float64{0.03, 0.04, 0.04}
	for i := range results {
		if results[i].BHAdjustedQValue != want[i] {
			t.Fatalf("result %d q-value = %f, want %f", i, results[i].BHAdjustedQValue, want[i])
		}
		if results[i].BHAdjustedQValue < results[i].EmpiricalPValue {
			t.Fatalf("result %d q-value %f must not be below raw p-value %f", i, results[i].BHAdjustedQValue, results[i].EmpiricalPValue)
		}
	}
}

func TestNullModelReportsMultipleTestingFamily(t *testing.T) {
	report, err := runNullModel(demoCorpusEnvelope(), 1000, 369)
	if err != nil {
		t.Fatal(err)
	}

	if report.SchemaVersion != "gematria-glitch.null-model.v1.1" {
		t.Fatalf("schema version = %q", report.SchemaVersion)
	}
	if report.TestFamilySize != len(report.Findings) {
		t.Fatalf("test family size = %d, findings = %d", report.TestFamilySize, len(report.Findings))
	}
	if report.Config.MultipleTesting != "benjamini_hochberg_fdr" {
		t.Fatalf("multiple testing method = %q", report.Config.MultipleTesting)
	}

	for _, finding := range report.Findings {
		if finding.BHAdjustedQValue < finding.EmpiricalPValue {
			t.Fatalf(
				"q-value %f below raw p-value %f for %s",
				finding.BHAdjustedQValue,
				finding.EmpiricalPValue,
				finding.SignatureID,
			)
		}
		if finding.BHAdjustedQValue <= 0 || finding.BHAdjustedQValue > 1 {
			t.Fatalf("q-value out of bounds for %s: %f", finding.SignatureID, finding.BHAdjustedQValue)
		}
	}
}

func TestNullModelRejectsDuplicateWordTokens(t *testing.T) {
	corpus := demoCorpusEnvelope()
	corpus.Records = append(corpus.Records, Entry{
		ID:    "demo-duplicate",
		Word:  corpus.Records[0].Word,
		Gloss: "duplicate token for ambiguity test",
		Source: SourceRecord{
			ID:        "demo-source-duplicate",
			Kind:      "declared_demo",
			Reference: "duplicate token safety test",
		},
	})

	if _, err := runNullModel(corpus, 1000, 369); err == nil {
		t.Fatal("duplicate word tokens must be rejected by the word-keyed permutation null model")
	}
}

func TestNullModelAdjustedOrderingIsMonotonic(t *testing.T) {
	report, err := runNullModel(demoCorpusEnvelope(), 2000, 369)
	if err != nil {
		t.Fatal(err)
	}

	for i := 1; i < len(report.Findings); i++ {
		previous := report.Findings[i-1]
		current := report.Findings[i]
		if previous.BHAdjustedQValue > current.BHAdjustedQValue {
			t.Fatalf(
				"q-value ordering drift at %d: %f > %f",
				i,
				previous.BHAdjustedQValue,
				current.BHAdjustedQValue,
			)
		}
	}
}
