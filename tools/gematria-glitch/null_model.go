package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"sort"
	"strconv"
	"strings"
)

const (
	minNullSimulations = 100
	maxNullSimulations = 1000000
)

type NullModelConfig struct {
	Model           string `json:"model"`
	Simulations     int    `json:"simulations"`
	Seed            uint64 `json:"seed"`
	MultipleTesting string `json:"multiple_testing"`
}

type NullModelFinding struct {
	SignatureID      string   `json:"signature_id"`
	Type             string   `json:"type"`
	Words            []string `json:"words"`
	ObservedValues   []int    `json:"observed_values"`
	NullHits         int      `json:"null_hits"`
	Simulations      int      `json:"simulations"`
	ChanceRate       float64  `json:"chance_rate"`
	EmpiricalPValue  float64  `json:"empirical_p_value"`
	BHAdjustedQValue float64  `json:"bh_adjusted_q_value"`
	SurpriseBits     float64  `json:"surprise_bits"`
	FrequencyClass   string   `json:"frequency_class"`
}

type NullModelReport struct {
	SchemaVersion    string             `json:"schema_version"`
	Protocol         string             `json:"protocol"`
	CorpusID         string             `json:"corpus_id"`
	CorpusVersion    string             `json:"corpus_version"`
	CorpusSHA256     string             `json:"corpus_sha256"`
	GematriaSystem   string             `json:"gematria_system"`
	ValueMultisetSHA string             `json:"value_multiset_sha256"`
	TestFamilySize   int                `json:"test_family_size"`
	Config           NullModelConfig    `json:"config"`
	Findings         []NullModelFinding `json:"findings"`
	Boundary         []string           `json:"boundary"`
}

type splitMix64 struct {
	state uint64
}

func (r *splitMix64) next() uint64 {
	r.state += 0x9e3779b97f4a7c15
	z := r.state
	z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9
	z = (z ^ (z >> 27)) * 0x94d049bb133111eb
	return z ^ (z >> 31)
}

func (r *splitMix64) intn(n int) int {
	if n <= 0 {
		panic("intn requires positive n")
	}
	return int(r.next() % uint64(n))
}

func runNullModel(corpus Corpus, simulations int, seed uint64) (NullModelReport, error) {
	if err := validateCorpus(corpus); err != nil {
		return NullModelReport{}, err
	}
	if err := validateNullModelCorpus(corpus); err != nil {
		return NullModelReport{}, err
	}
	if simulations < minNullSimulations || simulations > maxNullSimulations {
		return NullModelReport{}, fmt.Errorf(
			"null simulations must be between %d and %d",
			minNullSimulations,
			maxNullSimulations,
		)
	}

	corpusSHA, err := corpusDigest(corpus)
	if err != nil {
		return NullModelReport{}, err
	}
	valueSHA, err := valueMultisetDigest(corpus)
	if err != nil {
		return NullModelReport{}, err
	}

	findings := Analyze(corpus.Records)
	results := make([]NullModelFinding, len(findings))
	signatureIDs := make([]string, len(findings))
	for i, finding := range findings {
		signatureID, err := findingSignatureID(canonicalFindingSignature(finding))
		if err != nil {
			return NullModelReport{}, err
		}
		signatureIDs[i] = signatureID
		results[i] = NullModelFinding{
			SignatureID:    signatureID,
			Type:           finding.Type,
			Words:          append([]string(nil), finding.Words...),
			ObservedValues: append([]int(nil), finding.Values...),
			Simulations:    simulations,
		}
	}

	words := make([]string, len(corpus.Records))
	values := make([]int, len(corpus.Records))
	for i, entry := range corpus.Records {
		words[i] = entry.Word
		values[i] = Gematria(entry.Word)
	}

	rng := &splitMix64{state: seed}
	permuted := make([]int, len(values))
	assignments := make(map[string]int, len(words))

	for iteration := 0; iteration < simulations; iteration++ {
		copy(permuted, values)
		fisherYates(permuted, rng)

		clear(assignments)
		for i, word := range words {
			assignments[word] = permuted[i]
		}

		for i, finding := range findings {
			if findingOccursUnderAssignment(finding, assignments) {
				results[i].NullHits++
			}
		}
	}

	for i := range results {
		result := &results[i]
		result.ChanceRate = roundedRatio(result.NullHits, simulations)
		result.EmpiricalPValue = roundedRatio(result.NullHits+1, simulations+1)
		result.SurpriseBits = round6(-math.Log2(result.EmpiricalPValue))
		result.FrequencyClass = nullFrequencyClass(result.EmpiricalPValue)
	}
	applyBenjaminiHochberg(results)

	sort.Slice(results, func(i, j int) bool {
		if results[i].BHAdjustedQValue != results[j].BHAdjustedQValue {
			return results[i].BHAdjustedQValue < results[j].BHAdjustedQValue
		}
		if results[i].EmpiricalPValue != results[j].EmpiricalPValue {
			return results[i].EmpiricalPValue < results[j].EmpiricalPValue
		}
		if results[i].Type != results[j].Type {
			return results[i].Type < results[j].Type
		}
		return signatureIDsForSort(results[i], results[j])
	})

	return NullModelReport{
		SchemaVersion:    "gematria-glitch.null-model.v1.1",
		Protocol:         "GEMATRIA-GLITCH-1",
		CorpusID:         corpus.CorpusID,
		CorpusVersion:    corpus.Version,
		CorpusSHA256:     corpusSHA,
		GematriaSystem:   corpus.GematriaSystem,
		ValueMultisetSHA: valueSHA,
		TestFamilySize:   len(results),
		Config: NullModelConfig{
			Model:           "value_permutation",
			Simulations:     simulations,
			Seed:            seed,
			MultipleTesting: "benjamini_hochberg_fdr",
		},
		Findings: results,
		Boundary: []string{
			"NULL_MODEL != REALITY",
			"EMPIRICAL_P_VALUE != TRUTH_PROBABILITY",
			"BH_Q_VALUE != TRUTH_PROBABILITY",
			"MULTIPLE_TESTING_CORRECTION != SEMANTIC_PROOF",
			"SURPRISE != SIGNIFICANCE",
			"RARE_UNDER_NULL != SUPERNATURAL",
			"REPLICATION != PROOF",
			"PATTERN != PROOF",
		},
	}, nil
}


