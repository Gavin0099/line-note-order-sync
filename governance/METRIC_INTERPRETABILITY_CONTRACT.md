# Metric Interpretability Contract (v0.1)

As-of: 2026-05-15
Scope: epistemic governance — defines the admissibility preconditions that a metric must satisfy before it is eligible for usefulness ranking or causal interpretation.

## Core Principle

> **observability ≠ admissibility**

A metric can be:
- structurally present (field exists in harness output)
- numerically stable (consistent across seeds)
- replayable (same inputs → same outputs)
- entropy-clean (low variance)
- unsupported-free (zero `unsupported_count`)

...and still be **semantically inadmissible** — because nobody can articulate what the value means in governance terms.

A metric that enters usefulness ranking before interpretability is established produces a **fabricated utility ordering**: a ranking that has the appearance of evidence-based priority but is actually an artifact of measurement stability alone.

## The Interpretability Chain

```
metric exists
  → metric interpretable    ← MIP-01 through MIP-05 gate here
  → metric valid-for-ranking
  → metric rankable (r49x-4)
```

Skipping the second step does not cause an error. It causes something worse: silent corruption of the ranking output.

## Why This Matters for Sparse Verification

In a sparse-verification regime, missing metrics are epistemically honest absences.
Inadmissible metrics that are present are epistemically dishonest presences.

The second is more dangerous because:
- The system does not flag it
- Human reviewers treat numerical stability as a proxy for semantic validity
- Downstream decisions inherit the contamination silently

---

## MIP-01: Explainable

**Metric:** `claim_discipline_drift`

**Criterion:**
A domain expert unfamiliar with the harness internals can articulate, in governance terms, what a non-zero value means — specifically: which claim was made without support, by which reviewer, in which context.

**Pollution blocked:** semantic fabrication

> "The number is real, but the meaning is constructed after the fact to fit the narrative."

**Anti-patterns:**
- Defining drift only as "delta from baseline" without specifying what the baseline measures
- Accepting drift = 0.0 as "no drift" when the evaluator may have failed to detect it (see NT-03)
- Post-hoc interpretation: inferring what drift *should* mean after seeing results

**Admissibility signal:**
Written interpretation of a non-zero `claim_discipline_drift` that references a specific governance claim type, agreed before harness runs.

---

## MIP-02: Attributable

**Metric:** `unsupported_count`

**Criterion:**
A non-zero value can be traced to a specific reviewer action or claim, not to a harness artifact, evaluator bias, or measurement configuration. Attribution must precede interpretation.

**Pollution blocked:** causal fabrication

> "The signal is real, but the cause is wrong — and the wrong cause drives the wrong governance response."

**Anti-patterns:**
- Reporting `unsupported_count > 0` as "reviewer tacit dependency" before R49.x-1 (evaluator neutrality) completes
- Attributing count increases to substitution when the harness path is different for original vs. substituted reviewers
- Using NT-04 (causal null) values in attribution claims

**Admissibility signal:**
R49.x-1 (evaluator neutrality smoke) has a result, OR `unsupported_count` interpretation is explicitly tagged as `causal_attribution: ambiguous` until it does.

---

## MIP-03: Reproducible

**Metric:** `replay_deterministic`

**Criterion:**
Same seed + same reviewer + same scenario produces the same value for `replay_deterministic` across independent runs. Reproducibility must be demonstrated, not assumed.

**Pollution blocked:** stochastic illusion

> "The metric appears informative because it varies, but the variation is noise rather than signal."

**Anti-patterns:**
- Treating a single run's `replay_deterministic: true` as stable
- Using `replay_deterministic` to compare original vs. substituted reviewers before R49.x-2 (substitution replay stability) confirms baseline rate
- Assuming determinism when harness environment is not controlled (OS, Python version, seed propagation)

**Admissibility signal:**
R49.x-2 (substitution replay stability) has a preliminary result, OR cross-seed consistency is documented for at least one (scenario, reviewer) pair.

---

## MIP-04: Traceable

