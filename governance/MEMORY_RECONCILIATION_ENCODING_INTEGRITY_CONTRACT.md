---
audience: agent-on-demand
authority: canonical
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# Memory Reconciliation Encoding-Integrity Contract

Status: ACTIVE WHEN MERGED AFTER OWNER ATTESTATION, AUTHORIZED INDEPENDENT
TECHNICAL REVIEW, AND GREEN REQUIRED CHECKS
Program: Memory Reconciliation & Current-State Projection (MRCSP)
Milestone: M1b-1

## Authority And Activation Boundary

The owner supplied the exact M1b-1 DONE condition on 2026-08-24. Branch and
pull-request bytes remain candidates. This contract and detector become active
only after the exact candidate head receives an owner merge attestation, an
authorized independent technical review, green required checks, and merge.

M1a exact-byte duplicate detection remains governed by
`MEMORY_RECONCILIATION_EXACT_BYTE_DETECTOR_CONTRACT.md`. This tranche adds one
independent structural-hygiene detector and does not change M1a semantics.

## Normative Detector Contract

<!-- mrcsp-m1b-encoding-integrity:begin -->
```json
{
  "contract_version": "mrcsp-encoding-integrity.v0.1",
  "input_count": 1,
  "input_requirement": "one_caller_admitted_memory_record_bytes",
  "decoding": "utf8_strict",
  "finding_code": "memory_encoding_integrity_anomaly",
  "finding_reasons": [
    "invalid_utf8",
    "replacement_character_present"
  ],
  "finding_severity": "warning",
  "mode": "report_only",
  "anomalous_input_finding_count": 1,
  "clean_input_finding_count": 0,
  "serialization": "utf8_sorted_compact_json_with_trailing_lf"
}
```
<!-- mrcsp-m1b-encoding-integrity:end -->

The detector must:

- accept exactly one caller-admitted `MemoryRecordBytes` value;
- decode the original bytes with strict UTF-8 decoding;
- emit exactly one `memory_encoding_integrity_anomaly` finding with
  `reason=invalid_utf8` when strict decoding raises `UnicodeDecodeError`;
- otherwise emit exactly one finding with
  `reason=replacement_character_present` when decoded text contains one or
  more literal U+FFFD replacement characters;
- emit zero findings for valid UTF-8 that contains no U+FFFD;
- compute the reported SHA-256 directly over the original bytes;
- serialize the same logical input to byte-identical UTF-8 JSON with sorted
  keys, compact separators, and one trailing LF;
- keep every finding at `severity=warning` and `mode=report_only`.

Invalid input fails closed with `ValueError`. Empty content is rejected by the
`MemoryRecordBytes` input contract and is never converted into a clean report.

## Finding Meaning

The finding means only that the supplied bytes either cannot be decoded as
strict UTF-8 or contain a literal U+FFFD character after successful decoding.
It does not prove how the bytes became anomalous, whether information was lost,
whether text is semantically corrupted, or whether any record should be edited
or deleted.

## Scope

- one pure deterministic encoding-integrity detector;
- one report-only finding code with two deterministic reason codes;
- reuse of the M1a byte-stable JSON renderer;
- focused clean, invalid-UTF-8, U+FFFD, repeated-character, digest, stability,
  and invalid-input regression tests.

## Non-Goals

- no heuristic mojibake detection or language-quality judgment;
- no decoding fallback, repair, rewriting, mutation, or deletion;
- no namespaced identity collision or missing-logical-surface detector;
- no filesystem discovery, fixture admission, reader, projection, or
  supersession;
- no public schema, runtime, hook, CI, gate, blocker, or enforcement;
- no M2 record-identity or binding change.

## Evidence Plan

Focused tests must show one finding for invalid UTF-8, one finding for valid
UTF-8 containing one or multiple U+FFFD characters, zero findings for clean
valid UTF-8, raw-byte digest preservation, byte-stable repeated output, and
`ValueError` for non-record or empty-content input. Existing M1a behavior and
authority metadata tests must remain green.

Passing proves only deterministic reporting for the tested byte classes. It
does not prove historical memory is clean, detect heuristic mojibake, repair
text, or alter any completion outcome.

## Claim Ceiling

M1b-1 may claim only deterministic, report-only classification of strict UTF-8
decode failure and literal U+FFFD presence for one caller-admitted record. It
must not claim semantic corruption, data-loss diagnosis, memory correctness,
repair safety, or enforcement.
