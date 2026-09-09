package main

import "testing"

func TestGematriaKnownValues(t *testing.T) {
	cases := map[string]int{
		"נחש":  358,
		"משיח": 358,
		"הנחש": 363,
		"אהבה": 13,
		"אחד":  13,
		"אמת":  441,
		"אדם":  45,
		"לב":   32,
		"חכמה": 73,
		"שלום": 376,
		"תורה": 611,
		"אור":  207,
	}

	for word, want := range cases {
		if got := Gematria(word); got != want {
			t.Fatalf("Gematria(%q) = %d, want %d", word, got, want)
		}
	}
}

func TestCoreOddities(t *testing.T) {
	findings := Analyze(demoCorpus())

	required := map[string]bool{
		"EXACT_COLLISION":         false,
		"PALINDROME":              false,
		"PERFECT_SQUARE":          false,
		"TRIANGULAR_NUMBER":       false,
		"POWER_OF_TWO":            false,
		"PRIME_VALUE":             false,
		"DIGITAL_ROOT":            false,
		"SHARED_PRIME_FACTOR":     false,
		"LINGUISTIC_PREFIX_DELTA": false,
	}

	for _, f := range findings {
		if _, ok := required[f.Type]; ok {
			required[f.Type] = true
		}
	}

	for kind, found := range required {
		if !found {
			t.Errorf("expected finding type %s", kind)
		}
	}
}

func TestSpecificConnections(t *testing.T) {
	findings := Analyze(demoCorpus())

	if !hasFinding(findings, "EXACT_COLLISION", "נחש", "משיח") {
		t.Fatal("expected נחש and משיח exact collision")
	}
	if !hasFinding(findings, "EXACT_COLLISION", "אהבה", "אחד") {
		t.Fatal("expected אהבה and אחד exact collision")
	}
	if !hasFinding(findings, "PALINDROME", "הנחש") {
		t.Fatal("expected הנחש=363 palindrome")
	}
	if !hasFinding(findings, "SHARED_PRIME_FACTOR", "שלום", "תורה") {
		t.Fatal("expected שלום and תורה shared prime factor")
	}
	if !hasFinding(findings, "LINGUISTIC_PREFIX_DELTA", "נחש", "הנחש") {
		t.Fatal("expected נחש to הנחש prefix delta")
	}
}

func TestMathematicalClassifiers(t *testing.T) {
	if !isPerfectSquare(441) {
		t.Fatal("441 should be a perfect square")
	}
	if k, ok := triangularIndex(45); !ok || k != 9 {
		t.Fatalf("45 should be T(9), got k=%d ok=%v", k, ok)
	}
	if !isPowerOfTwo(32) {
		t.Fatal("32 should be a power of two")
	}
	if !isPrime(73) {
		t.Fatal("73 should be prime")
	}
	if got := digitalRoot(207); got != 9 {
		t.Fatalf("digitalRoot(207) = %d, want 9", got)
	}
}

func hasFinding(findings []Finding, kind string, words ...string) bool {
	for _, f := range findings {
		if f.Type != kind {
			continue
		}
		all := true
		for _, word := range words {
			found := false
			for _, candidate := range f.Words {
				if word == candidate {
					found = true
					break
				}
			}
			if !found {
				all = false
				break
			}
		}
		if all {
			return true
		}
	}
	return false
}
