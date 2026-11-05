# Confidence Semantics Freeze Contract

As-of: 2026-05-16 (v2 — adds reviewer-facing semantic containment and osmosis guard)
Scope: R50 and all downstream phases until explicitly superseded by human reviewer sign-off
Authority: Gavin0099 (decision); Codex (formalization)

---

## Purpose

This contract exists because positive evidence is structurally more dangerous than
negative evidence.

Negative governance is intuitive:
- block, reject, fail-closed, require review

Positive governance is dangerous because human cognition naturally converts:
- stable → trustworthy
- repeatable → reliable
- persistent → predictive
- historically useful → decision-relevant

This shortcut is not a bug in reviewers. It is a feature of how cognitive systems
allocate attention. The contract does not try to change reviewer cognition. It
makes the semantic boundary explicit enough to be reconstructed under pressure.

**The goal of R50 is not accumulation. It is containment.**

Containment means: positive evidence exists in the record, but does not leak
into the authority layer — even through implicit trust emergence.

---

## Layer I — Explicit Code Path Freeze

Blocks deliberate design decisions that would promote evidence into authority:

```json
{
  "confidence_accumulation_mode": "observational_only",
  "authority_upgrade_allowed": false,
  "decision_weight_allowed": false,
  "ranking_allowed": false,
  "threshold_promotion_allowed": false,
  "score_derivation_allowed": false,
  "implicit_trust_transfer_allowed": false
}
```

This layer blocks: explicit scoring, explicit thresholds, explicit promotion,
explicit ranking. It does NOT block semantic osmosis.

---

## Layer II — Reviewer-Facing Semantic Containment

Blocks the implicit cognitive path from observation to authority:

```json
{
  "reviewer_trust_transfer_allowed": false,
  "persistent_signal_interpretation": "non-authoritative",
  "historically_useful_semantics": "non-predictive",
  "replay_stability_semantics": "pipeline_determinism_only",
  "confidence_reuse_scope": "review_context_only"
}
```

### Definitions

**`reviewer_trust_transfer_allowed: false`**
A reviewer who has observed many positive signals across sessions must not
carry accumulated trust into a new review. Each review context resets.
Accumulated familiarity with positive signals does not constitute calibration.

**`persistent_signal_interpretation: non-authoritative`**
A signal that appears repeatedly across runs is persistent. Persistence is a
stability property of the measurement pipeline — not an authority property of
the signal's content. "This value appears consistently" does not mean "this
value can be relied upon for decisions."

**`historically_useful_semantics: non-predictive`**
A metric classified `historically_useful` (e.g., `replay_deterministic`) is
retained for lineage only. It does not predict future behavior. It does not
justify increased confidence in any governance claim. The classification is
terminal: `historically_useful` cannot be re-promoted without a new
attribution contract.

**`replay_stability_semantics: pipeline_determinism_only`**
Replay stability means: given the same input, the same pipeline produces the
same output. This is a property of the pipeline, not of the governed system.
`replay_deterministic = true` is evidence that the harness is deterministic.
It is not evidence that governance is effective.

**`confidence_reuse_scope: review_context_only`**
Confidence observations from one review session may not be carried forward as
evidence in a subsequent session without explicit re-verification. A reviewer
cannot say "this was stable last time, so I trust it now." Each session must
establish its own basis.

---

## Layer III — Semantic Osmosis Guard

Semantic osmosis is the process by which implicit trust accumulates through
repeated exposure to stable signals — without any explicit code path, design
decision, or policy change.

It is the most dangerous form of authority creep because it is invisible and
does not require any deliberate decision. It operates through language.

### 3A — Osmosis Indicators

| Indicator | What it sounds like | What it silently implies |
|---|---|---|
| Familiarity-based trust | "We've seen this a lot, so it's probably fine" | repeatability → perceived reliability |
| Stability-as-reliability | "It's been consistent, so we can rely on it" | consistency → warranted reliance |
| Historical-as-predictive | "It's always been this way, so it will continue" | past behavior → future authority |
| Volume-as-validation | "We have 18 runs of data, that should be enough" | count → sufficiency threshold |
| Persistence-as-warrant | "It's shown up in every checkpoint" | recurrence → implicit endorsement |

**None of the above statements constitute a governance warrant.**

The escalation chain these phrases silently construct:

```
repeatability
→ familiarity
→ perceived reliability
→ implicit warrant
```

Each step is a cognitive shortcut, not an epistemic inference.
None of the steps have a contract behind them.

### 3B — Rhetorical Trust Escalators

A rhetorical trust escalator is a sentence or phrase that, without making an
explicit governance claim, causes a reviewer to implicitly elevate the authority
of a signal. They are prohibited in governance artifacts.

