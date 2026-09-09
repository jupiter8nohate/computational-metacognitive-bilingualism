package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"sort"
	"strconv"
	"strings"
)

const maxQueryCandidates = 10000

type PathQuery struct {
	From     string `json:"from"`
	To       string `json:"to"`
	MaxDepth int    `json:"max_depth"`
	MaxPaths int    `json:"max_paths"`
}

type PathStep struct {
	EdgeID        string `json:"edge_id"`
	From          string `json:"from"`
	Relation      string `json:"relation"`
	To            string `json:"to"`
	Traversal     string `json:"traversal"`
	EvidenceTier  int    `json:"evidence_tier"`
	ReceiptSHA256 string `json:"receipt_sha256,omitempty"`
	Evidence      string `json:"evidence,omitempty"`
}

type GraphPath struct {
	PathID         string     `json:"path_id"`
	Nodes          []string   `json:"nodes"`
	Steps          []PathStep `json:"steps"`
	HopCount       int        `json:"hop_count"`
	EvidenceFloor  int        `json:"evidence_floor"`
	EvidenceClass  string     `json:"evidence_class"`
	ReceiptSHA256s []string   `json:"receipt_sha256s"`
	SourceNodeIDs  []string   `json:"source_node_ids"`
}

type PathQueryResult struct {
	SchemaVersion string      `json:"schema_version"`
	Protocol      string      `json:"protocol"`
	GraphSHA256   string      `json:"graph_sha256"`
	Query         PathQuery   `json:"query"`
	ResolvedFrom  []string    `json:"resolved_from"`
	ResolvedTo    []string    `json:"resolved_to"`
	Paths         []GraphPath `json:"paths"`
	Boundary      []string    `json:"boundary"`
}

type graphTraversal struct {
	Edge      GraphEdge
	Neighbor  string
	Direction string
}

func queryKnowledgeGraph(graph KnowledgeGraph, query PathQuery) (PathQueryResult, error) {
	if err := verifyKnowledgeGraph(graph); err != nil {
		return PathQueryResult{}, fmt.Errorf("query requires verified graph: %w", err)
	}
	if strings.TrimSpace(query.From) == "" || strings.TrimSpace(query.To) == "" {
		return PathQueryResult{}, fmt.Errorf("from and to selectors are required")
	}
	if query.MaxDepth < 1 || query.MaxDepth > 8 {
		return PathQueryResult{}, fmt.Errorf("max_depth must be between 1 and 8")
	}
	if query.MaxPaths < 1 || query.MaxPaths > 50 {
		return PathQueryResult{}, fmt.Errorf("max_paths must be between 1 and 50")
	}

	fromIDs := resolveGraphSelector(graph, query.From)
	if len(fromIDs) == 0 {
		return PathQueryResult{}, fmt.Errorf("from selector %q did not resolve to a graph node", query.From)
	}
	toIDs := resolveGraphSelector(graph, query.To)
	if len(toIDs) == 0 {
		return PathQueryResult{}, fmt.Errorf("to selector %q did not resolve to a graph node", query.To)
	}

	adjacency := buildGraphAdjacency(graph)
	targets := make(map[string]struct{}, len(toIDs))
	for _, id := range toIDs {
		targets[id] = struct{}{}
	}

	var candidates []GraphPath
	explored := 0
	for _, sourceID := range fromIDs {
		visited := map[string]bool{sourceID: true}
		var walk func(string, []string, []PathStep) error
		walk = func(current string, nodes []string, steps []PathStep) error {
			if len(steps) > 0 {
				if _, ok := targets[current]; ok {
					path := buildGraphPath(graph, nodes, steps)
					candidates = append(candidates, path)
				}
			}
			if len(steps) >= query.MaxDepth {
				return nil
			}

			for _, next := range adjacency[current] {
				if visited[next.Neighbor] {
					continue
				}
				explored++
				if explored > maxQueryCandidates {
					return fmt.Errorf("query exceeded %d candidate expansions; reduce max_depth", maxQueryCandidates)
				}
				visited[next.Neighbor] = true
				step := PathStep{
					EdgeID:        next.Edge.ID,
					From:          current,
					Relation:      next.Edge.Relation,
					To:            next.Neighbor,
					Traversal:     next.Direction,
					EvidenceTier:  graphEdgeEvidenceTier(next.Edge),
					ReceiptSHA256: next.Edge.ReceiptSHA256,
					Evidence:      next.Edge.Evidence,
				}
				if err := walk(
					next.Neighbor,
					append(append([]string(nil), nodes...), next.Neighbor),
					append(append([]PathStep(nil), steps...), step),
				); err != nil {
					return err
				}
				delete(visited, next.Neighbor)
			}
			return nil
		}

		if err := walk(sourceID, []string{sourceID}, nil); err != nil {
			return PathQueryResult{}, err
		}
	}

	sortGraphPaths(candidates)
	if len(candidates) > query.MaxPaths {
		candidates = candidates[:query.MaxPaths]
	}

	return PathQueryResult{
		SchemaVersion: "gematria-glitch.path-query.v1",
		Protocol:      "GEMATRIA-GLITCH-1",
		GraphSHA256:   graph.GraphSHA256,
		Query:         query,
		ResolvedFrom:  fromIDs,
		ResolvedTo:    toIDs,
		Paths:         candidates,
		Boundary: []string{
			"PATH != PROOF",
			"PATH_RANK != TRUTH",
			"EDGE != CAUSATION",
			"CONNECTED != IDENTICAL",
			"NO_PATH != NO_RELATIONSHIP",
		},
	}, nil
}

