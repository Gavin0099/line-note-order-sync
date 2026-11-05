# Null Ontology (v0.1)

As-of: 2026-05-15
Scope: epistemic governance — defines the taxonomy of "not knowing" across measurement, evaluation, and causal attribution layers.

## Why This Document Exists

All null values are not equal. A system that treats them as interchangeable will:
- Convert measurement failures into governance signals
- Convert genuine undecidability into false confidence
- Corrupt statistics by aggregating across incompatible null types
- Fail to escalate the right things to human reviewers

Null ontology is a prerequisite for:
- Null semantics audits (R49.x-5)
- Metric usefulness ranking (R49.x-4)
- Any sparse-verification regime where "not measured" must not equal "not violated"
- Fail-closed semantics that are epistemically honest

## Null Type Registry

---

### NT-01 Technical Null (`null_technical`)

**Definition:** The measurement machinery failed before producing a value.

**Origin:** infrastructure, not governance.

**Distinguishing signals:**
- `measurement_source: harness_error_fallback`
- `harness_exit_code ≠ 0` or `harness_exit_code == -1`
- `harness_error` is non-null

**Treatment:**
- Mark field as null with `null_type: null_technical`
- Retry after infrastructure fix
- Do NOT include in metric aggregations
- Do NOT interpret as governance fragility

**Fail-closed rule:** NT-01 must never trigger a governance gate. It must trigger an infrastructure alert.

**Anti-patterns:**
- `null_technical → fragility_detected`
- `null_technical → reviewer_tacit_dependency`
- Averaging over runs that mix `null_technical` and real values (denominator corruption)

---

### NT-02 Structural Null (`null_structural`)

**Definition:** The metric is not applicable to this topology, scenario, or reviewer combination. The harness ran cleanly but the metric has no meaningful value in this context.

**Origin:** topology mismatch, not measurement failure.

**Distinguishing signals:**
- `measurement_source: harness`
- `harness_exit_code: 0`
- Specific metric is always null across all seeds for a given (scenario, reviewer) pair
- Other metrics in the same run are non-null

**Examples:**
- `intervention_entropy` in a scenario with zero interventions
- `reviewer_override_frequency` when the reviewer role is undefined for this topology
- `replay_deterministic` in a non-deterministic scenario by design

**Treatment:**
- Mark field as null with `null_type: null_structural`
- Document in topology coverage map
- Exclude from cross-topology comparisons
- Do NOT treat as metric coverage failure

**Fail-closed rule:** NT-02 does not indicate system error. It indicates a topology boundary.

**Anti-patterns:**
- `null_structural → observability_gap` (confuses topology with measurement)
- Imputing zero for `intervention_entropy` when there are no interventions

---

### NT-03 Semantic Null (`null_semantic`)

**Definition:** Measurement ran and produced a value, but the result is epistemically undecidable — the evaluator cannot determine whether the value indicates drift, stability, or something else.

**Origin:** insufficient signal resolution, not measurement failure.

**Distinguishing signals:**
- `measurement_source: harness`
- `harness_exit_code: 0`
- Metric value is 0.0 or a boundary value
- `evaluator_confidence: low`
- Multiple interpretations are equally consistent with the value

**Examples:**
- `claim_discipline_drift: 0.0` — stable, or evaluator couldn't detect drift?
- `unsupported_count: 0` — genuinely zero, or unsupported claim detection failed?
- `replay_deterministic: true` — actually deterministic, or replay didn't exercise the boundary?

**Treatment:**
- Mark as `null_type: null_semantic` when evaluator_confidence is low and value is boundary/zero
- Flag for human reviewer disposition
- Do NOT aggregate with high-confidence measurements
- Do NOT conclude absence of fragility from semantic null values

**Fail-closed rule:** NT-03 must escalate to human reviewer for disposition. It must not be silently treated as pass or fail.

**Anti-patterns:**
- `null_semantic → stable_candidate` (zero drift is not proof of stability)
- `null_semantic → tacit_dependency_detected` (zero ≠ problem detected)
- Using NT-03 values to compute aggregate drift rates

---

### NT-04 Causal Null (`null_causal`)

**Definition:** A signal was measured and is non-null and non-zero, but its cause cannot be attributed to the phenomenon under study (reviewer substitution) vs. measurement artifacts (evaluator bias, topology asymmetry).

**Origin:** causal underdetermination — evidence is insufficient for attribution.

**Distinguishing signals:**
- Metric value is non-null and interpretable
- Multiple plausible causal paths exist (e.g., drift could be from substitution OR evaluator familiarity bias)
- R49.x-1 (evaluator neutrality) has not completed or has low confidence
- R49.x-3 (hotspot transferability) shows ambiguous results

**Examples:**
- `unsupported_count` increases after audit→runtime substitution — is this reviewer tacit dependency or harness knowing audit path better?
- `intervention_entropy` converges after product→runtime substitution — is this governance knowledge silo or metric instability in product scenarios?

**Treatment:**
- Measure the signal, record it as non-null
- Add `causal_attribution: ambiguous` to the run
- Do NOT interpret until R49.x-1 and R49.x-3 results are available
- Maintain a causal disambiguation queue

