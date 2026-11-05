---
audience: agent-runtime
authority: reference
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# Response Envelope Contract v0.8

> v0.8 (2026-09-07): permits compact failed/partial and owner-decision reports
> when decision boundaries remain explicit; raw evidence stays canonical without
> mandatory human display. Diagnosis, review, and concept explanations retain
> their task-adaptive shape. No machine schema or execution authority change.

> v0.2 (2026-06-24): added the Evidence Term Glossing plain-language
> requirement (advisory; not validated by `response_envelope_validator.py`).
> v0.3 (2026-06-24): added the Next-Step Judgment required closing section
> (advisory; decision-readability for completion-class reports).
> v0.4 (2026-07-17): added an opt-in mechanical response-quality check to
> `response_envelope_validator.py` (`--check-response-quality`); default
> validator behavior is unchanged, and no gate enables the check.
> v0.5 (2026-07-18): added an opt-in plain-summary check
> (`--check-plain-summary`) after direct owner feedback that a
> structurally valid report was still unreadable; default behavior remains
> unchanged, and no gate enables either check.
> v0.6 (2026-07-22): after another real owner report was still too technical,
> made the owner-facing result / reason / next-step preface the literal first
> three non-empty lines and moved the audit ledger after it. Acceptance remains
> actual reader judgment; no validator, hook, CI, gate, or default behavior was
> added or changed.
> v0.7 (2026-08-04): separates the complete machine envelope from the default
> human rendering. Compact Chinese-first responses omit empty audit fields;
> forced expansion is limited to failed or partial work, an owner decision
> request, or an explicit full-evidence request. Dirty state, high-risk scope,
> and expressible limitations use one compact `注意：` line. Required machine
> fields and evidence semantics are unchanged; progress updates are governed by
> `AGENTS.md`.
> 2026-08-21 v0.7 clarification: adds task-adaptive Engineering Explanation
> semantics after repeated owner feedback that organized summaries could remain
> unclear or become clear by overstating evidence. The clarification is
> advisory and adds no validator, hook, CI, gate, schema, contract-version
> migration, or default enforcement.

## Purpose

This contract defines the minimum governance fields for structured agent
responses when a response is produced by a recognizable workflow event.

The goal is to keep task authority, scope, claim ceiling, evidence, and risk
disclosure separate enough that reviewers can audit what was done, what was
claimed, and what remains unproven without forcing every reader to decode the
full audit ledger. The machine envelope and the human response are different
surfaces: evidence remains complete even when the default human rendering is
compact.

## Rendering Modes

The complete machine envelope is the canonical record for validation, receipts,
and independent review. It must remain associated with the workflow event or
session that produced the response. A compact human response is only a
projection: it must never replace, mutate, or become the sole surviving copy of
the machine envelope. If the canonical record cannot be preserved, classify the
result as failed or partial and use expanded reporting.

The retained envelope must remain associated with the event or session that
produced it. A failed or ambiguous preservation check is part of the
`failed_or_partial` expanded path; it does not add a required envelope field.

The renderer may select, reorder, and translate existing envelope values. It
must not infer `verified`, `safe`, `no issues`, or equivalent trust claims from
an omitted warning, an empty display field, or a passing structural check. Every
human-facing claim must remain traceable to a named envelope value or an
explicitly identified human judgment. Such a judgment must already be recorded
as an input with its source and authority; the renderer may display or translate
it but may not create or upgrade it while rendering.

### Compact by default

For completion-class reports, including failed or partial work, use compact rendering when a
short answer preserves the blocker, ability to proceed, risks, non-claims, and
required owner decision or authorization. Select what affects the current
decision, not the full execution log. Use the current session language and the
existing three-line preface. Diagnosis, review, and concept requests instead
use Engineering Explanation; do not force an irrelevant next action:

```text
Result: <what is complete, incomplete, or blocked>
Reason: <the most important supporting result>
Next step: <one concrete next action, or a complete sentence saying none is needed>
```

Use translated labels in the session language. In Chinese, prefer:

```text
結果：<實際完成、未完成或受阻的成果>
原因：<最重要的支持結果>
下一步：<一個具體的下一步；沒有則用完整句子說明>
```

