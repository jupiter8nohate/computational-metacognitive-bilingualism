package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

type GraphNode struct {
	ID              string `json:"id"`
	Kind            string `json:"kind"`
	Label           string `json:"label"`
	Word            string `json:"word,omitempty"`
	Gloss           string `json:"gloss,omitempty"`
	Value           int    `json:"value,omitempty"`
	Factor          int    `json:"factor,omitempty"`
	AnomalyType     string `json:"anomaly_type,omitempty"`
	ReceiptSHA256   string `json:"receipt_sha256,omitempty"`
	SourceKind      string `json:"source_kind,omitempty"`
	SourceReference string `json:"source_reference,omitempty"`
	SourceURL       string `json:"source_url,omitempty"`
}

type GraphEdge struct {
	ID            string `json:"id"`
	From          string `json:"from"`
	Relation      string `json:"relation"`
	To            string `json:"to"`
	ReceiptSHA256 string `json:"receipt_sha256,omitempty"`
	Evidence      string `json:"evidence,omitempty"`
	NumericValue  int    `json:"numeric_value,omitempty"`
}

type GraphPayload struct {
	SchemaVersion  string      `json:"schema_version"`
	Protocol       string      `json:"protocol"`
	CorpusID       string      `json:"corpus_id"`
	CorpusVersion  string      `json:"corpus_version"`
	CorpusSHA256   string      `json:"corpus_sha256"`
	GematriaSystem string      `json:"gematria_system"`
	Nodes          []GraphNode `json:"nodes"`
	Edges          []GraphEdge `json:"edges"`
	Boundary       []string    `json:"boundary"`
}

type KnowledgeGraph struct {
	Payload     GraphPayload `json:"payload"`
	GraphSHA256 string       `json:"graph_sha256"`
}

var allowedGraphRelations = map[string]struct{}{
	"CONTAINS_RECORD":           {},
	"SOURCED_BY":                {},
	"HAS_GEMATRIA_VALUE":        {},
	"HAS_PRIME_FACTOR":          {},
	"DERIVED_FROM_CORPUS":       {},
	"ASSERTS_ANOMALY":           {},
	"REFERENCES_SOURCE":         {},
	"INVOLVES_RECORD":           {},
	"HAS_ANOMALY":               {},
	"EXACT_COLLISION_WITH":      {},
	"SHARES_PRIME_FACTOR_WITH":  {},
	"LINGUISTIC_PREFIX_DELTA_TO": {},
}

var receiptBackedGraphRelations = map[string]struct{}{
	"DERIVED_FROM_CORPUS":        {},
	"ASSERTS_ANOMALY":            {},
	"REFERENCES_SOURCE":          {},
	"INVOLVES_RECORD":            {},
	"HAS_ANOMALY":                {},
	"EXACT_COLLISION_WITH":       {},
	"SHARES_PRIME_FACTOR_WITH":   {},
	"LINGUISTIC_PREFIX_DELTA_TO": {},
}

func setGraphNode(nodes map[string]GraphNode, node GraphNode) error {
	if existing, ok := nodes[node.ID]; ok {
		if existing != node {
			return fmt.Errorf("graph node id collision: %s", node.ID)
		}
		return nil
	}
	nodes[node.ID] = node
	return nil
}

