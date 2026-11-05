---
audience: agent-on-demand
authority: canonical
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# Memory Reconciliation Missing Logical Surface Contract

Status: ACTIVE WHEN MERGED AFTER OWNER ATTESTATION, AUTHORIZED INDEPENDENT
TECHNICAL REVIEW, AND GREEN REQUIRED CHECKS
Program: Memory Reconciliation & Current-State Projection (MRCSP)
Milestone: M1b-3

## Authority And Activation Boundary

The owner supplied the exact M1b-3 DONE condition on 2026-08-31. Branch bytes
remain candidates. This contract and detector become active only after the
exact candidate head receives an owner merge attestation, an authorized
independent technical review, green required checks, reviewed-head
preservation, and merge.

M1a, M1b-1, and M1b-2 keep their existing semantics. This tranche adds one
independent structural-hygiene detector and does not change earlier detectors
or `memory_pipeline.memory_layout` alias and resolution semantics.

## Normative Detector Contract

<!-- mrcsp-m1b-missing-logical-surface:begin -->
```json
{
  "contract_version": "mrcsp-missing-logical-memory-surface.v0.1",
  "input_count": 2,
  "input_requirement": "one_caller_admitted_existing_directory_and_one_configured_logical_name",
  "resolution": "memory_pipeline.memory_layout.resolve_memory_file",
  "finding_code": "missing_logical_memory_surface",
  "finding_severity": "warning",
  "mode": "report_only",
  "all_aliases_missing_finding_count": 1,
  "any_configured_alias_present_finding_count": 0,
  "serialization": "utf8_sorted_compact_json_with_trailing_lf"
}
```
<!-- mrcsp-m1b-missing-logical-surface:end -->

The detector must:

- accept one caller-admitted `pathlib.Path` that exists and is a directory and
  one exact logical name defined by `MEMORY_FILE_ALIASES`;
- reuse `memory_pipeline.memory_layout.resolve_memory_file()` without changing
  its alias ordering or resolution semantics;
- snapshot the resolver, its returned path, and that path's existence state
  once each, then use only those local snapshots for the decision and report;
- emit exactly one `missing_logical_memory_surface` finding when the resolver's
  returned path does not exist, meaning no configured alias existed during that
  observation;
- emit zero findings when the canonical file or any configured secondary alias
  exists;
- serialize unchanged input and filesystem state to byte-identical UTF-8 JSON
  with sorted keys, compact separators, and one trailing LF;
- keep the finding at `severity=warning` and `mode=report_only`.

Unknown logical names, invalid argument types, missing or non-directory roots,
and ordinary resolver or existence-check exceptions fail closed with
`ValueError`. They are not converted into a clean report.

## Finding Meaning

The finding means only that the caller-specified logical surface had no
configured alias present during one bounded observation. It does not establish
repository-wide completeness, memory correctness, freshness, supersession, or
that a file can be safely created or repaired.

## Scope

- one deterministic alias-aware missing logical surface detector;
- one warning-only, report-only finding code;
- reuse of the existing resolver and byte-stable JSON renderer;
- focused canonical, secondary-alias, missing, stability, invalid-input,
  resolver-exception, and snapshot-count tests.

## Non-Goals

- no directory or repository scanning;
- no Markdown parsing, content repair, file creation, mutation, or deletion;
- no alias inference, normalization, or semantic identity;
- no memory reader, projection, writer, freshness, or supersession judgment;
- no public schema, runtime, hook, CI, gate, blocker, or enforcement;
- no Gate 3 input, manifest, digest, runner, or status-artifact change;
- no M2 behavior.

## Evidence Plan

Focused tests must show zero findings for a canonical file and for a secondary
alias when the canonical file is absent, exactly one finding when all configured
aliases are absent, byte-identical repeated JSON, `ValueError` for invalid
inputs and ordinary resolver exceptions, and single-snapshot use of resolver,
resolved path, and existence state. Existing M1a, M1b-1, M1b-2, and authority
metadata tests must remain green.

Passing proves only deterministic report-only detection for the tested
caller-admitted logical surface and filesystem states. It does not prove any
repository or memory set is complete, correct, current, or safe to mutate.

## Claim Ceiling

M1b-3 may claim only deterministic alias-aware absence reporting for one
caller-specified configured logical surface at one observation. It must not
claim repository-wide completeness, memory correctness, freshness,
supersession, repair safety, or enforcement.
