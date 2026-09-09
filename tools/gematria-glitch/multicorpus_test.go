package main

import "testing"

func TestMultiCorpusReplicationDetectsRepeatedInstances(t *testing.T) {
	first := demoCorpusEnvelope()
	second, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := compareCorpora([]Corpus{first, second})
	if err != nil {
		t.Fatal(err)
	}
	if len(report.Corpora) != 2 {
		t.Fatalf("corpus count = %d, want 2", len(report.Corpora))
	}

	collision := findReplicationInstance(report, "EXACT_COLLISION", "נחש", "משיח")
	if collision == nil {
		t.Fatal("expected replicated נחש and משיח exact collision")
	}
	if collision.CorpusCount != 2 || collision.TotalCorpora != 2 {
		t.Fatalf("collision support = %d/%d, want 2/2", collision.CorpusCount, collision.TotalCorpora)
	}
	if collision.Status != "REPLICATED_ALL_CORPORA" {
		t.Fatalf("collision status = %s", collision.Status)
	}
	if collision.ReplicationRate != 1 {
		t.Fatalf("collision replication rate = %f, want 1", collision.ReplicationRate)
	}

	factor := findReplicationInstance(report, "SHARED_PRIME_FACTOR", "שלום", "תורה")
	if factor == nil {
		t.Fatal("expected replicated שלום and תורה shared factor")
	}
	if factor.CorpusCount != 2 {
		t.Fatalf("shared factor corpus count = %d, want 2", factor.CorpusCount)
	}
}

func TestMultiCorpusReplicationKeepsCorpusSpecificInstances(t *testing.T) {
	first := demoCorpusEnvelope()
	second, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := compareCorpora([]Corpus{first, second})
	if err != nil {
		t.Fatal(err)
	}

	prefix := findReplicationInstance(report, "LINGUISTIC_PREFIX_DELTA", "נחש", "הנחש")
	if prefix == nil {
		t.Fatal("expected first-corpus prefix delta")
	}
	if prefix.Status != "SINGLE_CORPUS" || prefix.CorpusCount != 1 {
		t.Fatalf("prefix status = %s count=%d, want SINGLE_CORPUS count=1", prefix.Status, prefix.CorpusCount)
	}

	loveOne := findReplicationInstance(report, "EXACT_COLLISION", "אהבה", "אחד")
	if loveOne == nil {
		t.Fatal("expected first-corpus אהבה and אחד collision")
	}
	if loveOne.Status != "SINGLE_CORPUS" {
		t.Fatalf("love/one status = %s, want SINGLE_CORPUS", loveOne.Status)
	}
}

func TestMultiCorpusTypeRecurrenceDistinguishesClassFrequency(t *testing.T) {
	first := demoCorpusEnvelope()
	second, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}

	report, err := compareCorpora([]Corpus{first, second})
	if err != nil {
		t.Fatal(err)
	}

	exact := findTypeRecurrence(report, "EXACT_COLLISION")
	if exact == nil || exact.CorpusCount != 2 || exact.RecurrenceRate != 1 {
		t.Fatalf("unexpected exact collision recurrence: %+v", exact)
	}

	prefix := findTypeRecurrence(report, "LINGUISTIC_PREFIX_DELTA")
	if prefix == nil || prefix.CorpusCount != 1 || prefix.RecurrenceRate != 0.5 {
		t.Fatalf("unexpected prefix recurrence: %+v", prefix)
	}
}

func TestFindingSignatureCanonicalizesSymmetricPairs(t *testing.T) {
	left := Finding{
		Type:   "EXACT_COLLISION",
		Words:  []string{"נחש", "משיח"},
		Values: []int{358, 358},
	}
	right := Finding{
		Type:   "EXACT_COLLISION",
		Words:  []string{"משיח", "נחש"},
		Values: []int{358, 358},
	}

	leftID, err := findingSignatureID(canonicalFindingSignature(left))
	if err != nil {
		t.Fatal(err)
	}
	rightID, err := findingSignatureID(canonicalFindingSignature(right))
	if err != nil {
		t.Fatal(err)
	}
	if leftID != rightID {
		t.Fatalf("symmetric collision signatures differ: %s != %s", leftID, rightID)
	}
}

func TestMultiCorpusRejectsDuplicateCorpusIdentity(t *testing.T) {
	corpus := demoCorpusEnvelope()
	if _, err := compareCorpora([]Corpus{corpus, corpus}); err == nil {
		t.Fatal("duplicate corpus identity must be rejected")
	}
}

func TestMultiCorpusRejectsSingleCorpus(t *testing.T) {
	if _, err := compareCorpora([]Corpus{demoCorpusEnvelope()}); err == nil {
		t.Fatal("single-corpus comparison must be rejected")
	}
}

func TestMultiCorpusBoundaries(t *testing.T) {
	second, err := loadCorpus("../../datasets/gematria/demo-corpus.replication.v1.json")
	if err != nil {
		t.Fatal(err)
	}
	report, err := compareCorpora([]Corpus{demoCorpusEnvelope(), second})
	if err != nil {
		t.Fatal(err)
	}

	for _, boundary := range []string{
		"REPLICATION != PROOF",
		"RECURRENCE != CAUSATION",
		"REPEATED != UNIVERSAL",
		"CORPUS_DEPENDENCE != FALSEHOOD",
		"ABSENCE != DISPROOF",
	} {
		if !containsString(report.Boundary, boundary) {
			t.Errorf("missing comparison boundary %q", boundary)
		}
	}
}

func findReplicationInstance(report MultiCorpusReport, kind string, words ...string) *ReplicationInstance {
	for i := range report.Instances {
		instance := &report.Instances[i]
		if instance.Type != kind {
			continue
		}
		all := true
		for _, word := range words {
			if !containsString(instance.Words, word) {
				all = false
				break
			}
		}
		if all {
			return instance
		}
	}
	return nil
}

func findTypeRecurrence(report MultiCorpusReport, kind string) *TypeRecurrence {
	for i := range report.TypeRecurrence {
		if report.TypeRecurrence[i].Type == kind {
			return &report.TypeRecurrence[i]
		}
	}
	return nil
}