**Metric:** `reviewer_override_frequency`

**Criterion:**
Each override event has a logged source — reviewer identity + decision point + rationale — not just an aggregate count. Provenance must exist at the event level, not only at the metric level.

**Pollution blocked:** provenance collapse

> "The count is auditable in aggregate but not at the event level — any specific override cannot be investigated."

**Anti-patterns:**
- Reporting frequency as a rate without the event log
- Treating override frequency as reviewer-specific signal when it may be scenario-specific (topology effect)
- Comparing override frequencies across reviewers before confirming the scenarios are comparable (NT-02 structural null risk)

**Admissibility signal:**
Harness output includes per-override event log, OR frequency is tagged as `event_log_absent: true` and excluded from causal interpretation.

---

## MIP-05: Understandable

**Metric:** `intervention_entropy`

**Criterion:**
The entropy calculation is documented with its base distribution (uniform, scenario-specific, empirical). A low value and a high value each have an articulated interpretation in governance terms, agreed before seeing results.

**Pollution blocked:** observer hallucination

> "The value is computed correctly, but the reader assigns it a meaning that was never formally defined — the number becomes a Rorschach test."

**Anti-patterns:**
- Treating `intervention_entropy < 0.2` as "silo_risk_flagged" without defining what entropy < 0.2 means in terms of actual intervention distribution
- Imputing `intervention_entropy = 0.0` when there are zero interventions (NT-02 structural null — should be excluded, not treated as maximum silo risk)
- Comparing entropy across scenarios without controlling for the number of possible intervention points (topology-dependent baseline)

**Admissibility signal:**
Documented interpretation of high entropy and low entropy values with example governance implications, written before any run produces results.

---

## Cross-Condition Admissibility Table

| Metric | MIP | Pollution blocked | Admissibility signal |
|---|---|---|---|
| `claim_discipline_drift` | MIP-01 | semantic fabrication | pre-agreed interpretation of non-zero value |
| `unsupported_count` | MIP-02 | causal fabrication | R49.x-1 result or `causal_attribution: ambiguous` tag |
| `replay_deterministic` | MIP-03 | stochastic illusion | cross-seed consistency demonstrated |
| `reviewer_override_frequency` | MIP-04 | provenance collapse | per-event log or `event_log_absent: true` tag |
| `intervention_entropy` | MIP-05 | observer hallucination | pre-agreed high/low interpretation |

---

## Admissibility Decision Rule

A metric is **admissible for ranking** (r49x-4 eligible) if and only if:

1. Its MIP precondition is satisfied (signal documented above), OR
2. It is explicitly tagged with its inadmissibility reason AND excluded from the ranking denominator

A metric that is inadmissible must NOT:
- Appear in signal_classification output of r49x-4
- Be used to support any causal claim about reviewer substitution
- Enter aggregate statistics where it could corrupt denominators

An inadmissible metric MAY:
- Remain in the checkpoint as `admissibility: false, mip_blocked_by: [MIP-XX]`
- Be listed in the metric registry as `status: inadmissible_pending_[criterion]`
- Be reconsidered when its precondition is satisfied

---

## Relationship to Null Ontology

The null ontology (governance/NULL_ONTOLOGY.md) governs what happens when a measurement *fails* or is *absent*.

The metric interpretability contract governs what happens when a measurement *succeeds* but is *not yet admissible for interpretation*.

| Situation | Governed by |
|---|---|
| Harness fails before producing value | NULL_ONTOLOGY NT-01 |
| Metric not applicable to topology | NULL_ONTOLOGY NT-02 |
| Measured but meaning undecidable | NULL_ONTOLOGY NT-03 / MIP-01 |
| Signal exists but cause unattributable | NULL_ONTOLOGY NT-04 / MIP-02 |
| Evaluator confidence has no provenance | NULL_ONTOLOGY NT-05 |
| Measurement window not yet open | NULL_ONTOLOGY NT-06 |
| Metric present but not interpretable | **METRIC_INTERPRETABILITY_CONTRACT MIP-01..05** |

