package main

import "testing"

const expectedFiglet3DDiagonal = `   ______        ______        ______
  /_____/\      /_____/\      /_____/
  \::::_\/_     \::::_\/_     \::::_\
   \:\/___/\     \:\/___/\     \:\/___/\
    \_::._\:\     \::___\/_     \::___\/_
      /____\:\     \:\____/\     \:\____/\
      \_____\/      \_____\/      \_____\/
`

func TestFiglet3DDiagonalIsByteStable(t *testing.T) {
	if figlet3DDiagonal != expectedFiglet3DDiagonal {
		t.Fatalf("FIGlet 3D Diagonal artifact changed")
	}
}

func TestCanonicalProtocolSequence(t *testing.T) {
	if err := validateProtocols(protocols); err != nil {
		t.Fatalf("canonical protocols invalid: %v", err)
	}
}

func TestProtocolSequenceRejectsDrift(t *testing.T) {
	copyOfProtocols := append([]Protocol(nil), protocols...)
	copyOfProtocols[0].Code = "GLT-9999"

	if err := validateProtocols(copyOfProtocols); err == nil {
		t.Fatal("expected sequence drift to fail validation")
	}
}