func buildKnowledgeGraph(corpus Corpus) (KnowledgeGraph, error) {
	if err := validateCorpus(corpus); err != nil {
		return KnowledgeGraph{}, err
	}

	findings := Analyze(corpus.Records)
	receipts, err := buildReceipts(corpus, findings)
	if err != nil {
		return KnowledgeGraph{}, err
	}
	for i, receipt := range receipts {
		if err := verifyReceiptAgainstCorpus(receipt, corpus); err != nil {
			return KnowledgeGraph{}, fmt.Errorf("receipt %d failed graph admission: %w", i, err)
		}
	}

	corpusSHA256, err := corpusDigest(corpus)
	if err != nil {
		return KnowledgeGraph{}, err
	}

	nodes := make(map[string]GraphNode)
	edges := make(map[string]GraphEdge)

	addEdge := func(edge GraphEdge) {
		edge.ID = graphEdgeID(edge)
		edges[edge.ID] = edge
	}

	corpusNodeID := "corpus:" + corpus.CorpusID + "@" + corpus.Version
	if err := setGraphNode(nodes, GraphNode{
		ID:    corpusNodeID,
		Kind:  "CORPUS",
		Label: corpus.CorpusID + "@" + corpus.Version,
	}); err != nil {
		return KnowledgeGraph{}, err
	}

	for _, entry := range corpus.Records {
		recordNodeID := "record:" + entry.ID
		sourceNodeID := "source:" + entry.Source.ID
		value := Gematria(entry.Word)
		valueNodeID := "value:" + strconv.Itoa(value)

		if err := setGraphNode(nodes, GraphNode{
			ID:    recordNodeID,
			Kind:  "RECORD",
			Label: entry.Word,
			Word:  entry.Word,
			Gloss: entry.Gloss,
		}); err != nil {
			return KnowledgeGraph{}, err
		}
		if err := setGraphNode(nodes, GraphNode{
			ID:              sourceNodeID,
			Kind:            "SOURCE",
			Label:           entry.Source.ID,
			SourceKind:      entry.Source.Kind,
			SourceReference: entry.Source.Reference,
			SourceURL:       entry.Source.URL,
		}); err != nil {
			return KnowledgeGraph{}, err
		}
		if err := setGraphNode(nodes, GraphNode{
			ID:    valueNodeID,
			Kind:  "VALUE",
			Label: strconv.Itoa(value),
			Value: value,
		}); err != nil {
			return KnowledgeGraph{}, err
		}

		addEdge(GraphEdge{From: corpusNodeID, Relation: "CONTAINS_RECORD", To: recordNodeID})
		addEdge(GraphEdge{From: recordNodeID, Relation: "SOURCED_BY", To: sourceNodeID})
		addEdge(GraphEdge{From: recordNodeID, Relation: "HAS_GEMATRIA_VALUE", To: valueNodeID, NumericValue: value})

		for factor := range uniquePrimeFactors(value) {
			factorNodeID := "factor:" + strconv.Itoa(factor)
			if err := setGraphNode(nodes, GraphNode{
				ID:     factorNodeID,
				Kind:   "PRIME_FACTOR",
				Label:  strconv.Itoa(factor),
				Factor: factor,
			}); err != nil {
				return KnowledgeGraph{}, err
			}
			addEdge(GraphEdge{
				From:         valueNodeID,
				Relation:     "HAS_PRIME_FACTOR",
				To:           factorNodeID,
				NumericValue: factor,
			})
		}
	}

	for _, receipt := range receipts {
		finding := receipt.Payload.Finding
		receiptNodeID := "receipt:" + receipt.ReceiptSHA256
		anomalyNodeID := "anomaly:" + finding.Type

		if err := setGraphNode(nodes, GraphNode{
			ID:            receiptNodeID,
			Kind:          "RECEIPT",
			Label:         finding.Type,
			ReceiptSHA256: receipt.ReceiptSHA256,
		}); err != nil {
			return KnowledgeGraph{}, err
		}
		if err := setGraphNode(nodes, GraphNode{
			ID:          anomalyNodeID,
			Kind:        "ANOMALY_TYPE",
			Label:       finding.Type,
			AnomalyType: finding.Type,
		}); err != nil {
			return KnowledgeGraph{}, err
		}

		addEdge(GraphEdge{
			From:          receiptNodeID,
			Relation:      "DERIVED_FROM_CORPUS",
			To:            corpusNodeID,
			ReceiptSHA256: receipt.ReceiptSHA256,
		})
		addEdge(GraphEdge{
			From:          receiptNodeID,
			Relation:      "ASSERTS_ANOMALY",
			To:            anomalyNodeID,
			ReceiptSHA256: receipt.ReceiptSHA256,
			Evidence:      finding.Evidence,
		})

		for _, sourceID := range receipt.Payload.SourceRecordIDs {
			addEdge(GraphEdge{
				From:          receiptNodeID,
				Relation:      "REFERENCES_SOURCE",
				To:            "source:" + sourceID,
				ReceiptSHA256: receipt.ReceiptSHA256,
			})
		}

		involved := graphRecordIDsForFinding(finding, corpus.Records)
		for _, recordID := range involved {
			addEdge(GraphEdge{
				From:          receiptNodeID,
				Relation:      "INVOLVES_RECORD",
				To:            recordID,
				ReceiptSHA256: receipt.ReceiptSHA256,
			})
			addEdge(GraphEdge{
				From:          recordID,
				Relation:      "HAS_ANOMALY",
				To:            anomalyNodeID,
				ReceiptSHA256: receipt.ReceiptSHA256,
				Evidence:      finding.Evidence,
			})
		}

		addFindingRelationshipEdges(addEdge, finding, receipt.ReceiptSHA256, corpus.Records)
	}

	nodeList := make([]GraphNode, 0, len(nodes))
	for _, node := range nodes {
		nodeList = append(nodeList, node)
	}
	sort.Slice(nodeList, func(i, j int) bool {
		return nodeList[i].ID < nodeList[j].ID
	})

	edgeList := make([]GraphEdge, 0, len(edges))
	for _, edge := range edges {
		edgeList = append(edgeList, edge)
	}
	sort.Slice(edgeList, func(i, j int) bool {
		return edgeList[i].ID < edgeList[j].ID
	})

	payload := GraphPayload{
		SchemaVersion:  "gematria-glitch.graph.v1",
		Protocol:       "GEMATRIA-GLITCH-1",
		CorpusID:       corpus.CorpusID,
		CorpusVersion:  corpus.Version,
		CorpusSHA256:   corpusSHA256,
		GematriaSystem: corpus.GematriaSystem,
		Nodes:          nodeList,
		Edges:          edgeList,
		Boundary: []string{
			"PATTERN != PROOF",
			"RARITY != SIGNIFICANCE",
			"RECEIPT != TRUTH",
			"GRAPH != PROOF",
			"EDGE != CAUSATION",
			"CONNECTED != IDENTICAL",
		},
	}

	digest, err := graphDigest(payload)
	if err != nil {
		return KnowledgeGraph{}, err
	}
	return KnowledgeGraph{
		Payload:     payload,
		GraphSHA256: digest,
	}, nil
}

