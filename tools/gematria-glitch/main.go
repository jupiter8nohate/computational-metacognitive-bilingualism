package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"os"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"
)

type SourceRecord struct {
	ID        string `json:"id"`
	Kind      string `json:"kind"`
	Reference string `json:"reference"`
	URL       string `json:"url,omitempty"`
}

type Entry struct {
	ID     string       `json:"id,omitempty"`
	Word   string       `json:"word"`
	Gloss  string       `json:"gloss,omitempty"`
	Source SourceRecord `json:"source,omitempty"`
}

type Corpus struct {
	SchemaVersion  string  `json:"schema_version"`
	CorpusID       string  `json:"corpus_id"`
	Version        string  `json:"version"`
	GematriaSystem string  `json:"gematria_system"`
	Records        []Entry `json:"records"`
}

type ReceiptPayload struct {
	SchemaVersion   string   `json:"schema_version"`
	Protocol        string   `json:"protocol"`
	GematriaSystem  string   `json:"gematria_system"`
	CorpusID        string   `json:"corpus_id"`
	CorpusVersion   string   `json:"corpus_version"`
	CorpusSHA256    string   `json:"corpus_sha256"`
	SourceRecordIDs []string `json:"source_record_ids"`
	Finding         Finding  `json:"finding"`
	Boundary        []string `json:"boundary"`
}

type Receipt struct {
	Payload       ReceiptPayload `json:"payload"`
	ReceiptSHA256 string         `json:"receipt_sha256"`
}

type Finding struct {
	Type         string   `json:"type"`
	Words        []string `json:"words"`
	Values       []int    `json:"values"`
	Evidence     string   `json:"evidence"`
	Confidence   string   `json:"confidence"`
	Boundary     string   `json:"boundary"`
	GlitchGlyph  string   `json:"glitch_glyph"`
	SupportCount int      `json:"support_count"`
	SupportBasis int      `json:"support_basis"`
	RarityScore  float64  `json:"rarity_score"`
}

var gematriaValues = map[rune]int{
	'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
	'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
	'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100,
	'ר': 200, 'ש': 300, 'ת': 400,
}

var glyphForType = map[string]string{
	"EXACT_COLLISION":         "🧬⃟",
	"PALINDROME":              "𓁹",
	"PERFECT_SQUARE":          "◇⃟",
	"TRIANGULAR_NUMBER":       "△⃟",
	"POWER_OF_TWO":            "⚡⃟",
	"PRIME_VALUE":             "✦⃟",
	"DIGITAL_ROOT":            "꩜",
	"SHARED_PRIME_FACTOR":     "𓂀",
	"LINGUISTIC_PREFIX_DELTA": "𓁹⃤",
}

func Gematria(text string) int {
	total := 0
	for _, r := range text {
		total += gematriaValues[r]
	}
	return total
}

func reverseDigits(n int) int {
	s := strconv.Itoa(n)
	var b strings.Builder
	for i := len(s) - 1; i >= 0; i-- {
		b.WriteByte(s[i])
	}
	value, _ := strconv.Atoi(b.String())
	return value
}

func digitalRoot(n int) int {
	if n == 0 {
		return 0
	}
	for n >= 10 {
		sum := 0
		for n > 0 {
			sum += n % 10
			n /= 10
		}
		n = sum
	}
	return n
}

func isPrime(n int) bool {
	if n < 2 {
		return false
	}
	if n == 2 {
		return true
	}
	if n%2 == 0 {
		return false
	}
	limit := int(math.Sqrt(float64(n)))
	for d := 3; d <= limit; d += 2 {
		if n%d == 0 {
			return false
		}
	}
	return true
}

func isPerfectSquare(n int) bool {
	if n < 0 {
		return false
	}
	root := int(math.Sqrt(float64(n)))
	return root*root == n
}

func triangularIndex(n int) (int, bool) {
	if n < 1 {
		return 0, false
	}
	k := int((math.Sqrt(float64(8*n+1)) - 1) / 2)
	return k, k*(k+1)/2 == n
}

func isPowerOfTwo(n int) bool {
	return n > 0 && n&(n-1) == 0
}

