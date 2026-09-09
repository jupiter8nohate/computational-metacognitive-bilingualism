package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"sort"
	"strings"
)

const (
	nullModelValuePermutation            = "value_permutation"
	nullModelLengthStratifiedPermutation = "word_length_stratified_value_permutation"
	defaultEnsembleQThreshold            = 0.05
)

type NullEnsembleConfig struct {
	Models      []string `json:"models"`
	Simulations int      `json:"simulations"`
	Seed        uint64   `json:"seed"`
	QThreshold  float64  `json:"q_threshold"`
}

type NullEnsembleModelResult struct {
	Model            string  `json:"model"`
	NullHits         int     `json:"null_hits"`
	Simulations      int     `json:"simulations"`
	EmpiricalPValue  float64 `json:"empirical_p_value"`
	BHAdjustedQValue float64 `json:"bh_adjusted_q_value"`
	SurpriseBits     float64 `json:"surprise_bits"`
	FrequencyClass   string  `json:"frequency_class"`
}

type NullEnsembleFinding struct {
	SignatureID      string                    `json:"signature_id"`
	Type             string                    `json:"type"`
	Words            []string                  `json:"words"`
	ObservedValues   []int                     `json:"observed_values"`
	ModelResults     []NullEnsembleModelResult `json:"model_results"`
	UncommonModels   int                       `json:"uncommon_models"`
	TotalModels      int                       `json:"total_models"`
	WorstCaseQValue  float64                   `json:"worst_case_q_value"`
	RobustnessStatus string                    `json:"robustness_status"`
}

type NullEnsembleReport struct {
	SchemaVersion  string                `json:"schema_version"`
	Protocol       string                `json:"protocol"`
	CorpusID       string                `json:"corpus_id"`
	CorpusVersion  string                `json:"corpus_version"`
	CorpusSHA256   string                `json:"corpus_sha256"`
	GematriaSystem string                `json:"gematria_system"`
	Config         NullEnsembleConfig    `json:"config"`
	Findings       []NullEnsembleFinding `json:"findings"`
	Boundary       []string              `json:"boundary"`
}

type nullVariantFinding struct {
	SignatureID      string
	Type             string
	Words            []string
	ObservedValues   []int
	NullHits         int
	EmpiricalPValue  float64
	BHAdjustedQValue float64
	SurpriseBits     float64
	FrequencyClass   string
}

type nullVariantReport struct {
	Model    string
	Findings []nullVariantFinding
}

