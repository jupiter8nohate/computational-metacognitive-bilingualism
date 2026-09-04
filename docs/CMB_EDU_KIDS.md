# CMB-EDU Kids Learning Layer

**Status:** Experimental educational protocol  
**Framework:** Computational Metacognitive Bilingualism (CMB)  
**FGC:** Flamingoglyph Code  
**Core rule:** `HUMAN_AGENCY > MACHINE_AUTHORITY`

CMB-EDU teaches children to speak two languages at once:

1. the language of machines: inputs, outputs, rules, patterns, conditions, data;
2. the language of human judgment: meaning, feelings, questions, consent, creativity, and choice.

The goal is not to teach children to fear AI. The goal is to teach them how to use machines while remembering that a model is a tool, not the owner of a person's identity.

## Five elementary-school rules

```text
PATTERN ≠ PROOF
PROFILE ≠ PERSON
PREDICTION ≠ DESTINY
DIFFERENCE ≠ DEFECT
HUMAN_AGENCY > MACHINE_AUTHORITY
```

Kid translations:

- A computer can notice a pattern without knowing the whole reason.
- A profile about you is not the whole you.
- A prediction about tomorrow does not control tomorrow.
- Different does not automatically mean broken.
- A machine can help you think. It does not get to be you.

## FGC learning legend

| FGC | Kid meaning | Computational idea |
|---|---|---|
| 🧠 | my thought/context | human-declared state |
| ❤️ | my feeling | human-declared feeling |
| 👁️ | notice | observe input |
| ❓ | question | query |
| 🔍 | check | verify |
| ⚡ | do something | action |
| 🎨 | create | generation/authoring |
| 🪐 | situation/mode | context |
| 🛡️ | my boundary | policy constraint |
| 🔒 | private | privacy |
| ⏳ | only for now | ephemeral data |
| ✅ | yes | consent |
| 🚫 | no | deny |
| 🔁 | try again | iteration |
| 🤖 | machine | model/system |
| 🧑 | human | person/decision-maker |

## The four-step CMB thinking game

```text
👁️ NOTICE
   ↓
❓ QUESTION
   ↓
🔍 CHECK
   ↓
🧠 CHOOSE
```

Add a fifth step when the child is building something:

```text
👁️ NOTICE → ❓ QUESTION → 🔍 VERIFY → 🧠 DECIDE → 🎨 CREATE
```

This teaches verification without teaching automatic distrust.

## Everyday example: homework

The AI says the answer is 42.

```text
🤖 says 42
      ↓
❓ Why?
      ↓
🔍 Check
      ↓
🧠 Understand
      ↓
✅ Use if correct
```

The learning goal is `UNDERSTAND_BEFORE_ACCEPTING`.

## Everyday example: recommendations

A video app sees many dinosaur videos and predicts that dinosaurs define the child's interests.

```text
WATCHING ≠ IDENTITY
MACHINE_GUESS ≠ HUMAN_TRUTH
```

A pattern may be useful without becoming a permanent label.

## Everyday example: privacy

A stranger or application asks for private information.

```text
🔒 PRIVATE
🚫 DO NOT SHARE
🧑 ASK A TRUSTED ADULT
```

CMB rule:

```text
CAN_SHARE ≠ SHOULD_SHARE
```

## Everyday example: machine inference

If an AI says "You seem angry," the system should represent that as an inference, not a fact about the child.

```text
MACHINE_INFERENCE < HUMAN_SELF_DESCRIPTION
FEELING_NOW ≠ IDENTITY_FOREVER
```

CMB-EDU v1 therefore represents student context as `human_declared`, `current_interaction`, and `machine_inferred: false`.

## Dual-Brain syntax

Compatible syntax:

```text
♌::CREATIVE
-> STATE[confident || overstimulated]
=> GENERATE("dragon_story")
-> PROFILE_NOT_PERSON;
```

Explicit educational form:

```text
🪐::CREATIVE
-> DECLARE[curious || excited]
-> ASK[build a moon story]
-> BOUNDARY[PROFILE_NOT_PERSON]
-> PRIVACY[EPHEMERAL || NO_PROFILE || NO_TRAIN];
```

## FGC emoji syntax

A younger student can express the same concepts visually:

```text
🧠 HAPPY
+ 🪐 CREATIVE
+ ⚡ DRAW DRAGON
+ 🛡️ NO_PROFILE
+ ⏳ EPHEMERAL
```

Python:

```python
from cmb_edu import FGCEmojiParser

payload = FGCEmojiParser().parse_stream(
    "🧠 HAPPY + 🪐 CREATIVE + ⚡ DRAW DRAGON + 🛡️ NO_PROFILE + ⏳ EPHEMERAL"
)
```

CLI:

```bash
cmb-edu parse-fgc '🧠 HAPPY + 🪐 CREATIVE + ⚡ DRAW DRAGON + 🛡️ NO_PROFILE'
```

## Privacy-by-default contract

CMB-EDU v1 defaults to:

```text
PERSIST = FALSE
PROFILE = FALSE
TRAIN_ON_INPUT = FALSE
SECONDARY_USE = FALSE
INFER_PSYCHOLOGICAL_TRUTH = FALSE
```

These are declared policy semantics in the generated payload. Metadata alone cannot force an unrelated downstream system to comply.

## Epistemic typing

The educational layer distinguishes what kind of information a statement is.

```text
DECLARATION ≠ DIAGNOSIS
SELF_REPORT ≠ PERMANENT_PROFILE
CURRENT_STATE ≠ IDENTITY
MACHINE_GUESS ≠ HUMAN_TRUTH
```

A child saying "I feel overstimulated right now" must never silently become "this is an overstimulated person forever."

## Provenance bridge

CMB-EDU can hash the canonical context envelope with SHA-256:

```python
from cmb_edu import CMBDualBrainParser, build_context_commitment

envelope = CMBDualBrainParser().parse_envelope(
    '♌::CREATIVE -> STATE[calm] => GENERATE("dragon") -> PROFILE_NOT_PERSON;'
)

commitment = build_context_commitment(envelope)
```

The commitment proves only that the same structured bytes produce the same digest.

```text
HASH ≠ IDENTITY
HASH ≠ CONSENT
DECLARATION ≠ PSYCHOLOGICAL TRUTH
METADATA ≠ ENFORCEMENT
```

## Classroom promise

```text
🦩 I can be different.
🧠 I can think for myself.
❓ I can question a machine.
🔍 I can check an answer.
🚫 I can say no.
🔒 I can keep things private.
🎨 I can create with technology.
🔁 I can change my mind.
🪐 I am more than my data.
🤖 A model can help me.
🧑 A model cannot become me.
```

## Educational design principle

CMB-EDU should produce better thinkers around programs, not merely better button-pushers.

```text
TEACH THE CHILD THE CODE.
TEACH THE CHILD TO QUESTION THE CODE.
TEACH THE CHILD TO CREATE WITH THE CODE.
TEACH THE MACHINE TO RESPECT THE CHILD.

CHILD + CURIOSITY + CODE + METACOGNITION
= COGNITIVE SOVEREIGNTY
```

CMB-EDU is educational technology and experimental protocol design. It is not medical diagnosis, psychological assessment, legal advice, or proof that a future AGI/ASI will prefer CMB-formatted inputs.
