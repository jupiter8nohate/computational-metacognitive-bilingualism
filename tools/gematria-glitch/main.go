package main

import (
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

type Entry struct {
	Word  string `json:"word"`
	Gloss string `json:"gloss,omitempty"`
}

type Finding struct {
	Type        string   `json:"type"`
	Words       []string `json:"words"`
	Values      []int    `json:"values"`
	Evidence    string   `json:"evidence"`
	Confidence  string   `json:"confidence"`
	Boundary    string   `json:"boundary"`
	GlitchGlyph string   `json:"glitch_glyph"`
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

	sort.SliceStable(findings, func(i, j int) bool {
		if findings[i].Type != findings[j].Type {
			return findings[i].Type < findings[j].Type
		}
		return strings.Join(findings[i].Words, "\x00") < strings.Join(findings[j].Words, "\x00")
	})
	return findings
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
	return []Entry{
		{Word: "נחש", Gloss: "serpent"},
		{Word: "משיח", Gloss: "anointed one"},
		{Word: "הנחש", Gloss: "the serpent"},
		{Word: "אהבה", Gloss: "love"},
		{Word: "אחד", Gloss: "one"},
		{Word: "אמת", Gloss: "truth"},
		{Word: "אדם", Gloss: "human"},
		{Word: "לב", Gloss: "heart"},
		{Word: "חכמה", Gloss: "wisdom"},
		{Word: "שלום", Gloss: "peace"},
		{Word: "תורה", Gloss: "Torah"},
		{Word: "אור", Gloss: "light"},
	}
}

func loadEntries(path string) ([]Entry, error) {
	if path == "" {
		return demoCorpus(), nil
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read corpus: %w", err)
	}
	var entries []Entry
	if err := json.Unmarshal(data, &entries); err != nil {
		return nil, fmt.Errorf("parse corpus: %w", err)
	}
	if len(entries) == 0 {
		return nil, fmt.Errorf("corpus must contain at least one entry")
	}
	for i, entry := range entries {
		if strings.TrimSpace(entry.Word) == "" {
			return nil, fmt.Errorf("entry %d has an empty word", i)
		}
	}
	return entries, nil
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
		b.WriteString("INTERPRETATION://HUMAN\n")
		b.WriteString("PROOF_OF_DESTINY://FALSE\n\n")
	}
	b.WriteString("𓁹 CHECKSUM://NUMBER_CAN_CONNECT | NUMBER_CANNOT_COMMAND_MEANING\n")
	return b.String()
}

func main() {
	inputPath := flag.String("input", "", "path to a JSON corpus; defaults to the built-in demonstration corpus")
	format := flag.String("format", "glitch", "output format: glitch or json")
	flag.Parse()

	entries, err := loadEntries(*inputPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(2)
	}

	findings := Analyze(entries)

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
	default:
		fmt.Fprintln(os.Stderr, "error: format must be glitch or json")
		os.Exit(2)
	}
}
