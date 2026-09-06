#!/usr/bin/env python3
"""Compile/run all GLT-8101 semantic engines and compare canonical result bytes."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "conformance" / "glitch-ir" / "v1"
BINDINGS = BASE / "bindings"
JSON_VECTOR = BASE / "GLT-8101-V001.json"
TEXT_VECTOR = BASE / "GLT-8101-V001.txt"


def run(command: list[str], *, cwd: Path | None = None) -> bytes:
    completed = subprocess.run(
        command,
        cwd=cwd or ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"required conformance tool is missing: {name}")
    return path


def verify_projection() -> dict[str, object]:
    vector = json.loads(JSON_VECTOR.read_text(encoding="utf-8"))
    expected_lines = [
        f"vector_id={vector['vector_id']}",
        f"protocol_version={vector['protocol_version']}",
        f"verification_label={vector['claim']['verification_label']}",
        f"evidence={vector['claim']['evidence']}",
        f"source={vector['claim']['source']}",
        f"human_review={vector['human_review']}",
        f"expected_verdict={vector['expected_result']['verdict']}",
        f"expected_operator={vector['expected_result']['operator']}",
        f"expected_state={vector['expected_result']['state']}",
    ]
    expected = "\n".join(expected_lines) + "\n"
    actual = TEXT_VECTOR.read_text(encoding="utf-8")
    if actual != expected:
        raise RuntimeError("GLITCH-IR text projection drifted from normative JSON fixture")
    return vector


def main() -> int:
    vector = verify_projection()
    expected = (
        f"{vector['vector_id']}|{vector['protocol_version']}|"
        f"{vector['expected_result']['verdict']}|"
        f"{vector['expected_result']['operator']}|"
        f"{vector['expected_result']['state']}\n"
    ).encode("utf-8")

    with tempfile.TemporaryDirectory(prefix="glt8101-") as temp_name:
        temp = Path(temp_name)
        rust_bin = temp / "rust-engine"
        cpp_bin = temp / "cpp-engine"
        ts_out = temp / "ts"
        ts_out.mkdir()

        require_tool("python3")
        require_tool("go")
        require_tool("rustc")
        require_tool("node")
        require_tool("sbcl")
        require_tool("runghc")
        require_tool("swipl")
        require_tool("g++")

        tsc = ROOT / "adapters" / "typescript-express" / "node_modules" / ".bin" / "tsc"
        if not tsc.exists():
            raise RuntimeError(
                "TypeScript compiler missing; run npm install in adapters/typescript-express"
            )

        run(["rustc", "--edition=2021", str(BINDINGS / "rust.rs"), "-o", str(rust_bin)])
        run(["g++", "-std=c++20", "-Wall", "-Wextra", "-Werror",
             str(BINDINGS / "cpp20.cpp"), "-o", str(cpp_bin)])
        run([
            str(tsc),
            str(BINDINGS / "typescript.ts"),
            "--target", "ES2020",
            "--module", "commonjs",
            "--outDir", str(ts_out),
            "--skipLibCheck",
        ])

        ts_file = ts_out / "typescript.js"
        engines = {
            "PY": ["python3", str(BINDINGS / "python.py"), str(TEXT_VECTOR)],
            "GO": ["go", "run", str(BINDINGS / "go.go"), str(TEXT_VECTOR)],
            "RS": [str(rust_bin), str(TEXT_VECTOR)],
            "TS": ["node", str(ts_file), str(TEXT_VECTOR)],
            "CL": ["sbcl", "--script", str(BINDINGS / "common_lisp.lisp"), str(TEXT_VECTOR)],
            "HS": ["runghc", str(BINDINGS / "haskell.hs"), str(TEXT_VECTOR)],
            "PL": ["swipl", "-q", "-s", str(BINDINGS / "prolog.pl"), "--", str(TEXT_VECTOR)],
            "CPP": [str(cpp_bin), str(TEXT_VECTOR)],
        }

        outputs: dict[str, bytes] = {}
        for runtime, command in engines.items():
            output = run(command)
            outputs[runtime] = output
            if output != expected:
                print(
                    f"GLITCH://SEMANTIC_DRIFT runtime={runtime} "
                    f"expected={expected!r} actual={output!r}",
                    file=sys.stderr,
                )
                return 1

        unique = set(outputs.values())
        if len(unique) != 1:
            print("GLITCH://SEMANTIC_DRIFT independent outputs differ", file=sys.stderr)
            return 1

        digest = hashlib.sha256(expected).hexdigest()
        print("GLT-8101 // CANONICAL_SYNCHRONY")
        for runtime in engines:
            print(f"{runtime:>3}  MATCH")
        print("agreement=8/8")
        print("semantic_drift=NONE")
        print(f"sha256={digest}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
