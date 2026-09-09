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

func TestRarityAnnotation(t *testing.T) {
	findings := Analyze(demoCorpus())

	collision := findFinding(findings, "EXACT_COLLISION", "נחש", "משיח")
	if collision == nil {
		t.Fatal("expected נחש and משיח exact collision")
	}
	if collision.SupportCount != 2 || collision.SupportBasis != len(demoCorpus()) {
		t.Fatalf("collision support = %d/%d, want 2/%d", collision.SupportCount, collision.SupportBasis, len(demoCorpus()))
	}
	if collision.RarityScore <= 0 || collision.RarityScore >= 1 {
		t.Fatalf("collision rarity score = %f, want value strictly between 0 and 1", collision.RarityScore)
	}

	prefix := findFinding(findings, "LINGUISTIC_PREFIX_DELTA", "נחש", "הנחש")
	if prefix == nil {
		t.Fatal("expected prefix delta finding")
	}
	wantPairs := len(demoCorpus()) * (len(demoCorpus()) - 1) / 2
	if prefix.SupportBasis != wantPairs {
		t.Fatalf("prefix support basis = %d, want %d", prefix.SupportBasis, wantPairs)
	}
}

func TestRankByRarity(t *testing.T) {
	findings := Analyze(demoCorpus())
	RankByRarity(findings)

	for i := 1; i < len(findings); i++ {
		if findings[i-1].RarityScore < findings[i].RarityScore {
			t.Fatalf("rarity ranking increased at index %d: %f < %f", i, findings[i-1].RarityScore, findings[i].RarityScore)
		}
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

func findFinding(findings []Finding, kind string, words ...string) *Finding {
	for i := range findings {
		f := &findings[i]
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
			return f
		}
	}
	return nil
}

func hasFinding(findings []Finding, kind string, words ...string) bool {
	return findFinding(findings, kind, words...) != nil
}