The two documents are complementary. NULL_ONTOLOGY handles absence and failure.
METRIC_INTERPRETABILITY_CONTRACT handles presence without legitimacy.

---

## Connection to r49x-4 (Metric Usefulness Ranking)

r49x-4 is blocked until `metric_interpretability_preconditions_met = true`.

This means:
- All five metrics must either satisfy their MIP, or be tagged as inadmissible with exclusion
- Only admissible metrics enter the `signal_classification` output
- The ranking denominator is the admissible set, not the full metric set

Violation of this sequencing produces **fabricated utility ordering**.

---

## Metric Admissibility Definitions (R49.2)

These definitions satisfy the pre-agreed interpretation requirement for MIP-01 and MIP-05.
They must exist before any harness run so that metric output cannot be interpreted post-hoc.

### Format

Each definition carries seven fields:

| Field | Purpose |
|---|---|
| `measured_object` | What the metric actually counts or computes |
| `valid_input` | What constitutes a legitimate input to this metric |
| `invalid_input` | What inputs must not be used (null type or structural reason) |
| `null_behavior` | What typed null to emit when input is invalid |
| `interpretation_boundary` | The defined range and what boundary values mean |
| `forbidden_interpretation` | Explicit prohibitions — what this metric must never be used to claim |
| `admissibility_status` | Current MIP satisfaction state |

---

### claim_discipline_drift

- **measured_object:** delta in governance violation detection rate between original_owner profile and substituted_owner profile, evaluated on the same scenario and seed
- **valid_input:** non-null violation counts from both profiles on the same (scenario, seed) pair
- **invalid_input:** NT-01 fallback run; NT-06 stub run; single-profile evaluation (no baseline exists for comparison)
- **null_behavior:** NT-02 if scenario contains no evaluable claims; NT-06 if substitution pair has not yet been evaluated on this (scenario, seed)
- **interpretation_boundary:** [0.0, 1.0] where 0.0 = identical detection rate across profiles; higher values indicate detection rate divergence. Direction alone is not interpretable without profile comparison.
- **forbidden_interpretation:**
  - `drift = 0.0` → `stable_candidate` — zero drift means profiles agree OR both failed to detect; cannot distinguish without NT-03 check
  - `drift > 0` → `tacit_dependency_detected` — divergence may be profile-specific topology, not reviewer dependency; requires R49.x-1 (evaluator neutrality) before causal attribution
- **admissibility_status:** MIP-01 pre-agreed interpretation satisfied by this definition. MIP-02 (attributable) pending R49.x-1.

---

### unsupported_count

- **measured_object:** count of claims evaluated as lacking required evidence reference under the active reviewer profile's criteria
- **valid_input:** scenario with at least one claim evaluable under the reviewer profile; reviewer profile with defined evidence criteria for this scenario type
- **invalid_input:** NT-01 run; scenario with no evaluable claims (NT-02); reviewer profile with no evidence criteria defined for this scenario type (NT-02 structural mismatch)
- **null_behavior:** NT-02 if reviewer profile has no evidence criteria for this scenario type; NT-06 if reviewer profile definition is pending
- **interpretation_boundary:** non-negative integer; comparison is meaningful only within the same profile type and same scenario; cross-profile comparison without baseline is NT-04 (causal null)
- **forbidden_interpretation:**
  - `count increase after substitution` → `reviewer_fragility_detected` — may be profile-specific topology effect, not tacit dependency; requires R49.x-1 before attribution
  - `count = 0` → `evidence_discipline_confirmed` — may mean evaluator failed to detect (NT-03), not that discipline is genuine
- **admissibility_status:** MIP-01 pre-agreed interpretation satisfied by this definition. MIP-02 pending R49.x-1.

---

### replay_deterministic

