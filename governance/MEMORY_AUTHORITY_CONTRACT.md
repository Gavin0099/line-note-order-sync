# Memory Authority Contract

<!-- mrcsp_activation_id: mrcsp-m1-authority-reader-v1 -->

> Version: 1.2.0
> Written: 2026-04-30
> Amended: 2026-08-21
> Status: ACTIVE - warning mode with active-window completion blocker candidate
> Authority: Memory Authority Enforcement Plan v0.3 (session 2026-04-30), amended by v1.1.0 canonical-writer alignment and v1.2.0 surface-authority terminology

---

## Purpose

This contract defines what makes a memory entry **traceably bound evidence**
rather than an unverifiable claim. Presence in `repo/memory/` is **necessary but
not sufficient** for cross-agent use and does not create normative authority.

A memory entry that lacks a traceable anchor can be contradicted without audit
trail, silently drift from reality, or be cited in governance decisions without
verifiable origin.

This contract also defines the current canonical writer boundary for new
session-derived memory. A memory entry may be visible under `memory/` and still
be non-canonical, unbound, stale, or only observation-grade evidence.

---

## 0. Amendment Record

### 0.1 v1.1.0 - Canonical Writer And Workflow Alignment

**Name of change**: canonical writer, memory binding, and workflow dispatcher
alignment.

**Rationale**: Version 1.0.0 described early memory authority semantics using
old daily bullet entries such as `- what changed:` plus `commit hash` and
`session_id` anchors. Current repository practice uses
`governance_tools.memory_record` canonical records and
`governance_tools.memory_workflow` guard summaries. The contract must describe
current admissibility and claim-boundary semantics so future agents do not treat
old-format memory entries as acceptable new records.

**Evidence**:

- `governance/MEMORY_PROTOCOL.md` requires all new session-derived memory to use
  `governance_tools.memory_record` and prohibits direct markdown append in
  `- what changed:` or `- what_changed:` format.
- `governance_tools/memory_record.py` emits `record_format_version`, `writer`,
  `commit`, `commit_hash`, `session_id`, `memory_binding`, `test_evidence`,
  `next_step`, and `plan_reconciliation`.
- `governance_tools/memory_record.py` sets `memory_binding: bound` only when the
  supplied commit string matches a hash-like regex; other values are written as
  `memory_binding: unbound`.
- `governance_tools/memory_authority_guard.py` detects `non_canonical_writer`,
  old-format entries after the canonical-writer cutoff, and active-window
  non-canonical writer violations.
- `governance_tools/memory_workflow.py` summarizes memory guard status and
  reports `completion_claim_allowed` for governed memory tasks.
- `PLAN.md` already records canonical writer, active-window guard summary,
  dispatcher routing, and opt-in blocker path as current memory authority
  surfaces, while explicitly not claiming historical debt cleanup or global
  enforcement closure.

**Updated violation semantics table**: see Section 4.

**Non-claims for this amendment**:

- no memory writer schema change;
- no memory guard behavior change;
- no memory workflow behavior change;
- no hook, CI, pre-push, closeout, or enforcement behavior change;
- no historical memory debt cleanup;
- no backfill of old memory records;
- no semantic correctness guarantee for memory content.

### 0.2 Report-Only `ok` Semantics

**Name of change**: report-only guard output interpretation hardening.

**Rationale**: Phase 1 `ok=True` is an execution/reporting status, not proof
that memory authority is clean. When warnings such as `unbound_memory` are
present, the guard must expose that distinction in machine-readable fields so
callers do not collapse report-only success into authority-clean semantics.

**Runtime interpretation fields**:

- `ok_meaning: guard_executed_report_only_not_authority_clean`
- `authority_integrity_status: clean | info_present | warnings_present`
- `enforcement_action: allow`
- `blocking_violation_codes: []`
- `report_only_violation_codes: [...]`
- `claim_ceiling: report_only_phase1`
- `not_claimed: [...]`

**Non-claims for this amendment**:

- no blocking enforcement upgrade;
- no hook, CI, pre-push, closeout, or gate-policy behavior change;
- no historical memory debt cleanup;
- no semantic truth verification.

### 0.3 v1.2.0 - Surface Authority Terminology

**Name of change**: separate canonical record properties from question-specific
memory authority.