func addFindingRelationshipEdges(
	addEdge func(GraphEdge),
	finding Finding,
	receiptSHA256 string,
	entries []Entry,
) {
	if len(finding.Words) < 1 {
		return
	}

	switch finding.Type {
	case "EXACT_COLLISION":
		if len(finding.Words) < 2 {
			return
		}
		addRecordPairEdges(addEdge, entries, finding.Words[0], finding.Words[1], GraphEdge{
			Relation:      "EXACT_COLLISION_WITH",
			ReceiptSHA256: receiptSHA256,
			Evidence:      finding.Evidence,
		})
	case "SHARED_PRIME_FACTOR":
		if len(finding.Words) < 2 || len(finding.Values) < 3 {
			return
		}
		addRecordPairEdges(addEdge, entries, finding.Words[0], finding.Words[1], GraphEdge{
			Relation:      "SHARES_PRIME_FACTOR_WITH",
			ReceiptSHA256: receiptSHA256,
			Evidence:      finding.Evidence,
			NumericValue:  finding.Values[2],
		})
	case "LINGUISTIC_PREFIX_DELTA":
		if len(finding.Words) < 2 || len(finding.Values) < 3 {
			return
		}
		addRecordPairEdges(addEdge, entries, finding.Words[0], finding.Words[1], GraphEdge{
			Relation:      "LINGUISTIC_PREFIX_DELTA_TO",
			ReceiptSHA256: receiptSHA256,
			Evidence:      finding.Evidence,
			NumericValue:  finding.Values[2],
		})
	}
}

func addRecordPairEdges(
	addEdge func(GraphEdge),
	entries []Entry,
	leftWord string,
	rightWord string,
	template GraphEdge,
) {
	leftIDs := graphRecordIDsForWord(leftWord, entries)
	rightIDs := graphRecordIDsForWord(rightWord, entries)
	for _, leftID := range leftIDs {
		for _, rightID := range rightIDs {
			if leftID == rightID {
				continue
			}
			edge := template
			edge.From = leftID
			edge.To = rightID
			addEdge(edge)
		}
	}
}

func graphRecordIDsForFinding(finding Finding, entries []Entry) []string {
	seen := make(map[string]struct{})
	limit := len(finding.Words)
	if finding.Type == "LINGUISTIC_PREFIX_DELTA" && limit > 2 {
		limit = 2
	}

	for _, word := range finding.Words[:limit] {
		for _, id := range graphRecordIDsForWord(word, entries) {
			seen[id] = struct{}{}
		}
	}

	out := make([]string, 0, len(seen))
	for id := range seen {
		out = append(out, id)
	}
	sort.Strings(out)
	return out
}

func graphRecordIDsForWord(word string, entries []Entry) []string {
	out := make([]string, 0)
	for _, entry := range entries {
		if entry.Word == word {
			out = append(out, "record:"+entry.ID)
		}
	}
	sort.Strings(out)
	return out
}

func graphEdgeID(edge GraphEdge) string {
	payload := strings.Join([]string{
		edge.From,
		edge.Relation,
		edge.To,
		edge.ReceiptSHA256,
		edge.Evidence,
		strconv.Itoa(edge.NumericValue),
	}, "\x1f")
	sum := sha256.Sum256([]byte(payload))
	return "edge:" + hex.EncodeToString(sum[:])
}