func resolveGraphSelector(graph KnowledgeGraph, selector string) []string {
	selector = strings.TrimSpace(selector)
	matches := make([]string, 0)

	for _, node := range graph.Payload.Nodes {
		if node.ID == selector {
			return []string{node.ID}
		}
	}

	for _, node := range graph.Payload.Nodes {
		if node.Kind == "RECORD" && (node.Word == selector || node.Label == selector) {
			matches = append(matches, node.ID)
		}
	}
	sort.Strings(matches)
	return matches
}

func buildGraphAdjacency(graph KnowledgeGraph) map[string][]graphTraversal {
	adjacency := make(map[string][]graphTraversal)
	for _, edge := range graph.Payload.Edges {
		adjacency[edge.From] = append(adjacency[edge.From], graphTraversal{
			Edge:      edge,
			Neighbor:  edge.To,
			Direction: "FORWARD",
		})
		adjacency[edge.To] = append(adjacency[edge.To], graphTraversal{
			Edge:      edge,
			Neighbor:  edge.From,
			Direction: "REVERSE",
		})
	}

	for nodeID := range adjacency {
		sort.Slice(adjacency[nodeID], func(i, j int) bool {
			left := adjacency[nodeID][i]
			right := adjacency[nodeID][j]
			if left.Neighbor != right.Neighbor {
				return left.Neighbor < right.Neighbor
			}
			if left.Edge.Relation != right.Edge.Relation {
				return left.Edge.Relation < right.Edge.Relation
			}
			if left.Direction != right.Direction {
				return left.Direction < right.Direction
			}
			return left.Edge.ID < right.Edge.ID
		})
	}
	return adjacency
}

func graphEdgeEvidenceTier(edge GraphEdge) int {
	if _, ok := receiptBackedGraphRelations[edge.Relation]; ok {
		if edge.ReceiptSHA256 != "" {
			return 3
		}
		return 1
	}

	switch edge.Relation {
	case "CONTAINS_RECORD", "SOURCED_BY", "HAS_GEMATRIA_VALUE", "HAS_PRIME_FACTOR":
		return 4
	default:
		return 1
	}
}

func buildGraphPath(graph KnowledgeGraph, nodes []string, steps []PathStep) GraphPath {
	evidenceFloor := 4
	if len(steps) == 0 {
		evidenceFloor = 0
	}
	receipts := make(map[string]struct{})
	for _, step := range steps {
		if step.EvidenceTier < evidenceFloor {
			evidenceFloor = step.EvidenceTier
		}
		if step.ReceiptSHA256 != "" {
			receipts[step.ReceiptSHA256] = struct{}{}
		}
	}

	receiptList := sortedSet(receipts)
	sourceList := graphPathSourceTrace(graph, nodes, receiptList)

	path := GraphPath{
		Nodes:          append([]string(nil), nodes...),
		Steps:          append([]PathStep(nil), steps...),
		HopCount:       len(steps),
		EvidenceFloor:  evidenceFloor,
		EvidenceClass:  graphEvidenceClass(evidenceFloor),
		ReceiptSHA256s: receiptList,
		SourceNodeIDs:  sourceList,
	}
	path.PathID = graphPathID(path)
	return path
}

func graphEvidenceClass(tier int) string {
	switch tier {
	case 4:
		return "DIRECT_STRUCTURAL"
	case 3:
		return "RECEIPT_BACKED"
	default:
		return "LOWER_ASSURANCE"
	}
}

