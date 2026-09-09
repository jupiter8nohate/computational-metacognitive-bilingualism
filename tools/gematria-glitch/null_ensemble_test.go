package main

import (
	"encoding/json"
	"sort"
	"testing"
)

func TestNullEnsembleDeterminism(t *testing.T) {
	corpus := demoCorpusEnvelope()

	first, err := runNullModelEnsemble(corpus, 2000, 369, 0.05)
	if err != nil {
		t.Fatal(err)
	}
	second, err := runNullModelEnsemble(corpus, 2000, 369, 0.05)
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
		t.Fatal("null-model ensemble must be deterministic for identical inputs")
	}
}

func TestNullEnsembleIncludesBothBaselines(t *testing.T) {
	report, err := runNullModelEnsemble(demoCorpusEnvelope(), 1000, 369, 0.05)
	if err != nil {
		t.Fatal(err)
	}

	want := []string{
		nullModelLengthStratifiedPermutation,
		nullModelValuePermutation,
	}
	got := append([]string(nil), report.Config.Models...)
	sort.Strings(got)
	sort.Strings(want)

	if len(got) != len(want) {
		t.Fatalf("models = %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("models = %v, want %v", got, want)
		}
	}
}

func TestLengthStratifiedPermutationPreservesEachStratumMultiset(t *testing.T) {
	corpus := demoCorpusEnvelope()
	values := make([]int, len(corpus.Records))
	lengths := make([]int, len(corpus.Records))
	for i, entry := range corpus.Records {
		values[i] = Gematria(entry.Word)
		lengths[i] = hebrewTokenLength(entry.Word)
	}

	rng := &splitMix64{state: 369}
	permuted, err := permuteValuesWithinLengthStrata(values, lengths, rng)
	if err != nil {
		t.Fatal(err)
	}

	originalByLength := valuesByLength(values, lengths)
	permutedByLength := valuesByLength(permuted, lengths)

	if len(originalByLength) != len(permutedByLength) {
		t.Fatal("stratum count changed")
	}
	for length, original := range originalByLength {
		after := permutedByLength[length]
		sort.Ints(original)
		sort.Ints(after)
		if len(original) != len(after) {
			t.Fatalf("length %d stratum size changed", length)
		}
		for i := range original {
			if original[i] != after[i] {
				t.Fatalf("length %d value multiset changed: %v != %v", length, original, after)
			}
		}
	}
}

func TestLengthStratifiedSingletonIsFixed(t *testing.T) {
	corpus := demoCorpusEnvelope()
	report, err := runNullVariant(
		corpus,
		1000,
		369,
		nullModelLengthStratifiedPermutation,
	)
	if err != nil {
		t.Fatal(err)
	}

	finding := findNullVariantFinding(report, "POWER_OF_TWO", "לב")
	if finding == nil {
		t.Fatal("expected POWER_OF_TWO finding for לב")
	}
	if finding.NullHits != 1000 {
		t.Fatalf("singleton length stratum must keep לב fixed; hits=%d", finding.NullHits)
	}
	if finding.EmpiricalPValue != 1 {
		t.Fatalf("singleton length-stratified p-value = %f, want 1", finding.EmpiricalPValue)
	}
}

func TestNullEnsembleAlignsFindingSignaturesAcrossModels(t *testing.T) {
	report, err := runNullModelEnsemble(demoCorpusEnvelope(), 1000, 369, 0.05)
	if err != nil {
		t.Fatal(err)
	}

	for _, finding := range report.Findings {
		if finding.TotalModels != 2 {
			t.Fatalf("finding %s total models = %d, want 2", finding.SignatureID, finding.TotalModels)
		}
		if len(finding.ModelResults) != 2 {
			t.Fatalf("finding %s model results = %d, want 2", finding.SignatureID, len(finding.ModelResults))
		}
		if finding.WorstCaseQValue < finding.ModelResults[0].BHAdjustedQValue ||
			finding.WorstCaseQValue < finding.ModelResults[1].BHAdjustedQValue {
			t.Fatalf("finding %s worst-case q-value is not conservative", finding.SignatureID)
		}
	}
}

func TestEnsembleRobustnessStatus(t *testing.T) {
	cases := []struct {
		uncommon int
		total    int
		want     string
	}{
		{0, 2, "NOT_UNCOMMON_UNDER_ENSEMBLE"},
		{1, 2, "UNCOMMON_IN_MODEL_SUBSET"},
		{2, 2, "UNCOMMON_ACROSS_ALL_MODELS"},
	}

	for _, tc := range cases {
		got := ensembleRobustnessStatus(tc.uncommon, tc.total)
		if got != tc.want {
			t.Fatalf("status(%d,%d) = %q, want %q", tc.uncommon, tc.total, got, tc.want)
		}
	}
}

func TestNullEnsembleRejectsInvalidQThreshold(t *testing.T) {
	corpus := demoCorpusEnvelope()

	for _, threshold := range []float64{0, -0.01, 1.01} {
		if _, err := runNullModelEnsemble(corpus, 1000, 369, threshold); err == nil {
			t.Fatalf("threshold %f must be rejected", threshold)
		}
	}
}

func TestNullEnsembleBoundaries(t *testing.T) {
	report, err := runNullModelEnsemble(demoCorpusEnvelope(), 1000, 369, 0.05)
	if err != nil {
		t.Fatal(err)
	}

	for _, boundary := range []string{
		"NULL_MODEL_ENSEMBLE != REALITY",
		"ROBUST_ACROSS_MODELS != TRUTH",
		"MODEL_AGREEMENT != CAUSATION",
		"Q_THRESHOLD != SEMANTIC_THRESHOLD",
		"ASSUMPTION_SENSITIVITY != FALSEHOOD",
		"EMPIRICAL_P_VALUE != TRUTH_PROBABILITY",
		"BH_Q_VALUE != TRUTH_PROBABILITY",
		"PATTERN != PROOF",
	} {
		if !containsString(report.Boundary, boundary) {
			t.Errorf("missing ensemble boundary %q", boundary)
		}
	}
}

func TestNullEnsembleDigestDeterminism(t *testing.T) {
	report, err := runNullModelEnsemble(demoCorpusEnvelope(), 1000, 369, 0.05)
	if err != nil {
		t.Fatal(err)
	}

	first, err := nullEnsembleDigest(report)
	if err != nil {
		t.Fatal(err)
	}
	second, err := nullEnsembleDigest(report)
	if err != nil {
		t.Fatal(err)
	}
	if first != second {
		t.Fatalf("ensemble digest drift: %s != %s", first, second)
	}
	if len(first) != 64 {
		t.Fatalf("ensemble digest length = %d, want 64", len(first))
	}
}

func valuesByLength(values, lengths []int) map[int][]int {
	out := make(map[int][]int)
	for i, length := range lengths {
		out[length] = append(out[length], values[i])
	}
	return out
}

func findNullVariantFinding(
	report nullVariantReport,
	kind string,
	words ...string,
) *nullVariantFinding {
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