func primeFactors(n int) []int {
	if n < 2 {
		return nil
	}
	factors := make([]int, 0)
	for d := 2; d*d <= n; d++ {
		for n%d == 0 {
			factors = append(factors, d)
			n /= d
		}
	}
	if n > 1 {
		factors = append(factors, n)
	}
	return factors
}

func uniquePrimeFactors(n int) map[int]struct{} {
	out := make(map[int]struct{})
	for _, factor := range primeFactors(n) {
		out[factor] = struct{}{}
	}
	return out
}

func finding(kind string, words []string, values []int, evidence string) Finding {
	return Finding{
		Type:        kind,
		Words:       words,
		Values:      values,
		Evidence:    evidence,
		Confidence:  "DETERMINISTIC_ARITHMETIC",
		Boundary:    "PATTERN != PROOF",
		GlitchGlyph: glyphForType[kind],
	}
}

func Analyze(entries []Entry) []Finding {
	values := make(map[string]int, len(entries))
	findings := make([]Finding, 0)

	for _, entry := range entries {
		value := Gematria(entry.Word)
		values[entry.Word] = value

		if value >= 10 && value == reverseDigits(value) {
			findings = append(findings, finding(
				"PALINDROME",
				[]string{entry.Word},
				[]int{value},
				fmt.Sprintf("%d == reverse(%d)", value, value),
			))
		}
		if isPerfectSquare(value) {
			root := int(math.Sqrt(float64(value)))
			findings = append(findings, finding(
				"PERFECT_SQUARE",
				[]string{entry.Word},
				[]int{value},
				fmt.Sprintf("%d = %d * %d", value, root, root),
			))
		}
		if k, ok := triangularIndex(value); ok {
			findings = append(findings, finding(
				"TRIANGULAR_NUMBER",
				[]string{entry.Word},
				[]int{value},
				fmt.Sprintf("T(%d) = %d", k, value),
			))
		}
		if isPowerOfTwo(value) {
			findings = append(findings, finding(
				"POWER_OF_TWO",
				[]string{entry.Word},
				[]int{value},
				fmt.Sprintf("%d = 2^%d", value, int(math.Log2(float64(value)))),
			))
		}
		if isPrime(value) {
			findings = append(findings, finding(
				"PRIME_VALUE",
				[]string{entry.Word},
				[]int{value},
				fmt.Sprintf("%d has no positive divisors other than 1 and itself", value),
			))
		}
		findings = append(findings, finding(
			"DIGITAL_ROOT",
			[]string{entry.Word},
			[]int{value, digitalRoot(value)},
			fmt.Sprintf("digital_root(%d) = %d", value, digitalRoot(value)),
		))
	}

	for i := 0; i < len(entries); i++ {
		for j := i + 1; j < len(entries); j++ {
			left := entries[i]
			right := entries[j]
			lv := values[left.Word]
			rv := values[right.Word]

			if lv == rv {
				findings = append(findings, finding(
					"EXACT_COLLISION",
					[]string{left.Word, right.Word},
					[]int{lv, rv},
					fmt.Sprintf("%s=%d and %s=%d", left.Word, lv, right.Word, rv),
				))
			}

			shared := sharedPrimeFactors(lv, rv)
			for _, factor := range shared {
				findings = append(findings, finding(
					"SHARED_PRIME_FACTOR",
					[]string{left.Word, right.Word},
					[]int{lv, rv, factor},
					fmt.Sprintf("%d and %d share prime factor %d", lv, rv, factor),
				))
			}

			if prefix, ok := singleRunePrefix(left.Word, right.Word); ok {
				delta := rv - lv
				prefixValue := Gematria(prefix)
				if delta == prefixValue {
					findings = append(findings, finding(
						"LINGUISTIC_PREFIX_DELTA",
						[]string{left.Word, right.Word, prefix},
						[]int{lv, rv, delta},
						fmt.Sprintf("%s + prefix %s(%d) = %s", left.Word, prefix, prefixValue, right.Word),
					))
				}
			}
			if prefix, ok := singleRunePrefix(right.Word, left.Word); ok {
				delta := lv - rv
				prefixValue := Gematria(prefix)
				if delta == prefixValue {
					findings = append(findings, finding(
						"LINGUISTIC_PREFIX_DELTA",
						[]string{right.Word, left.Word, prefix},
						[]int{rv, lv, delta},
						fmt.Sprintf("%s + prefix %s(%d) = %s", right.Word, prefix, prefixValue, left.Word),
					))
				}
			}
		}
	}

	annotateRarity(entries, findings)
	sort.SliceStable(findings, func(i, j int) bool {
		if findings[i].Type != findings[j].Type {
			return findings[i].Type < findings[j].Type
		}
		return strings.Join(findings[i].Words, "\x00") < strings.Join(findings[j].Words, "\x00")
	})
	return findings
}

