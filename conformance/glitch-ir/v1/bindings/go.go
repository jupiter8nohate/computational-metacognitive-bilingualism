package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func load(path string) (map[string]string, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	values := make(map[string]string)
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			return nil, fmt.Errorf("invalid vector line: %q", line)
		}
		values[parts[0]] = parts[1]
	}
	return values, scanner.Err()
}

func main() {
	if len(os.Args) != 2 {
		panic("usage: go.go VECTOR")
	}
	values, err := load(os.Args[1])
	if err != nil {
		panic(err)
	}
	verdict, operator, state := "ACCEPT", "NONE", "ACCEPTED"
	if values["verification_label"] == "PRESENT" && values["evidence"] != "PRESENT" {
		verdict, operator, state = "BACKTRACE", "GLT-0036", "CONTESTED"
	} else if values["source"] == "UNKNOWN" {
		verdict, operator, state = "BACKTRACE", "GLT-0036", "CONTESTED"
	}
	fmt.Printf("%s|%s|%s|%s|%s\n", values["vector_id"], values["protocol_version"], verdict, operator, state)
}