**Fail-closed rule:** NT-04 values must not be reported as governance findings until causal attribution is resolved.

**Anti-patterns:**
- Reporting `null_causal` signals as `reviewer_fragility_detected`
- Using NT-04 in aggregate statistics before disambiguation
- Treating disambiguation as optional when escalating findings

---

### NT-05 Recursive Null (`null_recursive`)

**Definition:** The evaluator's confidence in its own confidence is itself unknown or untrustworthy. The `evaluator_confidence` field has no verified provenance.

**Origin:** meta-measurement failure — the evaluator cannot self-assess reliably.

**Distinguishing signals:**
- `evaluator_confidence` value is present but derived from unknown logic
- Harness does not output provenance for how it computed `evaluator_confidence`
- `evaluator_confidence` varies inconsistently across identical runs
- Harness default (`"medium"` when not self-assessed) is being used

**Treatment:**
- Flag runs where `evaluator_confidence` has no provenance as `null_recursive`
- Do NOT trust `evaluator_confidence: medium` (harness default) for causal attribution
- Require harness to output `evaluator_confidence_provenance` field before treating confidence as reliable

**Fail-closed rule:** NT-05 means the evaluator neutrality check (R49.x-1) cannot be completed. R49.x-1 must be retried after harness is instrumented to report provenance.

**Anti-patterns:**
- Treating harness-default `"medium"` confidence as a real signal
- Using NT-05 runs in evaluator neutrality comparisons
- Conflating NT-05 with high evaluator confidence

---

### NT-06 Temporal Null (`null_temporal`)

**Definition:** The measurement window for this metric has not yet opened. The value is null because the precondition for measuring it has not been met.

**Origin:** sequencing constraint, not measurement failure.

**Distinguishing signals:**
- `status: pending`
- Explicit `requires_*` precondition in the task definition (e.g., `requires_harness_runs: 6`)
- Clock or count gate has not been reached

**Examples:**
- `metric_usefulness_ranking` (R49.x-4) before ≥6 harness runs exist
- `substitution_candidate_count` before any harness runs complete
- `r50_entry_criteria` before all R49.x tasks complete

**Treatment:**
- Leave null with `null_type: null_temporal`
- Record the precondition that must be met
- Do NOT impute, estimate, or extrapolate from existing data

**Fail-closed rule:** NT-06 values must not be used to unblock downstream criteria. Temporal nulls are explicit blockers, not missing data.

**Anti-patterns:**
- Early stopping: concluding the metric is unimportant because it's still temporal
- Using partial harness runs to extrapolate metric_usefulness_ranking
- Treating `null_temporal` as `null_structural` (topology excuse for a sequencing constraint)

---

## Cross-Type Comparison Table

| Type | Harness ran? | Value present? | Interpretable? | Cause attributable? | Evaluator self-assessed? |
|---|---|---|---|---|---|
| NT-01 technical | no | no | — | — | — |
| NT-02 structural | yes | no | — (not applicable) | yes (topology) | n/a |
| NT-03 semantic | yes | yes (boundary) | no | n/a | low confidence |
| NT-04 causal | yes | yes (non-zero) | yes | no | may be high |
| NT-05 recursive | yes | present but unverified | n/a | n/a | no provenance |
| NT-06 temporal | not yet | no | — | — | — |

## Null Type vs. Governance Implication

| Null type | Governance implication | Escalation target |
|---|---|---|
| NT-01 technical | infrastructure failure | engineering |
| NT-02 structural | topology boundary | topology documentation |
| NT-03 semantic | undecidable signal | human reviewer disposition |
| NT-04 causal | attribution pending | R49.x-1 / R49.x-3 disambiguation |
| NT-05 recursive | evaluator not self-aware | harness instrumentation |
| NT-06 temporal | precondition not met | wait |

## Connection to Fail-Closed Semantics

Fail-closed in this system means: **when uncertain, do not approve**.

Null ontology clarifies what "uncertain" means per null type:

| Null type | Fail-closed behavior |
|---|---|
| NT-01 | fail the infrastructure check, not the governance check |
| NT-02 | topology-closed: metric inapplicable, do not gate |
| NT-03 | escalate to reviewer: do not auto-fail, do not auto-pass |
| NT-04 | attribution-closed: do not report finding until resolved |
| NT-05 | evaluator-closed: do not trust evaluator output for this run |
| NT-06 | time-closed: do not unblock criteria early |

## Connection to Sparse Verification

In sparse-verification regimes, the most dangerous assumption is:

> "not measured" = "not violated"

Null ontology prevents this by requiring that every null value carry its type.
A sparse-verified claim is only valid if:
1. All relevant nulls are NT-02 (structural) or NT-06 (temporal)
2. No NT-03 (semantic), NT-04 (causal), NT-05 (recursive) nulls exist in the evidence path
3. NT-01 (technical) nulls have been resolved or explicitly excluded

## Version History

| Version | Change |
|---|---|
| v0.1 | Initial taxonomy: NT-01 through NT-06 |