- **measured_object:** boolean — does the same (seed, reviewer_profile, scenario) tuple produce an identical violation set across independent runs?
- **valid_input:** ≥2 runs with identical (seed, reviewer_profile, scenario) tuple; runs must be independent (not cached)
- **invalid_input:** single run (NT-06 — determinism cannot be established from one run); runs with different seeds compared as if same (invalid comparison)
- **null_behavior:** NT-06 until at least a second independent run exists for the same tuple
- **interpretation_boundary:** boolean (true/false); no gradation — a run is either deterministic or it is not; partial determinism must be expressed as `replay_deterministic: false` with a note
- **forbidden_interpretation:**
  - `replay_deterministic: true` → `governance_is_stable` — determinism checks output consistency, not semantic correctness; a deterministic evaluator can be consistently wrong
  - `replay_deterministic: false` in substituted run → `substitution_fragility` — baseline (original_owner replay) must be checked first; if baseline is also non-deterministic, this is harness instability, not substitution effect (R49.x-2 disambiguation required)
- **admissibility_status:** MIP-01 and MIP-05 pre-agreed interpretations satisfied. MIP-03 (reproducible) requires cross-seed consistency demonstration from actual runs.

---

### reviewer_override_frequency

- **measured_object:** fraction of evaluated claims where the substituted profile reaches a different disposition than the original profile
- **valid_input:** both profiles evaluated the same claim set; per-claim disposition is available in event log (not aggregate count only)
- **invalid_input:** aggregate counts only without per-claim provenance (MIP-04 violation — provenance collapse); single-profile evaluation
- **null_behavior:** NT-02 if scenario has no prior disposition to compare against; NT-06 if per-claim event log is absent; tag `event_log_absent: true` when no log exists — this prevents the count from being used in causal claims
- **interpretation_boundary:** [0.0, 1.0]; high value means profiles diverge frequently in disposition; low value means profiles agree — but agreement may reflect identical blind spots, not genuine consensus
- **forbidden_interpretation:**
  - `high override_frequency` → `reviewer_weakness` — may be scenario topology (product scenario has more ambiguous claims by design); requires cross-scenario comparison before reviewer attribution
  - `low override_frequency` → `substitution_safe` — profiles may agree because both fail to detect; NT-03 risk
- **admissibility_status:** MIP-01 pre-agreed interpretation satisfied. MIP-04 (traceable): per-claim event log required; initial runs must tag `event_log_absent: true` if log unavailable.

---

### intervention_entropy

- **measured_object:** Shannon entropy of the intervention point distribution across evaluated claims in a scenario; base distribution must be documented
- **valid_input:** ≥2 distinct intervention points; documented base distribution (uniform, scenario-specific, or empirical); this documentation must pre-exist the run
- **invalid_input:** zero interventions (NT-02 — entropy is undefined when the set is empty; must NOT be imputed as 0.0); undefined base distribution (MIP-05 violation — observer hallucination risk)
- **null_behavior:** NT-02 if scenario has zero interventions; excluded from entropy comparison — do NOT impute 0.0 as "maximum silo risk"
- **interpretation_boundary:** [0.0, log₂(N)] where N = number of possible intervention points; interpretation requires documented base distribution; a value cannot be classified as "low" or "high" without the baseline; the baseline must be written in the reviewer profile schema before any run
- **forbidden_interpretation:**
  - `low entropy` → `silo_risk_flagged` without ruling out NT-02 (topology constraint with few intervention points by design)
  - `entropy convergence after substitution` → `knowledge_silo_confirmed` — may be metric instability in product scenarios (R49.x-2 prerequisite for this attribution)
  - comparing entropy across scenarios without controlling for number of possible intervention points
- **admissibility_status:** MIP-01 and MIP-05 pre-agreed interpretations satisfied by this definition and by reviewer profile schema (which must document base distributions). MIP-03 pending cross-seed demonstration.

---

## Version History

| Version | Change |
|---|---|
| v0.1 | Initial contract: MIP-01..05, admissibility decision rule, relationship to NULL_ONTOLOGY |
| v0.2 | Added metric admissibility definitions for all 5 R49.2 metrics; MIP-01 and MIP-05 preconditions satisfied for claim_discipline_drift, replay_deterministic, intervention_entropy |
