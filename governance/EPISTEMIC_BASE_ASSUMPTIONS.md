# Epistemic Base Assumptions (v0.1)

As-of: 2026-05-15
Scope: governance recursion boundary

---

## What This Document Is

This document defines the **anti-regress stopping layer** for the epistemic governance stack.

These are NOT:
- Universal truths
- Philosophically final statements
- Mathematically necessary axioms
- Self-evident principles

These ARE:
- Governance recursion boundaries
- Chosen stopping points that prevent admissibility regress
- Operational assumptions chosen because removing them destabilizes the governance boundary

### Legitimacy Source

Each assumption below is chosen because:

> *Without this assumption, epistemic collapse becomes unbounded.*

This is different from:
- "because X therefore Y" (derived consistency — valid for rules and contracts)
- "self-evident" (dogmatic — not appropriate here)

The legitimacy is **bounded regress prevention**, not proof.

### Layer Positioning

| Layer | Governs | Legitimacy source |
|---|---|---|
| Rule | derived behavior | consistency |
| Contract | operational enforcement | enforceability |
| Metric | measurement | interpretability / admissibility |
| **Stopping assumption** | recursion boundary | bounded regress prevention |

Stopping assumptions do not justify themselves by appeal to higher-level principles, because there is no higher level in this governance stack. They justify themselves by the unacceptability of the collapse that follows their removal.

---

## Prohibited Operations

The following operations are **permanently prohibited** on any stopping assumption in this document:

| Prohibited operation | Reason |
|---|---|
| Confidence scoring (e.g., `assumption_strength = 0.92`) | Re-introduces admissibility recursion: who validates the score? |
| Metric ranking (e.g., SA-01 is more important than SA-03) | Implies a higher layer that ranks them; no such layer exists |
| Probabilistic interpretation (e.g., SA-02 applies 80% of the time) | Converts stopping condition into a conditional — removes the stop |
| Automatic override by runtime observation | Allows metric fabrication pressure to dissolve the stopping layer |
| Runtime mutation (adjusting the assumption based on experiment results) | Makes the stopping layer a function of the governed system — circular |

These prohibitions are not rules derived from a higher principle.
They are part of what it means to be a stopping assumption.
A stopping assumption that can be overridden by runtime observation is not a stopping assumption.

---

## The Four Stopping Assumptions

---

### SA-01: Fail-Closed Base Assumption

**Statement:**
Null values, unknown values, and undecidable signals must never be automatically elevated to pass, fail, or any governance verdict without explicit human disposition or typed classification.

**Without this assumption:**
Any null in the system can silently become a governance decision.
The entire null ontology (NT-01..NT-06) collapses into a binary pass/fail that the system cannot distinguish from real evidence.
Governance becomes indistinguishable from default behavior.

**Scope:**
Applies to all layers: measurement, interpretation, evaluation, ranking, and enforcement.

**Does NOT mean:**
- All nulls are failures
- Null-producing runs must be retried
- The system halts on null

**Does mean:**
- Null → nothing happens automatically
- Human disposition or typed null_status is required before any gate is triggered
- Downstream consumers must check for null_type before consuming

---

### SA-02: Anti-Reactive Governance Assumption

**Statement:**
Observation does not directly trigger enforcement. A signal must pass through interpretation, attribution, and disposition before any governance consequence is applied.

**Without this assumption:**
A single anomalous metric value can trigger a governance gate before its cause is understood.
NT-04 (causal null) signals become NT-03 (semantic null) signals become enforcement actions.
Panic-driven governance replaces evidence-driven governance.

**Scope:**
Applies to the path from measurement to enforcement.
Does not prevent observation from informing interpretation (observation → interpretation is allowed).
Prevents observation from bypassing interpretation (observation → enforcement is not allowed).

**Does NOT mean:**
- Observations are ignored
- Enforcement never happens
- High-signal runs are treated the same as null runs

**Does mean:**
- Every enforcement action has a traceable interpretation step before it
- Interpretation steps have a traceable attribution step before them (for causal claims)
- Speed of observation does not compress the interpretation chain

