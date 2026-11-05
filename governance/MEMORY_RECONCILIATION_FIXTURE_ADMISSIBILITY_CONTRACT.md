---
audience: agent-on-demand
authority: canonical
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# Memory Reconciliation Fixture Admissibility Contract

Status: ACTIVE WHEN MERGED AFTER AUTHORIZED INDEPENDENT REVIEW
Program: Memory Reconciliation & Current-State Projection (MRCSP)
Milestone: M0

## Authority And Activation Boundary

`MEMORY_SURFACE_AUTHORITY_CONTRACT.md` recommends that M0 define a fixture
admissibility contract and one redacted exact-duplicate fixture. It does not
specify the detailed DONE conditions.

The owner separately authorized this M0 tranche on 2026-08-24 and set the DONE
conditions: provenance, a redaction boundary, a pinned SHA-256 digest, and
fail-closed rejection of byte mismatch, missing provenance, missing digest, and
incomplete redaction. Those conditions are owner-set scope, not text derived
from line 607 of the M-1 contract.

The branch and pull-request bytes remain candidates. This contract and its one
fixture become active only after an independent review approves the complete M0
change and the change is merged.

## Problem

A duplicate-memory detector cannot be calibrated against a fixture merely
because two files look similar. Without provenance, an explicit redaction
boundary, and a pinned byte digest, a test corpus can silently drift or expose
source identifiers. Such a fixture would create false confidence in later
reader or detector work.

## Current Repository Truth

- M-1 defines question-specific memory authority and explicitly excludes an M0
  fixture or ground-truth oracle.
- M-1 recommends one redacted exact-duplicate fixture as the next tranche and
  explicitly defers M1a detector implementation.
- Before this tranche, the repository has no MRCSP fixture admissibility
  contract and no admitted MRCSP ground-truth fixture.

## Admissible Fixture Unit

One M0 fixture is one test-only pair:

1. a redacted source record;
2. a candidate record whose bytes must be exactly identical to the source; and
3. a test-only manifest that binds the pair to provenance, redaction metadata,
   and a pinned SHA-256 digest.

The pair is ground truth only for the relation `exact_byte_duplicate`. It is not
ground truth for semantic equivalence, contradiction, freshness, authority,
current-state selection, or reconciliation.

## Normative Admission Requirements

<!-- mrcsp-m0-admissibility-requirements:begin -->
```json
{
  "contract_version": "mrcsp-fixture-admissibility.v0.1",
  "fixture_count": 1,
  "fixture_usage": "test_only",
  "required_relation": "exact_byte_duplicate",
  "required_digest_algorithm": "sha256",
  "required_provenance_fields": [
    "kind",
    "basis",
    "created_by",
    "created_at"
  ],
  "required_redaction_boundaries": [
    "repository_identity",
    "person_identity",
    "session_identity",
    "commit_identity",
    "artifact_locator",
    "source_timestamp",
    "unneeded_free_text"
  ],
  "required_rejection_codes": [
    "byte_mismatch",
    "missing_provenance",
    "missing_digest",
    "incomplete_redaction"
  ]
}
```
<!-- mrcsp-m0-admissibility-requirements:end -->

An admitted fixture must satisfy every requirement below:

- both declared files exist under the test-only fixture directory;
- both declared paths are portable relative paths that resolve to distinct,
  non-symlink regular files inside that directory;
- the source bytes and candidate bytes are exactly equal;
- the manifest contains every required provenance field;
- `provenance.kind` is `synthetic_redacted_reconstruction`;
- redaction is declared `complete`, contains every required boundary, and says
  that original identifiers are not included;
- the digest algorithm is `sha256` and the pinned digest equals the SHA-256 of
  both files;
- the expected relation is exactly `exact_byte_duplicate`;
- the manifest preserves the M0 claim ceiling and test-only usage.

Admission is conjunctive and fail-closed. Missing, unknown, or inconsistent
metadata is not interpreted as an implied PASS.

## Provenance Boundary

The fixture is a synthetic redacted reconstruction created for this authorized
M0 tranche. Its provenance records the owner authorization and the M-1 next-
tranche recommendation as the basis for creation. It does not claim that the
fixture bytes were copied from a private or consumer repository record.

`created_by` identifies the fixture authoring role, not an independent reviewer
and not an authority decision. Independent review is recorded outside the
fixture manifest through the pull-request review path.

## Redaction Boundary

The fixture must replace or omit all real repository, person, session, commit,
artifact, and timestamp identifiers, plus free text unnecessary to establish
the exact-byte relation. Placeholders may preserve field shape, but no
placeholder may be reversible to a real source identifier.

`redaction.status=complete` is necessary but not sufficient. Every boundary in
the normative requirement block must be declared and
`original_identifiers_included` must be `false`.

## Required Rejection Cases

| Mutation | Required result | Code |
| --- | --- | --- |
| Candidate bytes differ from source bytes | reject | `byte_mismatch` |
| `provenance` is absent | reject | `missing_provenance` |
| `digest` is absent | reject | `missing_digest` |
| Redaction status, boundary coverage, or original-identifier exclusion is incomplete | reject | `incomplete_redaction` |

These are contract-test cases, not a production validator API.

Path escape, absolute or non-portable paths, missing or non-regular files,
symlinks, and identical normalized source/candidate paths are also rejected.
Those checks enforce the declared fixture-unit boundary; they do not add a
fifth owner-set content rejection case.

## Scope

- define fixture admissibility for MRCSP M0;
- add one redacted exact-byte-duplicate test fixture pair;
- pin the pair to a SHA-256 digest;
- prove the four owner-set rejection cases with test-local mutations;
- register this canonical contract in the human-facing authority table.

## Non-Goals

- no memory reader or current-state projection implementation;
- no M1a detector or reconciliation implementation;
- no writer, runtime, public schema, hook, CI, gate, blocker, or enforcement;
- no semantic duplicate, contradiction, freshness, or supersession judgment;
- no historical memory normalization or consumer replay;
- no second fixture.

## Evidence Plan

Focused tests must parse the normative JSON block, verify authority metadata,
recompute both file digests, verify exact byte equality, and show that each of
the four required mutations is rejected with its named code. Repository
authority consistency and document-path tests must remain green.

Passing proves only that this contract and the one fixture are internally
consistent at the tested revision. It does not prove detector correctness,
semantic reconciliation, privacy of any external source, or runtime behavior.

## Claim Ceiling

M0 may claim only that one synthetic, redacted, test-only exact-byte-duplicate
fixture satisfies this contract at the reviewed commit. It must not claim that
a reader or detector exists, that real memory has been reconciled, that
redaction is independently privacy-certified, or that any governance rule is
enforced at runtime.

## Deferred Work

M1a and every reader, detector, runtime, schema, hook, CI, gate, or enforcement
change require a separate owner-authorized tranche. M0 does not authorize them.