**Rationale**: `canonical` has been used for storage location, writer format,
and normative authority. That ambiguity can cause a reader to treat event
history or an unreviewed structured-memory section as authoritative current
state. MRCSP M-1 introduces `canonical_record`, `authority_class`,
`projection_status`, and `review_status`, with detailed resolution rules in
`governance/MEMORY_SURFACE_AUTHORITY_CONTRACT.md`.

**Evidence**:

- `governance/MEMORY_PROTOCOL.md` already states that canonical recording does
  not establish truth, human review, acceptance, commit, push, or normative
  authority by itself.
- Consumer observations supplied for MRCSP show stale projections and
  superseded reviews remaining retrievable beside later state.
- `memory_pipeline.memory_layout` already models `02`, `03`, and `04` as logical
  surfaces with repository-specific aliases.

**Non-claims for this amendment**:

- no runtime reader, reconciliation, detector, projection, schema, or fixture;
- no semantic truth, freshness, or contradiction verification;
- no auto-write, promotion, hook, CI, gate, or blocking change;
- no historical memory rewrite or authority migration;
- no dependency on unmerged PR #88 terminal-closeout behavior;
- no branch or pull-request bytes are active authority before an authorized
  review and merge of the complete M-1 document set;
- no M0 fixture work is authorized by M-1 activation.

---

## 1. Memory Types

### 1.1 Session-Derived Memory

**Definition**: Daily files, `memory/YYYY-MM-DD.md`, recording what changed,
what was observed, or what was decided in a specific session.

**Canonical writer requirement**: New session-derived memory MUST be written by
`governance_tools.memory_record`.

Canonical session-derived records include:

```yaml
- memory_type: session-derived
  record_format_version: 1.0
  writer: governance_tools.memory_record
  what_changed: <summary>
  commit: <source commit, observation sentinel, or other explicit binding value>
  commit_hash: <same value as commit in current writer output>
  session_id: <session id>
  memory_binding: <bound | unbound>
  test_evidence: <evidence summary>
  next_step: <next unfinished action and claim ceiling>
  plan_reconciliation: <updated | not_applicable | deferred:<reason> | not_declared>
```

Direct markdown append in old bullet formats such as `- what changed:` or
`- what_changed:` is not canonical for new session-derived memory.

**Binding requirement**: Each new session-derived entry SHOULD contain both:

- a `commit` / `commit_hash` value supplied to the canonical writer; and
- a `session_id`.

For source-code or documentation changes, `commit` / `commit_hash` SHOULD refer
to the source commit being recorded.

For runtime observations without a source commit, the record MAY use an explicit
observation sentinel such as `runtime-observation-no-source-commit`. Such records
are intentionally `memory_binding: unbound` and must state the observation-only
claim ceiling.

**Why**: Session-derived memory claims that changes, observations, or decisions
happened. The canonical writer supplies a consistent evidence envelope. Binding
fields make the claim auditable, but they do not make the claim true by
themselves.

**Important non-claims**:

- `writer: governance_tools.memory_record` proves canonical writer format, not
  semantic correctness.
- `memory_binding: bound` means the current writer classified the `commit` value
  as hash-like. It does not prove the commit exists on a remote, was reviewed,
  was pushed, or that the memory statement is true.
- `memory_binding: unbound` is not automatically invalid. Runtime observations
  and other non-source records may be valid observation evidence when explicitly
  labeled and claim-bounded.

### 1.2 Structural Long-Term Memory

**Definition**: `memory/00_long_term.md` contains persistent facts, conventions,
and governance state that span sessions.

**Binding requirement**: Each `##`-level section SHOULD carry a `promoted_by:`
marker indicating who (human reviewer or promotion artifact) authorized the
entry.

Acceptable forms:

```html
<!-- promoted_by: Gavin0099 / 2026-04-28 -->
<!-- promoted_by: phase_d_closeout / artifacts/governance/phase-d-reviewer-closeout.json -->
```

**Why**: Structural memory is cited as authority across sessions and by multiple
agents. Entries written without promotion authority are
`structural_memory_auto_write`: AI-inserted facts treated as governance authority
without human review.

**Violation code**: `structural_memory_auto_write`
**Scope**: `##`-level sections in `memory/00_long_term.md`
**Current mode**: reported as debt count, not per-section blocking.

---

## 2. Presence, Canonical Format, And Binding

