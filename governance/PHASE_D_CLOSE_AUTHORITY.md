---
audience: human-only
authority: canonical
can_override: false
overridden_by: ~
default_load: never
---

# Phase D Close Authority Contract

> document-status: canonical
> authority-chain: governance/AUTHORITY.md → PHASE_D_CLOSE_AUTHORITY.md → all subordinate surfaces
> audience: human-only
> default-load: never (agent must not load autonomously)
> updated: 2026-04-28

---

## Constitutional Status

This document is the **canonical authority source** for Phase D close semantics
in the AI Governance Framework.

All other documents, artifacts, and signals that reference, describe, or imply
Phase D completion status are **subordinate** to this contract. No derived or
reference document may override the authority established here.

This contract is registered in `governance/AUTHORITY.md` at authority level
`canonical`. Reviewers encountering contradictions between this document and
any other source — including README, PLAN.md, version tags, commit history, or
generated summaries — must treat this document as the governing source.

Agent systems must not load this document to derive Phase D status
autonomously. The purpose of this document is to govern human reviewer judgment,
not to provide runtime signals.

---

## Precedence Declaration

When evaluating Phase D completion claims, this contract takes precedence over:

| Signal | Precedence Status |
|--------|-------------------|
| `README.md` completion description | Subordinate — descriptive only, never authoritative |
| `PLAN.md` phase marker (`[x]`) | Subordinate — reflects state, does not confer authority |
| Implementation presence (code merged) | Non-authoritative |
| Commit history / merge confirmation | Non-authoritative |
| Version tags or release notes | Non-authoritative |
| Generated status summaries (AI-produced) | Non-authoritative |
| AI-produced assertions of Phase D completion | Explicitly excluded |
| Absence of open issues or tickets | Non-authoritative |
| State validator `recommended_phase_d_status` output | Non-authoritative (advisory only) |

**None of the above, individually or collectively, constitute a valid Phase D
completion claim under this contract.**

A completion claim is valid if and only if it satisfies the requirements
defined in § Required Authority Artifacts (reserved — pending review of this
constitutional section).

---

## What This Contract Does Not Claim

Governance contracts drift by over-claiming scope. The following are explicitly
outside the scope of this document:

- This contract does not govern Phase A–C or Phase E–G completion semantics.
- This contract does not define what implementation work was done in Phase D.
- This contract does not certify the quality or correctness of implementation.
- This contract does not describe the Phase D milestone — only the authority
  chain for declaring it closed.
- This contract is not itself a completion certificate. It defines the rules
  for issuing one.

---

## Explicit Non-Claims

This section defines what cannot constitute a valid Phase D completion claim.
Absence of a prohibition here does not imply permission. This section is
operative as written.

### NC-1: AI Self-Certification is Prohibited

An AI agent system — including the framework's own governance tools — may not:

- Produce a reviewer closeout artifact on behalf of a human reviewer
- Call `write_phase_d_closeout()` or any equivalent to assert completion
- Use its own output as evidence that Phase D is complete
- Pre-generate a closeout artifact for later human "approval"

Rationale: the gate is meaningless if the system that builds the gate can also
pass it. AI constructs the validator; AI does not pass the validator.

This prohibition applies to **authority acts**, not serialization assistance.
A tool that serializes a human reviewer's decision into the canonical JSON
format is permitted, provided: (1) the human reviewer is the source of the
decision, (2) the human's identity is in `reviewer_id`, and (3) the tool does
not assert, generate, or infer the reviewer's decision content. The invoker of
`write_phase_d_closeout()` must be a human acting on their own judgment.

### NC-2: Implementation Completion is Not Completion Authority

The following signals do not constitute Phase D completion, individually or
collectively:

- All planned code being merged
- All tests passing
- All implementation slices marked done
- A clean git working tree or clean CI
- Absence of open issues, tickets, or escalations

Implementation completion is a prerequisite for Phase D close consideration.
It is not an authority artifact. A system with all tests passing and no open
issues remains in `resumable` state until a valid authority artifact exists.

### NC-3: State Validator Output is Advisory Only

The output `recommended_phase_d_status = "completed"` from
`validate_state_reconciliation()` is an advisory signal. The validator observes
conditions; it does not authorize closure. A reviewer reading
`recommended = "completed"` must still produce an independent closeout artifact.
The validator output cannot substitute for that artifact.

### NC-4: Documentation Actions Do Not Confer Authority

The following actions do not constitute Phase D completion:

