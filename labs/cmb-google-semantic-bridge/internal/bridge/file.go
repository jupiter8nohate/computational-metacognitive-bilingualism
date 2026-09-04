package bridge

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"unicode/utf8"
)

const (
	MaxSourceBytes = 16 << 20
	MaxHashBytes   = 64 << 20
)

func ReadRegularFile(path string, maxBytes int64) ([]byte, error) {
	if maxBytes <= 0 {
		return nil, fmt.Errorf("maxBytes must be positive")
	}
	before, err := os.Lstat(path)
	if err != nil {
		return nil, fmt.Errorf("stat file: %w", err)
	}
	if before.Mode()&os.ModeSymlink != 0 {
		return nil, fmt.Errorf("file must not be a symbolic link")
	}
	if !before.Mode().IsRegular() {
		return nil, fmt.Errorf("file must be regular")
	}
	if before.Size() > maxBytes {
		return nil, fmt.Errorf("file exceeds %d bytes", maxBytes)
	}

	file, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("open file: %w", err)
	}
	defer file.Close()

	after, err := file.Stat()
	if err != nil {
		return nil, fmt.Errorf("stat opened file: %w", err)
	}
	if !os.SameFile(before, after) {
		return nil, fmt.Errorf("file changed identity while opening")
	}

	data, err := io.ReadAll(io.LimitReader(file, maxBytes+1))
	if err != nil {
		return nil, fmt.Errorf("read file: %w", err)
	}
	if int64(len(data)) > maxBytes {
		return nil, fmt.Errorf("file exceeds %d bytes", maxBytes)
	}

	final, err := file.Stat()
	if err != nil {
		return nil, fmt.Errorf("stat file after read: %w", err)
	}
	if final.Size() != before.Size() || final.ModTime() != before.ModTime() {
		return nil, fmt.Errorf("file changed while reading")
	}
	return data, nil
}

func ReadUTF8Source(path string) ([]byte, error) {
	data, err := ReadRegularFile(path, MaxSourceBytes)
	if err != nil {
		return nil, err
	}
	if len(data) == 0 {
		return nil, fmt.Errorf("source must not be empty")
	}
	if !utf8.Valid(data) {
		return nil, fmt.Errorf("source must be valid UTF-8")
	}
	return data, nil
}


func ReadRepositoryUTF8File(root, relative string) ([]byte, error) {
	rootInfo, err := os.Lstat(root)
	if err != nil {
		return nil, fmt.Errorf("stat repository root: %w", err)
	}
	if rootInfo.Mode()&os.ModeSymlink != 0 || !rootInfo.IsDir() {
		return nil, fmt.Errorf("repository root must be a real directory")
	}

	clean := filepath.Clean(relative)
	if clean == "." || filepath.IsAbs(clean) || clean != relative {
		return nil, fmt.Errorf("repository path must be normalized and relative")
	}
	parts := strings.Split(filepath.ToSlash(clean), "/")
	current := root
	for i, part := range parts {
		if part == "" || part == "." || part == ".." {
			return nil, fmt.Errorf("repository path must not escape the root")
		}
		current = filepath.Join(current, part)
		info, err := os.Lstat(current)
		if err != nil {
			return nil, fmt.Errorf("stat repository path %q: %w", relative, err)
		}
		if info.Mode()&os.ModeSymlink != 0 {
			return nil, fmt.Errorf("repository path %q contains a symbolic link", relative)
		}
		if i < len(parts)-1 && !info.IsDir() {
			return nil, fmt.Errorf("repository path %q crosses a non-directory component", relative)
		}
	}
	return ReadUTF8Source(current)
}
