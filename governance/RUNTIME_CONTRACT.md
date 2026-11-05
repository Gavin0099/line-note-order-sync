---
audience: agent-runtime
authority: canonical
can_override: false
overridden_by: ~
default_load: on-demand
---

# Runtime Contract v1.0

> **Priority**: gates runtime execution. Loaded when a runtime hook evaluates a
> task, not on every conversation turn.

`SYSTEM_PROMPT.md` §2.8 defines the **display contract**: the seven fields a
human sees in a `[Governance Contract]` block at task start.

This document defines the **runtime contract**: four additional fields that
`runtime_hooks/` reads to gate execution. They are not display fields. A model
emitting a task-start block on a surface with no runtime hook has nothing to say
about them.

## Why this document exists

These four fields were canonical once. Commit `94c0870c` (2026-03-12) added
`RULES`, `RISK`, `OVERSIGHT` and `MEMORY_MODE` to `SYSTEM_PROMPT.md`, to
`governance_tools/contract_validator.py` and to `docs/runtime-governance-update.md`
in one change. Commit `8994a5e1` (2026-03-20) rewrote the canonical section and
dropped them, touching neither the validator nor the runtime documentation.

The result was five months of authority drift: the validator required four
fields no codex defined, and the runtime kept gating on them. Relaxing the
validator to match the codex would have silently disabled rule routing and the
durable-memory oversight gate.

This document gives the four fields a canonical home that matches how they are
actually used, rather than restoring them to a display contract where three of
them do not belong.

## Fields

```text
RULES       = <comma-separated rule packs>
RISK        = <low|medium|high>
OVERSIGHT   = <auto|review-required|human-approval>
MEMORY_MODE = <stateless|candidate|durable>
```

- `RULES`: the rule packs routed into this task. Each name must resolve against
  the available packs, which include any `rule_roots` declared by a domain
  contract. At least one is required. An empty or absent `RULES` means no pack
  is routed — rule enforcement does not fall back to a default set.
- `RISK`: `low | medium | high`. Single-valued.
- `OVERSIGHT`: `auto | review-required | human-approval`. Single-valued.
- `MEMORY_MODE`: `stateless | candidate | durable`. Single-valued. `candidate`
  means session output is not yet durable project truth.

## Gates

- `RISK = high` must not complete under `OVERSIGHT = auto`.
- `MEMORY_MODE = durable` must not complete under `OVERSIGHT = auto`.
- `MEMORY_MODE = durable` under `OVERSIGHT = review-required` is allowed but
  warned: durable promotion normally follows an explicit review.

## Source of authority

The declared field is authoritative. A runtime caller may supply the same value
as an argument, but a caller value that **disagrees** with a declared value is a
failure, not an override.

This is deliberate. The two sources previously diverged unnoticed: a contract
could declare `RISK = high` / `OVERSIGHT = human-approval` and still be gated as
`low` / `auto`. A declaration that does not govern is an unevidenced claim.

When the contract does not declare a field, a caller-supplied value is used, so
a caller providing the only available value is not broken by this rule.

## Relationship to the display contract

| | display contract | runtime contract |
|---|---|---|
| defined in | `SYSTEM_PROMPT.md` §2.8 | this document |
| fields | `LANG`, `LEVEL`, `SCOPE`, `PLAN`, `LOADED`, `CONTEXT`, `PRESSURE` (+ optional `AGENT_ID`, `SESSION`) | `RULES`, `RISK`, `OVERSIGHT`, `MEMORY_MODE` |
| emitted at | task start, milestone, scope change, stop/escalation, material field change | when a runtime hook evaluates a task |
| audience | human reading the response | `runtime_hooks/` |

Both may appear in one `[Governance Contract]` block. They are validated
separately because they answer to different authorities and different surfaces.

**A display-only block is not a runtime-compliant block.** Validating the seven
display fields says nothing about whether a task may execute. Reporting a
display pass as runtime compliance is a governance failure.

## Validation

- `governance_tools.contract_validator.validate_display_contract` — display only
- `governance_tools.contract_validator.validate_runtime_contract` — runtime only
- `governance_tools.contract_validator.validate_contract` — both; this remains
  the default so that existing callers do not silently stop checking the runtime
  fields. Opting out is explicit via `include_runtime=False`.