- Updating README to describe Phase D as complete
- Setting PLAN.md phase marker to `[x]`
- Version bump, release tag, or CHANGELOG entry
- Commit message or PR description claiming Phase D completion
- This document being written, merged, or registered in AUTHORITY.md

Documentation describes completion after authority is established. It does not
create authority. Updating documentation before a valid closeout artifact exists
is a governance violation, not a completion act.

### NC-5: Proxy Signing is Prohibited

A human reviewer may not:

- Delegate closeout signing to an AI system
- Accept an AI-generated closeout artifact as their own signed confirmation
- Pre-authorize a future AI-generated closeout artifact
- Countersign an artifact they did not independently produce

Reviewer identity in the closeout artifact must correspond to a human who
independently evaluated the completion conditions at the time of signing.

---

## Required Authority Artifacts

This section defines the minimum requirements for a valid Phase D completion
claim. Requirements are ordered by logical precedence: authority event
semantics first, artifact presence second, schema fields last.

### A1: Required Authority Event

Phase D completion requires an **explicit reviewer decision** to accept
closeout responsibility.

The following are **insufficient** for authority transfer:

- Passive observation of passing tests or clean CI
- Merge approval of implementation code
- Absence of objection or silence
- Agreement with a generated summary or advisory output
- "Looks good", "LGTM", or equivalent shorthand

A valid authority event is one where a human reviewer independently evaluates
the completion conditions and explicitly accepts responsibility for declaring
Phase D closed. The decision must be contemporaneous with signing, not
retrospective pre-authorization.

### A2: Required Canonical Artifact

The authority event must be recorded in exactly one canonical artifact:

```
artifacts/governance/phase-d-reviewer-closeout.json
```

No alternate path, generated summary, status file, or derived projection may
substitute this artifact:

| Path | Status |
|------|--------|
| `artifacts/governance/phase-d-reviewer-closeout.json` | Canonical — required |
| Any other file path | Invalid substitute |
| Generated summaries (`*.summary.json`, etc.) | Invalid substitute |
| Session closeout reports | Invalid substitute |

The artifact must be present in the repository at the canonical path for any
completion claim to be valid. Validation tools must fail-closed when absent.

### A3: Required Writer Attribution

The artifact records two distinct identity claims that must not be conflated:

**A3a — Serialization Tool Identity (`writer_id`)**

`writer_id` identifies the tool that serialized the artifact into JSON. This
field is for schema integrity verification (see A7), not for authority
attribution. A governance tool (e.g., `governance_tools.phase_d_closeout_writer`)
may occupy this field — this does not violate NC-1, because the tool is a
serializer, not the authority actor. No authority semantics attach to `writer_id`.

**A3b — Reviewer Authority Identity (`reviewer_id`)**

`reviewer_id` is the sole field with authority semantics. Requirements:

- Must be present and non-empty
- Must identify a specific human — not a role, team, system, or AI identifier
- Anonymous, collective, or inferred attribution is invalid
- The holder must be the human who accepted closeout responsibility at signing

Auditability requirement: a third party must be able to determine which human
accepted closeout responsibility from `reviewer_id` alone, independent of
`writer_id`.

### A4: Required Explicit Acceptance

The artifact must record an explicit acceptance act, not implicit agreement:

- `reviewer_confirmation: "explicit"` — signals the confirmation was
  deliberate, not inferred
- `confirmed_at` — non-empty timestamp of the explicit acceptance

The following do not constitute explicit acceptance:

- Absence of a rejection
- Comment-only review without responsibility declaration
- Approval of a different artifact or scope
- Retrospective acknowledgment after the fact

### A5: Required Independence Declaration

The reviewer must declare independence from the implementation author:

- `confirmed_conditions` must include at least one entry asserting reviewer
  independence (e.g., `"reviewer_independent_of_author"`)
- Self-review — author reviewing their own work — is not a valid authority act
- Independence must be declared explicitly, not inferred from org structure

Rationale: authority transfer requires that the accepting party is not the same
party that produced the work being accepted.

### A6: Required Confirmed Conditions

The artifact must record the evidence basis on which the reviewer accepted
closeout responsibility:

- `confirmed_conditions` must be a non-empty list
- Each entry must represent a substantive condition the reviewer evaluated
- Required coverage (minimum):
  - Phase C surface gap status confirmed resolved
  - Validator output reviewed
  - Fail-closed semantics understood and accepted
  - No unresolved blocking conditions remain

Rationale: the list records the reviewer's decision basis, enabling independent
audit of whether the authority act was well-founded.

### A7: Required Integrity Constraints

Once written, the closeout artifact is immutable for authority purposes:

