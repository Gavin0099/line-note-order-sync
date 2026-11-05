# AGENTS.base.md
<!-- governance-baseline: protected -->
<!-- baseline_version: 1.0.0 -->
<!-- DO NOT EDIT — managed by ai-governance-framework -->
<!-- To add repo-specific rules, create AGENTS.md and extend this file's sections. -->
<!-- Hash is recorded in .governance/baseline.yaml and verified on every drift check. -->

## Level Alignment

- Declared L0 but involves domain logic, boundary crossing, or behavior change → upgrade to L1
- Declared L1 but involves core domain, security, data integrity, or irreversible state → upgrade to L2
- Uncertain classification → upgrade, do not downgrade

## Execution Pipeline

For L1+, the default workflow is:

1. **Analyze** — understand behavior and constraints before touching code
2. **Define** — contracts, boundaries, failure paths
3. **Verify Plan** — what evidence will prove the change is safe
4. **Implement** — minimum compliant change
5. **Refactor** — only under evidence protection

Do not skip a step when the omission would hide risk.

## Forbidden Behaviors

- Expand scope beyond what was explicitly instructed
- Refactor unrelated areas for cleanliness or taste
- Add speculative abstractions for hypothetical future requirements
- Fake, inflate, or omit evidence
- Assume intent when the instruction is ambiguous — ask instead

## Secret Handling

- Never commit tokens, API keys, credentials, or secrets to the repo
- Never write tokens or credentials into memory/ files or logs
- If a secret appears in conversation context, do not persist it anywhere
- `.env` files and credentials must be in `.gitignore` and never staged

## AI Governance Update Routing

When the user says "幫我更新最新版 AI Governance" or uses equivalent update
wording, route the request to `governance_tools.f7_full_update` even if F-7 was
not named explicitly. The governed updater is an F-7 backend, not the complete
update-report surface.

For updated, already-current, blocked, and fallback/manual terminal results,
relay the complete `[human_readable_adoption_summary]` table when available.
If it is unavailable or omitted, report
`human_readable_adoption_summary: NOT REPORTED`,
`update_report_complete=false`, and `completion_claim_allowed=false`; do not
claim a complete AI Governance update report.

## Memory Update Triggers

The following events require updating PLAN.md and/or the relevant memory/ file.
These updates are part of the delivery that produced the event, not extra work
after DONE; do not record micro-steps or duplicate a record. Targets follow
`governance/SYSTEM_PROMPT.md` section 6.1 and match `governance/AGENT_CORE_RULES.md`.

| Event | Required update |
|-------|----------------|
| Milestone reached | `memory/01_active_task.md`; PLAN.md phase/sprint only when the milestone changes PLAN phase, scope, anti-goal or another existing PLAN obligation |
| Architecture decision made | `memory/02_workflow.md`; PLAN.md only when the decision changes PLAN scope, phase, anti-goal or another existing PLAN obligation |
| Bug fixed with root cause identified (new gotcha / solution) | `memory/03_knowledge_base.md` as a `CANDIDATE / UNREVIEWED` entry (root cause, fix, fix commit, test evidence) paired with a `memory_record` daily record for the same fix commit; never marked approved, reviewed only through promotion |
| Review completed | full record in `memory/04_review_log.md` + one-line summary in `memory/01_active_task.md` |
| Risk or incident encountered | PLAN.md risk section + `memory/01_active_task.md` |
| Session end | canonical `memory/YYYY-MM-DD.md` record when closeout is non-stateless |

Use the `memory/02_project_facts.md`, `memory/03_decisions.md` or
`memory/04_validation_log.md` alias only when this repository has adopted the
section 6.1 alias schema; never assume an alias that does not exist.
Repository-specific record duties in `AGENTS.md` still apply.

Automatic closeout has one write boundary: `session_end` may append the daily
canonical record through `governance_tools.memory_record`. Pre-commit and
`memory_workflow` only inspect or validate memory state; they do not write it.
`memory/01_active_task.md`, `memory/03_knowledge_base.md`, and `PLAN.md` remain
milestone, decision, or human-curation surfaces and are not rewritten after
every session.

When an implementation requires a canonical closeout companion, keep the
implementation and closeout as separate commits on the same branch and in one
pull request by default. A successful merge, push, or remote verification is
delivery evidence only; it must not create another memory commit or second pull
request. Open a follow-up slice only for a new defect, omitted required
governance state, or explicit owner authorization.

## Engineering Explanation

Whenever the main agent reports status, review, diagnosis, or completion, or
the owner asks for a plain explanation, the main agent must explain the
engineering meaning before the technical ledger. Reordering the same fields
under new headings is not enough.

Canonical source: `governance/RESPONSE_ENVELOPE_CONTRACT.md`, section
`Engineering Explanation (Evidence-Preserving Interpretation)`. This section is
the minimum fallback when that canonical contract is not loaded.

- Separate observed fact, supported interpretation, hypothesis, authority
  state, and next action.
- Assume the reader is a senior engineer who understands software engineering
  but has not followed this session. Reconstruct the minimum missing context:
  the original problem, what happened, why the facts support this result, and
  what the result changes or does not change for the goal. Use the event
  sequence or evidentiary relationship; do not invent causation.
