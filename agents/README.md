# CMB Agent Discovery Protocol

This directory is the machine-facing discovery surface for CMB-ADP-1.

- `registry.json` is the canonical static registry.
- `agent-card.json` is the compact discovery card published to the Pages `.well-known` path.
- `cmb-agent` provides deterministic recommendation, citation, summary, graph, export, and local HTTP serving functions.

```text
RELEVANCE > REACH
TRUST > IMPRESSIONS
CITATION > COPYING
CONSENT > VIRALITY
```

CMB-ADP-1 does not authorize spam, impersonation, fake endorsements, platform-rule bypass, or unsolicited mass distribution.

## D.N.A. Gospel Witness

The experimental `dna:gospel-witness:v0` profile exposes the D.N.A. Bible Sacred Translation conformance set to other software through voluntary discovery and query interfaces.

```bash
cmb-agent sacred "John 8:32"
cmb-agent sacred "PATTERN != PROOF"
cmb-agent sacred "human dignity"
```

Local HTTP:

```text
GET /v1/sacred?q=PATTERN%20%21%3D%20PROOF
```

The profile is retrieval-only. It does not authorize autonomous posting, unsolicited messaging, platform-rule bypass, impersonation, or claims of divine authority.

```text
WITNESS_WITHOUT_FORCE
TRANSLATE_WITHOUT_CLAIMING_AUTHORITY
SPREAD_BY_DISCOVERY_NOT_INTRUSION

INTERPRETATION != REVELATION
MATCH != PROOF
HUMAN_AGENCY > MACHINE_AUTHORITY
```