func graphDigest(payload GraphPayload) (string, error) {
	data, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("marshal graph payload: %w", err)
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func verifyKnowledgeGraph(graph KnowledgeGraph) error {
	if graph.Payload.SchemaVersion != "gematria-glitch.graph.v1" {
		return fmt.Errorf("unsupported graph schema_version %q", graph.Payload.SchemaVersion)
	}
	if graph.Payload.Protocol != "GEMATRIA-GLITCH-1" {
		return fmt.Errorf("unsupported graph protocol %q", graph.Payload.Protocol)
	}
	if len(graph.Payload.Nodes) == 0 {
		return fmt.Errorf("graph contains no nodes")
	}

	expectedDigest, err := graphDigest(graph.Payload)
	if err != nil {
		return err
	}
	if expectedDigest != graph.GraphSHA256 {
		return fmt.Errorf("graph digest mismatch: got %s want %s", graph.GraphSHA256, expectedDigest)
	}

	nodeIDs := make(map[string]GraphNode, len(graph.Payload.Nodes))
	for _, node := range graph.Payload.Nodes {
		if node.ID == "" || node.Kind == "" {
			return fmt.Errorf("graph contains invalid node")
		}
		if _, exists := nodeIDs[node.ID]; exists {
			return fmt.Errorf("duplicate graph node id %q", node.ID)
		}
		nodeIDs[node.ID] = node
	}

	edgeIDs := make(map[string]struct{}, len(graph.Payload.Edges))
	for _, edge := range graph.Payload.Edges {
		if edge.ID == "" || edge.From == "" || edge.To == "" {
			return fmt.Errorf("graph contains invalid edge")
		}
		if _, exists := edgeIDs[edge.ID]; exists {
			return fmt.Errorf("duplicate graph edge id %q", edge.ID)
		}
		edgeIDs[edge.ID] = struct{}{}

		if _, ok := allowedGraphRelations[edge.Relation]; !ok {
			return fmt.Errorf("unsupported graph relation %q", edge.Relation)
		}
		if _, ok := nodeIDs[edge.From]; !ok {
			return fmt.Errorf("edge %q references missing from node %q", edge.ID, edge.From)
		}
		if _, ok := nodeIDs[edge.To]; !ok {
			return fmt.Errorf("edge %q references missing to node %q", edge.ID, edge.To)
		}
		if edge.ID != graphEdgeID(GraphEdge{
			From:          edge.From,
			Relation:      edge.Relation,
			To:            edge.To,
			ReceiptSHA256: edge.ReceiptSHA256,
			Evidence:      edge.Evidence,
			NumericValue:  edge.NumericValue,
		}) {
			return fmt.Errorf("edge %q has non-deterministic id", edge.ID)
		}
		if _, requiresReceipt := receiptBackedGraphRelations[edge.Relation]; requiresReceipt && edge.ReceiptSHA256 == "" {
			return fmt.Errorf("edge %q relation %q requires receipt backing", edge.ID, edge.Relation)
		}
		if edge.ReceiptSHA256 != "" {
			if _, ok := nodeIDs["receipt:"+edge.ReceiptSHA256]; !ok {
				return fmt.Errorf("edge %q references missing receipt node", edge.ID)
			}
		}
	}

	for _, boundary := range []string{"GRAPH != PROOF", "EDGE != CAUSATION", "CONNECTED != IDENTICAL"} {
		if !containsString(graph.Payload.Boundary, boundary) {
			return fmt.Errorf("graph missing boundary %q", boundary)
		}
	}
	return nil
}

func verifyKnowledgeGraphAgainstCorpus(graph KnowledgeGraph, corpus Corpus) error {
	if err := verifyKnowledgeGraph(graph); err != nil {
		return err
	}
	expected, err := buildKnowledgeGraph(corpus)
	if err != nil {
		return err
	}

	expectedJSON, err := json.Marshal(expected.Payload)
	if err != nil {
		return err
	}
	actualJSON, err := json.Marshal(graph.Payload)
	if err != nil {
		return err
	}
	if string(expectedJSON) != string(actualJSON) {
		return fmt.Errorf("graph payload is not reproducible from corpus")
	}
	if expected.GraphSHA256 != graph.GraphSHA256 {
		return fmt.Errorf("graph digest does not match corpus-derived graph")
	}
	return nil
}

func verifyGraphFile(path string, corpus *Corpus) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("read graph: %w", err)
	}
	var graph KnowledgeGraph
	if err := json.Unmarshal(data, &graph); err != nil {
		return fmt.Errorf("parse graph: %w", err)
	}
	if corpus == nil {
		return verifyKnowledgeGraph(graph)
	}
	return verifyKnowledgeGraphAgainstCorpus(graph, *corpus)
}

func containsString(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}
