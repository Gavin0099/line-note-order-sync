---
audience: agent-on-demand
authority: canonical
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# Solo-Owner Merge Authority Contract

Status: ACTIVE WHEN MERGED AFTER OWNER ATTESTATION, AUTHORIZED INDEPENDENT
TECHNICAL REVIEW, AND GREEN REQUIRED CHECKS

## Observed Failure And Applicability

PR #103's final reviewer-facing body required a human GitHub `APPROVED` review,
but its GitHub review list was empty when the PR was merged. The stated prose
gate and the recorded merge evidence therefore disagreed. A PR body must not
invent a merge authority requirement that is absent from the canonical
governance model.

This contract applies when the repository owner explicitly operates the
repository under a solo-owner authority model. It replaces a mandatory GitHub
`APPROVED` review with a conjunctive, evidence-bound merge decision. A GitHub
`APPROVED` review remains valid additional evidence when available, but it is
not a required predicate and cannot substitute for a missing predicate below.

## Normative Merge Decision

<!-- solo-owner-merge-vocabulary:begin -->
```json
{
  "attestation_states": [
    "recorded_for_exact_head",
    "missing",
    "stale",
    "inferred_or_agent_generated"
  ],
  "check_states": [
    "green_for_exact_head",
    "pending",
    "failing",
    "missing_or_unknown"
  ],
  "github_approval_states": [
    "present",
    "absent"
  ],
  "head_states": [
    "matches_reviewed_head",
    "substantive_change_after_review",
    "unknown"
  ],
  "merge_decisions": [
    "eligible",
    "ineligible"
  ],
  "technical_review_states": [
    "independent_approved_for_exact_head",
    "missing",
    "changes_requested",
    "stale",
    "not_independent"
  ]
}
```
<!-- solo-owner-merge-vocabulary:end -->

The merge decision is `eligible` only when all of these predicates hold for
the same exact candidate head:

1. `owner_merge_attestation=recorded_for_exact_head`;
2. `independent_technical_review=independent_approved_for_exact_head`;
3. `required_checks=green_for_exact_head`; and
4. `head_state=matches_reviewed_head`.

Any missing, unknown, stale, failing, or non-independent required predicate
makes the decision `ineligible`. The decision fails closed; it must not be
rounded up from partial evidence.

## Predicate Meanings

### Owner merge attestation

The repository owner must make a current, explicit human statement authorizing
merge of the exact candidate head or immutable range. It may be recorded in an
authenticated PR comment, an authoring session, or another durable handoff
surface that identifies the target bytes.

An agent must not infer this attestation from a PLAN item, memory `next_step`, a
general continuation instruction, its own recommendation, or the later fact
that a merge occurred. An authenticated owner merge action can prove who
performed the merge during a post-merge audit, but it does not retroactively
prove that the pre-merge attestation predicate was satisfied.

### Independent technical review

The review must be performed by a reviewer distinct from the implementation
authoring process, identify the exact head or immutable range reviewed, apply
the applicable `REVIEW_CRITERIA.md` evidence rules, and finish with no blocking
findings. A GitHub review object is one possible transport, not the authority
source. A bounded independent sub-agent or human review can satisfy this
predicate when its identity, target, evidence, and verdict are recorded.

### Green required checks

Every check configured as required for the target branch must report success
for the exact candidate head. Pending, failing, absent, or indeterminate
required contexts fail closed. Event-inapplicable jobs that are not configured
as required do not become required merely because they exist in a workflow.

### Reviewed-head preservation

The merge candidate must match the exact head approved by the independent
technical review. Any substantive change after that review invalidates the
review predicate and requires a new review of the changed head. Metadata-only
PR edits do not change the Git head and therefore do not invalidate a
commit-bound review.

## Normative Cases