- Silent overwrite or replacement invalidates authority trust
- Post-hoc modification of `reviewer_id`, `confirmed_at`, or
  `confirmed_conditions` invalidates the authority act
- A modified artifact requires a new complete authority event
- Partial updates (editing individual fields without re-signing) are not valid

Validation tools must treat schema version mismatch or unexpected field
modification as an integrity failure, not a warning.

---

### Schema Fields (Derived Serialization of A1–A7)

Schema compliance is necessary but not sufficient for a valid authority act.
Fields are listed here as serializations of the requirements above, not as the
requirements themselves.

| Field | Required | Constraint | Maps to |
|-------|----------|------------|---------|
| `closeout_schema` | Yes | Fixed value | Integrity (A7) |
| `writer_id` | Yes | Must match expected serializer ID | Serialization integrity (A3a, A7) — no authority semantics |
| `writer_version` | Yes | Must match expected version | Serialization integrity (A7) |
| `written_at` | Yes | Non-empty timestamp | Audit trail |
| `phase_completed` | Yes | Must be `"D"` | Scope |
| `verdict` | Yes | Must be `"completed"` | Explicit acceptance (A4) |
| `reviewer_id` | Yes | Non-empty, human-identifiable; sole authority field | Authority attribution (A3b) |
| `confirmed_at` | Yes | Non-empty timestamp | Explicit acceptance (A4) |
| `confirmed_conditions` | Yes | Non-empty list | Decision basis (A6) + Independence (A5) |
| `reviewer_confirmation` | Yes | Must be `"explicit"` | Explicit acceptance (A4) |

---

## Reviewer Independence Rules

This section defines authority invalidation conditions. Independence is not a
quality standard — it is an authority prerequisite. A closeout produced without
satisfying independence requirements is void, not merely weak.

The subject of all rules below is the `reviewer_id` holder (A3b).

### RI-1: Self-Review Invalidation

If the implementation author and the reviewer are the same person, the closeout
authority is **void**.

- Author identity is determined by commit authorship, PLAN.md task ownership,
  or any primary implementation responsibility
- Organizational title does not override this rule
- A contributor who authored any part of the Phase D implementation may not
  serve as the sole closeout reviewer for that implementation

There is no cure: a self-reviewed closeout cannot be remediated by adding a
reviewer note. A new closeout with a different reviewer_id is required.

### RI-2: Proxy Review Invalidation

If the reviewer did not independently evaluate the completion conditions, the
closeout authority is **void**, regardless of reviewer_id content.

The following do not constitute independent evaluation:

- Relying on an AI-generated summary as the primary evidence basis
- Countersigning a closeout artifact prepared by another party (human or AI)
- Delegating evaluation to a subordinate and signing the result without
  personal review
- Agreeing with a validator output without consulting primary sources

Independent evaluation requires the reviewer to directly examine the relevant
artifacts, outputs, and conditions — not summaries or proxies of them.

### RI-3: Organizational Authority Does Not Substitute for Independence

Organizational hierarchy is not a substitute for reviewer independence:

- Manager approval of a subordinate's implementation is not independent review
- Team lead sign-off on their own team's work is not independent review
- "Approved by senior engineer" does not constitute independence if that
  engineer participated in the implementation

Independence is defined by the reviewer's relationship to the work, not their
position relative to the author. A more senior person reviewing their own
team's implementation is less independent, not more authoritative.

### RI-4: Scope Mismatch Invalidation

Code review approval is not closeout authority acceptance:

- A reviewer who approved pull requests or implementation code has approved
  implementation quality, not Phase D completion
- Phase D closeout requires explicit acceptance of closeout responsibility —
  a distinct act from code review
- A reviewer must specifically confirm that they are accepting Phase D closeout
  responsibility, not merely that they reviewed the code

If a reviewer's `confirmed_conditions` do not include an explicit closeout
responsibility acceptance, the authority scope is insufficient.

### RI-5: Temporal Invalidation

Retroactive signing is presumptively void:

- A closeout artifact produced after Phase D was already marked `completed` in
  PLAN.md, `.governance-state.yaml`, or equivalent state records is
  presumptively invalid
- The authority act must precede or be contemporaneous with the completion
  claim, not follow from it
- Post-hoc artifacts produced to justify a pre-existing completion claim do not
  constitute valid authority events (see A1: decision must be contemporaneous)

If a retroactive artifact is presented, an auditor must be able to demonstrate
how the authority act preceded the completion claim. Absent such demonstration,
the artifact must be treated as void.

---

## Validator Role Boundary

**Validators may observe, reject, and recommend.**
**Validators may not authorize, certify, or close Phase D.**

