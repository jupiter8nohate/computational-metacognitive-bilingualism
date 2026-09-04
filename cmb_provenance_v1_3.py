
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import tempfile
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Final, Mapping, Sequence


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CMB // PROVENANCE & EXTERNAL-EVIDENCE LEDGER // v1.3.0                    ║
# ║                                                                              ║
# ║              COMPUTATIONAL METACOGNITIVE BILINGUALISM                       ║
# ║                                                                              ║
# ║  Declared Originator: Jupiter Hudson / WisdomLoveThePoet / Jupiter 8         ║
# ║  Artistic Branch: Algorithmic Disruption Art                                ║
# ║                                                                              ║
# ║  PATTERN ≠ PROOF                                                            ║
# ║  DECLARATION ≠ INDEPENDENT VERIFICATION                                     ║
# ║  LOCAL HASH CHAIN ≠ IMMUTABLE PUBLIC LEDGER                                 ║
# ║  REFERENCE ≠ VERIFIED EXTERNAL EVIDENCE                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# RECOVERY CHANGES FROM v1.2.0
# ----------------------------
# 1. Declaration version is separated from tool version so tool upgrades do not
#    silently change the v1.2 declaration hash.
# 2. External references live in a JSONL hash chain. The chain is tamper-evident,
#    not magically immutable; rewriting the whole local file remains possible.
# 3. Local record time is separated from externally displayed/witnessed time.
# 4. External references are explicitly UNVERIFIED until their evidence is checked.
# 5. A plain Git commit date is not treated as a trusted independent clock.
# 6. SHA-256 inputs, timestamps, sequence continuity, and chain continuity are
#    validated before records are accepted.


TOOL_VERSION: Final[str] = "1.3.0"
DECLARATION_VERSION: Final[str] = "1.2.0"
SCHEMA_VERSION: Final[str] = "cmb.framework.v1"
ANCHOR_SCHEMA_VERSION: Final[str] = "cmb.anchor.v1"
DECLARATION_TIMESTAMP_UTC: Final[str] = "2026-08-28T01:17:00Z"
DEFAULT_ANCHOR_STORE: Final[Path] = Path("cmb_anchors.jsonl")


@dataclass(frozen=True, slots=True)
class IntellectualFramework:
    name: str
    abbreviation: str
    declared_originator: str
    formal_definition: str
    methodology: tuple[str, ...]
    terminology: tuple[str, ...]
    artistic_branch: str
    dated_corpus: tuple[str, ...]
    original_works: tuple[str, ...]
    core_principles: tuple[str, ...]


CMB: Final[IntellectualFramework] = IntellectualFramework(
    name="Computational Metacognitive Bilingualism",
    abbreviation="CMB",
    declared_originator="Jupiter Hudson / WisdomLoveThePoet / Jupiter 8",
    formal_definition=(
        "A communication framework that deliberately translates human thought, "
        "philosophy, advocacy, metacognition, and cognitive-sovereignty principles "
        "into programming-inspired structures designed to remain meaningful to "
        "human readers while presenting explicit logical, semantic, and structural "
        "relationships to computational systems."
    ),
    methodology=(
        "Convert abstract human concepts into structured computational syntax.",
        "Use variables, conditions, assertions, functions, schemas, and types as rhetoric.",
        "Preserve human meaning while increasing explicit structural machine legibility.",
        "Create visual and cognitive interruption inside algorithmically mediated environments.",
        "Use code-form communication to encourage metacognition and AI literacy.",
        "Teach computational concepts while simultaneously communicating advocacy.",
        "Preserve human judgment as superior to automated classification.",
        "Separate observed patterns from evidentiary conclusions.",
        "Maintain the invariant: PATTERN != PROOF.",
    ),
    terminology=(
        "Computational Metacognitive Bilingualism",
        "CMB",
        "Algorithmic Disruption Art",
        "Cognitive Sovereignty",
        "Human-Machine Bilingual Communication",
        "Comment Canvas",
        "Cognitive Interrupt",
        "Pattern ≠ Proof",
    ),
    artistic_branch="Algorithmic Disruption Art",
    dated_corpus=(
        "Timestamped social-media CMB publications",
        "Archived code-poetry and executable-rhetoric works",
        "Public comment-canvas interventions",
        "Versioned manuscripts and research papers",
        "Repository commits",
        "Cryptographic provenance receipts",
    ),
    original_works=(
        "CMB manifestos",
        "Python-style advocacy works",
        "Algorithmic Disruption Art compositions",
        "Cognitive-sovereignty code-poetry",
        "Neurodiversity-centered executable rhetoric",
        "Original CMB diagrams",
        "Original CMB schemas",
        "Original CMB terminology",
        "Original CMB documentation",
    ),
    core_principles=(
        "PATTERN != PROOF",
        "HUMAN_AGENCY > MACHINE_AUTHORITY",
        "MEMORY != TRUTH",
        "DECLARATION != INDEPENDENT_VERIFICATION",
        "PROVENANCE != AUTOMATIC_LEGAL_OWNERSHIP",
    ),
)

