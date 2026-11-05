# Claim Enforcement Evidence Policy

Status: policy selected for evidence model; migration pending

## Purpose

This note records the current evidence boundary and selected evidence model for
`artifacts/claim-enforcement/` without changing runtime audit semantics in this
step.

It exists to stop agents from guessing whether session-scoped
claim-enforcement artifacts are disposable runtime noise or formal
governance evidence.

## Current Categories

### 1. Stable baseline and test evidence

The following category is treated as stable tracked evidence:

- `artifacts/claim-enforcement/checker-tests/*`

This includes checker inputs, expected outputs, and test reports used to
verify deterministic claim-enforcement behavior.

### 2. Session-scoped claim-enforcement evidence

The following categories contain session-scoped evidence packets:

- `artifacts/claim-enforcement/session-*/claim-enforcement-check.json`
- `artifacts/claim-enforcement/<session-id>/claim-enforcement-check.json`

`<session-id>` may be timestamp-shaped or UUID-shaped. These directories are
the same artifact class when they contain `claim-enforcement-check.json`.

## Repo Consumption

These session-scoped artifacts are not disposable by assumption. Repo tooling
currently consumes them.

Known consumers:

- `governance_tools/runtime_completeness_audit.py`
- `governance_tools/closeout_audit.py`

Current runtime completeness logic expects:

- `artifacts/claim-enforcement/<session_id>/claim-enforcement-check.json`

Current closeout audit logic recursively scans claim-enforcement check files to
derive aggregate governance signals such as count, drift, downgrade, block,
and override metrics.

## Historical Tracking State

Historical tracking is mixed.

Observed state:

- checker-test baseline evidence is tracked
- many historical session-scoped claim-enforcement packets are tracked
- newer session-scoped claim-enforcement packets may remain untracked

This means the repository historically mixed stable baseline evidence and raw
session-scoped evidence inside the same artifact root.

## Selected Model

This repository adopts the compact canonical receipt model.

Under this model:

- raw session-scoped claim-enforcement packets remain session-local runtime
  evidence
- compact tracked receipt or summary artifacts become the repo-level
  governance evidence surface
- checker-test baseline evidence remains tracked

This policy selects the target model, but does not complete migration in this
step.

## Current Rule

2026-06-18 owner-ratified update:

- `artifacts/claim-enforcement/claim-enforcement-receipts.ndjson` is selected
  to become ignored by default as an ordinary runtime artifact.
- Durable reviewer-facing claim-enforcement evidence must be produced by an
  explicit audit / reviewer milestone export, not by accidental runtime
  appends.
- Implementation is pending a separate slice. This policy update does not
  change `.gitignore`, tracking state, runtime behavior, hook behavior, or
  validator behavior.

Until compact receipt surfaces are defined and migration rules are finalized:

- new raw session-scoped claim-enforcement packets must not be automatically
  committed as repo evidence
- new raw session-scoped claim-enforcement packets must not be automatically
  ignored by policy changes made as cleanup side effects
- agents must not delete claim-enforcement session evidence as if it were
  ordinary runtime trash
- checker-test baseline evidence remains tracked

## Evidence Categories Under The Selected Model

### Tracked governance evidence

- `artifacts/claim-enforcement/checker-tests/*`
- future compact canonical receipt or summary artifacts for claim-enforcement

### Session-local runtime evidence

- `artifacts/claim-enforcement/session-*/claim-enforcement-check.json`
- `artifacts/claim-enforcement/<session-id>/claim-enforcement-check.json`

Raw packets may still be consumed by runtime audits, but they are not the
intended long-term tracked evidence surface under the selected model.

## Compact Receipt Surface (Defined, Not Yet Implemented)

The compact tracked evidence surface for this model is:

- `artifacts/claim-enforcement/claim-enforcement-receipts.ndjson`

This file is intended to be append-only NDJSON.

Purpose:

- preserve repo-level machine-readable evidence that claim-enforcement existed
  for a session
- avoid treating raw `session-*` packet directories as the primary tracked
  evidence surface
- provide a future tracked summary layer that is smaller and more reviewable
  than raw session packet history

### Receipt Row Shape (v0.1)

Each line should represent one session-scoped compact receipt with these
minimum fields:

