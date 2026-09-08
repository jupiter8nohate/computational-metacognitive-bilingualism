# CMB Digital Nervous Immune System

**Protocol:** CMB-DNIS-1  
**Status:** experimental bounded orchestration

CMB-DNIS-1 turns the nervous-system and immune-system metaphors into a testable software routing model.

The biological language is metaphorical. The system does not claim biological consciousness, hidden network visibility, self-replication, medical function, or the ability to control arbitrary external crawlers.

~~~text
SENSE
  |
  v
NORMALIZE
  |
  v
POSITION
  |
  v
CHAPERONE
  |
  v
POLICY
  |
  +--------------------+
  |                    |
 DENY              ALLOW / ESCALATE
  |                    |
  v                    v
REFLEX             RISK CHECK
  |                    |
  v               +----+----+
RECOVERY           |         |
PROPOSAL          LOW       HIGH
  |                |         |
  |                v         v
  |              REFLEX   CORTEX
  |                |       LIAISON
  +----------------+---------+
                   |
                   v
                RECEIPT
                   |
                   v
                 MEMORY
~~~

## Digital DNA

Every cell packet carries the same invariant digest.

~~~text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CAPABILITY != AUTHORITY
AGENT_CAN_PROPOSE != AGENT_CAN_MERGE
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

"Digital DNA" means a stable set of software invariants. It is not biological DNA.

## Cell agents

| Cell agent | Function | Authority |
| --- | --- | --- |
| RECEPTOR_CELL | Accept trusted caller-supplied events | Read-only |
| DENDRITIC_CELL | Normalize event structure | Read-only |
| POSITION_CELL | Calculate routing friction | Read-only |
| CHAPERONE_CELL | Validate structure and invariant continuity | Read-only |
| T_CELL_POLICY_GATE | Apply the authoritative policy result | Decision boundary only |
| REFLEX_CELL | Fail closed or allow low-risk authorized work | Bounded reflex |
| MACROPHAGE_RECOVERY | Propose bounded repair after concrete failure | Propose-only |
| CORTEX_LIAISON | Escalate consequential judgment to the human | Escalate-only |
| B_CELL_PROVENANCE | Produce a tamper-evident route digest | Receipt-only |
| MEMORY_CELL | Preserve a digest-only outcome reference | Bounded memory |

The machine-readable registry is `agents/immune-cell-registry.json`.

## Why some cells are deterministic

Not every role should be a generative AI model.

The strongest reflexes are deterministic:

- structural validation;
- cryptographic hashing;
- explicit policy denial;
- score bounds;
- fixed routing;
- authority checks.

Generative AI is most useful in bounded areas such as summarizing evidence, comparing recovery options, or proposing a minimal repair after a deterministic failure.

~~~text
DETERMINISTIC_REFLEX > MODEL_GUESS
MODEL_ADVICE != POLICY
AI_REPAIR != HUMAN_APPROVAL
~~~

## Sensor boundary

RECEPTOR_CELL does not sniff arbitrary internet traffic.

It can accept events from explicit adapters such as:

- GitHub events;
- application middleware;
- API gateways;
- MCP tools or resources;
- consent services;
- provenance verifiers;
- rate-limit or security telemetry supplied by infrastructure you control.

~~~text
SENSOR_INPUT != OMNISCIENCE
MCP != PACKET_SNIFFER
OBSERVATION != UNDERSTANDING
~~~

## Reflex and cortex split

Low-risk, reversible, explicitly authorized actions can take the reflex path.

High-risk, irreversible, ambiguous, or policy-escalated actions are routed to CORTEX_LIAISON for human judgment.

~~~text
SYSTEM_CAN_REFLEX
AGENT_CAN_PROPOSE
HUMAN_CAN_JUDGE

CAPABILITY != AUTHORITY
~~~

## Memory without covert profiling

MEMORY_CELL stores a digest-only outcome reference in the reference implementation.

This is deliberate. An immune memory metaphor must not silently become surveillance architecture.

~~~text
MEMORY != SECRET_PROFILE
RECURRENCE != PROOF
MINIMIZE_DATA > HOARD_DATA
~~~

## Recovery

MACROPHAGE_RECOVERY maps onto the existing Steward repair model.

It may propose a bounded repair after a concrete failure. Existing repository governance still applies:

~~~text
AI_CHANGE != ACCEPTED_CHANGE
TEST_PASS != HUMAN_APPROVAL
PR != MERGE
RECOVERY > SILENT_FAILURE
~~~

## Python reference

~~~python
from cmb_agents.immune_system import Decision, Signal, process_signal

trace = process_signal(
    Signal(
        event_id="evt-001",
        source_kind="webhook",
        requested_action="TRANSLATE",
        payload_digest="sha256:" + ("0" * 64),
        sensitivity=0.1,
        consent_present=True,
        reversible=True,
    ),
    policy_decider=lambda signal: Decision.ALLOW,
)

print(trace.final_decision.value)
print(trace.receipt)
~~~

In production, the `policy_decider` should be backed by the existing CMB policy engine or another explicitly authorized policy source rather than a hardcoded lambda.