PREEXISTING_TRADITIONS: Final[tuple[str, ...]] = (
    "ASCII art",
    "ANSI art",
    "BBS culture",
    "code poetry",
    "Perl poetry",
    "codework",
    "electronic literature",
    "creative programming",
    "software art",
)

CLAIM_SCOPE: Final[Mapping[str, object]] = MappingProxyType(
    {
        "declared_origin": (
            "The CMB name, formal definition, methodology, terminology, "
            "documented corpus, framework architecture, and original authored works "
            "are declared by Jupiter Hudson as originating within his CMB project."
        ),
        "artistic_branch": (
            "Algorithmic Disruption Art is declared as the artistic branch and "
            "public-expression methodology of the CMB framework."
        ),
        "historical_position": (
            "CMB is positioned as a new synthesis and formalization rather than "
            "as the invention of programming-based art, code poetry, or electronic literature."
        ),
        "not_claimed": PREEXISTING_TRADITIONS,
    }
)

FACT: Final[str] = "FACT"
DECLARATION: Final[str] = "DECLARATION"
HYPOTHESIS: Final[str] = "HYPOTHESIS"
INFERENCE: Final[str] = "INFERENCE"
UNKNOWN: Final[str] = "UNKNOWN"

CMB_HISTORICAL_STATUS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "framework_authorship": DECLARATION,
        "earliest_use_of_term_CMB": DECLARATION,
        "historically_first_framework_of_its_kind": HYPOTHESIS,
        "older_code_art_traditions_exist": FACT,
        "independent_historical_priority_verified": UNKNOWN,
    }
)

PATTERN_IS_PROOF: Final[bool] = False
MACHINE_AUTHORITY_OVER_HUMAN_JUDGMENT: Final[bool] = False
DECLARATION_EQUALS_INDEPENDENT_VERIFICATION: Final[bool] = False
PROVENANCE_EQUALS_AUTOMATIC_LEGAL_OWNERSHIP: Final[bool] = False
SELF_REPORTED_TIMESTAMP_EQUALS_WITNESSED_TIMESTAMP: Final[bool] = False


def validate_invariants() -> None:
    if PATTERN_IS_PROOF:
        raise RuntimeError("Invariant violation: PATTERN must not equal PROOF.")
    if MACHINE_AUTHORITY_OVER_HUMAN_JUDGMENT:
        raise RuntimeError("Invariant violation: machine classification cannot supersede human judgment.")
    if DECLARATION_EQUALS_INDEPENDENT_VERIFICATION:
        raise RuntimeError("Invariant violation: an authorship declaration is not independent verification.")
    if PROVENANCE_EQUALS_AUTOMATIC_LEGAL_OWNERSHIP:
        raise RuntimeError(
            "Invariant violation: provenance evidence does not automatically establish legal ownership or enforceability."
        )
    if SELF_REPORTED_TIMESTAMP_EQUALS_WITNESSED_TIMESTAMP:
        raise RuntimeError(
            "Invariant violation: a self-reported timestamp is not an independently witnessed timestamp."
        )