This boundary is permanent and not subject to configuration or escalation.
No validator output, regardless of content, constitutes a Phase D completion
authorization. Validators are detection and advisory instruments, not authority
actors.

### VRB-1: `recommended_phase_d_status = "completed"` is Advisory Only

The output `recommended_phase_d_status = "completed"` from
`validate_state_reconciliation()` signals that observed conditions are
consistent with completion — it does not authorize completion.

- A reviewer reading `recommended = "completed"` is receiving a readiness
  signal, not a permission to mark Phase D done
- The validator cannot know whether a valid authority event (A1) has occurred,
  only whether the canonical artifact is present and schema-valid
- A reviewer who acts on `recommended = "completed"` without producing an
  independent closeout artifact has not satisfied the authority requirements
  of this contract

The validator recommends. The reviewer decides. These are distinct acts.

### VRB-2: Validator Pass Cannot Substitute for Reviewer Closeout Artifact

A passing validator result — `ok=True`, `closeout_ok=True`, all checks green —
does not substitute for the canonical reviewer closeout artifact.

- `assess_phase_d_closeout()` returning `ok=True` means the artifact is
  present and schema-valid; it does not certify reviewer independence, decision
  quality, or authority legitimacy
- Even a fully passing validator state leaves Phase D in `resumable`, not
  `completed`, until the authority event (A1) is satisfied
- No combination of validator outputs, however favorable, constitutes closeout
  authority

### VRB-3: Validator Failure Blocks; It Does Not Decide Authority

Validator failure blocks a completion claim. It does not itself make an
authority decision:

- `assess_phase_d_closeout()` returning `ok=False` is a block signal, not a
  rejection of reviewer authority
- A validator reporting `trusted_writer=False` or `review_confirmed=False` is
  reporting a schema or integrity failure — the reviewer's judgment is not
  being evaluated, only the artifact's structure
- Validator failures must be resolved (e.g., artifact re-issued with correct
  fields) before a completion claim can proceed; they do not terminate the
  reviewer's ability to issue a new, correct closeout

**A validator cannot replace a reviewer.**
**A reviewer cannot silently override a validator.**

Silent override — proceeding to mark Phase D completed while a validator
reports failure, without a separate explicit authority artifact — is a
governance violation.

However, if a validator failure is caused by a known tooling defect, schema
migration lag, or documented false positive, a reviewer may override via a
separate explicit exception authority artifact. That artifact must:

- Identify the specific validator failure being overridden
- State the grounds for override (e.g., known defect, schema migration)
- Be independently reviewable (not self-certified)
- Be recorded in the governance audit trail

This exception path preserves fail-closed semantics while preventing permanent
governance lock-in from validator defects. Without an explicit exception
artifact, block is default and reviewers have no unilateral authority to
override.

---

## Failure Semantics (Fail-Closed)

**Default state: `resumable`.** In the absence of a valid authority artifact at
the canonical path, Phase D completion status is `resumable`. Block is the
default, not an exception. No affirmative action is required to maintain it.

Block is not permanent — each failure mode has a remediation path. The path is
proportionate to the failure's nature: structural failures are re-issuance
problems; authority failures require a new authority event; independence failures
require a new reviewer.

---

### FS-1: Blocked vs. Void

Two distinct failure effects apply to Phase D completion claims:

**Blocked** — The claim cannot proceed. The failure is structural or procedural:
artifact absent, schema invalid, required fields missing or incorrect. Remediation
is corrective: produce or re-issue the artifact. The authority relationship is
not impugned.

**Void** — The authority act was invalid at the time it occurred. Remediating a
void closeout requires a new authority event (A1), not a corrected artifact. A
void determination cannot be cured by:

- Adding a reviewer note or counter-signature to the existing artifact
- Ratifying the artifact via second-party annotation
- Producing documentation asserting the original act was valid

A new, complete authority act satisfying A1–A7 is the sole remediation.

---

### FS-2: Failure Mode Table