func graphPathSourceTrace(graph KnowledgeGraph, pathNodes []string, receiptSHA256s []string) []string {
	sources := make(map[string]struct{})
	pathNodeSet := make(map[string]struct{}, len(pathNodes))
	receiptSet := make(map[string]struct{}, len(receiptSHA256s))

	for _, id := range pathNodes {
		pathNodeSet[id] = struct{}{}
		if strings.HasPrefix(id, "source:") {
			sources[id] = struct{}{}
		}
	}
	for _, digest := range receiptSHA256s {
		receiptSet[digest] = struct{}{}
	}

	for _, edge := range graph.Payload.Edges {
		if edge.Relation == "SOURCED_BY" {
			if _, ok := pathNodeSet[edge.From]; ok && strings.HasPrefix(edge.To, "source:") {
				sources[edge.To] = struct{}{}
			}
		}
		if edge.Relation == "REFERENCES_SOURCE" && edge.ReceiptSHA256 != "" {
			if _, ok := receiptSet[edge.ReceiptSHA256]; ok && strings.HasPrefix(edge.To, "source:") {
				sources[edge.To] = struct{}{}
			}
		}
	}

	return sortedSet(sources)
}

func sortedSet(values map[string]struct{}) []string {
	out := make([]string, 0, len(values))
	for value := range values {
		out = append(out, value)
	}
	sort.Strings(out)
	return out
}

func graphPathID(path GraphPath) string {
	parts := make([]string, 0, len(path.Steps)*2+len(path.Nodes))
	parts = append(parts, path.Nodes...)
	for _, step := range path.Steps {
		parts = append(parts,
			step.EdgeID,
			step.Traversal,
			strconv.Itoa(step.EvidenceTier),
		)
	}
	sum := sha256.Sum256([]byte(strings.Join(parts, "\x1f")))
	return "path:" + hex.EncodeToString(sum[:])
}

func sortGraphPaths(paths []GraphPath) {
	sort.SliceStable(paths, func(i, j int) bool {
		left := paths[i]
		right := paths[j]
		if left.EvidenceFloor != right.EvidenceFloor {
			return left.EvidenceFloor > right.EvidenceFloor
		}
		if left.HopCount != right.HopCount {
			return left.HopCount < right.HopCount
		}
		return left.PathID < right.PathID
	})
}

func renderPathQueryGlitch(result PathQueryResult) string {
	var b strings.Builder
	b.WriteString("𓁹 Err ⃝or⃟⃤://GRAPH_PATH_QUERY\n")
	fmt.Fprintf(&b, "FROM://%s\n", result.Query.From)
	fmt.Fprintf(&b, "TO://%s\n", result.Query.To)
	fmt.Fprintf(&b, "MAX_DEPTH://%d\n", result.Query.MaxDepth)
	fmt.Fprintf(&b, "PATHS_FOUND://%d\n\n", len(result.Paths))

	for index, path := range result.Paths {
		fmt.Fprintf(&b, "꩜ PATH://%d\n", index+1)
		fmt.Fprintf(&b, "PATH_ID://%s\n", path.PathID)
		fmt.Fprintf(&b, "HOPS://%d\n", path.HopCount)
		fmt.Fprintf(&b, "EVIDENCE_FLOOR://%d\n", path.EvidenceFloor)
		fmt.Fprintf(&b, "EVIDENCE_CLASS://%s\n", path.EvidenceClass)
		fmt.Fprintf(&b, "NODES://%s\n", strings.Join(path.Nodes, " -> "))
		for _, step := range path.Steps {
			fmt.Fprintf(
				&b,
				"𓂀 %s -[%s/%s]-> %s\n",
				step.From,
				step.Relation,
				step.Traversal,
				step.To,
			)
		}
		if len(path.ReceiptSHA256s) > 0 {
			fmt.Fprintf(&b, "RECEIPTS://%s\n", strings.Join(path.ReceiptSHA256s, " | "))
		}
		if len(path.SourceNodeIDs) > 0 {
			fmt.Fprintf(&b, "SOURCES://%s\n", strings.Join(path.SourceNodeIDs, " | "))
		}
		b.WriteString("PATH_RANK != TRUTH\n")
		b.WriteString("EDGE != CAUSATION\n\n")
	}

	if len(result.Paths) == 0 {
		b.WriteString("NO_PATH_FOUND != NO_RELATIONSHIP\n")
	}
	b.WriteString("♡⃟ INTERPRETATION://HUMAN\n")
	return b.String()
}
