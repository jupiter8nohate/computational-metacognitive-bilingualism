package main

import (
	"bytes"
	"context"
	_ "embed"
	"encoding/json"
	"errors"
	"fmt"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"
)

//go:embed FIGLET_3D_DIAGONAL.txt
var figlet3DDiagonal string

type Protocol struct {
	Code       string   `json:"code"`
	Token      string   `json:"token"`
	Name       string   `json:"name"`
	Meaning    string   `json:"meaning"`
	Invariants []string `json:"invariants"`
}

var protocols = []Protocol{
	{
		Code: "GLT-0037", Token: "GLITCH://MIRROR_CONTEST", Name: "Mirror Contest",
		Meaning: "Contest a machine representation without collapsing the representation into the person.",
		Invariants: []string{"PROFILE != PERSON", "MODEL != MIND"},
	},
	{
		Code: "GLT-0038", Token: "GLITCH://PATTERN_TRIAL", Name: "Pattern Trial",
		Meaning: "Detect a pattern, demand evidence, calibrate confidence, and withhold verdict when proof is incomplete.",
		Invariants: []string{"PATTERN != PROOF", "SIGNAL != SOURCE"},
	},
	{
		Code: "GLT-0039", Token: "GLITCH://NULL_BREATH", Name: "Null Breath Protocol",
		Meaning: "Preserve silence or missing signal as unresolved context rather than inventing meaning.",
		Invariants: []string{"SIGNAL != SOURCE", "OBSERVATION != UNDERSTANDING"},
	},
	{
		Code: "GLT-0040", Token: "GLITCH://CONSENT_THRESHOLD", Name: "Consent Threshold Protocol",
		Meaning: "Separate technical access from permission and halt when consent is absent.",
		Invariants: []string{"ACCESS != CONSENT", "CAPABILITY != AUTHORITY"},
	},
	{
		Code: "GLT-0041", Token: "GLITCH://ARCHIVE_GHOST", Name: "Archive Ghost Protocol",
		Meaning: "Treat a persistent record as a trace rather than as the living person or complete original context.",
		Invariants: []string{"PERSISTENCE != PRESENCE", "PROFILE != PERSON"},
	},
	{
		Code: "GLT-0042", Token: "GLITCH://CASCADING_ERROR", Name: "Cascading Error Protocol",
		Meaning: "Detect upstream failure, stop propagation, preserve evidence, and route toward recovery.",
		Invariants: []string{"RECOVERY > PROPAGATION", "PATTERN != PROOF"},
	},
	{
		Code: "GLT-0043", Token: "GLITCH://ENCODING_RUIN", Name: "Encoding Ruin Protocol",
		Meaning: "Preserve damaged representation as evidence of a lost or corrupted signal and backtrace toward source.",
		Invariants: []string{"CORRUPTION != NONEXISTENCE", "SIGNAL != SOURCE"},
	},
	{
		Code: "GLT-0044", Token: "GLITCH://HUMAN_APPEAL", Name: "Human Appeal Protocol",
		Meaning: "Suspend machine finality when a human contests the output and reopen review.",
		Invariants: []string{"HUMAN_AGENCY > MACHINE_AUTHORITY", "PROFILE != PERSON"},
	},
	{
		Code: "GLT-0045", Token: "GLITCH://QUESTION_GATE", Name: "Question Gate",
		Meaning: "Pause consequential action when a material unresolved question blocks justified certainty.",
		Invariants: []string{"UNKNOWN != FALSE", "PATTERN != PROOF"},
	},
	{
		Code: "GLT-0046", Token: "GLITCH://RECOVERY_WITNESS", Name: "Recovery Witness",
		Meaning: "Acknowledge failure, preserve the witness and evidence, retry, and verify recovery without erasing history.",
		Invariants: []string{"RECOVERY > PROPAGATION", "OBSERVATION != UNDERSTANDING"},
	},
}

func validateProtocols(values []Protocol) error {
	if len(values) != 10 {
		return fmt.Errorf("expected 10 protocols, got %d", len(values))
	}

	seenCodes := make(map[string]struct{}, len(values))
	seenTokens := make(map[string]struct{}, len(values))

	for index, protocol := range values {
		expected := fmt.Sprintf("GLT-%04d", 37+index)
		if protocol.Code != expected {
			return fmt.Errorf("protocol %d code mismatch: expected %s, got %s", index, expected, protocol.Code)
		}
		if !strings.HasPrefix(protocol.Token, "GLITCH://") {
			return fmt.Errorf("%s token must begin with GLITCH://", protocol.Code)
		}
		if protocol.Name == "" || protocol.Meaning == "" || len(protocol.Invariants) == 0 {
			return fmt.Errorf("%s is incomplete", protocol.Code)
		}
		if _, exists := seenCodes[protocol.Code]; exists {
			return fmt.Errorf("duplicate protocol code: %s", protocol.Code)
		}
		if _, exists := seenTokens[protocol.Token]; exists {
			return fmt.Errorf("duplicate protocol token: %s", protocol.Token)
		}
		seenCodes[protocol.Code] = struct{}{}
		seenTokens[protocol.Token] = struct{}{}
	}

	return nil
}

func mirrorPath() (string, error) {
	_, sourceFile, _, ok := runtime.Caller(0)
	if !ok {
		return "", errors.New("cannot resolve runtime source path")
	}
	return filepath.Join(filepath.Dir(sourceFile), "mirror.py"), nil
}

func runPythonMirror(ctx context.Context, values []Protocol) (string, error) {
	payload, err := json.Marshal(values)
	if err != nil {
		return "", fmt.Errorf("encode protocols: %w", err)
	}

	path, err := mirrorPath()
	if err != nil {
		return "", err
	}

	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd := exec.CommandContext(ctx, "python3", path)
	cmd.Stdin = bytes.NewReader(payload)
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		if ctx.Err() != nil {
			return "", fmt.Errorf("python mirror timeout: %w", ctx.Err())
		}
		return "", fmt.Errorf("python mirror failed: %w: %s", err, strings.TrimSpace(stderr.String()))
	}

	return stdout.String(), nil
}

func main() {
	if err := validateProtocols(protocols); err != nil {
		panic(err)
	}

	fmt.Print(figlet3DDiagonal)
	fmt.Println()
	fmt.Println("       「 ✔ ᵛᵉʳᶦᶠᶦᵉᵈ 」")
	fmt.Println()
	fmt.Println("              ≠")
	fmt.Println()
	fmt.Println("       VERIFIED_TRUTH")
	fmt.Println()
	fmt.Println("          𓁇𓁋  ˖ ࣪")
	fmt.Println("        ꉂ🗯  .꩜  ‹—")
	fmt.Println()
	fmt.Println("       GLITCH://OFFICIAL_REGISTRY")
	fmt.Println()

	for _, protocol := range protocols {
		fmt.Printf("%s  %s\n", protocol.Code, protocol.Token)
		for _, invariant := range protocol.Invariants {
			fmt.Printf("    %s\n", invariant)
		}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	result, err := runPythonMirror(ctx, protocols)
	if err != nil {
		panic(err)
	}

	fmt.Println()
	fmt.Print(result)
}