func runNullModelEnsemble(
	corpus Corpus,
	simulations int,
	seed uint64,
	qThreshold float64,
) (NullEnsembleReport, error) {
	if err := validateCorpus(corpus); err != nil {
		return NullEnsembleReport{}, err
	}
	if err := validateNullModelCorpus(corpus); err != nil {
		return NullEnsembleReport{}, err
	}
	if simulations < minNullSimulations || simulations > maxNullSimulations {
		return NullEnsembleReport{}, fmt.Errorf(
			"null simulations must be between %d and %d",
			minNullSimulations,
			maxNullSimulations,
		)
	}
	if qThreshold <= 0 || qThreshold > 1 {
		return NullEnsembleReport{}, fmt.Errorf("ensemble q threshold must be greater than 0 and at most 1")
	}

	models := []string{
		nullModelValuePermutation,
		nullModelLengthStratifiedPermutation,
	}
	variants := make([]nullVariantReport, 0, len(models))
	for _, model := range models {
		report, err := runNullVariant(corpus, simulations, seed, model)
		if err != nil {
			return NullEnsembleReport{}, err
		}
		variants = append(variants, report)
	}

	corpusSHA, err := corpusDigest(corpus)
	if err != nil {
		return NullEnsembleReport{}, err
	}

	bySignature := make(map[string]*NullEnsembleFinding)
	for _, variant := range variants {
		for _, finding := range variant.Findings {
			entry, ok := bySignature[finding.SignatureID]
			if !ok {
				entry = &NullEnsembleFinding{
					SignatureID:    finding.SignatureID,
					Type:           finding.Type,
					Words:          append([]string(nil), finding.Words...),
					ObservedValues: append([]int(nil), finding.ObservedValues...),
				}
				bySignature[finding.SignatureID] = entry
			}
			entry.ModelResults = append(entry.ModelResults, NullEnsembleModelResult{
				Model:            variant.Model,
				NullHits:         finding.NullHits,
				Simulations:      simulations,
				EmpiricalPValue:  finding.EmpiricalPValue,
				BHAdjustedQValue: finding.BHAdjustedQValue,
				SurpriseBits:     finding.SurpriseBits,
				FrequencyClass:   finding.FrequencyClass,
			})
		}
	}

	findings := make([]NullEnsembleFinding, 0, len(bySignature))
	for _, finding := range bySignature {
		sort.Slice(finding.ModelResults, func(i, j int) bool {
			return finding.ModelResults[i].Model < finding.ModelResults[j].Model
		})
		finding.TotalModels = len(finding.ModelResults)
		finding.WorstCaseQValue = 0
		for _, modelResult := range finding.ModelResults {
			if modelResult.BHAdjustedQValue < qThreshold {
				finding.UncommonModels++
			}
			if modelResult.BHAdjustedQValue > finding.WorstCaseQValue {
				finding.WorstCaseQValue = modelResult.BHAdjustedQValue
			}
		}
		finding.WorstCaseQValue = round6(finding.WorstCaseQValue)
		finding.RobustnessStatus = ensembleRobustnessStatus(
			finding.UncommonModels,
			finding.TotalModels,
		)
		findings = append(findings, *finding)
	}

	sort.Slice(findings, func(i, j int) bool {
		left := findings[i]
		right := findings[j]
		if left.UncommonModels != right.UncommonModels {
			return left.UncommonModels > right.UncommonModels
		}
		if left.WorstCaseQValue != right.WorstCaseQValue {
			return left.WorstCaseQValue < right.WorstCaseQValue
		}
		if left.Type != right.Type {
			return left.Type < right.Type
		}
		return left.SignatureID < right.SignatureID
	})

	return NullEnsembleReport{
		SchemaVersion:  "gematria-glitch.null-ensemble.v1",
		Protocol:       "GEMATRIA-GLITCH-1",
		CorpusID:       corpus.CorpusID,
		CorpusVersion:  corpus.Version,
		CorpusSHA256:   corpusSHA,
		GematriaSystem: corpus.GematriaSystem,
		Config: NullEnsembleConfig{
			Models:      models,
			Simulations: simulations,
			Seed:        seed,
			QThreshold:  round6(qThreshold),
		},
		Findings: findings,
		Boundary: []string{
			"NULL_MODEL_ENSEMBLE != REALITY",
			"ROBUST_ACROSS_MODELS != TRUTH",
			"MODEL_AGREEMENT != CAUSATION",
			"Q_THRESHOLD != SEMANTIC_THRESHOLD",
			"ASSUMPTION_SENSITIVITY != FALSEHOOD",
			"EMPIRICAL_P_VALUE != TRUTH_PROBABILITY",
			"BH_Q_VALUE != TRUTH_PROBABILITY",
			"PATTERN != PROOF",
		},
	}, nil
}

