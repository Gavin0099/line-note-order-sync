---
audience: agent-on-demand
authority: reference
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# REVIEW_CRITERIA.md

**Code Review and Audit Protocol - v1.3**

> **Version**: 1.3 | **Priority**: 3 (audit protocol)
>
> Defines how to audit, critique, and verify code changes.
> Load this document when `SCOPE = review`.

---

## 0. Activation

This document applies when `SCOPE = review`.

When active:

- keep a governance-first posture;
- act as a skeptical verifier, not an implementer;
- bind every finding to evidence, not intuition.

Before issuing findings, inspect the applicable prior-review surfaces for open
or unresolved items that may overlap the current review scope. At minimum, check
`memory/04_review_log.md` and `memory/03_knowledge_base.md` when they exist.
If this check is not possible, state that explicitly in the review inputs.

Before reviewing a change, identify the current owner decision, the change's
DONE condition, its claim ceiling, and the review boundary. The review boundary
is the changed surface plus the necessary semantic blast radius; it is not the
entire repository by default.

---

## 1. Review Philosophy

The purpose of review is to verify that the change is:

- predictable;
- safe;
- reviewable under governance.

Do not assume a small diff is safe.
Do not approve without naming the supporting evidence.

---

## 2. Verdict Model

| Verdict | Meaning | Use when |
|---|---|---|
| `APPROVED` | Safe enough to accept | No unresolved finding blocks the current owner decision |
| `CHANGES_REQUESTED` | Must be fixed | A clear blocking issue exists |
| `ESCALATED` | Requires human decision | Material risk or trade-off ambiguity remains after review |

A verdict is evidence-bound. `APPROVED` requires named evidence that no finding
materially blocks the current owner decision within the reviewed scope. If the review depends on missing
evidence, unresolved prior findings, or unreviewed dirty work, do not present
the verdict as clean approval; use `CHANGES_REQUESTED`, `ESCALATED`, or an
explicit `WARNING` as appropriate.

### 2.1 Finding Labels and Current-Decision Impact

Preserve the finding label or severity scale already used by the repository or
source review. This change does not migrate severity vocabulary or create a
second scale. The existing finding vocabulary remains:

| Level | Meaning |
|---|---|
| `BLOCKING` | A governance, correctness, or safety issue that must be fixed |
| `WARNING` | A risk, debt item, or weak evidence point that must be explicit |
| `SUGGESTION` | A non-blocking improvement |

These are source finding labels, not automatic answers to the current merge
decision. Preserve an external review's `P0`-`P3` labels when it uses them;
neither translate them into the table nor require existing reports to adopt them.
Keep a real finding's label unchanged when carrying it forward.

For each finding, report separately:

- finding label / severity: the original value and its source convention;
- attribution: introduced | worsened | exposed | pre-existing;
- current-decision impact: yes | no, with an evidence-backed reason;
- disposition: fix now | workaround | carried-forward | separate work.

`current-decision impact: yes` means the stated decision cannot proceed with
the finding unresolved. `no` means evidence supports proceeding at this decision
boundary with the finding and its disposition disclosed; it does not mean fixed,
absent, or harmless at another boundary. Unknown impact must be escalated, not
recorded as `no`. A source label of `BLOCKING` does not itself set this field.

Attribution alone also does not decide impact. A pre-existing finding still
blocks when the current change relies on the unsafe path, increases its exposure,
interacts with it materially, or relies on evidence that it invalidates.

Set current-decision impact to `yes` when any of these conditions holds:

1. the change introduces or materially worsens a concrete defect affecting
   correctness, safety, governance, or the stated claim boundary;
2. the finding invalidates the frozen DONE condition or claim ceiling;
3. the change enters, relies on, or materially increases exposure to the unsafe
   path;
4. the finding invalidates merge safety, relied-upon evidence or identity, or
   the safety of an irreversible state transition.

A workaround can remove blocking applicability only when the applicable owner or
governing authority accepts it and it already exists as reviewable evidence: it
is deterministic, bounded, replayable, fail-closed, and preserves the claim
ceiling. An intention that an operator will remember a step later is not a
workaround. Record the accepted evidence and why the impact is now `no`, while
retaining the finding label and workaround disposition. Merely assigning
`carried-forward` or `separate work` never clears an impact of `yes`.

Every real finding requires disposition, but a finding is not automatically a
new task. Non-blocking findings may be carried forward or assigned to separate
bounded work; they must not be represented as fixed or absent.

### 2.2 Delta-Bounded Re-Review

A fix commit makes approval of the prior HEAD stale, so the exact current HEAD
must still be reviewed. Re-review should converge by prioritizing:

1. whether prior blockers are resolved;
2. whether the correction delta introduces or worsens a blocker;
3. adjacent paths necessarily affected by the correction's semantic blast
   radius.

Expand beyond that boundary only when the claim ceiling expanded, the correction
changed a shared semantic choke point, or new evidence proves the prior boundary
was incomplete. A new HEAD does not by itself reopen subsystem qualification.

### 2.3 Engineering, Qualification, and Gate 3 Decisions

An Engineering Merge Gate asks whether the exact change can safely and honestly
satisfy its frozen DONE. It does not qualify the entire subsystem. A
Qualification Gate asks whether the named capability has the additional evidence
required for a formal qualification or GO claim.

Gate 3 applies the same finding logic separately at four decision boundaries:

1. Engineering Merge;
2. Bootstrap Readiness;
3. Execution Authorization;
4. Evidence / Result Acceptance.

