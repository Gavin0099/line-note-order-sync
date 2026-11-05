---
audience: agent-on-demand
authority: canonical
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

<!-- mrcsp_activation_id: mrcsp-m1-authority-reader-v1 -->

# Memory Surface Authority And Reader Contract

Status: ACTIVE WHEN MERGED AFTER AUTHORIZED REVIEW
Program: Memory Reconciliation & Current-State Projection (MRCSP)
Milestone: M-1

## Activation Boundary

The bytes in a branch or pull request are a candidate contract. They become
active only when an authorized review approves the complete M-1 change and that
change is merged. The approved merge atomically activates this file together
with its matching `AUTHORITY.md`, `MEMORY_PROTOCOL.md`, and
`MEMORY_AUTHORITY_CONTRACT.md` changes; none of those files may activate M-1 by
itself.

Activation does not authorize M0. After M-1 is active, M0 still requires a
separate owner-authorized fixture-admissibility tranche.

## Problem

The repository currently uses `canonical` for three different properties:

- a canonical storage location;
- a canonical writer or record format; and
- normative authority for a class of decisions.

Those properties are not interchangeable. A record can be stored in the
canonical location and written by the canonical writer without proving semantic
truth, human acceptance, current authorization, or current state.

## Current Repository Truth

- `governance/MEMORY_PROTOCOL.md` already says canonical recording establishes
  provenance and placement for a declared claim class, not truth or acceptance.
- `governance/MEMORY_AUTHORITY_CONTRACT.md` separates presence, canonical
  format, binding, and truth.
- `memory_pipeline.memory_layout` resolves repository-specific aliases for the
  logical `02`, `03`, and `04` surfaces.
- `governance/AUTHORITY.md` historically classified `01` through `04` as
  globally canonical and directly promotable. M-1 replaces that file-level
  shortcut with question-specific authority roles.
- This contract is based only on merged `main`. It does not consume PR #88
  terminal-closeout behavior; any future integration requires separately merged
  authority.

## Target Outcome

M-1 defines how a reader determines which surface may answer a specific class
of question, while preserving ambiguity for reviewer resolution. It does not
implement a reader.

## Terminology

| Term | Meaning |
| --- | --- |
| `canonical_record` | A record produced through the required canonical writer and format at the canonical storage location. |
| `authority_class` | The class of question a source is qualified to answer. |
| `projection_status` | `current`, `historical`, `superseded`, or `candidate`. |
| `review_status` | `reviewed`, `unreviewed`, or `disputed`. |

`canonical_record` does not imply authoritative current state.

## Surface Model

| Surface | Authority class | Reader use | Limitation |
| --- | --- | --- | --- |
| `memory/YYYY-MM-DD.md` | event and provenance history | what was recorded, claimed, observed, or bound at that time | does not determine final current state |
| `PLAN.md` plus the current approved change | approved intent and work ordering | what work is currently ordered within the human-authorized scope | PLAN cannot create authorization and memory `next_step` cannot override current human instruction |
| logical `01_active_task` | reviewed current-state projection | current progress interpretation with traceable source anchors | not independent evidence authority |
| logical `02_tech_stack` / `02_workflow` | current operational and architecture projection | current build, deployment, runtime, and architecture baseline | not historical evidence by itself |
| logical `03_knowledge_base` | section-qualified reusable knowledge | promoted, reviewed, non-superseded reusable knowledge | file presence alone does not qualify a section as authoritative |
| logical `04_review_log` | append-only review history | historical reviews and the latest valid authority-qualified non-superseded verdict | latest timestamp alone is insufficient when authority is invalid or disputed |
| `memory/00_long_term.md` | section-qualified cross-session context | promoted durable context | canonical storage path does not make every section normative authority |

Logical surfaces must be resolved through `memory_pipeline.memory_layout` or an
equivalent declared alias contract. Readers must not require one hard-coded
consumer filename.

## Reader Resolution Rules

There is no global ordering such as `03 > daily > PLAN`. Resolution depends on
the question class:

| Question class | Qualified source | Resolution |
| --- | --- | --- |
| event history | daily record plus cited evidence | preserve what was recorded at that time |
| current authorization | current human instruction or approved change | memory and PLAN do not create new permission |
| approved work ordering | PLAN within current authorization | daily `next_step` remains a candidate only |
| current progress | eligible current `01` projection plus source anchors | unresolved eligibility or source conflict becomes a non-resolved review state |
| current operations | eligible current `02` projection plus source anchors | unresolved eligibility or source conflict becomes a non-resolved review state |
| reusable knowledge | promoted, reviewed, non-superseded `03` section | candidate or disputed knowledge cannot be upgraded silently |
| current review verdict | latest valid, authority-qualified, non-superseded review | retain older verdicts as history |

