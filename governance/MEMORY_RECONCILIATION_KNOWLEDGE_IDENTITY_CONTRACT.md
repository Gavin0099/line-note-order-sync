---
audience: agent-on-demand
authority: canonical
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# Memory Reconciliation Knowledge-Identity Collision Contract

Status: ACTIVE WHEN MERGED AFTER OWNER ATTESTATION, AUTHORIZED INDEPENDENT
TECHNICAL REVIEW, AND GREEN REQUIRED CHECKS
Program: Memory Reconciliation & Current-State Projection (MRCSP)
Milestone: M1b-2

## Authority And Activation Boundary

The owner supplied the exact M1b-2 DONE condition on 2026-08-24. Branch and
pull-request bytes remain candidates. This contract and detector become active
only after the exact candidate head receives an owner merge attestation, an
authorized independent technical review, green required checks, reviewed-head
preservation, and merge.

M1a exact-byte duplicate detection and M1b-1 encoding-integrity reporting keep
their existing semantics. This tranche adds one independent structural-hygiene
detector and does not change either earlier detector.

## Problem And Evidence Boundary

The owner-provided MRCSP plan records reuse of `knowledge:T-012` as the
motivating structural-hygiene failure. That observation justifies a bounded
exact-identity detector, but no consumer bytes or parser-derived identity are
published in this tranche. The detector therefore consumes only identities the
caller has already admitted and does not claim consumer replay.

## Normative Detector Contract

<!-- mrcsp-m1b-knowledge-identity:begin -->
```json
{
  "contract_version": "mrcsp-knowledge-identity-collision.v0.1",
  "input_count": 2,
  "input_requirement": "distinct_caller_admitted_knowledge_identity_observations",
  "comparison": "case_sensitive_exact_knowledge_id",
  "qualified_identity_namespace": "knowledge",
  "finding_code": "knowledge_identity_collision",
  "finding_severity": "warning",
  "mode": "report_only",
  "equal_identity_finding_count": 1,
  "different_identity_finding_count": 0,
  "serialization": "utf8_sorted_compact_json_with_trailing_lf"
}
```
<!-- mrcsp-m1b-knowledge-identity:end -->

The detector must:

- accept exactly two caller-admitted `KnowledgeIdentityObservation` values;
- traverse the supplied sequence exactly once, materialize at most three items
  into an immutable local collection, and validate and use only that collection;
- convert ordinary iteration, materialization, attribute-access, and field
  validation exceptions into `ValueError` without catching `BaseException`;
- require plain built-in string fields, distinct non-empty record identifiers,
  non-empty surface names, and non-empty knowledge identifiers without
  surrounding whitespace;
- compare the supplied knowledge identifiers with exact case-sensitive string
  equality and without normalization or semantic parsing;
- emit exactly one `knowledge_identity_collision` finding when the identifiers
  are equal and zero findings when they differ;
- qualify a finding as `knowledge:<knowledge_id>` without inferring a namespace
  from Markdown structure;
- order record identities deterministically so input order cannot affect output;
- serialize the same logical input to byte-identical UTF-8 JSON with sorted
  keys, compact separators, and one trailing LF;
- keep every finding at `severity=warning` and `mode=report_only`.

Invalid input fails closed with `ValueError`; it is not converted into a clean
report.

## Finding Meaning

The finding means only that two independently identified, caller-admitted
knowledge observations carry the same exact knowledge identifier. It does not
prove that the records are semantically equivalent, that either record is
wrong, that one should be deleted, or that the identifier was parsed correctly
from source Markdown.

## Scope

- one pure deterministic namespaced knowledge-identity detector;
- one explicit caller-admitted identity observation type;
- one warning-only, report-only finding code;
- reuse of the M1a byte-stable JSON renderer;
- focused positive, negative, ordering, stability, and invalid-input tests.

## Non-Goals

- no Markdown heading, block, file, directory, or repository scanning;
- no identifier extraction, normalization, case folding, aliasing, or semantic
  identity inference;
- no duplicate-content, encoding-integrity, missing-logical-surface, freshness,
  contradiction, supersession, or current-state judgment;
- no reader, projection, writer, mutation, deletion, or repair;
- no public schema, runtime, hook, CI, gate, blocker, or enforcement;
- no M2 record-identity, supersession, binding, or work-item change.

## Evidence Plan

Focused tests must show exactly one finding for two distinct records with the
same exact knowledge identifier, zero findings after a one-character or
case-only identifier change, identical serialized bytes across repeated and
reversed input, and `ValueError` for invalid collection, count, element,
identity, or forged input. Existing M1a and M1b-1 behavior and authority
metadata tests must remain green.

Passing proves only deterministic exact-identifier collision reporting for the
tested caller-admitted observations. It does not prove real repository identity
uniqueness, parser correctness, semantic duplication, or enforcement.

## Claim Ceiling

M1b-2 may claim only deterministic, report-only classification of exact
case-sensitive knowledge-identifier reuse across two caller-admitted,
independently identified observations. It must not claim semantic collision,
source parsing, repository-wide hygiene, remediation safety, or enforcement.