def cmb_authorship_statement() -> str:
    return (
        "Computational Metacognitive Bilingualism (CMB), as named, defined, "
        "systematized, and documented within this corpus, is declared by "
        "Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 as his original framework. "
        "CMB combines programming-language rhetoric, metacognition, human-machine "
        "communication, AI literacy, neurodiversity advocacy, cognitive sovereignty, "
        "and algorithmically mediated public communication. Algorithmic Disruption "
        "Art is positioned as the artistic branch of CMB. The framework builds upon "
        "earlier traditions including code poetry, ASCII and ANSI art, Perl poetry, "
        "codework, electronic literature, creative programming, and software art, "
        "without claiming invention of those preexisting traditions."
    )


def cmb_claim_boundary_statement() -> str:
    return (
        "This declaration records an authorship and provenance claim. "
        "It does not, by itself, establish independent historical priority, "
        "copyright ownership of abstract ideas, patent rights, trademark rights, "
        "or automatic legal enforceability. A cryptographic hash proves the "
        "declaration text has not changed; it does not prove when the text was "
        "first written unless corroborated by an independent external anchor "
        "(see ANCHORING below)."
    )


def canonical_framework_payload() -> dict[str, object]:
    # IMPORTANT: retain the v1.2 canonical field name/value to preserve that hash.
    return {
        "schema_version": SCHEMA_VERSION,
        "framework_version": DECLARATION_VERSION,
        "framework": asdict(CMB),
        "claim_scope": {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in CLAIM_SCOPE.items()
        },
        "historical_status": dict(CMB_HISTORICAL_STATUS),
        "authorship_statement": cmb_authorship_statement(),
        "claim_boundary_statement": cmb_claim_boundary_statement(),
        "declaration_timestamp_utc": DECLARATION_TIMESTAMP_UTC,
    }