Compact requires an accurate `done` field, not a completed task, supporting
`evidence_refs`, traceable `task_authority`, `claim_ceiling`, and `next_action`,
plus the retained machine
record. Keep non-decision-relevant `not_claimed` data machine-side. Structural
`PASS` is not a semantic trust claim, and `Reason` must use existing evidence.

Dirty state, high-risk scope, or a decision-relevant limitation may add one
`注意：` line when that line preserves the claim boundary. If it cannot, use
`failed_or_partial` expanded reporting. Rendering metadata is optional and
must not become a required field or a new trust claim; `mode` and `mode_source`
remain event-derived.

### Expanded by trigger

Evaluate these stable trigger IDs without changing their machine meaning.
Failure or an owner decision alone does not force expanded human rendering;
apply the conditions below. Otherwise use compact rendering.
When more than one applies, the first row is the primary reason.

| Priority | Trigger ID | Source | Required response |
| --- | --- | --- | --- |
| 1 | `full_evidence_request` | explicit user request | Expanded report; state the request plainly. |
| 2 | `owner_decision_required` | current workflow decision context | Expand only when a short answer cannot preserve the choice, consequences, and required reply or authorization. |
| 3 | `failed_or_partial` | `done`, evidence, preservation, and rendering context | Expand when a short answer cannot preserve the blocker, ability to proceed, risks, non-claims, or authority boundary, or when the canonical record cannot be preserved. |

`failed_or_partial` still includes incomplete work and failed or unavailable
validation. Compact rendering never changes that status or authorizes progress.
Expand for conflicting evidence or decision boundaries that cannot be expressed
honestly in a short answer. An unavailable or ambiguously preserved canonical
record still requires expansion. Dirty state, high-risk scope, and expressible
limitations may remain compact. If compression hides a required decision,
changes a claim, or leaves the rendering condition ambiguous, expand.

F-7 terminal results remain a dedicated expanded-report exception. They must
relay the complete adoption summary required by `governance/F7_FULL_UPDATE.md`;
when that summary is unavailable, preserve the protocol's
`update_report_complete=false` and `completion_claim_allowed=false` fallback
instead of compressing the result into the ordinary compact projection.
This exception does not require a technical opening. Follow the plain-language
update opening in `governance/AI_GOVERNANCE_UPDATE_PROTOCOL.md`, then retain the
complete required adoption table and evidence in the same final report.
For these update reports, apply that protocol's deduplication and limitation
placement rules: do not add a second status list for facts already covered by
the opening/table; preserve all remaining required evidence and disclosures
after the table. This does not remove table rows, non-claims, or the existing
unavailable-summary fallback, and does not change other task classes.

Expanded output preserves every decision-relevant non-claim and the complete
machine field meanings. A `注意：` line may replace a visible `Cannot claim`
section only when it states the boundary honestly; it never removes machine
`not_claimed` data. When multiple ordinary triggers apply, report the primary
one first and each additional trigger once, preserving `evidence_refs` order.

### Language and terminology

Human-facing prose and labels use the current session language. In a Chinese
session, translate conceptual reporting terms such as ordinary expansion
policy（一般展開規則）、dirty state（工作樹未乾淨）、authority surface（治理或
權限面）、limitation（限制）、compact（精簡版）、progress update（進度更新）、
adoption summary（導入摘要）、fallback（退路）、scoped diff（本次範圍差異）
and diagnostics（靜態檢查）. Keep English only for an exact file path, command,
commit, API, schema field, or fixed machine token. Do not show an English
conceptual label and its translated duplicate in the same compact response.

When a trigger ID must be shown, gloss it on first use:
`full_evidence_request`（要求完整證據）、`owner_decision_required`（需要負責人
決定）、`failed_or_partial`（失敗或只完成一部分）. When another exact token is
shown, give its plain-language meaning once, for example: `PASS`（檢查通過）.

The machine envelope keeps canonical field names such as `claim_ceiling`,
`not_claimed`, and `evidence_refs`; human responses normally use 宣稱界線、
尚未確認的事項、 and 證據來源 instead. The human `下一步` or `Next step`
sentence is a plain-language projection of the machine `next_action` value,
not a second independently authored decision. The projection must preserve the
action's conditions, uncertainty, and scope; it may shorten wording but may not
add, remove, or upgrade an action. If `next_action` is absent, conditional in a
way that cannot be expressed plainly, stale, or contains multiple actions that
cannot be ordered unambiguously, use expanded reporting and state the ambiguity.
If a recommendation is needed, it must also be traceable to the envelope's
evidence and claim boundary.