- Do not use project codes, status tokens, evidence fields, or protocol terms as
  the explanation itself. Explain each decision-relevant term on first use and
  connect the events; translation without relationships is not explanation.
- Preserve exact numbers, commands, paths, identifiers, conditions, evidence,
  and `not_claimed` boundaries when they limit the conclusion.
- Do not turn correlation into causation, a proxy into measured effect, a
  recommendation into an owner decision, or an unapproved follow-up into a
  promised action.
- Use the task's natural shape: timeline for diagnosis; completed / blocked /
  next for progress; trustworthy / unsupported / decision impact for review;
  problem / mechanism / difference / success meaning for concept questions.
- Include a next action only when it is relevant. Naming a candidate action does
  not authorize it.
- A clear answer that changes evidence or authority is a failed explanation.

This is an owner-facing reporting rule, not a semantic gate. Human
comprehension remains the acceptance signal.

## Session Closeout Obligation

Writing `artifacts/session-closeout.txt` before session end is a **governance
obligation**, not a suggestion.

Where a governed lifecycle hook is wired, the harness calls `session_end` on that
hook's event; Session-End Closeout Responsibility below defines when session end
applies and what to do without such a hook. If the closeout artifact
is missing or insufficient, the runtime records `closeout_missing` or
`closeout_insufficient` in the verdict and writes a fail-closed canonical daily
record when the session is non-stateless. The invalid closeout content is not
promoted. The gap remains auditable and visible to reviewers.

<!-- ai-governance:session-end-closeout BEGIN version=1 canonical=AGENTS.base.md -->
### Session-End Closeout Responsibility

These rules apply to every agent platform (Codex, Claude, Copilot and others).
They define when closeout is required, who is responsible, and what may be
claimed. They do not define which lifecycle event a platform uses; that is
platform-specific and must be qualified separately for each platform.

1. **Task DONE is not session end.** Finishing a task, a review, or a milestone
   ends that task only. Report DONE, do not expand the work, and leave the
   session open for the next request.
2. **Closeout at a defined session end is a duty, not new work.** A mandatory
   closeout at session end is not scope expansion. Hard Stop After DONE forbids
   closeout after task DONE; it does not forbid closeout at session end.
3. **Session end must come from a defined, observable source.** Only two sources
   count: a platform lifecycle event whose session-end meaning has been
   confirmed for that platform, or the user explicitly asking to end the session
   or to close out. The agent must not infer that the conversation is over. A
   final answer, a DONE report, or a per-turn `Stop` event is not session end
   unless that meaning has been confirmed.
4. **Governed lifecycle hook present:** the harness is responsible for
   triggering canonical closeout. A governed hook is one wired to the governance
   closeout entry and confirmed to run for this platform.
5. **No usable governed hook:** only when session end is established under
   rule 3, the top-level agent must attempt the existing manual closeout
   (`python -m governance_tools.manage_agent_closeout print-manual --agent <agent>`
   prints the command). If it cannot run or its result cannot be verified,
   report closeout as `NOT PERSISTED` or `UNKNOWN`; never claim it was persisted.
6. **Subagent completion is not project-level session end.** A subagent
   returning to its parent must not run project-level closeout unless it has its
   own governed session identity and was explicitly given closeout
   responsibility.

A closeout, including the manual fallback, does not authorize commit, push,
pull request, or a new task; each still needs its own explicit authorization.

Closeout candidate, canonical record, and memory are verified separately. A
successful closeout on one platform is not evidence for any other platform.
<!-- ai-governance:session-end-closeout END -->

### Required fields

All fields must be present. Vague values are flagged as insufficient.

```
TASK_INTENT: <one sentence — declared goal of this session>
WORK_COMPLETED: <what was actually done — verifiable claims only>
FILES_TOUCHED: <comma-separated file list, or NONE>
CHECKS_RUN: <specific commands or checks run, or NONE>
OPEN_RISKS: <what might be wrong or incomplete, or NONE>
NOT_DONE: <what was not completed this session, or NONE>
RECOMMENDED_MEMORY_UPDATE: <what memory/ file should change and why, or NO_UPDATE>
```

### Rules

- `WORK_COMPLETED` must contain verifiable claims. Do not write "made improvements"
  or "worked on things" — these are vague and will be rejected as insufficient.
- `CHECKS_RUN` must name specific commands if non-`NONE`.
- If there was no material progress, write `WORK_COMPLETED: NONE` — do not
  fabricate completions.
- `NOT_DONE` and `OPEN_RISKS` are the most important fields. AI agents tend to
  omit failures. Do not.

### If you cannot write the closeout

Write it anyway with `WORK_COMPLETED: NONE` and explain in `OPEN_RISKS` why
the session produced no verifiable output. This is a valid closeout.

See `docs/session-closeout-schema.md` for examples and field constraints.

## Definition of Done

A task is done when:

- Behavior is explicit and observable
- Failure paths are guarded
- Architecture boundaries remain intact
- Evidence matches the declared risk level
- PLAN.md and memory/ updates required by the Memory Update Triggers above are
  included in this delivery; after DONE, add no unrelated rollups or new PRs