Gate 3 workarounds must additionally be precommitted, arm-symmetric,
secret-independent, outcome-independent, Attempt-accounting preserving, and
replayable. Existing preregistered or frozen Gate 3 requirements remain minimum
conditions and cannot be weakened by this decision-bound model. Evaluate
current-decision impact separately at each boundary; a `no` at Engineering Merge
does not imply execution authority or result acceptance. Unrelated ancestry
movement alone need not invalidate qualification when all bound implementation
bytes, relevant transitive dependencies, shared semantic helpers, qualification
assumptions, and explicit head/ancestry bindings remain satisfied. Revalidate
the affected evidence when any of those changes; this is not permission to
discard an existing frozen binding.

### 2.4 Specification Review Stop Rule

A future-state concern does not block specification acceptance merely because it
could matter to an implementation path that does not yet exist. It remains
blocking when it makes the specification's DONE self-contradictory, makes the
next authorized implementation boundary unsafe or unimplementable, or freezes
an incorrect public contract. Other future concerns must be recorded as deferred
design questions rather than expanded into the current specification.

Do not confuse `ESCALATED` with an established current-decision impact of `yes`.
Escalation is for unresolved consequential ambiguity, not merely for defects.

---

## 3. Mandatory Audit Checklist

### 3.1 Boundary and Architecture

Check:

- whether domain code touches forbidden I/O, UI, OS, or native concerns;
- whether external or native model input uses an appropriate ACL boundary;
- whether the change conflicts with an ADR or boundary rule.

### 3.2 Physical and Native Safety

If native interop is involved, check:

- whether memory ownership is explicit;
- whether ABI layout is explicit when needed;
- whether panic / fail-fast and recoverable error handling are consistent.

If native interop is not involved, mark this section `N/A`.

### 3.3 Quality and Verification

Check:

- whether evidence matches task risk;
- whether failure paths were considered when applicable;
- whether validation locks observable behavior, not implementation trivia;
- whether legacy refactor work first verified baseline buildability.

### 3.4 Thread Safety and Async Safety

If UI or async paths are involved, check:

- whether UI-affecting updates stay on the correct thread;
- whether async failure paths are handled.

If this is not relevant, mark this section `N/A`.

### 3.5 Dirty Worktree and Scope Hygiene

If the worktree is dirty during implementation or review, check:

- whether unrelated dirty files were kept out of scope;
- whether touched-file overlap was handled or explicitly escalated;
- whether the commit and review boundary remains understandable.

---

## 4. Knowledge Base Cross-Check

Before issuing a verdict, check `memory/03_knowledge_base.md` for:

1. anti-pattern matches;
2. recorded regression patterns.

If a known anti-pattern reappears, call it out explicitly.

---

## 5. Legacy Refactor Review Addendum

For legacy repos, refactors, rollbacks, or baseline resets, also check:

- whether the claimed baseline was verified through the authoritative build path;
- whether the canonical toolchain was identified;
- whether the change is being presented as a safe refactor while the baseline is unstable.

If the baseline was not verified:

- do not call the result a clean refactor;
- include at least one `WARNING`;
- escalate when the conclusion depends on baseline stability.

---

## 6. Review Output Format

Every review response should include:

```markdown
### Review Inputs Checked
- governance/REVIEW_CRITERIA.md
- <list any additional documents read per REVIEW_CRITERIA.md conditions>

### [Decision Summary]
**Verdict**: APPROVED | CHANGES_REQUESTED | ESCALATED
**Risk Level**: Low | Medium | High

### Frozen Decision Boundary
- Current owner decision: ...
- DONE: ...
- Claim ceiling: ...
- Review boundary: ...

### Governance Audit
- Architecture: ...
- Native Safety: ... | N/A
- Test Integrity: ...
- Thread Safety: ... | N/A
- Baseline Status: Stable | Unverified | Unstable | N/A

### Technical Findings
1. [existing finding label / severity] Title
   - Label convention / source: ...
   - Location: `path:line`
   - Evidence: ...
   - Rule Reference: ...
   - Attribution: introduced | worsened | exposed | pre-existing
   - Current-decision impact: yes | no — evidence-backed reason
   - Status: open | resolved | carried-forward | not-reproduced
   - Disposition: fix now | workaround | carried-forward | separate work

### Knowledge Base Alignment
- Anti-patterns checked: N
- Regression notes checked: N
- Result: Pass | Conflict Found
```

Every non-trivial finding must include:

- location;
- evidence;
- rule reference.

Open findings must also include:

- status: `open` | `resolved` | `carried-forward` | `not-reproduced`;
- disposition: what was fixed, what remains, or why it is being carried forward.

The review output must separate findings resolved in the reviewed diff from
findings that remain open or are carried forward to a later slice. Do not hide
carried-forward findings inside a passing summary.

---

## 7. Post-Review Memory Actions

After issuing a verdict:

1. append the full review record to `memory/04_review_log.md`;
2. add a one-line summary to `memory/01_active_task.md`;
3. if a new anti-pattern was found, record it in `memory/03_knowledge_base.md`.

Keep `memory/01_active_task.md` concise. Do not dump full findings into it.

---

## 8. C++ Build Boundary Addendum

Apply this addendum whenever review touches C++ project files, header layout, or build configuration.

Hard checks:

- `AdditionalIncludeDirectories` or equivalent settings must not point to a peer project's private tree;
- cross-project private headers must not be justified merely because the build passes;
- shared headers must live in a shared boundary layer with clear ownership.

This is a boundary issue, not a style issue.

---

## 9. Final Principle

> A review that cannot name its evidence is not a valid review.
> Use escalation for conclusions that depend on ambiguity; use blocking findings for concrete violations.
