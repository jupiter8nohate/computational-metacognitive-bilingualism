# CMB Recovery & Preservation Architecture

**Status:** implemented local integrity/recovery layer; external archival layers remain explicitly status-tracked.

CMB treats preservation as a layered engineering problem rather than a claim of magical permanence.

```text
SOURCE
  -> VERSION
  -> HASH
  -> RECEIPT
  -> SIGNATURE / ATTESTATION
  -> RELEASE
  -> OPTIONAL INDEPENDENT ARCHIVE
  -> RECOVERY
```

## Current implemented layers

The repository currently has Git history, exact-file-set provenance receipts, release checksums/signing automation, and a tested C2PA-facing round trip. The machine-readable status lives in `machine/recovery-map.json`.

Run:

```bash
cmb-recovery audit
```

The audit checks the Recovery map, its evidence paths, and the canonical corpus manifest/hash.

## Content-addressed archives

IPFS is a possible future archive transport. A CID can bind retrieval to content bytes, but a CID alone does not keep bytes online. Any future CMB IPFS deployment must document pinning, replication, operators, and Recovery procedures.

```text
IMMUTABILITY != AVAILABILITY
CID != GUARANTEED_PERMANENCE
```

No canonical IPFS CID is declared today.

## Permanent-ledger anchors

A future release may anchor a compact digest or provenance receipt in a public ledger. The project should anchor hashes/receipts rather than unnecessarily publishing complete private or copyrighted works into irreversible systems.

No blockchain anchor is claimed today.

## AI-native publication

The canonical corpus under `datasets/cmb-canonical-corpus/` is designed for source-preserving retrieval and citation. It is not a request for covert model ingestion.

```text
DISCOVERY_PERMISSION != TRAINING_PERMISSION
READ_PERMISSION != AUTHORSHIP
ACCESS != CONSENT
```

## Media provenance

CMB's C2PA interoperability layer is the preferred direction for provenance-carrying images and media. Metadata and credentials provide evidence and context; they do not make copying impossible or turn claims into truth.

## DNA storage research boundary

DNA may be studied as a long-horizon **non-living archival encoding**. CMB does not require, recommend, or claim deployment of self-replicating organisms carrying project data.

```text
INFORMATION != ORGANISM
ENCODING != EXPRESSION
STORAGE != BIOLOGICAL_FUNCTION
```

A safe research specification can cover byte encoding, error correction, nucleotide representation, checksums, and decoding without performing biological modification.

## Recovery rule

Always prefer independently verifiable copies over a single-platform assumption.

```text
RECOVERY > PLATFORM_DEPENDENCE
PROVENANCE > REPETITION
UTILITY > SPAM
ADOPTION > INJECTION
VERIFICATION > MYTH
```