Authority conflicts must not be silently resolved. If the qualified sources do
not establish one answer, the reader returns `reviewer_required`, `disputed`,
`insufficient_authority`, or `unassessable` as appropriate.

### Current Projection Eligibility

A structured projection can resolve a current-progress or current-operations
question only when all of these predicates hold:

1. `projection_status=current`;
2. `review_status=reviewed` by an authority-qualified reviewer;
3. its source anchors are traceable and cover the latest qualified evidence and
   the latest known substantive state transition within the declared work item;
4. no later qualified contradictory evidence or substantive state transition
   remains unreconciled; and
5. the reader can determine the coverage boundary without semantic guessing.

If any predicate cannot be established, the projection does not become current
authority. Return `reviewer_required`, `disputed`, `insufficient_authority`, or
`unassessable` according to the evidence available.

<!-- mrcsp-reader-vocabulary:begin -->
```json
{
  "query_classes": [
    "event_history",
    "current_authorization",
    "approved_work_ordering",
    "current_progress",
    "current_operations",
    "reusable_knowledge",
    "current_review_verdict"
  ],
  "projection_statuses": ["current", "historical", "superseded", "candidate"],
  "review_statuses": ["reviewed", "unreviewed", "disputed"],
  "reviewer_authority_states": [
    "authority_qualified",
    "self_attested_only",
    "unqualified",
    "unknown",
    "not_applicable"
  ],
  "anchor_states": [
    "not_applicable",
    "covers_latest_qualified_evidence",
    "later_qualified_evidence_unreconciled",
    "missing_or_untraceable"
  ],
  "state_transition_coverage_states": [
    "covers_latest_substantive_transition",
    "missing_latest_substantive_transition",
    "not_applicable"
  ],
  "later_change_states": [
    "none_unreconciled",
    "unreconciled_qualified_change",
    "unknown",
    "not_applicable"
  ],
  "coverage_boundary_states": [
    "determinable_without_semantic_guessing",
    "indeterminable",
    "not_applicable"
  ],
  "knowledge_promotion_states": [
    "promoted",
    "candidate",
    "unqualified",
    "not_applicable"
  ],
  "supersession_states": [
    "current_non_superseded",
    "superseded",
    "unknown",
    "not_applicable"
  ],
  "review_validity_states": ["valid", "invalid", "unknown", "not_applicable"],
  "review_recency_states": [
    "latest_valid",
    "not_latest",
    "unknown",
    "not_applicable"
  ],
  "resolution_states": [
    "resolved",
    "reviewer_required",
    "disputed",
    "insufficient_authority",
    "unassessable"
  ]
}
```
<!-- mrcsp-reader-vocabulary:end -->

## Contract Cases

The following block is reviewable contract data, not a runtime reader or
detector implementation.