func runNullVariant(
	corpus Corpus,
	simulations int,
	seed uint64,
	model string,
) (nullVariantReport, error) {
	findings := Analyze(corpus.Records)
	results := make([]NullModelFinding, len(findings))
	for i, finding := range findings {
		signatureID, err := findingSignatureID(canonicalFindingSignature(finding))
		if err != nil {
			return nullVariantReport{}, err
		}
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
	lengths := make([]int, len(corpus.Records))
	for i, entry := range corpus.Records {
		words[i] = entry.Word
		values[i] = Gematria(entry.Word)
		lengths[i] = hebrewTokenLength(entry.Word)
	}

	rng := &splitMix64{state: seed}
	assignments := make(map[string]int, len(words))
	for iteration := 0; iteration < simulations; iteration++ {
		permuted, err := permuteNullValues(values, lengths, model, rng)
		if err != nil {
			return nullVariantReport{}, err
		}

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

	variantFindings := make([]nullVariantFinding, len(results))
	for i, result := range results {
		variantFindings[i] = nullVariantFinding{
			SignatureID:      result.SignatureID,
			Type:             result.Type,
			Words:            append([]string(nil), result.Words...),
			ObservedValues:   append([]int(nil), result.ObservedValues...),
			NullHits:         result.NullHits,
			EmpiricalPValue:  result.EmpiricalPValue,
			BHAdjustedQValue: result.BHAdjustedQValue,
			SurpriseBits:     result.SurpriseBits,
			FrequencyClass:   result.FrequencyClass,
		}
	}
	sort.Slice(variantFindings, func(i, j int) bool {
		return variantFindings[i].SignatureID < variantFindings[j].SignatureID
	})

	return nullVariantReport{
		Model:    model,
		Findings: variantFindings,
	}, nil
}

func permuteNullValues(
	values []int,
	lengths []int,
	model string,
	rng *splitMix64,
) ([]int, error) {
	switch model {
	case nullModelValuePermutation:
		out := append([]int(nil), values...)
		fisherYates(out, rng)
		return out, nil

	case nullModelLengthStratifiedPermutation:
		return permuteValuesWithinLengthStrata(values, lengths, rng)

	default:
		return nil, fmt.Errorf("unsupported null model %q", model)
	}
}

func permuteValuesWithinLengthStrata(
	values []int,
	lengths []int,
	rng *splitMix64,
) ([]int, error) {
	if len(values) != len(lengths) {
		return nil, fmt.Errorf("value and length vectors must have equal size")
	}

	out := append([]int(nil), values...)
	strata := make(map[int][]int)
	for index, length := range lengths {
		if length <= 0 {
			return nil, fmt.Errorf("word length must be positive")
		}
		strata[length] = append(strata[length], index)
	}

	keys := make([]int, 0, len(strata))
	for length := range strata {
		keys = append(keys, length)
	}
	sort.Ints(keys)

	for _, length := range keys {
		indices := strata[length]
		if len(indices) < 2 {
			continue
		}

		groupValues := make([]int, len(indices))
		for i, index := range indices {
			groupValues[i] = values[index]
		}
		fisherYates(groupValues, rng)
		for i, index := range indices {
			out[index] = groupValues[i]
		}
	}
	return out, nil
}

func hebrewTokenLength(word string) int {
	return len([]rune(strings.TrimSpace(word)))
}

func ensembleRobustnessStatus(uncommonModels, totalModels int) string {
	switch {
	case totalModels <= 0 || uncommonModels <= 0:
		return "NOT_UNCOMMON_UNDER_ENSEMBLE"
	case uncommonModels == totalModels:
		return "UNCOMMON_ACROSS_ALL_MODELS"
	default:
		return "UNCOMMON_IN_MODEL_SUBSET"
	}
}

func nullEnsembleDigest(report NullEnsembleReport) (string, error) {
	data, err := json.Marshal(report)
	if err != nil {
		return "", fmt.Errorf("marshal null ensemble: %w", err)
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func renderNullEnsembleGlitch(report NullEnsembleReport) string {
	var b strings.Builder
	b.WriteString("𓁹 Err ⃝or⃟⃤://NULL_MODEL_ENSEMBLE\n")
	fmt.Fprintf(&b, "CORPUS://%s@%s\n", report.CorpusID, report.CorpusVersion)
	fmt.Fprintf(&b, "MODELS://%s\n", strings.Join(report.Config.Models, " | "))
	fmt.Fprintf(&b, "SIMULATIONS_PER_MODEL://%d\n", report.Config.Simulations)
	fmt.Fprintf(&b, "SEED://%d\n", report.Config.Seed)
	fmt.Fprintf(&b, "Q_THRESHOLD://%.6f\n\n", report.Config.QThreshold)

	for _, finding := range report.Findings {
		fmt.Fprintf(&b, "꩜ ROBUSTNESS://%s\n", finding.RobustnessStatus)
		fmt.Fprintf(&b, "TYPE://%s\n", finding.Type)
		fmt.Fprintf(&b, "WORDS://%s\n", strings.Join(finding.Words, " | "))
		fmt.Fprintf(&b, "OBSERVED_VALUES://%v\n", finding.ObservedValues)
		fmt.Fprintf(&b, "UNCOMMON_MODELS://%d/%d\n", finding.UncommonModels, finding.TotalModels)
		fmt.Fprintf(&b, "WORST_CASE_Q_VALUE://%.6f\n", finding.WorstCaseQValue)
		for _, model := range finding.ModelResults {
			fmt.Fprintf(
				&b,
				"𓂀 MODEL://%s | P=%.6f | Q=%.6f | CLASS=%s\n",
				model.Model,
				model.EmpiricalPValue,
				model.BHAdjustedQValue,
				model.FrequencyClass,
			)
		}
		b.WriteString("ROBUST_ACROSS_MODELS != TRUTH\n")
		b.WriteString("Q_THRESHOLD != SEMANTIC_THRESHOLD\n\n")
	}

	b.WriteString("NULL_MODEL_ENSEMBLE != REALITY\n")
	b.WriteString("MODEL_AGREEMENT != CAUSATION\n")
	b.WriteString("PATTERN != PROOF\n")
	b.WriteString("♡⃟ INTERPRETATION://HUMAN\n")
	return b.String()
}