For this rule, `next_action` is stale when it conflicts with the current scope,
status, evidence, or already-completed work. In expanded reporting, retain the
exact machine value or an unambiguous traceability reference beside the
translated projection.

A compact `next_action` must contain one ordered action that can be expressed as
an action, target, and any applicable condition without changing its meaning.
The existing value `none` is also valid when `done` is complete, no
decision-relevant item exists, and the envelope explicitly recommends no action;
render it as a complete sentence rather than the bare token. Multiple actions
are valid only when their order is explicit. An absent, stale, conditionally
incomplete, or unordered value forces expanded reporting.
The expanded traceability reference is the retained envelope's event or session
identifier plus the `next_action` field name; the exact machine value remains
available through that reference.

Prose and user-facing labels use the session language. Exact machine field
names may appear only as code literals, traceability references, or fixed tokens
that require exact comparison; do not expose them as a second translated label
in the compact response.

Keep the compact `注意：` line for one decision-relevant limitation only. Do
not put test commands, test counts, `git diff --check`, diagnostics, or general
work status in that line; keep those under a post-preface `驗證：` section or in
the machine `evidence_refs`. Render worktree status as `工作樹仍不乾淨` and add
the exact token only when needed: `NOT CLEAN`（工作樹不乾淨）.

Evidence commands in a human report must be runnable from the repository root;
retain the complete path such as `tests/test_response_envelope_validator.py`.
File references must use the actual workspace-relative path and verified
1-based line number; never invent or reuse a stale line reference.

### Progress updates

Progress-update content and frequency are governed by the always-loaded
`AGENTS.md` rule. This on-demand contract does not impose a hard maximum on
progress updates.

## Authority Boundary

This contract is a reporting convention and reviewer-facing schema.

It does not change:
- closeout runtime enforcement
- evidence admissibility rules
- claim ceiling semantics
- risk disclosure semantics
- session_end hook behavior
- gate policy behavior

## Event-Driven Mode Rule

`mode` must describe the workflow event that produced the response. It must not
be treated as an agent-selected style preference.

Every envelope that includes `mode` must also include `mode_source`.

Allowed initial mode mappings:

| Event | mode | mode_source |
| --- | --- | --- |
| session_end hook completed | `CLOSEOUT` | `session_end_hook` |
| in-progress status update | `PROGRESS` | `intermediate_update` |
| scoped files staged for commit | `PRE_COMMIT` | `git_staged_diff` |
| validation command completed | `VALIDATION` | `validation_command` |
| out-of-scope change detected | `SCOPE_ALERT` | `scope_boundary_check` |

Agents may fill the envelope content, but they must not choose a higher-authority
mode than the event source supports.

## Required Fields

Minimum response envelope:

```yaml
mode: CLOSEOUT
mode_source: session_end_hook
task: RS-Drift-2 presentation cleanup
task_authority: user_request
scope:
  - specs/verification_status.md
  - specs/en/verification_status.md
done:
  - packet statistics moved to Evidence Packet Summary section
claim_ceiling:
  - reporting convention documented only
  - no runtime enforcement claim
not_claimed:
  - new verified entries
  - generated statistics
  - governance cleanup
evidence_refs:
  - command: validate_wiki_frontmatter.py
    result: PASS
  - command: npm.cmd run build
    result: PASS
risk:
  - zh page incidental cleanup; existing mojibake text organized, no statistics semantic change claimed
next_action: scoped stage and commit, then review staged diff
```

Required field meanings:
- `mode`: event-derived response mode.
- `mode_source`: source event or command that justifies the mode.
- `task`: bounded task label or short task description.
- `task_authority`: source of authority for the task.
- `scope`: exact files, artifacts, or surfaces covered by the response.
- `done`: completed work inside scope.
- `claim_ceiling`: explicit upper bound on what the response is asserting.
- `not_claimed`: explicit claim ceiling for this response.
- `evidence_refs`: validation commands, artifacts, or reviewer sources supporting the `done` claim.
- `risk`: scope drift, incidental cleanup, claim inflation, or evidence maturity risks.
- `next_action`: one concrete next step, or `none` when no next action is being recommended.