> Presence in `repo/memory/` = cross-agent visibility.
> Canonical writer format = consistent session-derived evidence envelope.
> Binding = traceability signal supplied by commit/session fields.
> Truth = still requires evidence, review, and current-state verification.

For this contract, `canonical_record` means canonical storage and writer-format
requirements were met. The record's `authority_class`, `projection_status`, and
`review_status` remain separate. Question-specific resolution is defined by
`governance/MEMORY_SURFACE_AUTHORITY_CONTRACT.md` and must preserve unresolved
conflicts for reviewer decision.

The MRCSP authority model activates atomically only when an authorized review
approves and merges the aligned `AUTHORITY.md`, `MEMORY_PROTOCOL.md`,
`MEMORY_AUTHORITY_CONTRACT.md`, and
`MEMORY_SURFACE_AUTHORITY_CONTRACT.md` changes. A branch or partial document
update is candidate evidence only. Activation does not authorize M0.

Presence alone does NOT grant authority.

Canonical writer format alone does NOT prove semantic correctness.

A source-bound record does NOT prove the commit was pushed, reviewed, or accepted
unless the record or adjacent evidence explicitly says so and that evidence is
verified.

A runtime-observation record without a source commit may still be valid
observation evidence when it is explicit about:

- what runtime state was observed;
- where the artifact or state lives;
- what was not changed;
- what cannot be claimed from the observation.

Private tool memory, for example
`C:\Users\..\.claude\projects\..\memory\MEMORY.md`, is **not cross-agent
canonical** under any conditions. Closeouts or governance artifacts that cite the
private tool memory path as authoritative are invalid.

**Violation code**: `private_memory_cited`

---

## 3. Missing Canonical Memory

If session-level work is performed, such as commits created or durable artifacts
written, but no corresponding daily memory file exists for that date, the session
record is incomplete.

**Violation code**: `missing_canonical_memory`
**Detection**: guard checks whether a daily memory file exists for dates where
git log shows recent commits.
**Mode**: warning evidence; heuristic false positives are possible on no-commit
sessions or unusual workflows.

---

## 4. Violation Semantics

| Code | Severity | Blocks by default | Meaning |
|------|----------|-------------------|---------|
| `unbound_memory` | warning | no | Daily entry lacks sufficient binding anchors or records an intentionally unbound observation |
| `structural_memory_auto_write` | info | no | `memory/00_long_term.md` section lacks `promoted_by` |
| `private_memory_cited` | warning | no | Closeout or governance artifact cites private `.claude` memory path |
| `missing_canonical_memory` | warning | no | Commits exist but no daily memory file exists for the date |
| `non_canonical_writer` | warning | no | Session-derived entry was not written in canonical writer format |
| `old_format_entry_after_canonical_writer_cutoff` | warning | no | Old-format daily memory entry appears after the canonical-writer cutoff and should be rewritten through the canonical writer |
| `test_evidence_provenance_not_found` | warning | no | Success-style `test_evidence` lacks an existing provenance path under a declared evidence root (see below) |
| `session_like_non_session_memory_type` | warning in raw guard; blocker in policy-backed gates | raw guard: no; `memory_workflow` / CI with policy file: yes | Active-window typed entry uses non-session `memory_type` while carrying session memory fields |
| `authority_override_used` | warning | no | A policy-backed blocker was downgraded by an `authority_override` entry field |
| `non_daily_session_shaped_memory_entry` | warning | no | Non-daily `memory/*.md` file contains a block that looks like a daily session-derived memory entry |
| `active_non_canonical_writer` | blocker candidate | opt-in / workflow-dependent | Current-window non-canonical writer violation detected by the active-window filter |

Current semantics:

- Historical `unbound_memory` remains warning evidence unless a separate cleanup
  or enforcement slice changes that policy.
- Historical `non_canonical_writer` remains warning evidence unless a separate
  cleanup or enforcement slice changes that policy.
- `active_non_canonical_writer` is a current completion blocker candidate for
  memory completion claims when surfaced by `memory_workflow` or explicitly
  checked with active-window options.
- `session_like_non_session_memory_type` remains report-only when
  `memory_authority_guard` is run with its default arguments. In gate consumers
  that load `governance/memory_blocking_policy.json`, the same code is the first
  selective blocker for active-window entries. Pre-window reasons and entries
  carrying `authority_override` stay report-only.