func annotateRarity(entries []Entry, findings []Finding) {
	entryBasis := len(entries)
	if entryBasis < 1 {
		entryBasis = 1
	}
	pairBasis := len(entries) * (len(entries) - 1) / 2
	if pairBasis < 1 {
		pairBasis = 1
	}

	for i := range findings {
		f := &findings[i]
		support := 1
		basis := entryBasis

		switch f.Type {
		case "EXACT_COLLISION":
			target := f.Values[0]
			support = countEntries(entries, func(value int) bool { return value == target })
		case "PALINDROME":
			support = countEntries(entries, func(value int) bool {
				return value >= 10 && value == reverseDigits(value)
			})
		case "PERFECT_SQUARE":
			support = countEntries(entries, isPerfectSquare)
		case "TRIANGULAR_NUMBER":
			support = countEntries(entries, func(value int) bool {
				_, ok := triangularIndex(value)
				return ok
			})
		case "POWER_OF_TWO":
			support = countEntries(entries, isPowerOfTwo)
		case "PRIME_VALUE":
			support = countEntries(entries, isPrime)
		case "DIGITAL_ROOT":
			target := f.Values[1]
			support = countEntries(entries, func(value int) bool {
				return digitalRoot(value) == target
			})
		case "SHARED_PRIME_FACTOR":
			factor := f.Values[2]
			support = countEntries(entries, func(value int) bool {
				return factor > 1 && value%factor == 0
			})
		case "LINGUISTIC_PREFIX_DELTA":
			basis = pairBasis
			targetDelta := f.Values[2]
			support = countPrefixDeltaPairs(entries, targetDelta)
		}

		if support < 1 {
			support = 1
		}
		if support > basis {
			support = basis
		}
		f.SupportCount = support
		f.SupportBasis = basis
		f.RarityScore = math.Round((1-float64(support)/float64(basis))*1_000_000) / 1_000_000
	}
}

func countEntries(entries []Entry, predicate func(int) bool) int {
	count := 0
	for _, entry := range entries {
		if predicate(Gematria(entry.Word)) {
			count++
		}
	}
	return count
}

func countPrefixDeltaPairs(entries []Entry, targetDelta int) int {
	count := 0
	for i := 0; i < len(entries); i++ {
		for j := i + 1; j < len(entries); j++ {
			if prefixDeltaMatches(entries[i].Word, entries[j].Word, targetDelta) ||
				prefixDeltaMatches(entries[j].Word, entries[i].Word, targetDelta) {
				count++
			}
		}
	}
	return count
}

func prefixDeltaMatches(shorter, longer string, targetDelta int) bool {
	prefix, ok := singleRunePrefix(shorter, longer)
	if !ok {
		return false
	}
	return Gematria(longer)-Gematria(shorter) == targetDelta && Gematria(prefix) == targetDelta
}

func RankByRarity(findings []Finding) {
	sort.SliceStable(findings, func(i, j int) bool {
		if findings[i].RarityScore != findings[j].RarityScore {
			return findings[i].RarityScore > findings[j].RarityScore
		}
		if findings[i].Type != findings[j].Type {
			return findings[i].Type < findings[j].Type
		}
		return strings.Join(findings[i].Words, "\x00") < strings.Join(findings[j].Words, "\x00")
	})
}

func sharedPrimeFactors(a, b int) []int {
	left := uniquePrimeFactors(a)
	right := uniquePrimeFactors(b)
	shared := make([]int, 0)
	for factor := range left {
		if _, ok := right[factor]; ok {
			shared = append(shared, factor)
		}
	}
	sort.Ints(shared)
	return shared
}