| # | Failure | Source | Effect | Remediation |
|---|---------|--------|--------|-------------|
| F1 | Canonical artifact absent | A2 | **Blocked** | Produce valid artifact via authority event (A1) |
| F2 | Artifact at non-canonical path | A2 | **Blocked** | Re-issue at `artifacts/governance/phase-d-reviewer-closeout.json` |
| F3 | Schema version mismatch | A7 | **Blocked** (integrity) | Re-issue with correct schema |
| F4 | Artifact modified post-issuance | A7 | **Void** | New complete authority event; re-issue |
| F5 | `reviewer_id` empty or missing | A3b | **Blocked** | Re-issue with human-identifiable `reviewer_id` |
| F6 | `reviewer_id` identifies non-human entity | A3b | **Blocked** | Re-issue with valid human `reviewer_id` |
| F7 | `reviewer_confirmation` ≠ `"explicit"` | A4 | **Blocked** | Re-issue with correct field value |
| F8 | `confirmed_at` empty or missing | A4 | **Blocked** | Re-issue with valid timestamp |
| F9 | `confirmed_conditions` empty | A6 | **Blocked** | Re-issue with substantive conditions |
| F10 | Independence not declared in conditions | A5 | **Blocked** | Re-issue with explicit independence assertion |
| F11 | Required condition coverage absent | A6 | **Blocked** | Re-issue with complete evidence basis |
| F12 | Author is sole reviewer (self-review) | RI-1 | **Void** — no cure | New authority event; different, non-author reviewer |
| F13 | Reviewer did not independently evaluate | RI-2 | **Void** | New authority event; independent evaluation required |
| F14 | Reviewer accepted wrong scope (code review) | RI-4 | **Void** | New authority event; explicit closeout scope acceptance |
| F15 | Artifact produced retroactively | RI-5 | **Presumptively void** | Auditable demonstration that A1 preceded completion claim |
| F16 | Validator failure, no exception artifact | VRB-3 | **Blocked** | Fix artifact defect OR produce exception authority artifact |
| F17 | Exception artifact missing required fields | VRB-3 | **Blocked** | Re-issue exception artifact with: specific failure, grounds, independent review |

---

### FS-3: Fail-Closed Default

**Validation tools must fail-closed.** When the canonical artifact is absent,
tools must not produce `ok=True` or any equivalent success signal. Absent
artifact = block. This behavior is not configurable.

The following do not lift the fail-closed default:

- Implementation complete (all slices done, all tests passing)
- Validator output `recommended_phase_d_status = "completed"`
- PLAN.md phase marker `[x]` set
- README or CHANGELOG describing Phase D as complete
- Version tags, release notes, or commit messages asserting completion
- Any combination of the above signals

The default is lifted only by a valid canonical artifact satisfying A1–A7 at
the canonical path.

---

### FS-4: Proportionate Remediation

Remediation scope must be proportionate to the failure type.

**F1–F11 (structural/procedural failures):** Artifact correctness problems.
Remediation = re-issue the artifact. Re-issuance requires a new valid authority
event — the reviewer must independently re-evaluate, not merely approve a
corrected form. Partial field correction is not valid; re-issuance means a new
complete artifact.

**F12–F14 (authority legitimacy failures):** Require a new authority event with
a reviewer who satisfies all independence requirements. The defective artifact is
not amended; it is replaced.

**F15 (retroactive signing):** The party asserting validity must produce auditable
evidence that the authority event (A1) preceded the completion claim. Without such
evidence, the artifact is void. An auditor is not required to demonstrate
invalidity — the presumption is void absent affirmative demonstration.

**F16–F17 (validator override):** Two remediation paths exist:

1. Fix the artifact defect that caused validator failure (re-issuance, F1–F11 path)
2. Produce an explicit exception authority artifact identifying: the specific
   failure being overridden, the grounds (known defect, schema migration,
   documented false positive), and signed by an independent reviewer

The exception path does not bypass the authority event requirement. The exception
artifact itself requires independent review and must be recorded in the governance
audit trail.

---

## Single-Contributor Adaptation Mode (SCAM-1)

This section clarifies how reviewer-independence semantics apply when the
repository has only one active maintainer.

### SCAM-1A: No Silent Waiver

Single-contributor operation does not waive RI-1 through RI-5. In particular,
`self-review` remains non-authoritative for constitutional close claims. The
independence requirement is not considered satisfied by default due to project
size.

### SCAM-1B: Allowed Outcomes Under Single-Contributor Constraints

When no independent human reviewer is available, the project may:

1. Remain in `resumable` status (fail-closed default), or
2. Publish an explicitly bounded claim labeled `reviewer_independence_pending`
   for operational continuity tracking only.

The bounded claim path is non-authoritative and cannot be used as a substitute
for a valid closeout authority event.

### SCAM-1C: Minimum Disclosure Requirements

Any closeout-related report emitted under single-contributor constraints must
declare all of the following:

- `independence_mode: single_contributor`
- `authority_status: non_authoritative`
- `independence_gap: reviewer_independence_pending`

This disclosure requirement prevents implicit legitimacy inflation and preserves
auditor-visible boundary conditions.