| Field | Type | Notes |
|-------|------|-------|
| `schema_version` | string | initial value: `0.1` |
| `artifact_type` | string | fixed value: `claim-enforcement-receipt` |
| `session_id` | string | timestamp-shaped or UUID-shaped session identifier |
| `recorded_at` | ISO-8601 UTC string | when the compact receipt row was written |
| `claim_enforcement_check_present` | bool | whether the raw session packet existed when observed |
| `source_packet_dir` | string | expected raw packet directory path for that session |
| `raw_packet_policy` | string | initial value: `session_local` |
| `repo_evidence_status` | string | initial value: `compact_receipt` |
| `evidence_scope` | string | fixed value: `session_scoped` |

Optional future fields may be added only with explicit schema-version
governance.

### Example Row

```json
{
  "schema_version": "0.1",
  "artifact_type": "claim-enforcement-receipt",
  "session_id": "585cfd62-322d-4bde-8f87-786a096ea010",
  "recorded_at": "2026-06-02T12:00:00Z",
  "claim_enforcement_check_present": true,
  "source_packet_dir": "artifacts/claim-enforcement/585cfd62-322d-4bde-8f87-786a096ea010",
  "raw_packet_policy": "session_local",
  "repo_evidence_status": "compact_receipt",
  "evidence_scope": "session_scoped"
}
```

### Authority Boundary

Under the selected model:

- raw session packets remain the runtime-facing session evidence artifacts
- compact receipts become the intended tracked repo-facing evidence surface
- compact receipts do not automatically replace runtime consumers in this step
- compact receipts must not be treated as proof that historical raw-packet
  tracking has already been normalized

Any change to claim-enforcement evidence tracking must be an explicit policy
decision, not a side effect of dirty-tree cleanup.

## CE-1C Implementation Status

The following have been implemented (CE-1C.1 through CE-1C.3):

- `governance_tools/claim_enforcement_receipt_writer.py` — append-only
  NDJSON writer with CE-1B minimum fields (CE-1C.1)
- `runtime_hooks/core/session_end.py` — dual-write: compact receipt
  appended alongside raw packet on every session closeout; wrapped in
  try/except so write failure cannot break raw packet emission (CE-1C.2)
- `governance_tools/claim_enforcement_receipt_validator.py` — read-side
  validator detecting malformed rows, policy deviations, and coverage
  gaps (unreceipted raw packets) (CE-1C.3)

## Tracking Boundary (CE-1C.4)

### Evidence surface roles

| Surface | Role | Tracking rule |
|---------|------|---------------|
| `artifacts/claim-enforcement/<session_id>/claim-enforcement-check.json` | runtime-facing session evidence | not auto-committed; may remain untracked |
| `artifacts/claim-enforcement/claim-enforcement-receipts.ndjson` | repo-facing compact evidence index | tracked only on manual promotion/review, not on every runtime run |
| `artifacts/claim-enforcement/checker-tests/*` | stable test baseline | tracked |

### Rationale for manual-only promotion of receipts.ndjson

Auto-committing every dual-write append would make
`claim-enforcement-receipts.ndjson` equivalent to another runtime log.
Its value as a repo-facing evidence surface depends on being committed
deliberately — when a governance review or session promotion warrants it.

### .gitignore rule for timestamp-shaped session directories

Timestamp-shaped session directories (`session-*/`) are safe to ignore
because they follow a predictable naming pattern that does not overlap
with stable evidence directories (`checker-tests/`) or the receipts file.

Pattern added: `artifacts/claim-enforcement/session-*/`

UUID-shaped session directories are NOT covered by this pattern due to
design risk: a wildcard broad enough to match UUIDs would also match
other future artifact directories. UUID output path redesign is deferred
to CE-1D.

### Explicit non-decisions (CE-1C.4)

This boundary definition does not declare:

- that all existing UUID-shaped raw session directories should be ignored
- that `claim-enforcement-receipts.ndjson` is already in its final form
- that runtime_completeness_audit.py or closeout_audit.py consume the
  compact receipt
- that historical raw session evidence has been migrated

## Migration Still Required

Future governance work must still address:

1. ~~writer/generation path~~ — **done (CE-1C.1)**
2. tracking rule for compact surface — **partially addressed (CE-1C.4)**
3. ignore rule for raw session packets — **partially addressed: timestamp-shaped (CE-1C.4); UUID-shaped deferred (CE-1D)**
4. how historical tracked raw session packets are handled — not yet decided
5. how runtime audits distinguish raw runtime evidence from tracked
   governance evidence — not yet decided

## Non-Decisions

This note does not declare:

- that all raw session evidence must be committed
- that all raw session evidence is already ignored
- that current historical tracking is correct or normalized
- that `session-index.ndjson` should remain tracked
- that compact receipt auto-write equals auto-commit
- that compact receipt shape is final