func singleRunePrefix(shorter, longer string) (string, bool) {
	if utf8.RuneCountInString(longer) != utf8.RuneCountInString(shorter)+1 {
		return "", false
	}
	longerRunes := []rune(longer)
	shorterRunes := []rune(shorter)
	if string(longerRunes[1:]) != string(shorterRunes) {
		return "", false
	}
	return string(longerRunes[0]), true
}

func demoCorpus() []Entry {
	return demoCorpusEnvelope().Records
}

func demoCorpusEnvelope() Corpus {
	source := func(id string) SourceRecord {
		return SourceRecord{
			ID:        "demo-source-" + id,
			Kind:      "declared_demo",
			Reference: "GEMATRIA-GLITCH-1 demonstration corpus",
		}
	}
	return Corpus{
		SchemaVersion:  "gematria-glitch.corpus.v1",
		CorpusID:       "cmb.gematria.demo",
		Version:        "1.0.0",
		GematriaSystem: "mispar_hechrachi",
		Records: []Entry{
			{ID: "demo-001", Word: "נחש", Gloss: "serpent", Source: source("001")},
			{ID: "demo-002", Word: "משיח", Gloss: "anointed one", Source: source("002")},
			{ID: "demo-003", Word: "הנחש", Gloss: "the serpent", Source: source("003")},
			{ID: "demo-004", Word: "אהבה", Gloss: "love", Source: source("004")},
			{ID: "demo-005", Word: "אחד", Gloss: "one", Source: source("005")},
			{ID: "demo-006", Word: "אמת", Gloss: "truth", Source: source("006")},
			{ID: "demo-007", Word: "אדם", Gloss: "human", Source: source("007")},
			{ID: "demo-008", Word: "לב", Gloss: "heart", Source: source("008")},
			{ID: "demo-009", Word: "חכמה", Gloss: "wisdom", Source: source("009")},
			{ID: "demo-010", Word: "שלום", Gloss: "peace", Source: source("010")},
			{ID: "demo-011", Word: "תורה", Gloss: "Torah", Source: source("011")},
			{ID: "demo-012", Word: "אור", Gloss: "light", Source: source("012")},
		},
	}
}

func loadCorpus(path string) (Corpus, error) {
	if path == "" {
		return demoCorpusEnvelope(), nil
	}

	data, err := os.ReadFile(path)
	if err != nil {
		return Corpus{}, fmt.Errorf("read corpus: %w", err)
	}

	var corpus Corpus
	if err := json.Unmarshal(data, &corpus); err == nil && len(corpus.Records) > 0 {
		if err := validateCorpus(corpus); err != nil {
			return Corpus{}, err
		}
		return corpus, nil
	}

	var entries []Entry
	if err := json.Unmarshal(data, &entries); err != nil {
		return Corpus{}, fmt.Errorf("parse corpus: %w", err)
	}
	if len(entries) == 0 {
		return Corpus{}, fmt.Errorf("corpus must contain at least one entry")
	}
	for i := range entries {
		if entries[i].ID == "" {
			entries[i].ID = fmt.Sprintf("legacy-%03d", i+1)
		}
		if entries[i].Source.ID == "" {
			entries[i].Source = SourceRecord{
				ID:        fmt.Sprintf("legacy-source-%03d", i+1),
				Kind:      "legacy_array",
				Reference: "legacy JSON array input",
			}
		}
	}
	corpus = Corpus{
		SchemaVersion:  "gematria-glitch.corpus.v1",
		CorpusID:       "legacy.local",
		Version:        "1",
		GematriaSystem: "mispar_hechrachi",
		Records:        entries,
	}
	if err := validateCorpus(corpus); err != nil {
		return Corpus{}, err
	}
	return corpus, nil
}