<!-- mrcsp-resolution-cases:begin -->
```json
[
  {
    "id": "daily_vs_plan",
    "query_class": "approved_work_ordering",
    "sources": ["daily_next_step", "plan"],
    "projection_status": "historical",
    "review_status": "reviewed",
    "reviewer_authority_state": "not_applicable",
    "anchor_state": "not_applicable",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "not_applicable",
    "coverage_boundary_state": "not_applicable",
    "expected_current_source": "plan_within_current_authorization",
    "expected_resolution": "resolved",
    "history_preserved": true
  },
  {
    "id": "daily_vs_reviewed_01",
    "query_class": "current_progress",
    "sources": ["covered_daily_history", "reviewed_current_01"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": "reviewed_current_01",
    "expected_resolution": "resolved",
    "history_preserved": true
  },
  {
    "id": "old_review_vs_newer_authority_qualified_review",
    "query_class": "current_review_verdict",
    "sources": ["older_valid_review", "newer_authority_qualified_review"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "knowledge_promotion_state": "not_applicable",
    "supersession_state": "current_non_superseded",
    "review_validity_state": "valid",
    "review_recency_state": "latest_valid",
    "expected_current_source": "newer_authority_qualified_review",
    "expected_resolution": "resolved",
    "history_preserved": true
  },
  {
    "id": "candidate_kb_vs_promoted_kb",
    "query_class": "reusable_knowledge",
    "sources": ["candidate_kb_section", "promoted_reviewed_kb_section"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "knowledge_promotion_state": "promoted",
    "supersession_state": "current_non_superseded",
    "review_validity_state": "not_applicable",
    "review_recency_state": "not_applicable",
    "expected_current_source": "promoted_reviewed_kb_section",
    "expected_resolution": "resolved",
    "history_preserved": true
  },
  {
    "id": "superseded_vs_current",
    "query_class": "current_progress",
    "sources": ["superseded_claim", "reviewed_current_claim"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": "reviewed_current_claim",
    "expected_resolution": "resolved",
    "history_preserved": true
  },
  {
    "id": "qualified_source_conflict",
    "query_class": "current_progress",
    "sources": ["reviewed_current_01", "later_conflicting_daily_evidence"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "later_qualified_evidence_unreconciled",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "unreconciled_qualified_change",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": null,
    "expected_resolution": "reviewer_required",
    "history_preserved": true
  },
  {
    "id": "unreviewed_current_projection",
    "query_class": "current_progress",
    "sources": ["unreviewed_01", "daily_history"],
    "projection_status": "current",
    "review_status": "unreviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": null,
    "expected_resolution": "reviewer_required",
    "history_preserved": true
  },
  {
    "id": "disputed_current_projection",
    "query_class": "current_progress",
    "sources": ["disputed_01", "conflicting_qualified_sources"],
    "projection_status": "current",
    "review_status": "disputed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": null,
    "expected_resolution": "disputed",
    "history_preserved": true
  },
  {
    "id": "missing_projection_anchors",
    "query_class": "current_operations",
    "sources": ["reviewed_02_without_traceable_anchors"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "missing_or_untraceable",
    "state_transition_coverage": "missing_latest_substantive_transition",
    "later_change_state": "unknown",
    "coverage_boundary_state": "indeterminable",
    "expected_current_source": null,
    "expected_resolution": "insufficient_authority",
    "history_preserved": true
  },
  {
    "id": "legacy_projection_unassessable",
    "query_class": "current_progress",
    "sources": ["legacy_01_without_status_or_coverage"],
    "projection_status": "candidate",
    "review_status": "unreviewed",
    "reviewer_authority_state": "unknown",
    "anchor_state": "missing_or_untraceable",
    "state_transition_coverage": "missing_latest_substantive_transition",
    "later_change_state": "unknown",
    "coverage_boundary_state": "indeterminable",
    "expected_current_source": null,
    "expected_resolution": "unassessable",
    "history_preserved": true
  },
  {
    "id": "self_attested_reviewer_projection",
    "query_class": "current_progress",
    "sources": ["self_attested_reviewed_01"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "self_attested_only",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": null,
    "expected_resolution": "insufficient_authority",
    "history_preserved": true
  },
  {
    "id": "unqualified_reviewer_projection",
    "query_class": "current_progress",
    "sources": ["unqualified_reviewed_01"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "unqualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": null,
    "expected_resolution": "insufficient_authority",
    "history_preserved": true
  },
  {
    "id": "unknown_reviewer_authority_projection",
    "query_class": "current_progress",
    "sources": ["reviewed_01_unknown_reviewer_authority"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "unknown",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": null,
    "expected_resolution": "insufficient_authority",
    "history_preserved": true
  },
  {
    "id": "missing_latest_state_transition",
    "query_class": "current_operations",
    "sources": ["reviewed_02_missing_latest_state_transition"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "missing_latest_substantive_transition",
    "later_change_state": "none_unreconciled",
    "coverage_boundary_state": "determinable_without_semantic_guessing",
    "expected_current_source": null,
    "expected_resolution": "reviewer_required",
    "history_preserved": true
  },
  {
    "id": "indeterminable_coverage_boundary",
    "query_class": "current_progress",
    "sources": ["reviewed_01_ambiguous_coverage_boundary"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "covers_latest_qualified_evidence",
    "state_transition_coverage": "covers_latest_substantive_transition",
    "later_change_state": "unknown",
    "coverage_boundary_state": "indeterminable",
    "expected_current_source": null,
    "expected_resolution": "unassessable",
    "history_preserved": true
  },
  {
    "id": "candidate_only_knowledge",
    "query_class": "reusable_knowledge",
    "sources": ["candidate_kb_section"],
    "projection_status": "candidate",
    "review_status": "unreviewed",
    "reviewer_authority_state": "unknown",
    "anchor_state": "not_applicable",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "not_applicable",
    "coverage_boundary_state": "not_applicable",
    "knowledge_promotion_state": "candidate",
    "supersession_state": "current_non_superseded",
    "review_validity_state": "not_applicable",
    "review_recency_state": "not_applicable",
    "expected_current_source": null,
    "expected_resolution": "insufficient_authority",
    "history_preserved": true
  },
  {
    "id": "superseded_promoted_knowledge",
    "query_class": "reusable_knowledge",
    "sources": ["superseded_promoted_kb_section"],
    "projection_status": "superseded",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "not_applicable",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "not_applicable",
    "coverage_boundary_state": "not_applicable",
    "knowledge_promotion_state": "promoted",
    "supersession_state": "superseded",
    "review_validity_state": "not_applicable",
    "review_recency_state": "not_applicable",
    "expected_current_source": null,
    "expected_resolution": "insufficient_authority",
    "history_preserved": true
  },
  {
    "id": "invalid_current_review_verdict",
    "query_class": "current_review_verdict",
    "sources": ["invalid_review"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "not_applicable",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "not_applicable",
    "coverage_boundary_state": "not_applicable",
    "knowledge_promotion_state": "not_applicable",
    "supersession_state": "current_non_superseded",
    "review_validity_state": "invalid",
    "review_recency_state": "latest_valid",
    "expected_current_source": null,
    "expected_resolution": "insufficient_authority",
    "history_preserved": true
  },
  {
    "id": "non_latest_valid_review_verdict",
    "query_class": "current_review_verdict",
    "sources": ["older_valid_review", "newer_valid_review"],
    "projection_status": "historical",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "not_applicable",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "not_applicable",
    "coverage_boundary_state": "not_applicable",
    "knowledge_promotion_state": "not_applicable",
    "supersession_state": "current_non_superseded",
    "review_validity_state": "valid",
    "review_recency_state": "not_latest",
    "expected_current_source": null,
    "expected_resolution": "reviewer_required",
    "history_preserved": true
  },
  {
    "id": "superseded_current_review_verdict",
    "query_class": "current_review_verdict",
    "sources": ["superseded_review"],
    "projection_status": "superseded",
    "review_status": "reviewed",
    "reviewer_authority_state": "authority_qualified",
    "anchor_state": "not_applicable",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "not_applicable",
    "coverage_boundary_state": "not_applicable",
    "knowledge_promotion_state": "not_applicable",
    "supersession_state": "superseded",
    "review_validity_state": "valid",
    "review_recency_state": "latest_valid",
    "expected_current_source": null,
    "expected_resolution": "reviewer_required",
    "history_preserved": true
  },
  {
    "id": "unqualified_current_review_verdict",
    "query_class": "current_review_verdict",
    "sources": ["unqualified_latest_review"],
    "projection_status": "current",
    "review_status": "reviewed",
    "reviewer_authority_state": "unqualified",
    "anchor_state": "not_applicable",
    "state_transition_coverage": "not_applicable",
    "later_change_state": "not_applicable",
    "coverage_boundary_state": "not_applicable",
    "knowledge_promotion_state": "not_applicable",
    "supersession_state": "current_non_superseded",
    "review_validity_state": "valid",
    "review_recency_state": "latest_valid",
    "expected_current_source": null,
    "expected_resolution": "insufficient_authority",
    "history_preserved": true
  }
]
```
<!-- mrcsp-resolution-cases:end -->

