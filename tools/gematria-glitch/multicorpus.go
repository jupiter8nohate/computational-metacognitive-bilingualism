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

const maxComparisonCorpora = 16

type ComparisonCorpus struct {
	CorpusID      string `json:"corpus_id"`
	CorpusVersion string `json:"corpus_version"`
	CorpusSHA256  string `json:"corpus_sha256"`
	RecordCount   int    `json:"record_count"`
}

type ReplicationInstance struct {
	SignatureID     string   `json:"signature_id"`
	Type            string   `json:"type"`
	Words           []string `json:"words"`
	Values          []int    `json:"values"`
	CorpusRefs      []string `json:"corpus_refs"`
	CorpusCount     int      `json:"corpus_count"`
	TotalCorpora    int      `json:"total_corpora"`
	ReplicationRate float64  `json:"replication_rate"`
	Status          string   `json:"status"`
}

type TypeRecurrence struct {
	Type           string   `json:"type"`
	CorpusRefs     []string `json:"corpus_refs"`
	CorpusCount    int      `json:"corpus_count"`
	TotalCorpora   int      `json:"total_corpora"`
	RecurrenceRate float64  `json:"recurrence_rate"`
}

type MultiCorpusReport struct {
	SchemaVersion  string                `json:"schema_version"`
	Protocol       string                `json:"protocol"`
	GematriaSystem string                `json:"gematria_system"`
	Corpora        []ComparisonCorpus    `json:"corpora"`
	Instances      []ReplicationInstance `json:"instances"`
	TypeRecurrence []TypeRecurrence      `json:"type_recurrence"`
	Boundary       []string              `json:"boundary"`
}

type findingSignature struct {
	Type   string   `json:"type"`
	Words  []string `json:"words"`
	Values []int    `json:"values"`
}

type replicationAccumulator struct {
	signature findingSignature
	corpora   map[string]struct{}
}