<!-- solo-owner-merge-cases:begin -->
```json
[
  {
    "case_id": "all_required_predicates_without_github_approval",
    "owner_merge_attestation": "recorded_for_exact_head",
    "independent_technical_review": "independent_approved_for_exact_head",
    "required_checks": "green_for_exact_head",
    "head_state": "matches_reviewed_head",
    "github_approved_review": "absent",
    "expected_decision": "eligible"
  },
  {
    "case_id": "github_approval_is_additional_evidence",
    "owner_merge_attestation": "recorded_for_exact_head",
    "independent_technical_review": "independent_approved_for_exact_head",
    "required_checks": "green_for_exact_head",
    "head_state": "matches_reviewed_head",
    "github_approved_review": "present",
    "expected_decision": "eligible"
  },
  {
    "case_id": "missing_owner_attestation",
    "owner_merge_attestation": "missing",
    "independent_technical_review": "independent_approved_for_exact_head",
    "required_checks": "green_for_exact_head",
    "head_state": "matches_reviewed_head",
    "github_approved_review": "present",
    "expected_decision": "ineligible"
  },
  {
    "case_id": "missing_independent_review",
    "owner_merge_attestation": "recorded_for_exact_head",
    "independent_technical_review": "missing",
    "required_checks": "green_for_exact_head",
    "head_state": "matches_reviewed_head",
    "github_approved_review": "present",
    "expected_decision": "ineligible"
  },
  {
    "case_id": "changes_requested",
    "owner_merge_attestation": "recorded_for_exact_head",
    "independent_technical_review": "changes_requested",
    "required_checks": "green_for_exact_head",
    "head_state": "matches_reviewed_head",
    "github_approved_review": "present",
    "expected_decision": "ineligible"
  },
  {
    "case_id": "required_checks_pending",
    "owner_merge_attestation": "recorded_for_exact_head",
    "independent_technical_review": "independent_approved_for_exact_head",
    "required_checks": "pending",
    "head_state": "matches_reviewed_head",
    "github_approved_review": "present",
    "expected_decision": "ineligible"
  },
  {
    "case_id": "required_checks_failing",
    "owner_merge_attestation": "recorded_for_exact_head",
    "independent_technical_review": "independent_approved_for_exact_head",
    "required_checks": "failing",
    "head_state": "matches_reviewed_head",
    "github_approved_review": "present",
    "expected_decision": "ineligible"
  },
  {
    "case_id": "substantive_change_after_review",
    "owner_merge_attestation": "recorded_for_exact_head",
    "independent_technical_review": "stale",
    "required_checks": "green_for_exact_head",
    "head_state": "substantive_change_after_review",
    "github_approved_review": "present",
    "expected_decision": "ineligible"
  },
  {
    "case_id": "post_merge_action_is_not_pre_merge_attestation",
    "owner_merge_attestation": "inferred_or_agent_generated",
    "independent_technical_review": "independent_approved_for_exact_head",
    "required_checks": "green_for_exact_head",
    "head_state": "matches_reviewed_head",
    "github_approved_review": "absent",
    "expected_decision": "ineligible"
  }
]
```
<!-- solo-owner-merge-cases:end -->

## Reviewer-Facing Language

For a solo-owner repository, use this merge condition:

> Merge requires an owner merge attestation for the exact head, an independent
> technical review approving that same head, green required checks for that
> head, and no substantive change after review. A GitHub `APPROVED` review is
> optional additional evidence, not a mandatory authority predicate.

Do not write "human APPROVED review required" or "GitHub APPROVED required"
unless a separate owner decision has deliberately adopted that stronger model
and the repository's enforcement and reviewer workflow are aligned with it.

## Claim Ceiling And Non-Goals

This contract defines decision authority and reporting semantics only. It does
not change GitHub branch protection, rulesets, required checks, reviewer
permissions, CI, runtime, hooks, schemas, gates, blockers, or enforcement.

It does not make PR #103 retroactively compliant with the prose gate its final
PR body stated. Its fixed-head technical evidence remains evidence; the missing
pre-merge GitHub approval remains a historical process discrepancy. This
contract governs future solo-owner merge decisions after activation.

M1b and every reader, writer, reconciliation, mutation, or enforcement tranche
remain outside this correction and require separate owner authorization.