## Scope

- define storage, writer, authority, projection, and review terminology;
- define question-specific reader resolution;
- reconcile the human-facing authority registry and canonical memory contracts;
- freeze reviewable contract cases for M-1.

## Non-Goals

- no M0 consumer fixture or ground-truth oracle;
- no reader, detector, schema, reconciliation, or projection implementation;
- no semantic contradiction or freshness judgment;
- no LLM analysis, auto-write, promotion, blocking, hook, CI, or gate change;
- no historical memory rewrite or migration;
- no dependency on unmerged PR #88 behavior.

## Boundary And API Considerations

This tranche adds no runtime API. Future readers must consume logical memory
surfaces rather than hard-coded filenames and must preserve authority conflicts
as explicit review states. A future machine-readable schema requires a separate
approved tranche.

## Failure Paths And Risk Points

- treating `canonical_record` as semantic truth;
- treating PLAN as permission rather than ordering inside approved scope;
- treating the newest timestamp as the highest-authority review;
- treating every `03` section as promoted knowledge;
- hiding a conflict by selecting one surface through a global priority order;
- using unmerged PR #88 semantics as current framework authority.

## Evidence Plan

M-1 contract tests must verify the five required resolution cases, the explicit
conflict case, all negative eligibility cases, vocabulary consistency,
authority-table activation, and aligned non-claims in the canonical memory
contracts. Passing those tests proves document alignment only, not reader
behavior or semantic correctness.

## Claim Ceiling

M-1 may claim only that an approved merge of the complete document set defines a
question-specific, traceable current-state projection contract without adding
runtime behavior. Branch and pull-request bytes remain candidates until that
merge. Even after activation, M0 is not authorized without a separate owner
decision.

## Next Implementation Tranche Recommendation

After M-1 is approved, define the M0 fixture admissibility contract and one
redacted exact-duplicate fixture. Do not begin M1a detector implementation in
this tranche.