func validateCorpus(corpus Corpus) error {
	if corpus.SchemaVersion != "gematria-glitch.corpus.v1" {
		return fmt.Errorf("unsupported corpus schema_version %q", corpus.SchemaVersion)
	}
	if strings.TrimSpace(corpus.CorpusID) == "" {
		return fmt.Errorf("corpus_id is required")
	}
	if strings.TrimSpace(corpus.Version) == "" {
		return fmt.Errorf("corpus version is required")
	}
	if corpus.GematriaSystem != "mispar_hechrachi" {
		return fmt.Errorf("unsupported gematria_system %q", corpus.GematriaSystem)
	}
	if len(corpus.Records) == 0 {
		return fmt.Errorf("corpus must contain at least one record")
	}

	entryIDs := make(map[string]struct{}, len(corpus.Records))
	sourceIDs := make(map[string]struct{}, len(corpus.Records))
	for i, entry := range corpus.Records {
		if strings.TrimSpace(entry.ID) == "" {
			return fmt.Errorf("record %d has an empty id", i)
		}
		if _, exists := entryIDs[entry.ID]; exists {
			return fmt.Errorf("duplicate record id %q", entry.ID)
		}
		entryIDs[entry.ID] = struct{}{}

		if strings.TrimSpace(entry.Word) == "" {
			return fmt.Errorf("record %q has an empty word", entry.ID)
		}
		if strings.TrimSpace(entry.Source.ID) == "" {
			return fmt.Errorf("record %q has an empty source id", entry.ID)
		}
		if strings.TrimSpace(entry.Source.Kind) == "" {
			return fmt.Errorf("record %q has an empty source kind", entry.ID)
		}
		if strings.TrimSpace(entry.Source.Reference) == "" {
			return fmt.Errorf("record %q has an empty source reference", entry.ID)
		}
		if _, exists := sourceIDs[entry.Source.ID]; exists {
			return fmt.Errorf("duplicate source id %q", entry.Source.ID)
		}
		sourceIDs[entry.Source.ID] = struct{}{}
	}
	return nil
}