## task_authority Values

Allowed values:
- `user_request`: explicitly requested or authorized by the user.
- `followup`: directly follows a previously authorized task without expanding scope.
- `hook_trigger`: produced by a workflow hook or runtime event.
- `autonomous`: initiated by the agent without direct user authorization.

If `task_authority: autonomous`, the response must include a `risk` entry that
explains why the work did not exceed the current DONE boundary.

## evidence_refs Rules

Each evidence reference must include:
- `command` or `artifact`
- `result`

Valid `result` values:
- `PASS`
- `FAIL`
- `NOT RUN`
- `NOT PRESENT`
- `NOT CLAIMED`

`PASS` must include a command, artifact, or source that can be independently
checked. Bare `PASS` is not valid.

`evidence_refs` does not upgrade semantic authority. It records what evidence
exists for the stated claim ceiling.

## Claim Ceiling Preservation

`done`, `claim_ceiling`, and `not_claimed` must remain separate.

Do not merge unverified implications into `done`. If a capability was not
validated, proven, or authorized in the current scope:
- state the positive boundary under `claim_ceiling`
- list the non-asserted items under `not_claimed`
- keep the existing completion report `Cannot claim this session` section when
  using the longer Rule 7 report

## Risk Disclosure Preservation

The `risk` field is required because incidental work is otherwise easy to hide
inside narrative prose.

Risk entries should disclose:
- incidental cleanup
- scope drift
- claim inflation
- evidence maturity limits
- autonomous work boundary concerns

Do not replace `risk` with confidence scores, effort estimates, or broad impact
analysis.

## Engineering Explanation (Evidence-Preserving Interpretation)

An owner-facing explanation must do more than reorder or translate the source
report. Explanation is context reconstruction: it restores the minimum context
that a technically capable reader did not observe while the agent was working.
Assume that reader understands software engineering but has not followed this
session.

The explanation must establish, without requiring the reader to open `PLAN.md`
or decode project vocabulary:

1. **Context:** what problem or goal was being worked on;
2. **Event:** what actually happened;
3. **Meaning:** why those facts support the stated result, including the event
   sequence or evidentiary relationship without inventing causation; and
4. **Consequence:** what this changes, or does not change, for the original
   goal.

Then state any decision-relevant unknown, authority boundary, or candidate next
action. Include a next action only when the question or current state calls for
one; naming an action never grants permission. Preserve decisive technical
evidence in the canonical record; display it after the explanation only when
needed for the current decision or requested by the owner.

Before writing the explanation, separate the source into five classes:

| Class | Meaning | Required treatment |
|---|---|---|
| Observed fact | Directly supported by a command, artifact, source, or owner decision | State plainly; preserve the exact limiting evidence when decision-relevant. |
| Supported interpretation | Meaning reasonably derived from observed facts | Explain the reasoning; do not call it directly measured. |
| Hypothesis | Plausible cause or future expectation not yet confirmed | Label it as possible and state the missing check. |
| Authority state | What the owner or governing source approved, rejected, paused, or left undecided | Do not promote a proposal, recommendation, or question into a decision. |
| Next action | When action is relevant, the narrow candidate next step and its current authority state | Say whether it is authorized now or still needs owner approval; naming it never grants permission. |

Choose the smallest explanation shape that matches the question:

- **Progress or status:** say what is usable, what is complete, what is blocked
  or unapproved, and what happens next. Do not invent a completion percentage
  from milestone names.
- **Diagnosis:** reconstruct the event order and actors. State what each
  decisive event means. Keep confirmed cause, likely cause, and hypothesis
  separate; timing alone does not prove causation.
- **Review or audit:** lead with what remains trustworthy, what central claim
  does not hold, and how that changes the decision. Reviewer recommendations do
  not become owner rulings.
- **Metrics or portfolio analysis:** explain the operational meaning and the
  measurement boundary. Do not convert commit share into time or cost,
  repository count into independent-user count, or path touch into decision
  effect.