func validateNullModelCorpus(corpus Corpus) error {
	seen := make(map[string]string, len(corpus.Records))
	for _, entry := range corpus.Records {
		if previousID, exists := seen[entry.Word]; exists {
			return fmt.Errorf(
				"null model requires unique word tokens; %q appears in records %q and %q",
				entry.Word,
				previousID,
				entry.ID,
			)
		}
		seen[entry.Word] = entry.ID
	}
	return nil
}

func applyBenjaminiHochberg(results []NullModelFinding) {
	if len(results) == 0 {
		return
	}

	type rankedFinding struct {
		index       int
		pValue      float64
		signatureID string
	}

	ranked := make([]rankedFinding, len(results))
	for i, result := range results {
		ranked[i] = rankedFinding{
			index:       i,
			pValue:      result.EmpiricalPValue,
			signatureID: result.SignatureID,
		}
	}
	sort.Slice(ranked, func(i, j int) bool {
		if ranked[i].pValue != ranked[j].pValue {
			return ranked[i].pValue < ranked[j].pValue
		}
		return ranked[i].signatureID < ranked[j].signatureID
	})

	previous := 1.0
	familySize := float64(len(ranked))
	for rank := len(ranked); rank >= 1; rank-- {
		item := ranked[rank-1]
		adjusted := item.pValue * familySize / float64(rank)
		if adjusted > 1 {
			adjusted = 1
		}
		if adjusted > previous {
			adjusted = previous
		}
		adjusted = round6(adjusted)
		results[item.index].BHAdjustedQValue = adjusted
		previous = adjusted
	}
}

func signatureIDsForSort(left, right NullModelFinding) bool {
	return left.SignatureID < right.SignatureID
}

func fisherYates(values []int, rng *splitMix64) {
	for i := len(values) - 1; i > 0; i-- {
		j := rng.intn(i + 1)
		values[i], values[j] = values[j], values[i]
	}
}

func findingOccursUnderAssignment(finding Finding, assigned map[string]int) bool {
	if len(finding.Words) == 0 {
		return false
	}

	valueFor := func(word string) (int, bool) {
		value, ok := assigned[word]
		return value, ok
	}

	switch finding.Type {
	case "EXACT_COLLISION":
		if len(finding.Words) < 2 {
			return false
		}
		left, leftOK := valueFor(finding.Words[0])
		right, rightOK := valueFor(finding.Words[1])
		return leftOK && rightOK && left == right

	case "PALINDROME":
		value, ok := valueFor(finding.Words[0])
		return ok && value >= 10 && value == reverseDigits(value)

	case "PERFECT_SQUARE":
		value, ok := valueFor(finding.Words[0])
		return ok && isPerfectSquare(value)

	case "TRIANGULAR_NUMBER":
		value, ok := valueFor(finding.Words[0])
		if !ok {
			return false
		}
		_, triangular := triangularIndex(value)
		return triangular

	case "POWER_OF_TWO":
		value, ok := valueFor(finding.Words[0])
		return ok && isPowerOfTwo(value)

	case "PRIME_VALUE":
		value, ok := valueFor(finding.Words[0])
		return ok && isPrime(value)

	case "DIGITAL_ROOT":
		if len(finding.Values) < 2 {
			return false
		}
		value, ok := valueFor(finding.Words[0])
		return ok && digitalRoot(value) == finding.Values[1]

	case "SHARED_PRIME_FACTOR":
		if len(finding.Words) < 2 || len(finding.Values) < 3 {
			return false
		}
		left, leftOK := valueFor(finding.Words[0])
		right, rightOK := valueFor(finding.Words[1])
		factor := finding.Values[2]
		return leftOK && rightOK && factor > 1 && left%factor == 0 && right%factor == 0

	case "LINGUISTIC_PREFIX_DELTA":
		if len(finding.Words) < 2 || len(finding.Values) < 3 {
			return false
		}
		shorter, shorterOK := valueFor(finding.Words[0])
		longer, longerOK := valueFor(finding.Words[1])
		return shorterOK && longerOK && longer-shorter == finding.Values[2]

	default:
		return false
	}
}