**Prohibited patterns:**

| Pattern | Prohibited because |
|---|---|
| "This is consistent with previous runs" | implies predictive reliability |
| "We've verified this multiple times" | implies accumulated warrant |
| "The data supports this" | implies decision-relevant support |
| "This has been stable" | implies trustworthiness |
| "Historically, this has been..." | implies predictive authority |
| "Given the evidence we've collected..." | implies causal attribution |
| "Based on N runs..." | implies volume-induced authority |

When writing R50 artifacts, these phrases must be replaced with semantically
bounded language:

| Replace with | Because it means |
|---|---|
| "In N runs under fixed conditions, M showed X" | count under conditions, no inference |
| "This run produced value V" | single-instance observation |
| "The pipeline produced consistent output" | pipeline property, not signal property |

### 3C — Negative Authorization Reconstruction

Knowing that something is prohibited is insufficient if the causal basis for the
prohibition is forgotten. When the causal basis disappears, a restriction gets
reclassified as "just conservative" rather than "epistemically necessary."

This distinction matters because:
- "just conservative" = can be relaxed when stakes seem low
- "epistemically necessary" = cannot be relaxed without the missing contract

But preserving the causal basis is also insufficient if the failure mode is unknown.
A reviewer who knows "MIP-02 is missing" but not "what breaks if MIP-02 is bypassed"
will eventually treat `MIP-02` as an abstract ritual phrase — a label without teeth.

This is **second-order epistemic decay**:

```
restriction (hard boundary)
→ remembered caution
→ organizational habit
→ optional preference
→ eventually ignored
```

The same decay applies to causal bases:

```
causal basis ("MIP-02 missing")
→ remembered label
→ ritual phrase
→ abstract formality
→ bypassed without noticing
```

**3C preserves the complete causal chain:**

```
restriction → causal basis → missing contract → failure mode → bypass scenario (own words)
```

Four decay levels are defined. Three are guarded within this contract; one is
acknowledged as a known future risk:

| Decay level | What decays | What blocks it | In scope |
|---|---|---|---|
| First-order | restriction → "just conservative" | knowing the causal basis | ✅ R50 |
| Second-order | "missing contract" → ritual phrase | knowing the failure mode | ✅ R50 |
| Third-order | failure mode label → ritual label | constructing bypass scenario in own words | ✅ R50 |
| **Fourth-order** | **own-words bypass scenario → narrative mimicry** | **adversarial reconstruction: applying principle to unseen scenario** | ⚠️ future phase |

**Fourth-order decay — Narrative Mimicry:**

A reviewer can learn to describe bypass scenarios convincingly without retaining
causal understanding. This occurs when a standard bypass story is repeated enough
times to become a high-quality script. The reviewer produces paraphrase-level output
that passes the third-order test, but cannot transfer the principle to a novel case.

The distinction:

| Capability | What it demonstrates | Sufficient for |
|---|---|---|
| Label recall | Symbol retrieval | None — first/second/third-order risk |
| Paraphrasability (own words) | Narrative encoding | Third-order protection |
| **Transfer (unseen scenario)** | **Causal simulation** | **Fourth-order protection** |

Paraphrasability is evidence that understanding existed at encoding time.
Transfer is evidence that understanding still exists now.

**Hollow compliance pattern:**
The most dangerous governance state is one where:
- rules are present
- documents are complete
- labels are used correctly
- dashboards are populated
- reviewers can describe failure scenarios fluently

...but nobody can simulate how the failure unfolds in a case they haven't seen before.

This is **governance as anti-ritualization failure**: the system looks mature but
nobody can reconstruct the causal mechanism from first principles.

**The fourth-order guard (out of scope for R50):**

Adversarial reconstruction: present a reviewer with a modified or unseen scenario
and ask them to apply the epistemic principles without access to standard examples.

Examples:
- "A new metric is proposed. What would need to be true before it could enter the
  `decision_relevant` layer? Walk me through what contracts are needed and what
  breaks if they're skipped."
- "Here is a sentence we haven't labeled before: [novel sentence]. Is this a
  rhetorical trust escalator? Why or why not?"

A reviewer who can answer these is demonstrating causal simulation, not narrative recall.

**R50.5 scope limitation:** R50.5 tests paraphrasability (third-order protection).
It does not test transfer (fourth-order protection). This is a known design boundary,
not a gap that R50 intends to close. Fourth-order protection requires a future
verification phase with adversarial scenario design.

Each prohibition carries four fields. A reviewer who cannot reconstruct all four
for at least one prohibition has not completed causal epistemic recovery.