func compareCorpora(corpora []Corpus) (MultiCorpusReport, error) {
	if len(corpora) < 2 {
		return MultiCorpusReport{}, fmt.Errorf("comparison requires at least two corpora")
	}
	if len(corpora) > maxComparisonCorpora {
		return MultiCorpusReport{}, fmt.Errorf("comparison supports at most %d corpora", maxComparisonCorpora)
	}

	system := corpora[0].GematriaSystem
	seenCorpusRefs := make(map[string]struct{}, len(corpora))
	comparisonCorpora := make([]ComparisonCorpus, 0, len(corpora))
	instanceMap := make(map[string]*replicationAccumulator)
	typeMap := make(map[string]map[string]struct{})

	for i, corpus := range corpora {
		if err := validateCorpus(corpus); err != nil {
			return MultiCorpusReport{}, fmt.Errorf("corpus %d: %w", i, err)
		}
		if corpus.GematriaSystem != system {
			return MultiCorpusReport{}, fmt.Errorf(
				"corpus %s@%s uses gematria system %q, expected %q",
				corpus.CorpusID,
				corpus.Version,
				corpus.GematriaSystem,
				system,
			)
		}

		ref := corpusRef(corpus)
		if _, exists := seenCorpusRefs[ref]; exists {
			return MultiCorpusReport{}, fmt.Errorf("duplicate corpus reference %q", ref)
		}
		seenCorpusRefs[ref] = struct{}{}

		digest, err := corpusDigest(corpus)
		if err != nil {
			return MultiCorpusReport{}, err
		}
		comparisonCorpora = append(comparisonCorpora, ComparisonCorpus{
			CorpusID:      corpus.CorpusID,
			CorpusVersion: corpus.Version,
			CorpusSHA256:  digest,
			RecordCount:   len(corpus.Records),
		})

		findings := Analyze(corpus.Records)
		seenSignaturesInCorpus := make(map[string]struct{})
		seenTypesInCorpus := make(map[string]struct{})

		for _, finding := range findings {
			signature := canonicalFindingSignature(finding)
			signatureID, err := findingSignatureID(signature)
			if err != nil {
				return MultiCorpusReport{}, err
			}

			if _, duplicate := seenSignaturesInCorpus[signatureID]; !duplicate {
				seenSignaturesInCorpus[signatureID] = struct{}{}
				accumulator, ok := instanceMap[signatureID]
				if !ok {
					accumulator = &replicationAccumulator{
						signature: signature,
						corpora:   make(map[string]struct{}),
					}
					instanceMap[signatureID] = accumulator
				}
				accumulator.corpora[ref] = struct{}{}
			}

			if _, duplicate := seenTypesInCorpus[finding.Type]; !duplicate {
				seenTypesInCorpus[finding.Type] = struct{}{}
				if typeMap[finding.Type] == nil {
					typeMap[finding.Type] = make(map[string]struct{})
				}
				typeMap[finding.Type][ref] = struct{}{}
			}
		}
	}

	sort.Slice(comparisonCorpora, func(i, j int) bool {
		left := comparisonCorpora[i].CorpusID + "@" + comparisonCorpora[i].CorpusVersion
		right := comparisonCorpora[j].CorpusID + "@" + comparisonCorpora[j].CorpusVersion
		return left < right
	})

	instances := make([]ReplicationInstance, 0, len(instanceMap))
	total := len(corpora)
	for signatureID, accumulator := range instanceMap {
		refs := sortedSet(accumulator.corpora)
		count := len(refs)
		instances = append(instances, ReplicationInstance{
			SignatureID:     signatureID,
			Type:            accumulator.signature.Type,
			Words:           append([]string(nil), accumulator.signature.Words...),
			Values:          append([]int(nil), accumulator.signature.Values...),
			CorpusRefs:      refs,
			CorpusCount:     count,
			TotalCorpora:    total,
			ReplicationRate: ratio(count, total),
			Status:          replicationStatus(count, total),
		})
	}
	sort.Slice(instances, func(i, j int) bool {
		if instances[i].CorpusCount != instances[j].CorpusCount {
			return instances[i].CorpusCount > instances[j].CorpusCount
		}
		if instances[i].Type != instances[j].Type {
			return instances[i].Type < instances[j].Type
		}
		return instances[i].SignatureID < instances[j].SignatureID
	})

	typeRecurrence := make([]TypeRecurrence, 0, len(typeMap))
	for kind, corpusSet := range typeMap {
		refs := sortedSet(corpusSet)
		typeRecurrence = append(typeRecurrence, TypeRecurrence{
			Type:           kind,
			CorpusRefs:     refs,
			CorpusCount:    len(refs),
			TotalCorpora:   total,
			RecurrenceRate: ratio(len(refs), total),
		})
	}
	sort.Slice(typeRecurrence, func(i, j int) bool {
		if typeRecurrence[i].CorpusCount != typeRecurrence[j].CorpusCount {
			return typeRecurrence[i].CorpusCount > typeRecurrence[j].CorpusCount
		}
		return typeRecurrence[i].Type < typeRecurrence[j].Type
	})

	return MultiCorpusReport{
		SchemaVersion:  "gematria-glitch.multicorpus.v1",
		Protocol:       "GEMATRIA-GLITCH-1",
		GematriaSystem: system,
		Corpora:        comparisonCorpora,
		Instances:      instances,
		TypeRecurrence: typeRecurrence,
		Boundary: []string{
			"REPLICATION != PROOF",
			"RECURRENCE != CAUSATION",
			"REPEATED != UNIVERSAL",
			"CORPUS_DEPENDENCE != FALSEHOOD",
			"ABSENCE != DISPROOF",
		},
	}, nil
}

func canonicalFindingSignature(finding Finding) findingSignature {
	words := append([]string(nil), finding.Words...)
	values := append([]int(nil), finding.Values...)

	switch finding.Type {
	case "EXACT_COLLISION", "SHARED_PRIME_FACTOR":
		if len(words) >= 2 && len(values) >= 2 {
			type pair struct {
				word  string
				value int
			}
			pairs := []pair{
				{word: words[0], value: values[0]},
				{word: words[1], value: values[1]},
			}
			sort.Slice(pairs, func(i, j int) bool {
				if pairs[i].word != pairs[j].word {
					return pairs[i].word < pairs[j].word
				}
				return pairs[i].value < pairs[j].value
			})
			words[0], values[0] = pairs[0].word, pairs[0].value
			words[1], values[1] = pairs[1].word, pairs[1].value
		}
	}

	return findingSignature{
		Type:   finding.Type,
		Words:  words,
		Values: values,
	}
}