func valueMultisetDigest(corpus Corpus) (string, error) {
	values := make([]int, len(corpus.Records))
	for i, entry := range corpus.Records {
		values[i] = Gematria(entry.Word)
	}
	sort.Ints(values)
	data, err := json.Marshal(values)
	if err != nil {
		return "", fmt.Errorf("marshal value multiset: %w", err)
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func roundedRatio(numerator, denominator int) float64 {
	if denominator <= 0 {
		return 0
	}
	return round6(float64(numerator) / float64(denominator))
}

func round6(value float64) float64 {
	return math.Round(value*1_000_000) / 1_000_000
}

func nullFrequencyClass(p float64) string {
	switch {
	case p < 0.01:
		return "RARE_UNDER_NULL"
	case p < 0.05:
		return "UNCOMMON_UNDER_NULL"
	case p < 0.20:
		return "OCCASIONAL_UNDER_NULL"
	default:
		return "COMMON_UNDER_NULL"
	}
}

func renderNullModelGlitch(report NullModelReport) string {
	var b strings.Builder
	b.WriteString("𓁹 Err ⃝or⃟⃤://NULL_MODEL_TEST\n")
	fmt.Fprintf(&b, "MODEL://%s\n", report.Config.Model)
	fmt.Fprintf(&b, "CORPUS://%s@%s\n", report.CorpusID, report.CorpusVersion)
	fmt.Fprintf(&b, "SIMULATIONS://%d\n", report.Config.Simulations)
	fmt.Fprintf(&b, "SEED://%d\n", report.Config.Seed)
	fmt.Fprintf(&b, "TEST_FAMILY_SIZE://%d\n", report.TestFamilySize)
	fmt.Fprintf(&b, "MULTIPLE_TESTING://%s\n", report.Config.MultipleTesting)
	fmt.Fprintf(&b, "VALUE_MULTISET_SHA256://%s\n\n", report.ValueMultisetSHA)

	for _, result := range report.Findings {
		fmt.Fprintf(&b, "꩜ NULL_TEST://%s\n", result.FrequencyClass)
		fmt.Fprintf(&b, "TYPE://%s\n", result.Type)
		fmt.Fprintf(&b, "WORDS://%s\n", strings.Join(result.Words, " | "))
		fmt.Fprintf(&b, "OBSERVED_VALUES://%v\n", result.ObservedValues)
		fmt.Fprintf(&b, "NULL_HITS://%d/%d\n", result.NullHits, result.Simulations)
		fmt.Fprintf(&b, "CHANCE_RATE://%.6f\n", result.ChanceRate)
		fmt.Fprintf(&b, "EMPIRICAL_P_VALUE://%.6f\n", result.EmpiricalPValue)
		fmt.Fprintf(&b, "BH_Q_VALUE://%.6f\n", result.BHAdjustedQValue)
		fmt.Fprintf(&b, "SURPRISE_BITS://%.6f\n", result.SurpriseBits)
		b.WriteString("EMPIRICAL_P_VALUE != TRUTH_PROBABILITY\n")
		b.WriteString("BH_Q_VALUE != TRUTH_PROBABILITY\n")
		b.WriteString("RARE_UNDER_NULL != SUPERNATURAL\n\n")
	}

	b.WriteString("NULL_MODEL != REALITY\n")
	b.WriteString("SURPRISE != SIGNIFICANCE\n")
	b.WriteString("PATTERN != PROOF\n")
	b.WriteString("♡⃟ INTERPRETATION://HUMAN\n")
	return b.String()
}

func nullModelSummary(report NullModelReport) string {
	if len(report.Findings) == 0 {
		return "NO_FINDINGS"
	}
	best := report.Findings[0]
	return strings.Join([]string{
		best.Type,
		strings.Join(best.Words, "|"),
		strconv.FormatFloat(best.EmpiricalPValue, 'f', 6, 64),
		strconv.FormatFloat(best.BHAdjustedQValue, 'f', 6, 64),
	}, ":")
}