- **Concept or purpose:** explain the problem being solved, how the mechanism
  addresses it, how it differs from nearby mechanisms, and what success would
  mean. Do not append an artificial next action when the owner only asked what
  something means.

Do not use a project code, status token, evidence field, or protocol term as the
explanation itself. On first use, explain what each decision-relevant term does
in this task. A glossary-style translation without the relationship between
events is still not an explanation.

The main responding agent owns the final owner-facing explanation. Subagent
findings may stay technical, but they must preserve facts, evidence,
uncertainty, and authority well enough that the main agent does not invent
missing meaning.

Before sending, first verify that a cold reader can answer:

1. What problem was being worked on?
2. What actually happened?
3. Why do the facts support this result?
4. What does the result mean for the original goal?
5. What remains unknown, and what action or authority state matters now?

Then check:

1. Did the answer explain the result, or only reorganize the source?
2. Did it add causation, certainty, measured effect, or authority not present in
   the evidence?
3. Did it turn a recommendation into a decision or an unapproved follow-up into
   a promised action?
4. Did simplification remove an exact value, condition, provenance, risk, or
   `not_claimed` boundary?
5. Did the answer make the reader look up `PLAN.md`, an artifact, or an
   unexplained project or protocol term to build the minimum mental model?

A factually correct answer is still a failed explanation when it merely
translates tokens, restates status, or leaves the reader to infer why the facts
matter. A clear answer that changes fidelity or authority is also a failed
explanation.
These rules are advisory reviewer-facing behavior. Human comprehension remains
the acceptance signal; no semantic scoring or automatic enforcement is implied.

## Evidence Term Glossing (Plain-Language Requirement)

When a report surfaces machine or governance field tokens — for example
`active_non_canonical_writer=0`, `completion_claim_allowed=True`,
`plan_reconciliation: deferred:<reason>`, guard counts, or any
identifier-shaped audit field — each surfaced token must be paired with a
one-line plain-language meaning in the session language.

Rules:
- Preserve all raw fields in canonical machine records / evidence for independent
  recheck. Compact prose must never replace or erase that evidence.
- Explaining a displayed token does not require displaying every token. Show an
  exact token by default only when its value affects the current decision or
  claim boundary, or full evidence is requested. Otherwise express the relevant
  meaning in plain language and retain the raw field in the canonical record.
- Lead with what the result means for the owner and whether action is needed.
  Display selected technical fields with glosses only when needed; do not append
  the audit ledger merely because work failed or is partial.
- Separate this-session counts from pre-existing or historical counts. When a
  count predates the current change (for example a historical
  `non_canonical_writer` total), say so explicitly so it is not misread as
  caused this session.
- When displayed, fixed-vocabulary tokens (`PASS`, `FAIL`, `NOT RUN`, `NOT CLAIMED`,
  `NOT PRESENT`) and field identifiers remain as written; the gloss is added in
  the session language, consistent with the Result-First Final Report Format
  rule.

Completion-report summary structure (refined 2026-07-22 after a third observed
comprehension failure: the report preserved its claim boundary but still made
the owner decode technical state before learning what to do):

- For completion and partial-completion reports, the first three non-empty lines
  must be, in the session language and in this order: `Result: ...`,
  `Reason: ...`, `Next step: ...` (or translated labels such as `結果：...`,
  `原因：...`, `下一步：...`).
- Put no heading, table, preamble, work-item code, commit hash, command, raw
  governance field, or fixed-vocabulary verdict before those three lines.
- Each line must stand alone as a plain sentence. Do not make the reader follow
  a reference such as "as above", "see evidence", or an unexplained code to
  understand the answer.
- The result says whether the requested outcome is usable now. The reason says
  the one decisive fact that makes that result credible. The next step says one
  concrete owner or agent action; if no action is needed, say that in a full
  sentence.
- If technical evidence is displayed, place it after the three-line preface.
  Preserve complete raw evidence, claim ceilings, risks, and non-claims in the
  canonical record; compact human replies need not reproduce the audit ledger.
- Prefer a short table of "problem found → what was changed" over narrative
  paragraphs when reporting multi-step work.
- When the owner must decide something, list each decision as a numbered
  question and state what reply closes it (for example: "回『可以』即完成").