- `test_evidence_provenance_not_found` accepts evidence under any root declared
  in the repo's `contract.yaml` as `evidence_roots:`, **in addition to** the
  framework-owned root `artifacts`. Consumer declarations are additive: the
  framework writes its own runtime closeouts, verdicts and receipts under
  `artifacts/`, so a contract cannot remove it. An `evidence_roots:` key present
  but empty is reported as `contract_declared_empty` with a warning, not as an
  absent declaration.
- The finding's `provenance_subcode` splits it into four triage buckets that
  must not be collapsed: `no_parsable_artifact_reference` (no reference the
  tool could parse — path detection is heuristic, so this is a parser outcome,
  never proof the author cited nothing), `outside_declared_roots` (an existing
  output file cited from an undeclared location — a contract gap),
  `artifact_not_found` (declared root, absent file), and `path_unsafe`
  (absolute, traversing, or escaping the repository). The `reason` string keeps
  its legacy wording because `memory_authority_baseline` derives bucket
  identity from `reason`; renaming it would invalidate every existing baseline.
  `run_guard` reports the roots in effect under `evidence_root_policy` so a
  reader can tell which case applies.
- `authority_override_used` is report-only in all current paths. It makes
  blocker downgrades visible in guard output; `memory_workflow` and CI surface
  it when the override occurs in the current memory diff. It is audit
  visibility, not reviewer identity verification.
- `non_daily_session_shaped_memory_entry` is report-only in all current paths.
  It makes F6 placement bypasses visible without banning structural memory
  files or expanding B0 blocking semantics.
- `repo_state_b0_blocker_count` and `current_diff_b0_blocker_count` are
  observation fields in `memory_workflow` / CI output. They split B0 blocker
  visibility by repository state vs. current diff without narrowing enforcement:
  repo-state B0 blockers still block while this observation period is active.
- `memory_workflow --check --repo . --run-guard` reports whether the guard ran,
  summarizes warnings/blockers, and exposes `completion_claim_allowed`.
- `memory_authority_guard` `ok=True` means the report-only guard executed. It
  does not mean memory authority is clean; callers must inspect
  `authority_integrity_status`, `violation_counts_by_code`, and `not_claimed`.
- `completion_claim_allowed=True` means the scoped memory workflow check found no
  current blocker candidate for the completion claim. It is not proof that the
  memory content is semantically correct.

This contract preserves warning-mode historical debt. It does not clean,
backfill, or upgrade historical records.

---

## 5. Amendment

To change this contract: create a new version (for example `1.1.0`, `1.2.0`, or
`2.0.0`) with:

- name of what changed;
- rationale;
- evidence explaining why the change is needed;
- updated violation semantics table;
- explicit non-claims.

Silent modification = authority contract violation.

---

## 6. Tool Reference

Canonical writer:

```powershell
python -m governance_tools.memory_record `
  --project-root . `
  --commit <commit-or-observation-sentinel> `
  --session-id <session-id> `
  --plan-reconciliation <updated|not_applicable|deferred:reason> `
  --what-changed "..." `
  --test-evidence "..." `
  --next-step "..."
```

Memory workflow dispatcher:

```powershell
python -m governance_tools.memory_workflow --check --repo . --run-guard
```

Selective blocker mode:

```powershell
python -m governance_tools.memory_workflow --check --repo . --run-guard --fail-on-blocker
```

Memory authority guard:

```powershell
python -m governance_tools.memory_authority_guard --memory-root memory --project-root .
```

Current behavior summary:

- `memory_authority_guard` default CLI output is warning/report-only;
- `memory_workflow` and `ci_memory_workflow_check` load
  `governance/memory_blocking_policy.json` and may selectively block enabled
  codes such as `session_like_non_session_memory_type`;
- managed pre-commit may surface the same memory workflow verdict as advisory
  text; CI remains the authoritative gate surface;
- receipt presence proves workflow status was observed, not that memory
  completion was semantically correct.

---

## 7. Non-Claims

This contract does not claim:

- historical memory debt is cleaned;
- all old memory records are canonical;
- all bound records are true;
- all unbound records are invalid;
- all runtime observations are source-bound;
- memory workflow enforcement is globally blocking;
- memory entries prove semantic correctness;
- memory entries prove remote push, human acceptance, or review unless that
  evidence is separately recorded and verified.