def canonical_json() -> str:
    return json.dumps(
        canonical_framework_payload(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_digest(data: str) -> str:
    return sha256_bytes(data.encode("utf-8"))


def framework_sha256() -> str:
    return sha256_digest(canonical_json())


def is_sha256_hex(value: str) -> bool:
    normalized = value.strip().lower()
    return len(normalized) == 64 and all(ch in "0123456789abcdef" for ch in normalized)


@dataclass(frozen=True, slots=True)
class ProvenanceReceipt:
    schema_version: str
    framework: str
    abbreviation: str
    declaration_version: str
    tool_version: str
    declared_originator: str
    artistic_branch: str
    declaration_timestamp_utc: str
    timestamp_status: str
    hash_algorithm: str
    canonical_sha256: str
    status: str
    principle: str


def build_provenance_receipt() -> ProvenanceReceipt:
    return ProvenanceReceipt(
        schema_version=SCHEMA_VERSION,
        framework=CMB.name,
        abbreviation=CMB.abbreviation,
        declaration_version=DECLARATION_VERSION,
        tool_version=TOOL_VERSION,
        declared_originator=CMB.declared_originator,
        artistic_branch=CMB.artistic_branch,
        declaration_timestamp_utc=DECLARATION_TIMESTAMP_UTC,
        timestamp_status="SELF_REPORTED_UNLESS_CORROBORATED",
        hash_algorithm="SHA-256",
        canonical_sha256=framework_sha256(),
        status="AUTHORSHIP_AND_PROVENANCE_DECLARATION",
        principle="PATTERN != PROOF",
    )


def provenance_receipt_json() -> str:
    return json.dumps(asdict(build_provenance_receipt()), ensure_ascii=False, sort_keys=True, indent=2)


def verify_framework_hash(expected_sha256: str) -> bool:
    normalized = expected_sha256.strip().lower()
    if not is_sha256_hex(normalized):
        return False
    return hmac.compare_digest(framework_sha256(), normalized)


ANCHOR_TYPES: Final[tuple[str, ...]] = (
    "public_post",
    "hosted_git_reference",
    "rfc3161_timestamp",
    "public_ledger",
    "other",
)

ANCHOR_REFERENCE_STATUS: Final[str] = "UNVERIFIED_EXTERNAL_REFERENCE"


class AnchorLedgerError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ExternalAnchorRecord:
    schema_version: str
    sequence: int
    anchor_type: str
    description: str
    location: str
    framework_sha256_at_anchor_time: str
    local_recorded_at_utc: str
    claimed_external_time_utc: str | None
    external_time_basis: str | None
    verification_status: str
    previous_record_sha256: str | None
    record_sha256: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_utc_timestamp(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include a timezone or end in Z.")
    return parsed.astimezone(timezone.utc)


def _anchor_hash_payload(anchor: ExternalAnchorRecord) -> dict[str, object]:
    payload = asdict(anchor)
    payload.pop("record_sha256", None)
    return payload


def compute_anchor_record_sha256(anchor: ExternalAnchorRecord) -> str:
    serialized = json.dumps(
        _anchor_hash_payload(anchor),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_digest(serialized)


def validate_anchor_record(anchor: ExternalAnchorRecord) -> None:
    if anchor.schema_version != ANCHOR_SCHEMA_VERSION:
        raise AnchorLedgerError(f"Unsupported anchor schema: {anchor.schema_version!r}.")
    if anchor.sequence < 1:
        raise AnchorLedgerError("Anchor sequence must be >= 1.")
    if anchor.anchor_type not in ANCHOR_TYPES:
        raise AnchorLedgerError(
            f"Unknown anchor_type {anchor.anchor_type!r}; must be one of {ANCHOR_TYPES}."
        )
    if not anchor.location.strip():
        raise AnchorLedgerError("Anchor location must not be empty.")
    if not anchor.description.strip():
        raise AnchorLedgerError("Anchor description must not be empty.")
    if not is_sha256_hex(anchor.framework_sha256_at_anchor_time):
        raise AnchorLedgerError("Anchor framework hash is not valid SHA-256 hex.")
    if anchor.previous_record_sha256 is not None and not is_sha256_hex(anchor.previous_record_sha256):
        raise AnchorLedgerError("previous_record_sha256 is not valid SHA-256 hex.")
    if not is_sha256_hex(anchor.record_sha256):
        raise AnchorLedgerError("record_sha256 is not valid SHA-256 hex.")
    parse_utc_timestamp(anchor.local_recorded_at_utc)
    if anchor.claimed_external_time_utc is not None:
        parse_utc_timestamp(anchor.claimed_external_time_utc)
    if (anchor.claimed_external_time_utc is None) != (anchor.external_time_basis is None):
        raise AnchorLedgerError(
            "claimed_external_time_utc and external_time_basis must either both be set or both be omitted."
        )
    if anchor.verification_status != ANCHOR_REFERENCE_STATUS:
        raise AnchorLedgerError(
            "This tool records external references but does not cryptographically verify them; "
            f"verification_status must be {ANCHOR_REFERENCE_STATUS!r}."
        )
    expected = compute_anchor_record_sha256(anchor)
    if not hmac.compare_digest(expected, anchor.record_sha256.lower()):
        raise AnchorLedgerError(
            f"Anchor record {anchor.sequence} failed its SHA-256 integrity check."
        )


def load_anchor_ledger(path: Path = DEFAULT_ANCHOR_STORE) -> list[ExternalAnchorRecord]:
    if not path.exists():
        return []

    anchors: list[ExternalAnchorRecord] = []
    previous_hash: str | None = None

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AnchorLedgerError(f"Unable to read anchor ledger {path}: {exc}") from exc

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            raise AnchorLedgerError(f"Blank line detected at ledger line {line_number}.")
        try:
            raw = json.loads(line)
            anchor = ExternalAnchorRecord(**raw)
        except (json.JSONDecodeError, TypeError) as exc:
            raise AnchorLedgerError(f"Malformed anchor record at line {line_number}: {exc}") from exc

        validate_anchor_record(anchor)

        expected_sequence = len(anchors) + 1
        if anchor.sequence != expected_sequence:
            raise AnchorLedgerError(
                f"Sequence break at line {line_number}: expected {expected_sequence}, got {anchor.sequence}."
            )
        if anchor.previous_record_sha256 != previous_hash:
            raise AnchorLedgerError(
                f"Hash-chain break at line {line_number}: previous_record_sha256 does not match."
            )

        anchors.append(anchor)
        previous_hash = anchor.record_sha256

    return anchors


def _append_jsonl_record(path: Path, record: ExternalAnchorRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and path.stat().st_size:
        with path.open("rb") as check:
            check.seek(-1, os.SEEK_END)
            if check.read(1) != b"\n":
                raise AnchorLedgerError(
                    f"Refusing to append to {path}: existing ledger does not end with a newline."
                )

    encoded = (
        json.dumps(asdict(record), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")

    try:
        with path.open("ab") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise AnchorLedgerError(f"Unable to append anchor ledger {path}: {exc}") from exc


def add_anchor(
    anchor_type: str,
    location: str,
    description: str,
    path: Path = DEFAULT_ANCHOR_STORE,
    *,
    claimed_external_time_utc: str | None = None,
    external_time_basis: str | None = None,
    local_recorded_at_utc: str | None = None,
) -> ExternalAnchorRecord:
    anchors = load_anchor_ledger(path)
    previous_hash = anchors[-1].record_sha256 if anchors else None

    if (claimed_external_time_utc is None) != (external_time_basis is None):
        raise ValueError(
            "Provide both claimed_external_time_utc and external_time_basis, or neither."
        )

    if claimed_external_time_utc is not None:
        parse_utc_timestamp(claimed_external_time_utc)

    provisional = ExternalAnchorRecord(
        schema_version=ANCHOR_SCHEMA_VERSION,
        sequence=len(anchors) + 1,
        anchor_type=anchor_type,
        description=description.strip(),
        location=location.strip(),
        framework_sha256_at_anchor_time=framework_sha256(),
        local_recorded_at_utc=local_recorded_at_utc or utc_now_iso(),
        claimed_external_time_utc=claimed_external_time_utc,
        external_time_basis=external_time_basis.strip() if external_time_basis else None,
        verification_status=ANCHOR_REFERENCE_STATUS,
        previous_record_sha256=previous_hash,
        record_sha256="0" * 64,
    )

    finalized = replace(provisional, record_sha256=compute_anchor_record_sha256(provisional))
    validate_anchor_record(finalized)
    _append_jsonl_record(path, finalized)
    return finalized


def anchor_ledger_status(anchors: Sequence[ExternalAnchorRecord]) -> Mapping[str, object]:
    return {
        "reference_count": len(anchors),
        "reference_types_used": sorted({a.anchor_type for a in anchors}),
        "ledger_chain_valid": True,
        "externally_verified_by_this_tool": False,
        "ledger_tip_sha256": anchors[-1].record_sha256 if anchors else None,
    }


def run_self_test() -> None:
    validate_invariants()

    first_hash = framework_sha256()
    second_hash = framework_sha256()
    if first_hash != second_hash:
        raise RuntimeError("Canonical serialization is not deterministic.")
    if not verify_framework_hash(first_hash):
        raise RuntimeError("Framework integrity self-verification failed.")
    if CMB.artistic_branch != "Algorithmic Disruption Art":
        raise RuntimeError("CMB artistic branch invariant failed.")
    if "code poetry" not in PREEXISTING_TRADITIONS:
        raise RuntimeError("Historical claim boundary is incomplete.")

    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = Path(tmpdir) / "anchors.jsonl"

        first = add_anchor(
            "other",
            "selftest://one",
            "self-test anchor one",
            path=ledger,
            local_recorded_at_utc="1970-01-01T00:00:00Z",
        )
        second = add_anchor(
            "public_post",
            "selftest://two",
            "self-test anchor two",
            path=ledger,
            claimed_external_time_utc="1970-01-02T00:00:00Z",
            external_time_basis="self-test external clock reference",
            local_recorded_at_utc="1970-01-02T00:00:01Z",
        )

        loaded = load_anchor_ledger(ledger)
        if len(loaded) != 2:
            raise RuntimeError("Anchor ledger round-trip failed.")
        if loaded[0].record_sha256 != first.record_sha256:
            raise RuntimeError("First anchor record changed during round-trip.")
        if loaded[1].previous_record_sha256 != first.record_sha256:
            raise RuntimeError("Anchor hash chain failed.")
        if loaded[1].record_sha256 != second.record_sha256:
            raise RuntimeError("Second anchor record changed during round-trip.")

        tampered = ledger.read_text(encoding="utf-8").replace(
            "self-test anchor one",
            "tampered anchor one",
            1,
        )
        ledger.write_text(tampered, encoding="utf-8")
        try:
            load_anchor_ledger(ledger)
        except AnchorLedgerError:
            pass
        else:
            raise RuntimeError("Tamper detection self-test failed.")


def render_public_declaration(
    anchors: Sequence[ExternalAnchorRecord] | None = None,
    *,
    anchor_store: Path = DEFAULT_ANCHOR_STORE,
) -> str:
    receipt = build_provenance_receipt()
    anchors = list(anchors) if anchors is not None else load_anchor_ledger(anchor_store)
    status = anchor_ledger_status(anchors)

    lines = [
        "═" * 78,
        "COMPUTATIONAL METACOGNITIVE BILINGUALISM // CMB",
        "INTELLECTUAL ORIGIN & METHOD DECLARATION",
        "═" * 78,
        "",
        cmb_authorship_statement(),
        "",
        "CLAIM BOUNDARY:",
        cmb_claim_boundary_statement(),
        "",
        f"Declaration Version : {receipt.declaration_version}",
        f"Tool Version        : {receipt.tool_version}",
        f"Schema Version      : {receipt.schema_version}",
        f"Declared Creator    : {receipt.declared_originator}",
        f"Artistic Branch     : {receipt.artistic_branch}",
        f"Timestamp (UTC)     : {receipt.declaration_timestamp_utc}  (self-reported)",
        f"SHA-256             : {receipt.canonical_sha256}",
        "",
        "CORE INVARIANTS:",
        "  PATTERN != PROOF",
        "  HUMAN_AGENCY > MACHINE_AUTHORITY",
        "  DECLARATION != INDEPENDENT_VERIFICATION",
        "  PROVENANCE != AUTOMATIC_LEGAL_OWNERSHIP",
        "  SELF_REPORTED_TIMESTAMP != WITNESSED_TIMESTAMP",
        "",
        "EXTERNAL EVIDENCE REFERENCES:",
        f"  Reference count              : {status['reference_count']}",
        f"  Reference types used         : {', '.join(status['reference_types_used']) or 'none'}",
        f"  Local ledger hash-chain valid: {status['ledger_chain_valid']}",
        f"  Verified externally by tool  : {status['externally_verified_by_this_tool']}",
        f"  Ledger tip SHA-256           : {status['ledger_tip_sha256'] or 'none'}",
    ]

    if anchors:
        lines.append("  References:")
        for anchor in anchors:
            external_time = anchor.claimed_external_time_utc or "not recorded"
            lines.append(
                f"    - #{anchor.sequence} [{anchor.anchor_type}] {anchor.location} "
                f"| external time: {external_time} | status: {anchor.verification_status}"
            )
    else:
        lines.extend(
            (
                "  No external evidence references recorded.",
                "  Stronger evidence requires an independently verifiable source, such as",
                "  a valid RFC 3161 timestamp token or another durable third-party record.",
            )
        )

    lines.extend(
        (
            "",
            "NOTE:",
            "  The local JSONL ledger is tamper-evident through hash chaining, not immutable.",
            "  A public Git commit date alone is not treated as an independently trusted clock.",
            "  External references remain unverified until their underlying evidence is checked.",
            "",
            "═" * 78,
        )
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmb_provenance.py",
        description="CMB authorship, provenance, and external-evidence reference tool.",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_ANCHOR_STORE,
        help=f"Anchor ledger path (default: {DEFAULT_ANCHOR_STORE}).",
    )

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare", help="Print declaration, stable hash, and evidence references.")
    sub.add_parser("receipt", help="Print the machine-readable provenance receipt.")

    verify = sub.add_parser("verify", help="Check a SHA-256 hash against the declaration.")
    verify.add_argument("expected_sha256")

    anchor = sub.add_parser("anchor", help="Append an external evidence reference.")
    anchor.add_argument("anchor_type", choices=ANCHOR_TYPES)
    anchor.add_argument("location", help="URL, commit reference, transaction ID, TSA token reference, etc.")
    anchor.add_argument("description", help="Human-readable description of the external evidence.")
    anchor.add_argument(
        "--external-time",
        dest="claimed_external_time_utc",
        help="Timestamp shown by the external source, with timezone; recorded as a claim until verified.",
    )
    anchor.add_argument(
        "--time-basis",
        dest="external_time_basis",
        help="What external system or artifact supplies --external-time.",
    )

    sub.add_parser("anchors", help="List external evidence references.")
    sub.add_parser("verify-ledger", help="Verify the local anchor hash chain.")
    sub.add_parser("selftest", help="Run integrity and tamper-detection tests.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        run_self_test()

        if args.command == "declare":
            print(render_public_declaration(anchor_store=args.store))

        elif args.command == "receipt":
            print(provenance_receipt_json())

        elif args.command == "verify":
            ok = verify_framework_hash(args.expected_sha256)
            print("MATCH" if ok else "NO MATCH")
            return 0 if ok else 1

        elif args.command == "anchor":
            if (args.claimed_external_time_utc is None) != (args.external_time_basis is None):
                parser.error("--external-time and --time-basis must be supplied together.")

            anchor = add_anchor(
                args.anchor_type,
                args.location,
                args.description,
                path=args.store,
                claimed_external_time_utc=args.claimed_external_time_utc,
                external_time_basis=args.external_time_basis,
            )
            print(f"Reference appended: #{anchor.sequence} [{anchor.anchor_type}] {anchor.location}")
            print(f"  declaration SHA-256 : {anchor.framework_sha256_at_anchor_time}")
            print(f"  record SHA-256      : {anchor.record_sha256}")
            print(f"  verification status : {anchor.verification_status}")

        elif args.command == "anchors":
            anchors = load_anchor_ledger(args.store)
            if not anchors:
                print("No external evidence references recorded.")
            for anchor in anchors:
                print(
                    f"#{anchor.sequence} [{anchor.anchor_type}] {anchor.location} ✦ "
                    f"{anchor.description} ({anchor.verification_status})"
                )

        elif args.command == "verify-ledger":
            anchors = load_anchor_ledger(args.store)
            tip = anchors[-1].record_sha256 if anchors else "none"
            print(f"LEDGER OK ✦ {len(anchors)} record(s), tip={tip}")

        elif args.command == "selftest":
            print("Self-test passed.")

    except (AnchorLedgerError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