---

### SA-03: Traceability Assumption

**Statement:**
Absent provenance is not treated as present provenance. A signal, confidence value, or metric without a documented source is not assigned a default trust level.

**Without this assumption:**
NT-05 (recursive null — evaluator has no provenance) is dissolved.
The evaluator_confidence field defaults to "medium" and is treated as a real signal.
Any metric can be used as if it had been properly validated, simply by omitting provenance documentation.

**Scope:**
Applies to every field that carries epistemic weight: evaluator_confidence, measurement_source, harness_exit_code, evidence_refs, causal_attribution.

**Does NOT mean:**
- Every field must have full provenance chains
- Absent provenance triggers governance gates
- Unknown sources are treated as hostile

**Does mean:**
- Absent provenance is explicitly marked as `provenance: absent`
- Absent provenance prevents the field from being consumed as real evidence
- A default value with absent provenance is tagged NT-05, not treated as real

---

### SA-04: Epistemic Visibility Assumption

**Statement:**
Evaluator uncertainty must be visible to consumers of evaluator output. An evaluator that cannot express its own uncertainty must not be treated as a reliable source of governance signals.

**Without this assumption:**
NT-05 (recursive null) is not detectable.
The system cannot distinguish a confident evaluator from an evaluator that is silently guessing.
Confidence values collapse into noise that cannot be separated from real signal.

**Scope:**
Applies to all evaluators in the system: harness, reviewer, governance agent, or any component that produces an output consumed by downstream governance logic.

**Does NOT mean:**
- Evaluators must always have high confidence
- Low-confidence evaluators are excluded from the system
- Uncertainty must be quantified precisely

**Does mean:**
- Evaluator output includes a visible confidence level and its provenance
- When confidence has no provenance, it is tagged `harness_default_NT-05` and treated accordingly
- Evaluators that cannot self-report uncertainty are not used for causal attribution

---

## Stopping Boundary Declaration

These four assumptions are the floor of the epistemic governance stack for this framework.

**They do not require further validation.**

Asking "what justifies SA-01?" is a valid philosophical question.
It is not a valid governance question within this system.

Within this governance boundary, the answer to "what justifies SA-01?" is:
> Without SA-01, governance becomes indistinguishable from default behavior. That outcome is unacceptable. Therefore SA-01 is assumed.

This is the only form of justification available at the stopping layer.

---

## Revision Policy

These assumptions CAN be revised. They are not permanent.

However, revision requires:

1. **Explicit deliberate process** — not runtime observation
   A harness result showing SA-02 might be too strict does not revise SA-02.
   An explicit governance review process revises SA-02.

2. **Replacement, not erosion**
   A revision removes an assumption and replaces it with a more precisely scoped one.
   It does not "weaken" an assumption by adding exceptions that compound over time.

3. **Documented consequence analysis**
   Before revision: document what governance collapse becomes possible without the old assumption.
   After revision: document what collapse the new assumption prevents.

4. **Version increment**
   Every revision to this document increments the version.
   Revisions are never made in-place without history.

What revision is NOT:
- Adding a `confidence: 0.8` qualifier to an existing assumption
- Runtime mutation based on observed metric values
- Gradual erosion through accumulated exceptions

---

## Relationship to Other Governance Documents

| Document | Governs | Stopped by |
|---|---|---|
| NULL_ONTOLOGY | absence and failure | SA-01 (null cannot auto-escalate) |
| METRIC_INTERPRETABILITY_CONTRACT | presence without legitimacy | SA-03 (traceability), SA-04 (visibility) |
| r49x-4 metric_usefulness_ranking | admissible metric ordering | SA-02 (no observation → enforcement shortcut) |
| This document | governance recursion boundary | No higher document. Stopped here. |

---

## Version History

| Version | Change |
|---|---|
| v0.1 | Initial stopping layer: SA-01..04, prohibited operations, revision policy, boundary declaration |