func corpusDigest(corpus Corpus) (string, error) {
	data, err := json.Marshal(corpus)
	if err != nil {
		return "", fmt.Errorf("marshal corpus: %w", err)
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func sourceRecordIDs(f Finding, entries []Entry) []string {
	ids := make(map[string]struct{})
	for _, word := range f.Words {
		for _, entry := range entries {
			if entry.Word == word && entry.Source.ID != "" {
				ids[entry.Source.ID] = struct{}{}
			}
		}
	}
	out := make([]string, 0, len(ids))
	for id := range ids {
		out = append(out, id)
	}
	sort.Strings(out)
	return out
}

func buildReceipts(corpus Corpus, findings []Finding) ([]Receipt, error) {
	digest, err := corpusDigest(corpus)
	if err != nil {
		return nil, err
	}

	receipts := make([]Receipt, 0, len(findings))
	for _, f := range findings {
		payload := ReceiptPayload{
			SchemaVersion:   "gematria-glitch.receipt.v1",
			Protocol:        "GEMATRIA-GLITCH-1",
			GematriaSystem:  corpus.GematriaSystem,
			CorpusID:        corpus.CorpusID,
			CorpusVersion:   corpus.Version,
			CorpusSHA256:    digest,
			SourceRecordIDs: sourceRecordIDs(f, corpus.Records),
			Finding:         f,
			Boundary: []string{
				"PATTERN != PROOF",
				"RARITY != SIGNIFICANCE",
				"RECEIPT != TRUTH",
			},
		}
		hash, err := receiptDigest(payload)
		if err != nil {
			return nil, err
		}
		receipts = append(receipts, Receipt{
			Payload:       payload,
			ReceiptSHA256: hash,
		})
	}
	return receipts, nil
}

func receiptDigest(payload ReceiptPayload) (string, error) {
	data, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("marshal receipt payload: %w", err)
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func verifyReceipt(receipt Receipt) error {
	if receipt.Payload.SchemaVersion != "gematria-glitch.receipt.v1" {
		return fmt.Errorf("unsupported receipt schema_version %q", receipt.Payload.SchemaVersion)
	}
	if receipt.Payload.Protocol != "GEMATRIA-GLITCH-1" {
		return fmt.Errorf("unsupported receipt protocol %q", receipt.Payload.Protocol)
	}
	expected, err := receiptDigest(receipt.Payload)
	if err != nil {
		return err
	}
	if expected != receipt.ReceiptSHA256 {
		return fmt.Errorf("receipt digest mismatch: got %s want %s", receipt.ReceiptSHA256, expected)
	}
	return nil
}

func verifyReceiptAgainstCorpus(receipt Receipt, corpus Corpus) error {
	if err := verifyReceipt(receipt); err != nil {
		return err
	}
	if err := validateCorpus(corpus); err != nil {
		return err
	}

	digest, err := corpusDigest(corpus)
	if err != nil {
		return err
	}
	if receipt.Payload.CorpusSHA256 != digest {
		return fmt.Errorf("corpus digest mismatch")
	}
	if receipt.Payload.CorpusID != corpus.CorpusID {
		return fmt.Errorf("corpus id mismatch")
	}
	if receipt.Payload.CorpusVersion != corpus.Version {
		return fmt.Errorf("corpus version mismatch")
	}
	if receipt.Payload.GematriaSystem != corpus.GematriaSystem {
		return fmt.Errorf("gematria system mismatch")
	}

	expectedSources := sourceRecordIDs(receipt.Payload.Finding, corpus.Records)
	if !sameStrings(receipt.Payload.SourceRecordIDs, expectedSources) {
		return fmt.Errorf("source record ids do not match corpus")
	}

	recomputed := Analyze(corpus.Records)
	if !containsFinding(recomputed, receipt.Payload.Finding) {
		return fmt.Errorf("finding is not reproducible from corpus")
	}
	return nil
}

func sameStrings(left, right []string) bool {
	if len(left) != len(right) {
		return false
	}
	for i := range left {
		if left[i] != right[i] {
			return false
		}
	}
	return true
}

func containsFinding(findings []Finding, target Finding) bool {
	targetJSON, err := json.Marshal(target)
	if err != nil {
		return false
	}
	for _, candidate := range findings {
		candidateJSON, err := json.Marshal(candidate)
		if err == nil && string(candidateJSON) == string(targetJSON) {
			return true
		}
	}
	return false
}

func verifyReceiptFile(path string, corpus *Corpus) (int, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return 0, fmt.Errorf("read receipts: %w", err)
	}
	var receipts []Receipt
	if err := json.Unmarshal(data, &receipts); err != nil {
		return 0, fmt.Errorf("parse receipts: %w", err)
	}
	if len(receipts) == 0 {
		return 0, fmt.Errorf("receipt file contains no receipts")
	}
	for i, receipt := range receipts {
		var err error
		if corpus == nil {
			err = verifyReceipt(receipt)
		} else {
			err = verifyReceiptAgainstCorpus(receipt, *corpus)
		}
		if err != nil {
			return 0, fmt.Errorf("receipt %d: %w", i, err)
		}
	}
	return len(receipts), nil
}

func renderGlitch(findings []Finding) string {
	var b strings.Builder
	b.WriteString("𓁹 Err ⃝or⃟⃤://GEMATRIA_GLITCH_SCAN\n")
	b.WriteString("BOUNDARY://PATTERN != PROOF\n\n")
	for _, f := range findings {
		fmt.Fprintf(&b, "%s %s://%s\n", f.GlitchGlyph, "ODDITY", f.Type)
		fmt.Fprintf(&b, "WORDS://%s\n", strings.Join(f.Words, " | "))
		fmt.Fprintf(&b, "VALUES://%v\n", f.Values)
		fmt.Fprintf(&b, "EVIDENCE://%s\n", f.Evidence)
		fmt.Fprintf(&b, "SUPPORT://%d/%d\n", f.SupportCount, f.SupportBasis)
		fmt.Fprintf(&b, "RARITY_SCORE://%.6f\n", f.RarityScore)
		b.WriteString("RARITY != SIGNIFICANCE\n")
		b.WriteString("INTERPRETATION://HUMAN\n")
		b.WriteString("PROOF_OF_DESTINY://FALSE\n\n")
	}
	b.WriteString("𓁹 CHECKSUM://NUMBER_CAN_CONNECT | NUMBER_CANNOT_COMMAND_MEANING\n")
	return b.String()
}

func main() {
	inputPath := flag.String("input", "", "path to a JSON corpus; defaults to the built-in demonstration corpus")
	format := flag.String("format", "glitch", "output format: glitch, json, receipts, or graph")
	rank := flag.Bool("rank", false, "rank findings by corpus rarity score")
	verifyReceipts := flag.String("verify-receipts", "", "verify a JSON receipt array and exit")
	verifyGraph := flag.String("verify-graph", "", "verify a JSON anomaly graph and exit")
	pathFrom := flag.String("path-from", "", "path query start selector: exact node id or Hebrew record word")
	pathTo := flag.String("path-to", "", "path query destination selector: exact node id or Hebrew record word")
	pathDepth := flag.Int("path-depth", 3, "maximum path query depth from 1 to 8")
	pathLimit := flag.Int("path-limit", 5, "maximum returned paths from 1 to 50")
	pathFormat := flag.String("path-format", "glitch", "path query output format: glitch or json")
	flag.Parse()

	if *verifyReceipts != "" && *verifyGraph != "" {
		fmt.Fprintln(os.Stderr, "error: verify-receipts and verify-graph are mutually exclusive")
		os.Exit(2)
	}

	if (*pathFrom == "") != (*pathTo == "") {
		fmt.Fprintln(os.Stderr, "error: path-from and path-to must be supplied together")
		os.Exit(2)
	}
	if *pathFrom != "" && (*verifyReceipts != "" || *verifyGraph != "") {
		fmt.Fprintln(os.Stderr, "error: path query cannot be combined with verification modes")
		os.Exit(2)
	}

	if *verifyGraph != "" {
		var corpus *Corpus
		if *inputPath != "" {
			loaded, err := loadCorpus(*inputPath)
			if err != nil {
				fmt.Fprintln(os.Stderr, "error:", err)
				os.Exit(2)
			}
			corpus = &loaded
		}
		if err := verifyGraphFile(*verifyGraph, corpus); err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
		if corpus == nil {
			fmt.Println("VERIFIED://GRAPH | MODE://SELF_CONSISTENCY")
		} else {
			fmt.Println("VERIFIED://GRAPH | MODE://CORPUS_BOUND")
		}
		return
	}

	if *verifyReceipts != "" {
		var corpus *Corpus
		if *inputPath != "" {
			loaded, err := loadCorpus(*inputPath)
			if err != nil {
				fmt.Fprintln(os.Stderr, "error:", err)
				os.Exit(2)
			}
			corpus = &loaded
		}
		count, err := verifyReceiptFile(*verifyReceipts, corpus)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
		if corpus == nil {
			fmt.Printf("VERIFIED://%d RECEIPTS | MODE://SELF_CONSISTENCY\n", count)
		} else {
			fmt.Printf("VERIFIED://%d RECEIPTS | MODE://CORPUS_BOUND\n", count)
		}
		return
	}

	corpus, err := loadCorpus(*inputPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(2)
	}

	findings := Analyze(corpus.Records)
	if *rank {
		RankByRarity(findings)
	}

	if *pathFrom != "" {
		graph, err := buildKnowledgeGraph(corpus)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
		result, err := queryKnowledgeGraph(graph, PathQuery{
			From:     *pathFrom,
			To:       *pathTo,
			MaxDepth: *pathDepth,
			MaxPaths: *pathLimit,
		})
		if err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
		switch *pathFormat {
		case "glitch":
			fmt.Print(renderPathQueryGlitch(result))
		case "json":
			encoder := json.NewEncoder(os.Stdout)
			encoder.SetIndent("", "  ")
			if err := encoder.Encode(result); err != nil {
				fmt.Fprintln(os.Stderr, "error:", err)
				os.Exit(2)
			}
		default:
			fmt.Fprintln(os.Stderr, "error: path-format must be glitch or json")
			os.Exit(2)
		}
		return
	}

	switch *format {
	case "glitch":
		fmt.Print(renderGlitch(findings))
	case "json":
		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "  ")
		if err := encoder.Encode(findings); err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
	case "receipts":
		receipts, err := buildReceipts(corpus, findings)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "  ")
		if err := encoder.Encode(receipts); err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
	case "graph":
		graph, err := buildKnowledgeGraph(corpus)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "  ")
		if err := encoder.Encode(graph); err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			os.Exit(2)
		}
	default:
		fmt.Fprintln(os.Stderr, "error: format must be glitch, json, receipts, or graph")
		os.Exit(2)
	}
}
