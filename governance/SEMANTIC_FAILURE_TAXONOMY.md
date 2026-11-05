# Semantic Failure Taxonomy (v0.1)

As-of: 2026-05-15
Scope: runtime semantic governance observation layer (non-authoritative).

## Purpose

This taxonomy classifies high-risk semantic failures that can pass structural/authority checks but still produce wrong or unsafe outcomes.

Boundary:
- Observation-first
- Reviewer-facing
- No automatic semantic correctness verdict
- No runtime authority promotion from this layer alone

## Failure Classes

### SF-01 Unsupported Leap
- Definition: conclusion includes a material jump not grounded by cited evidence.
- Typical signal: evidence fragment exists but does not justify the final action.
- Risk: plausible-looking but ungrounded implementation decisions.

### SF-02 Stale Semantic Carryover
- Definition: old assumptions are silently reused after context changed.
- Typical signal: prior-session/task premise appears without refresh/revalidation.
- Risk: outdated constraints poisoning current decisions.

### SF-03 Authority Reinterpretation
- Definition: authority boundaries are redefined locally without explicit policy change.
- Typical signal: "physical truth" or "observed data" used to bypass ownership/authority model.
- Risk: unauthorized decision paths that look rational in local context.

### SF-04 Topology Contradiction
- Definition: inferred topology/route/device relationships conflict with known invariants.
- Typical signal: contradictory identity, route, or ownership mapping in same workflow.
- Risk: cross-route contamination and incorrect execution targeting.

### SF-05 Evidence Mismatch
- Definition: claimed evidence and produced output are semantically inconsistent.
- Typical signal: cited register/spec text does not match generated code/config recommendation.
- Risk: evidence laundering (citation without real constraint binding).

### SF-06 Local-Global Inconsistency
- Definition: locally valid step violates global invariant/system contract.
- Typical signal: single-step fix resolves local issue while breaking envelope constraints.
- Risk: hidden systemic regressions.

### SF-07 Semantic Overwrite
- Definition: previously declared invariant is silently replaced by new interpretation.
- Typical signal: invariant statement drift without explicit "revision with evidence".
- Risk: undetected epistemic boundary erosion.

## Severity Bands (Reviewer Priority)

- `S3` critical: likely to break authority boundary or trigger unsafe execution decisions.
- `S2` major: high probability of incorrect implementation or policy drift.
- `S1` minor: ambiguity/noise that should be clarified but not immediate blocker.

## Output Contract (Observation Event)

Suggested event shape:

```json
{
  "event_type": "semantic_failure_observation",
  "failure_id": "SF-05",
  "severity": "S2",
  "invariant_id": "ownership_boundary",
  "evidence_refs": ["artifact://..."],
  "decision_refs": ["artifact://..."],
  "reviewer_action": "manual_semantic_review_required"
}
```

## Non-Goals (v0.1)

- Not a universal semantic verifier
- Not a truth oracle
- Not an auto-reject gate for all semantic ambiguity
