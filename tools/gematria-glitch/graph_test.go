package main

import (
	"encoding/json"
	"testing"
)

func TestKnowledgeGraphDeterminism(t *testing.T) {
	corpus := demoCorpusEnvelope()

	first, err := buildKnowledgeGraph(corpus)
	if err != nil {
		t.Fatal(err)
	}
	second, err := buildKnowledgeGraph(corpus)
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
		t.Fatal("knowledge graph generation must be deterministic")
	}
	if err := verifyKnowledgeGraph(first); err != nil {
		t.Fatalf("generated graph failed verification: %v", err)
	}
}

func TestKnowledgeGraphTypedEdges(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	required := []string{
		"CONTAINS_RECORD",
		"SOURCED_BY",
		"HAS_GEMATRIA_VALUE",
		"HAS_PRIME_FACTOR",
		"DERIVED_FROM_CORPUS",
		"ASSERTS_ANOMALY",
		"REFERENCES_SOURCE",
		"INVOLVES_RECORD",
		"HAS_ANOMALY",
		"EXACT_COLLISION_WITH",
		"SHARES_PRIME_FACTOR_WITH",
		"LINGUISTIC_PREFIX_DELTA_TO",
	}

	for _, relation := range required {
		if !graphHasRelation(graph, relation) {
			t.Errorf("expected graph relation %s", relation)
		}
	}
}

func TestKnowledgeGraphHasTraceableFactorChain(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	if !graphHasEdge(graph, "record:demo-010", "HAS_GEMATRIA_VALUE", "value:376") {
		t.Fatal("expected peace record to connect to Gematria value 376")
	}
	if !graphHasEdge(graph, "value:376", "HAS_PRIME_FACTOR", "factor:47") {
		t.Fatal("expected 376 to connect to prime factor 47")
	}
	if !graphHasEdge(graph, "record:demo-010", "SOURCED_BY", "source:demo-source-010") {
		t.Fatal("expected peace record to retain source trace")
	}
	if !graphHasEdge(graph, "record:demo-010", "SHARES_PRIME_FACTOR_WITH", "record:demo-011") {
		t.Fatal("expected peace and Torah records to share a receipt-backed factor edge")
	}
}

func TestSemanticGraphEdgesAreReceiptBacked(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	semantic := map[string]bool{
		"HAS_ANOMALY":                 true,
		"EXACT_COLLISION_WITH":        true,
		"SHARES_PRIME_FACTOR_WITH":    true,
		"LINGUISTIC_PREFIX_DELTA_TO":  true,
		"ASSERTS_ANOMALY":             true,
		"REFERENCES_SOURCE":           true,
		"INVOLVES_RECORD":             true,
		"DERIVED_FROM_CORPUS":         true,
	}

	for _, edge := range graph.Payload.Edges {
		if !semantic[edge.Relation] {
			continue
		}
		if edge.ReceiptSHA256 == "" {
			t.Fatalf("semantic edge %s must be receipt-backed", edge.ID)
		}
		if !graphHasNode(graph, "receipt:"+edge.ReceiptSHA256) {
			t.Fatalf("semantic edge %s references missing receipt node", edge.ID)
		}
	}
}

func TestKnowledgeGraphTamperDetection(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}
	if len(graph.Payload.Edges) == 0 {
		t.Fatal("expected graph edges")
	}

	graph.Payload.Edges[0].Evidence += " tampered"
	if err := verifyKnowledgeGraph(graph); err == nil {
		t.Fatal("tampered graph must fail verification")
	}
}

func TestKnowledgeGraphCorpusBoundVerification(t *testing.T) {
	corpus := demoCorpusEnvelope()
	graph, err := buildKnowledgeGraph(corpus)
	if err != nil {
		t.Fatal(err)
	}

	if err := verifyKnowledgeGraphAgainstCorpus(graph, corpus); err != nil {
		t.Fatalf("graph should verify against source corpus: %v", err)
	}

	changed := corpus
	changed.Version = "1.0.1"
	if err := verifyKnowledgeGraphAgainstCorpus(graph, changed); err == nil {
		t.Fatal("graph must fail against a changed corpus version")
	}
}

func TestKnowledgeGraphBoundaries(t *testing.T) {
	graph, err := buildKnowledgeGraph(demoCorpusEnvelope())
	if err != nil {
		t.Fatal(err)
	}

	for _, boundary := range []string{
		"PATTERN != PROOF",
		"RARITY != SIGNIFICANCE",
		"RECEIPT != TRUTH",
		"GRAPH != PROOF",
		"EDGE != CAUSATION",
		"CONNECTED != IDENTICAL",
	} {
		if !containsString(graph.Payload.Boundary, boundary) {
			t.Errorf("missing graph boundary %q", boundary)
		}
	}
}

func graphHasRelation(graph KnowledgeGraph, relation string) bool {
	for _, edge := range graph.Payload.Edges {
		if edge.Relation == relation {
			return true
		}
	}
	return false
}

func graphHasEdge(graph KnowledgeGraph, from, relation, to string) bool {
	for _, edge := range graph.Payload.Edges {
		if edge.From == from && edge.Relation == relation && edge.To == to {
			return true
		}
	}
	return false
}

func graphHasNode(graph KnowledgeGraph, id string) bool {
	for _, node := range graph.Payload.Nodes {
		if node.ID == id {
			return true
		}
	}
	return false
}