func findingSignatureID(signature findingSignature) (string, error) {
	data, err := json.Marshal(signature)
	if err != nil {
		return "", fmt.Errorf("marshal finding signature: %w", err)
	}
	sum := sha256.Sum256(data)
	return "sig:" + hex.EncodeToString(sum[:]), nil
}

func corpusRef(corpus Corpus) string {
	return corpus.CorpusID + "@" + corpus.Version
}

func ratio(numerator, denominator int) float64 {
	if denominator <= 0 {
		return 0
	}
	value := float64(numerator) / float64(denominator)
	return math.Round(value*1_000_000) / 1_000_000
}

func replicationStatus(count, total int) string {
	switch {
	case count <= 1:
		return "SINGLE_CORPUS"
	case count == total:
		return "REPLICATED_ALL_CORPORA"
	default:
		return "REPLICATED_SUBSET"
	}
}

func loadComparisonCorpora(pathsCSV string) ([]Corpus, error) {
	raw := strings.Split(pathsCSV, ",")
	paths := make([]string, 0, len(raw))
	for _, item := range raw {
		path := strings.TrimSpace(item)
		if path != "" {
			paths = append(paths, path)
		}
	}
	if len(paths) < 2 {
		return nil, fmt.Errorf("compare-inputs requires at least two comma-separated corpus paths")
	}
	if len(paths) > maxComparisonCorpora {
		return nil, fmt.Errorf("compare-inputs supports at most %d corpora", maxComparisonCorpora)
	}

	corpora := make([]Corpus, 0, len(paths))
	for _, path := range paths {
		corpus, err := loadCorpus(path)
		if err != nil {
			return nil, fmt.Errorf("%s: %w", path, err)
		}
		corpora = append(corpora, corpus)
	}
	return corpora, nil
}

func renderMultiCorpusGlitch(report MultiCorpusReport) string {
	var b strings.Builder
	b.WriteString("𓁹 Err ⃝or⃟⃤://MULTI_CORPUS_REPLICATION\n")
	fmt.Fprintf(&b, "CORPORA://%d\n", len(report.Corpora))
	fmt.Fprintf(&b, "SYSTEM://%s\n\n", report.GematriaSystem)

	for _, instance := range report.Instances {
		fmt.Fprintf(&b, "🧬⃟ REPLICATION://%s\n", instance.Status)
		fmt.Fprintf(&b, "TYPE://%s\n", instance.Type)
		fmt.Fprintf(&b, "WORDS://%s\n", strings.Join(instance.Words, " | "))
		fmt.Fprintf(&b, "VALUES://%v\n", instance.Values)
		fmt.Fprintf(&b, "CORPUS_SUPPORT://%d/%d\n", instance.CorpusCount, instance.TotalCorpora)
		fmt.Fprintf(&b, "REPLICATION_RATE://%.6f\n", instance.ReplicationRate)
		fmt.Fprintf(&b, "CORPORA://%s\n", strings.Join(instance.CorpusRefs, " | "))
		b.WriteString("REPLICATION != PROOF\n\n")
	}

	b.WriteString("𓂀 TYPE_RECURRENCE\n")
	for _, recurrence := range report.TypeRecurrence {
		fmt.Fprintf(
			&b,
			"%s://%d/%d | RATE=%.6f\n",
			recurrence.Type,
			recurrence.CorpusCount,
			recurrence.TotalCorpora,
			recurrence.RecurrenceRate,
		)
	}

	b.WriteString("\nREPEATED != UNIVERSAL\n")
	b.WriteString("ABSENCE != DISPROOF\n")
	b.WriteString("♡⃟ INTERPRETATION://HUMAN\n")
	return b.String()
}
