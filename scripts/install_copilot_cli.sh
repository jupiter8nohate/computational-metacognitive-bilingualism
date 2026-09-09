#!/usr/bin/env bash
set -euo pipefail

version="${CMB_COPILOT_CLI_VERSION:-1.0.83}"
expected_sha256="${CMB_COPILOT_CLI_SHA256:-ffbe1c429664b8a05efed67ecdb467123e40fcaa3c6c14ef9a98ba74da4687b7}"
archive="/tmp/copilot-linux-x64.tar.gz"
extract_dir="/tmp/cmb-copilot-cli"

url="https://github.com/github/copilot-cli/releases/download/v${version}/copilot-linux-x64.tar.gz"

curl --fail --location --proto '=https' --tlsv1.2 "$url" --output "$archive"
printf '%s  %s\n' "$expected_sha256" "$archive" | sha256sum --check --strict

rm -rf "$extract_dir"
mkdir -p "$extract_dir" "$HOME/.local/bin"
tar -xzf "$archive" -C "$extract_dir"

binary="$(find "$extract_dir" -type f -name copilot -print -quit)"
if [[ -z "$binary" ]]; then
  echo "Copilot CLI binary not found in verified archive." >&2
  exit 1
fi

install -m 0755 "$binary" "$HOME/.local/bin/copilot"
echo "$HOME/.local/bin" >> "${GITHUB_PATH:-/dev/null}"
"$HOME/.local/bin/copilot" --version
