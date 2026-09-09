package main

import "testing"

func TestPathQueryResolvesHebrewWords(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	result, err := queryKnowledgeGraph(graph, PathQuery{
		From:     "נחש",
		To:       "משיח",
		MaxDepth: 2,
		MaxPaths: 10,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(result.ResolvedFrom) != 1 || result.ResolvedFrom[0] != "record:demo-001" {
		t.Fatalf("unexpected from resolution: %v", result.ResolvedFrom)
	}
	if len(result.ResolvedTo) != 1 || result.ResolvedTo[0] != "record:demo-002" {
		t.Fatalf("unexpected to resolution: %v", result.ResolvedTo)
	}
	if len(result.Paths) < 2 {
		t.Fatalf("expected at least two paths, got %d", len(result.Paths))
	}
}

func TestPathRankingPrefersDirectStructuralEvidenceFloor(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	result, err := queryKnowledgeGraph(graph, PathQuery{
		From:     "נחש",
		To:       "משיח",
		MaxDepth: 2,
		MaxPaths: 10,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Paths) == 0 {
		t.Fatal("expected paths")
	}

	first := result.Paths[0]
	if first.EvidenceFloor != 4 {
		t.Fatalf("first path evidence floor = %d, want 4", first.EvidenceFloor)
	}
	if first.HopCount != 2 {
		t.Fatalf("first path hops = %d, want 2", first.HopCount)
	}
	if !pathHasNode(first, "value:358") {
		t.Fatalf("expected strongest path through value:358, got %v", first.Nodes)
	}

	foundReceiptBackedDirect := false
	for _, path := range result.Paths {
		if path.HopCount == 1 && path.EvidenceFloor == 3 {
			foundReceiptBackedDirect = true
			if len(path.ReceiptSHA256s) == 0 {
				t.Fatal("receipt-backed direct path missing receipt trace")
			}
		}
	}
	if !foundReceiptBackedDirect {
		t.Fatal("expected one-hop receipt-backed collision path")
	}
}

func TestPathQueryCarriesSourceTrace(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	result, err := queryKnowledgeGraph(graph, PathQuery{
		From:     "שלום",
		To:       "תורה",
		MaxDepth: 4,
		MaxPaths: 10,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Paths) == 0 {
		t.Fatal("expected paths between שלום and תורה")
	}

	foundFactorPath := false
	for _, path := range result.Paths {
		if pathHasNode(path, "factor:47") {
			foundFactorPath = true
			if !containsString(path.SourceNodeIDs, "source:demo-source-010") {
				t.Fatalf("factor path missing source trace for שלום: %v", path.SourceNodeIDs)
			}
			if !containsString(path.SourceNodeIDs, "source:demo-source-011") {
				t.Fatalf("factor path missing source trace for תורה: %v", path.SourceNodeIDs)
			}
		}
	}
	if !foundFactorPath {
		t.Fatal("expected shared factor 47 path")
	}
}

func TestPathQueryDeterminism(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}
	query := PathQuery{
		From:     "אהבה",
		To:       "אחד",
		MaxDepth: 2,
		MaxPaths: 10,
	}

	first, err := queryKnowledgeGraph(graph, query)
	if err != nil {
		t.Fatal(err)
	}
	second, err := queryKnowledgeGraph(graph, query)
	if err != nil {
		t.Fatal(err)
	}
	if len(first.Paths) != len(second.Paths) {
		t.Fatal("deterministic query returned different path counts")
	}
	for i := range first.Paths {
		if first.Paths[i].PathID != second.Paths[i].PathID {
			t.Fatalf("path order drift at index %d", i)
		}
	}
}

func TestPathQueryNoPathBoundary(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	result, err := queryKnowledgeGraph(graph, PathQuery{
		From:     "אהבה",
		To:       "אמת",
		MaxDepth: 1,
		MaxPaths: 5,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Paths) != 0 {
		t.Fatalf("expected no one-hop path, got %d", len(result.Paths))
	}
	if !containsString(result.Boundary, "NO_PATH != NO_RELATIONSHIP") {
		t.Fatal("missing no-path epistemic boundary")
	}
}

func TestPathQueryRejectsUnboundedRequests(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	for _, query := range []PathQuery{
		{From: "נחש", To: "משיח", MaxDepth: 0, MaxPaths: 5},
		{From: "נחש", To: "משיח", MaxDepth: 9, MaxPaths: 5},
		{From: "נחש", To: "משיח", MaxDepth: 2, MaxPaths: 0},
		{From: "נחש", To: "משיח", MaxDepth: 2, MaxPaths: 51},
	} {
		if _, err := queryKnowledgeGraph(graph, query); err == nil {
			t.Fatalf("expected bounded query rejection: %+v", query)
		}
	}
}

func TestPathQueryRejectsUnknownSelector(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	_, err = queryKnowledgeGraph(graph, PathQuery{
		From:     "לא-קיים",
		To:       "משיח",
		MaxDepth: 2,
		MaxPaths: 5,
	})
	if err == nil {
		t.Fatal("unknown selector must fail")
	}
}

func pathHasNode(path GraphPath, nodeID string) bool {
	for _, candidate := range path.Nodes {
		if candidate == nodeID {
			return true
		}
	}
	return false
}

func TestPathQueryDoesNotUseCorpusAsUniversalShortcut(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	result, err := queryKnowledgeGraph(graph, PathQuery{
		From:     "אהבה",
		To:       "אמת",
		MaxDepth: 2,
		MaxPaths: 10,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Paths) != 0 {
		t.Fatalf("corpus membership must not create a path between unrelated records: %v", result.Paths)
	}
}