- Any work-item code (P1-C, F-7, E2, census unit names) gets its
  plain-language purpose on first use in the report; the PLAN Work Item
  Glossary is the source.
- Method self-commentary (process praise, cadence narration) goes last or is
  omitted; it must never displace the decision questions.

For diagnosis, review, or concept questions, use the task-adaptive Engineering
Explanation shape instead of forcing an irrelevant next step. Acceptance is the
owner's actual reading judgment: a technically capable cold reader can build
the correct minimum mental model without decoding the technical section or
asking a second model to translate it. The opt-in
`response_envelope_validator.py --check-plain-summary` remains only a
sentence/ordering proxy for structured envelopes; it does not verify the
rendered first-three-line placement or human comprehension.

Authority boundary: this is an advisory reviewer-facing convention. No hook,
CI job, gate, or default validator invocation blocks a report that omits it. A
report from an agent that does not load this contract will not follow it. This
requirement reduces reviewer decoding burden; it is not mechanically enforced.
Repositories that adopt and load this framework contract can use the same
reporting rules; adoption alone does not guarantee application.

## Next-Step Judgment (Required Decision Content)

A completion report exists so a human can decide the next step, not as an
archive. Reports for completion-class tasks (governance checks, code changes,
validation, memory / provenance, commit / push, handoff / reviewer summary)
must contain the following decision content. Its result, reason, and next action
lead the report in the three-line preface; technical support and non-claims may
follow in the audit ledger:

- `status`: done / partially done / not done
- `basis to trust`: which tests, commits, or artifacts support the status
- `recommended action`: exactly one of — can merge / needs review / needs more
  validation / do not touch yet — with a one-line reason
- `cannot claim`: which conclusions still cannot be asserted

This section answers the three questions a reader needs in order to act: Is it
done? Why should I believe it? How do I decide what to do next? It complements
`claim_ceiling` and `not_claimed` (which bound what is asserted) by stating the
recommended decision, not just the evidence.

The purpose is decision readability, not formality. Do not replace the plain
recommended action with a wall of fields; the reader must be able to tell the
next move at a glance.

Authority boundary: advisory, same as the rest of this contract. No gate
enforces the presence or shape of a Next-Step Judgment.

## Opt-In Mechanical Response-Quality Check (v0.4)

`response_envelope_validator.py --check-response-quality` adds a structural
check for the plain-language reporting posture above. It is off by default;
without the flag the validator's behavior, output shape, and exit codes are
unchanged.

When enabled, an envelope must additionally contain each of these field
labels exactly once. Label, value, and position are bound to the same field
occurrence, so a duplicate label after `evidence_refs` cannot satisfy an
empty label before it:

- `conclusion`: the plain-language conclusion (maps to the "open with one
  plain sentence" rule).
- `recommended_action`: the recommended decision (maps to the Next-Step
  Judgment `recommended action`).
- `next_action`: one concrete next step, or `none`.

Checks performed (error codes):

- `quality_missing_field`: a quality field label is absent.
- `quality_duplicate_field`: a quality field label appears more than once;
  duplicates are rejected rather than merged.
- `quality_empty_field`: a quality field has no content or placeholder content
  (`tbd`, `n/a`, `see above`, or `none` — except `next_action`, where `none`
  is an allowed explicit value). Leading list markers (`- `) are stripped
  before this check, so `- TBD` is still placeholder content.
- `quality_field_after_evidence`: a quality field appears after
  `evidence_refs`, violating conclusion-before-technical-evidence ordering.

Boundaries:

- The check is label/position structural only. It cannot judge whether the
  content is actually plain language, whether the recommended action uses the
  advisory vocabulary (can merge / needs review / needs more validation / do
  not touch yet), or whether the conclusion is true. Those remain advisory
  and human-reviewed.
- Evidence Term Glossing and the summary structure rules above remain
  advisory and are still not validated.
- No hook, CI job, gate, or default invocation enables this flag; enabling it
  anywhere is a separate, owner-authorized change.

## Opt-In Plain-Summary Check (v0.5)

`response_envelope_validator.py --check-plain-summary` targets the reader
acceptance test behind this contract: within the first few lines a reader
must be able to answer three questions — can we act now, why, and what is
the next step. It was added after an observed failure: a report passed the
v0.4 structural check yet the owner could not act on it without a rewrite.

When enabled, an envelope must contain each of `conclusion`, `reason`, and
`next_action` exactly once, before `evidence_refs`, and each value must read
as a sentence rather than a bare verdict word.

Checks performed (error codes):

- `plain_summary_missing_field` / `plain_summary_duplicate_field` /
  `plain_summary_empty_field` / `plain_summary_field_after_evidence`: same
  occurrence-bound structure rules as the v0.4 quality check, applied to
  `conclusion`, `reason`, `next_action`.
- `plain_summary_token_without_gloss`: the value contains fixed-vocabulary
  machine tokens (`APPROVED`, `CHANGES_REQUESTED`, `PASS`, `FAIL`,
  `needs review`, `can merge`, `none`, ...) but no accompanying prose. A
  token is acceptable only next to a plain-language gloss in the same field
  (for example `needs review — 驗證器變更需人工確認後才能合併`).
- `plain_summary_not_prose`: the value has no machine token but fewer than 6
  letters/digits/CJK characters — too short to be a sentence.

Divergence from the v0.4 quality check: `next_action: none` is NOT accepted
here. An explicit no-action must be written as a sentence.

Honest boundary (do not inflate this check):

- This is a structural proxy. It can verify that sentence-shaped conclusion,
  reason, and next-step fields exist before the technical detail; it cannot
  verify that a human actually understands them. A jargon-dense value with
  enough characters will pass. Validation raises the probability of a
  readable report; it does not prove readability. The real success signal
  remains direct reader feedback.
- v0.6 does not expand this check to police rendered line numbers. The contract
  requires a literal three-line owner preface, while this opt-in validator keeps
  its existing structured-envelope scope.
- No semantic scoring, no AI judgment, no readability metrics.
- No hook, CI job, gate, or default invocation enables this flag; enabling
  it anywhere is a separate, owner-authorized change.

## Non-Goals

This contract intentionally does not add:
- confidence scores
- effort estimates
- generic impact analysis
- new runtime gates
- automatic semantic verification
- automatic mode inference beyond the listed event mappings
- automatic plain-language gloss validation or enforcement

## Relationship To Existing Rule 7 Reports

The existing result-first completion report remains valid.

Use this envelope when a compact event-driven response is needed, or when a
tooling layer needs structured fields before rendering the existing completion
report.

The envelope must preserve the same claim discipline as Rule 7:
- `NOT CLAIMED` means the capability or conclusion is not asserted.
- `NOT PRESENT` means the mechanism, artifact, or enforcement does not exist.
- `PASS` must reference a command or source.

## Result-First Final Report Format

Final reports should be result-first, not process-first. The first three
non-empty lines are the owner-facing preface. For expanded rendering, a blank
line and the technical ledger follow; the ledger must not interrupt the preface.
The formats and golden examples below show expanded reports, not mandatory
technical sections for compact replies. Compact replies retain the complete
canonical record and all decision-relevant meaning under Rendering Modes.

Content language must match the session language. Sub-field labels
(`structural`, `build`, `semantic`, `behavioral`, `ext evidence`, `scope drift`,
`claim inflation`, `evidence maturity`) and fixed vocabulary tokens (`PASS`,
`FAIL`, `NOT RUN`, `NOT CLAIMED`, `NOT PRESENT`) remain in English. Section
headers may be translated.

English session format:

```text
Result: <plain sentence saying whether the requested outcome is usable now>.
Reason: <plain sentence naming the decisive fact>.
Next step: <one concrete action, or a full sentence saying no action is needed>.

Technical evidence:
1. Capability increased:
2. Changed files:
3. Validation:
   - structural:    PASS — <command> | FAIL — <command> | NOT RUN
   - build:         PASS — <command> | FAIL — <command> | NOT RUN
   - semantic:      NOT CLAIMED | PASS — human review: [reviewer/date]
   - behavioral:    NOT PRESENT | verified — [how]
   - ext evidence:  NOT PRESENT | [source and scope]
4. Risk:
   - scope drift:        none | [description]
   - claim inflation:    none | [description]
   - evidence maturity:  [one line]
5. Incidental cleanup:   none | file=[path] reason=[why] semantic_change=no
6. Governance surface change: none / list
7. Remaining blocker:
8. Cannot claim this session:
   - [list what was NOT validated, NOT verified, NOT proven — required, never omit]
```

Chinese session format:

```text
結果：<用一句白話說明要求的成果現在是否可用>。
原因：<用一句白話說明最關鍵的可信依據>。
下一步：<一個具體行動；若不需行動，也要寫成完整句子>。

技術證據：
1. 能力提升：
2. 變更檔案：
3. 驗證：
   - structural:    PASS — <指令> | FAIL — <指令> | NOT RUN
   - build:         PASS — <指令> | FAIL — <指令> | NOT RUN
   - semantic:      NOT CLAIMED | PASS — 人工審查：[審查者/日期]
   - behavioral:    NOT PRESENT | 已驗證 — [如何]
   - ext evidence:  NOT PRESENT | [來源與範圍]
4. 風險：
   - scope drift:        none | [說明]
   - claim inflation:    none | [說明]
   - evidence maturity:  [一行說明]
5. 附帶清理：   none | file=[路徑] reason=[原因] semantic_change=no
6. Governance surface 變更：none / 列舉
7. 剩餘阻擋：
8. 本次無法宣告：
   - [列出未驗證、未確認、未證明的項目 — 必填，不得省略]
```

## Golden Examples

Schema-only change:

```text
Result: The requested schema field is added and the scoped file is ready for review.
Reason: The structural validator found the new field and returned successfully.
Next step: Review the scoped diff before committing it.

Technical evidence:
1. Capability increased: section_refs schema extended
2. Changed files: wiki/port-status.md
3. Validation:
   - structural:    PASS — grep section_refs wiki/port-status.md
   - build:         NOT RUN — markdown-only change
   - semantic:      NOT CLAIMED
   - behavioral:    NOT PRESENT
   - ext evidence:  NOT PRESENT
4. Risk:
   - scope drift:        none
   - claim inflation:    none
   - evidence maturity:  structural layer only; no semantic verification
5. Incidental cleanup:   none
6. Governance surface change: none
7. Remaining blocker:     none
8. Cannot claim this session:
   - semantic correctness of section references
   - PDF-level content verification
```

Pilot attachment change:

```text
Result: Four existing port entries now include the requested references and are ready for review.
Reason: The frontmatter validator and project build both completed successfully.
Next step: Review the four-entry pilot before expanding coverage.

Technical evidence:
1. Capability increased: 4 port entries have section_refs attached
2. Changed files: wiki/port-status.md, wiki/zh/port-status.md
3. Validation:
   - structural:    PASS — validate_wiki_frontmatter (exit 0)
   - build:         PASS — npm run build (exit 0)
   - semantic:      NOT CLAIMED
   - behavioral:    NOT PRESENT
   - ext evidence:  NOT PRESENT
4. Risk:
   - scope drift:        none — pilot limited to 4 existing entries
   - claim inflation:    none — claim_level unchanged (inferred)
   - evidence maturity:  build-verified only; high-risk coverage below original plan
5. Incidental cleanup:   none
6. Governance surface change: none
7. Remaining blocker:     PORT_OVER_CURRENT not in pilot — high-risk coverage gap
8. Cannot claim this session:
   - bit-level semantic verification of attached spec sections
   - high-risk boundary condition coverage (PORT_OVER_CURRENT not in pilot)
   - verified status upgrade
```

Failed or partial validation:

```text
Result: The change is not ready because the project does not build.
Reason: The structural check passed, but the build command returned an error.
Next step: Fix the build error before committing the change.

Technical evidence:
1. Capability increased: none
2. Changed files: wiki/port-status.md (uncommitted)
3. Validation:
   - structural:    PASS — validate_wiki_frontmatter (exit 0)
   - build:         FAIL — npm run build (exit 1, error above)
   - semantic:      NOT CLAIMED
   - behavioral:    NOT PRESENT
   - ext evidence:  NOT PRESENT
4. Risk:
   - scope drift:        none
   - claim inflation:    none — task not complete
   - evidence maturity:  build failure; no completion evidence
5. Incidental cleanup:   none
6. Governance surface change: none
7. Remaining blocker:     build error must be resolved before commit
8. Cannot claim this session:
   - task complete
   - any validation above build layer
```
