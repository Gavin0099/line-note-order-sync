---
audience: agent-on-demand
authority: canonical
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# Memory Reconciliation Exact-Byte Detector Contract

Status: ACTIVE WHEN MERGED AFTER AUTHORIZED INDEPENDENT REVIEW
Program: Memory Reconciliation & Current-State Projection (MRCSP)
Milestone: M1a

## Authority And Activation Boundary

The owner authorized this M1a tranche by supplying its exact DONE condition on
2026-08-24. The branch and pull-request bytes remain candidates. This contract
and its detector become active only after an authorized independent review
approves the complete M1a change and the change is merged.

M0 fixture admission remains governed by
`MEMORY_RECONCILIATION_FIXTURE_ADMISSIBILITY_CONTRACT.md`. M1a consumes record
bytes only after admission; it does not create a production fixture-admission
API or infer admission from matching bytes.

## Problem

M0 established one admissible exact-byte-duplicate pair, but no detector exists
that can turn that relation into a deterministic report. A later detector must
not overstate byte equality as semantic equivalence, stale state, bad memory,
or authority resolution.

## Normative Detector Contract

<!-- mrcsp-m1a-exact-byte-detector:begin -->
```json
{
  "contract_version": "mrcsp-exact-byte-detector.v0.1",
  "input_count": 2,
  "input_requirement": "distinct_identified_records_already_admitted_by_caller",
  "comparison": "raw_bytes_sha256",
  "finding_code": "duplicate_memory_entry",
  "finding_severity": "warning",
  "mode": "report_only",
  "equal_bytes_finding_count": 1,
  "different_bytes_finding_count": 0,
  "serialization": "utf8_sorted_compact_json_with_trailing_lf"
}
```
<!-- mrcsp-m1a-exact-byte-detector:end -->

The detector must:

- accept exactly two non-empty byte payloads with distinct, non-empty record
  identifiers and non-empty surface names;
- compute SHA-256 directly over each original byte payload without decoding,
  newline conversion, field normalization, or semantic parsing;
- emit exactly one `duplicate_memory_entry` finding when both digests match;
- emit zero findings when the digests differ;
- sort record identities and surfaces so input ordering cannot change output;
- serialize the same logical input to byte-identical UTF-8 JSON with sorted
  keys, compact separators, and one trailing LF;
- keep the finding at `severity=warning` and `mode=report_only`.

Invalid input fails closed with `ValueError`; it is not converted into a clean
report.

## Finding Meaning

`duplicate_memory_entry` means only that two independently identified record
payloads have the same raw-byte SHA-256 digest. It does not mean either record
is invalid, unnecessary, stale, authoritative, semantically equivalent, or
safe to delete.

## Scope

- one pure deterministic exact-byte detector;
- one report-only finding code;
- one byte-stable JSON renderer;
- focused positive, negative, ordering, and invalid-input regression tests;
- replay against the single admitted M0 fixture.

## Non-Goals

- no filesystem discovery or fixture-admission implementation;
- no normalized or semantic duplicate detection;
- no freshness, contradiction, supersession, or current-state judgment;
- no memory reader, projection, writer, mutation, or deletion;
- no public schema, runtime, hook, CI, gate, blocker, or enforcement;
- no second fixture, consumer replay, or historical memory scan.

## Evidence Plan

Focused tests must show that the admitted M0 pair produces exactly one finding,
a one-byte mutation produces zero findings, reversed input order produces the
same serialized bytes, identical input is byte-stable across repeated calls,
and invalid record count or identity fails closed. M0 admission and authority
metadata tests must remain green.

Passing proves only deterministic raw-byte duplicate reporting for the tested
pair and mutations. It does not prove semantic reconciliation, reader
correctness, fixture privacy beyond the M0 contract, or runtime enforcement.

## Claim Ceiling

M1a may claim only that the reviewed detector reports exact raw-byte equality
for two caller-admitted, independently identified records and produces stable
report-only JSON. It must not claim that real memory is reconciled, that a
duplicate should be removed, or that any completion outcome or governance gate
has changed.

## Deferred Work

Normalization, semantic analysis, readers, projections, public schemas,
runtime integration, hooks, CI, gates, blockers, enforcement, additional
fixtures, and consumer or historical scans require separate owner-authorized
tranches.