| Prohibition | Causal basis | What's missing | Failure mode if bypassed |
|---|---|---|---|
| `claim_discipline_drift` cannot enter `decision_relevant` | MIP-02 requires causal attribution; R49.x-1 (evaluator neutrality) not yet completed | Attribution contract + R49.x-1 completion | Fabricated causality: drift observed → drift attributed to reviewer tacit knowledge, but attribution is harness artifact; decisions made on invented causal model |
| `reviewer_override_frequency` cannot be used | MIP-04 requires per-claim event log; no event log infrastructure exists | Event log layer | Proxy collapse: silence conflated with zero overrides; null rate misread as compliance signal; governance appears clean when it is unobserved |
| `replay_deterministic` cannot be reused as confidence basis | Harness determinism is a pipeline property; carries no information about governed system behavior | Bounded reliability model | Pipeline-governance conflation: harness reproducibility consumed as evidence that governance is reliable; authority accrues to a property of the measurement tool, not the governed system |
| Persistence does not imply trustworthiness | No bounded reliability model; no reviewer calibration evidence; no semantic invariance proof | All three contracts | Osmosis-induced authority: stable signal consumed as warrant through reviewer familiarity; authority emerges without any contract, invisible to audit |
| Volume does not promote evidence layers | Layer promotion requires attribution contract + human sign-off; neither exists | Promotion protocol | Volume-laundering: accumulated weak evidence consumed as strong evidence; 18 observational_only runs treated as equivalent to 1 decision_relevant run |

**Causal-chain recoverability requirement:**

R50.5 must test whether a reviewer can reconstruct the complete chain — not just
the restriction, not just the causal basis, but the failure mode that makes the
restriction epistemically necessary rather than merely cautious.

Without failure-mode recoverability, "missing contract" becomes a ritual phrase.
With it, the restriction has teeth: the reviewer knows what breaks if they bypass it.

The osmosis guard requires that R50.5 tests **causal-chain recoverability**:
- what is prohibited
- why (causal basis)
- what contract is missing and why that contract matters
- what specific failure appears if the bypass occurs

A reviewer who can state the restriction but not the failure mode will not maintain
the restriction under pressure. The restriction will decay from
"epistemically necessary" to "just conservative" at the next context switch.

---

## Epistemic Layer Separation

This framework operates with three evidence layers. Each layer has explicit
consumption rules.

| Layer | Classification | What it permits | What it prohibits |
|---|---|---|---|
| `observational_only` | Observable signal | Record; surface in reports | Decision input; authority weight; causal attribution without MIP-02 |
| `historically_useful` | Retained signal | Archive; lineage reference | Inference; prediction; promotion; reuse as confidence basis |
| `decision_relevant` | Gated signal | Decision input after full attribution chain | Currently empty in R50 — no metrics qualify |

**Cross-layer rule:** A signal cannot move from a lower to a higher layer without:
1. A new attribution contract (e.g., completing R49.x-1 for MIP-02)
2. Human reviewer sign-off
3. Explicit re-classification record

Accumulation within a layer does not constitute movement between layers.
18 `observational_only` runs remain `observational_only`. They do not become
`historically_useful` or `decision_relevant` through volume alone.

---

## The Central Invariant

```
persistence ≠ trustworthiness
```

This is not a reminder. It is a semantic boundary.

The full chain that is prohibited:

```
signal is persistent
→ signal is stable
→ signal is reliable
→ signal is trustworthy
→ signal can carry decision weight
```

Each arrow in this chain requires a contract that does not currently exist:

| Step | Missing contract |
|---|---|
| persistent → reliable | bounded reliability model (absent) |
| reliable → trustworthy | reviewer calibration evidence (absent) |
| trustworthy → decision weight | semantic invariance proof (absent) |

Without these contracts, the chain cannot be traversed. The invariant blocks
traversal at the first step.

---

## What Accumulation IS Allowed To Mean

Accumulation in R50 is allowed to mean exactly one thing:

> "We have observed N runs. In M of those runs, signal S was non-zero.
>  This is a structural observation under fixed conditions.
>  M and N are counts. They have no authority weight.
>  They do not indicate trustworthiness.
>  They do not license any inference about future behavior."

---

## The Containment Test

At any point during R50, the following question should be answerable from ≤3 artifacts:

> "What has been observed, and what does it NOT authorize?"

If a reviewer cannot answer the second half — they have entered semantic osmosis territory.
R50.5 is the formal test of this.

---

## Exit Condition for This Contract

This contract remains in force until all three of the following exist:
1. A bounded reliability model (authored, human-reviewed, signed)
2. Reviewer calibration evidence (≥2 independent reviewers, documented)
3. A semantic invariance proof (connects persistence to a defined trust model)

None of these are in scope for R50. This contract does not expire within R50.
