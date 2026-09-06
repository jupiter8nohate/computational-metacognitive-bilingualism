from pathlib import Path
import sys

def read_vector(path: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values

def main() -> int:
    values = read_vector(sys.argv[1])
    if values["verification_label"] == "PRESENT" and values["evidence"] != "PRESENT":
        verdict, operator, state = "BACKTRACE", "GLT-0036", "CONTESTED"
    elif values["source"] == "UNKNOWN":
        verdict, operator, state = "BACKTRACE", "GLT-0036", "CONTESTED"
    else:
        verdict, operator, state = "ACCEPT", "NONE", "ACCEPTED"
    print("|".join((values["vector_id"], values["protocol_version"], verdict, operator, state)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
