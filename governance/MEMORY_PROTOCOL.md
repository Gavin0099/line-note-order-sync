---
audience: agent-runtime
authority: canonical
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

<!-- mrcsp_activation_id: mrcsp-m1-authority-reader-v1 -->

# Memory Protocol

Status: extracted from AGENTS.md
Semantic change: no
Runtime behavior change: no
Enforcement change: no

## Purpose

This protocol defines repo-local memory authority, canonical memory writing,
delivery and closeout memory, PLAN sync, and memory interpretation rules.

## Memory Surfaces

You wake up fresh each session. These files are continuity:
- Daily notes: `memory/YYYY-MM-DD.md` (create `memory/` if needed).
- Long-term memory: `memory/00_long_term.md`.

Capture decisions, durable context, and lessons. Skip secrets unless the user
explicitly asks to keep them.

### Storage, Writer, And Authority Are Separate

The following terms must not be collapsed:

- `canonical storage` names the required repository location;
- `canonical writer` names the required record-production path and format;
- `canonical_record` means the record satisfies those storage and writer
  requirements;
- `authority_class` identifies which class of question a source is qualified to
  answer;
- `projection_status` identifies `current`, `historical`, `superseded`, or
  `candidate` interpretation;
- `review_status` identifies `reviewed`, `unreviewed`, or `disputed` state.

A `canonical_record` is event/provenance evidence. It is not automatically an
authoritative current-state projection. Detailed surface roles and
question-specific reader rules are defined in
`governance/MEMORY_SURFACE_AUTHORITY_CONTRACT.md`.

The MRCSP M-1 authority model activates only through an authorized review and
merge that contains the matching `AUTHORITY.md`, `MEMORY_PROTOCOL.md`,
`MEMORY_AUTHORITY_CONTRACT.md`, and
`MEMORY_SURFACE_AUTHORITY_CONTRACT.md` changes. No single file activates it.
M-1 activation does not authorize M0: fixture admissibility and fixture creation
require a separate owner-authorized tranche.

## Cross-Agent Memory Channel

- Shared memory for all agents in this workspace must live under this repo's
  `memory/` directory.
- `memory/00_long_term.md` is the canonical storage path for long-term
  cross-agent memory in main sessions. File placement does not make every
  section normative authority; section-level promotion and review still apply.
- External/private tool memory paths are not cross-agent authority and must not
  be cited as repo governance state.
- If important context exists only in an external/private memory file, copy a
  distilled version into `memory/YYYY-MM-DD.md` and/or `memory/00_long_term.md`
  before using it for repo decisions.

## Long-Term Memory

- Load `memory/00_long_term.md` only in main sessions with the user.
- Do not load it in shared contexts.
- It can contain personal context and must not leak to strangers.
- In main sessions, it may be read, edited, and updated when durable context
  should persist.

## Write It Down

- Memory does not survive as "mental notes"; durable context must be written.
- In a governed repository, an ambiguous request to "record this in memory" or
  "remember this" defaults to the repository's canonical memory workflow when
  the content concerns that repository's task state, decisions, evidence,
  closeout, or durable governance knowledge.
- If the content is a personal preference, reminder, cross-repo habit, or
  private-cache pointer, classify that route explicitly before writing. Do not
  treat private/tool memory as governance authority.
- When repository memory is the correct route, write session-derived records
  (`memory/YYYY-MM-DD.md`, review log, active-task summary) through the
  canonical writer. A knowledge-base gotcha follows the Knowledge-Base
  Candidate Rule below.
- Canonical recording establishes valid provenance and placement for the
  declared claim class. It does not establish truth, human review, acceptance,
  commit, push, or normative authority by itself.
- When a durable lesson is learned, update the appropriate governance doc,
  tool doc, or skill.
- When a mistake is found, document it so future sessions do not repeat it.

## Canonical Memory Writer Rule

Any entry claiming `memory_type: session-derived` must be written via
`governance_tools.memory_record`, not by direct markdown append.

Canonical path:

```powershell
python -m governance_tools.memory_record `
  --what-changed "..." `
  --commit <git-sha> `
  --session-id <session-id> `
  --test-evidence "..." `
  --plan-reconciliation <updated|not_applicable|deferred:reason> `
  --next-step "..." `
  --project-root .
```

All new session-derived memory entries must use the canonical writer CLI.
Direct markdown append in `- what changed:` or `- what_changed:` format is
prohibited for new entries.

`--test-evidence` is required and must contain non-whitespace evidence. When no
validation ran, record that boundary explicitly as `NOT RUN: <reason>`. When
the entry intentionally makes no validation claim, use
`NOT CLAIMED: <boundary>`. A missing, blank, or marker-only value is rejected
before the writer creates or appends a daily memory file. This input check does
not prove that non-empty evidence is true, durable, or admissible; the existing
provenance advisory and memory authority workflow remain responsible for those
separate checks.

The guard flags direct-format entries in files dated `>= 2026-05-01` as
`old_format_entry_after_canonical_writer_cutoff`.

Violation code: `non_canonical_writer` warning in `memory_authority_guard`.
Historical violations before the cutoff are not to be backfilled unless a
separate scoped cleanup is approved.

## Knowledge-Base Candidate Rule

`governance_tools.memory_record` writes session-derived records only (`daily`,
`review-log`, `active-task-summary`); it has no knowledge-base surface.

A knowledge-base gotcha for a bug fixed with root cause identified may be
written directly to `memory/03_knowledge_base.md` (or the adopted alias
`memory/03_decisions.md`) as a candidate entry marked `CANDIDATE / UNREVIEWED`.
It must contain the root cause, the fix, the fix commit hash and the test
evidence, and must be paired with a canonical daily record written by
`governance_tools.memory_record` for the same fix commit (`--commit <fix-sha>`).
A candidate is not reviewed knowledge: it never claims promotion, never carries
`Approved by`, and becomes authoritative only through the existing promotion
path.

```markdown
## CANDIDATE / UNREVIEWED: <short title>
- Root cause: ...
- Fix: ...
- Fix commit: <git-sha>
- Test evidence: ...
- Daily record: memory/YYYY-MM-DD.md (memory_record, commit <git-sha>)
```

Keep the marker at the start of the heading so a candidate heading does not equal
a promoted heading; this holds only while session task titles do not themselves
start with `CANDIDATE / UNREVIEWED`, so task titles must not. A candidate does not claim `memory_type: session-derived`.
Editing the knowledge base still falls under the Memory Workflow Dispatch Rule.

Relation to promotion, including `AUTO_PROMOTE`:

- Candidate entries are not inputs to auto-promotion. The promotion path
  (`memory_pipeline.promotion_policy`, `memory_pipeline.memory_promoter`)
  promotes session candidate snapshots, not knowledge-base lines, and never
  edits a candidate entry; known limit: a task titled with the candidate marker
  skips the knowledge-base write yet still logs `Promoted memory` and
  `Approved by` under that heading, which is not approval of the candidate.
- An `Approved by:` line written by promotion is a promotion record for the
  promoted entry. It is never evidence that an agent-written candidate was
  reviewed.
- Write one candidate per root cause; when it recurs, update or cite the
  existing candidate instead of writing a separate duplicate.
- When promotion records the same root cause, the promoted entry supersedes the
  candidate. The pair is recognised by the same fix commit hash in both
  entries; readers use the promoted entry and the candidate stays as history.
  The promotion code does not detect this pairing itself; a promoted entry
  carries the fix commit only when its summary includes it.

## Memory Workflow Dispatch Rule

Repo memory tasks are governed operations, not normal markdown edits.

Before claiming completion for any task that edits `memory/**`, the agent must
run the memory workflow dispatcher:

```powershell
python -m governance_tools.memory_workflow --check --repo .
```

If the repo consumes this framework through a submodule, run the dispatcher from
that submodule path:

```powershell
python ai-governance-framework/governance_tools/memory_workflow.py --check
```

The dispatcher reports whether canonical writer and memory authority guard
requirements apply. If `memory/**` files are changed and the dispatcher was not
run, the agent must not claim memory completion.

If the authority guard was not run after memory changes, report memory status as
not verified. Historical `missing_canonical_memory` continuity gaps are warning
evidence, not clean-completion evidence.

When validating a memory completion claim, run:

```powershell
python -m governance_tools.memory_workflow --check --repo . --run-guard
```

`missing_canonical_memory` and legacy `unbound_memory` are warning evidence.
`active_non_canonical_writer` is reported as a blocker candidate for the current
memory completion claim. This dispatcher is report-only unless a later
selective-blocking phase explicitly changes enforcement.

Selective blocking is opt-in:

```powershell
python -m governance_tools.memory_workflow --check --repo . --run-guard --fail-on-blocker
```

With `--fail-on-blocker`, the dispatcher exits non-zero only for current
completion blocker candidates, such as `active_non_canonical_writer` or a
`memory/**` diff checked without the required authority guard. Historical debt
such as `missing_canonical_memory` remains warning evidence.

The managed `pre-commit` hook may surface this dispatcher as an advisory when
`memory/**` changes are present. That hook advisory does not enable selective
blocking; use `--fail-on-blocker` explicitly when a scoped memory completion
gate is required.

Session closeout records the dispatcher status as advisory evidence. The
session-end hook exposes a `memory_workflow` surface, and closeout receipt schema
`1.2` persists the dispatcher status, task classification, warning codes,
blocker codes, guard summary, and memory completion claim allowance. Receipt
presence is evidence that the workflow status was observed; it is not, by
itself, proof that memory completion was allowed.

## Delivery And Closeout Memory Protocol

Use a two-commit delivery sequence when a completed implementation needs
canonical session memory:

1. complete and validate the bounded implementation scope;
2. commit that implementation scope;
3. use the canonical writer to bind the memory entry to that local
   implementation commit;
4. commit `memory/**` and any closeout companions separately;
5. push both commits and verify the remote ref resolves to the intended head.

### Single-PR Closeout Contract

The two-commit sequence is a commit boundary, not a requirement for two pull
requests. By default, keep the implementation commit and its canonical
closeout companion commit on the same branch and deliver them through one pull
request.

When a canonical closeout companion is required, add it before the pull request
is merged. Successful merge, push, and remote-ref verification belong in the
final delivery report. They must not, by themselves, create another memory
commit, repository mutation, follow-up branch, or second pull request.

A follow-up slice is justified only when:

- post-merge verification exposes a new defect or contradiction;
- required governance state was omitted and must be corrected; or
- the owner explicitly authorizes a separate bookkeeping or remediation slice.

This contract does not weaken branch protection, required checks, review
requirements, or the separation between implementation and closeout commits.

`memory_binding: bound` proves only that the named commit resolves to a commit
object in the local repository. It does not prove that the commit was pushed,
that a remote contains it, or that the memory prose is true.

The closeout companion commit may contain:

- `memory/**`;
- `PLAN.md` only when the added canonical entry declares
  `plan_reconciliation: updated`;
- a receipt or runtime closeout/verdict artifact produced for that closeout;
- an artifact path directly cited by the added canonical entry.

Implementation, release, package, and general documentation paths are not
closeout companions. In particular, `CHANGELOG.md` and
`artifacts/release/**` belong to their implementation or release scope.

`mixed_scope_memory_binding` is a report-only observation when a single staged
scope or commit adds canonical memory bound to an earlier local commit while
also changing non-closeout paths. It does not block hooks or CI. A product
commit followed by a separate memory closeout commit is the expected path and
must not produce that finding.

Remote verification belongs in the final delivery evidence. Do not append a
new memory entry solely to say that the closeout commit was pushed; that would
create an unbounded memory-commit loop. If push state is unknown, report it as
unknown and use `verify remote push state` as the unfinished next action.

## Memory State Trace Consistency

Memory entries must not mix completed and pending state.

`next_step` must describe the next unfinished action, not repeat an action
already recorded as completed in the same memory entry.

If `memory_binding: bound` is recorded, the named commit must resolve to a
local Git commit object. Hash-shaped text alone is not a binding. Local commit
existence must not be interpreted as remote or push evidence.

`bound_session_id` is a fallback only when an eligible runtime artifact anchors
that session ID. Auto-detection failure, explicit uncommitted tokens, and
non-Git paths remain writable as `unbound`; they must not be upgraded to
`bound` from their text shape.

If push status is unknown, write `verify remote push state` instead of
`commit and push`.

If push is confirmed, `next_step` must name the next unfinished slice rather
than repeat commit or push for the completed scope.

When correcting ambiguous historical memory state, prefer adding a new
canonical corrective memory entry over rewriting historical entries.

## Memory State Interpretation Rule

Memory entries are state evidence of prior work, not authorization for current
action.

Reader resolution is question-specific. There is no global memory precedence
such as `03 > daily > PLAN`:

- event-history questions use daily records and their cited evidence;
- current authorization comes from current human instruction or an approved
  change, never from memory or PLAN alone;
- approved work ordering uses PLAN within the currently authorized scope;
- current progress and operations use `01` / `02` projections only when their
  status is current, their review is authority-qualified, their anchors cover
  the latest qualified evidence and substantive state transition, and no later
  qualified change remains unreconciled;
- reusable knowledge requires a promoted, reviewed, non-superseded `03`
  section;
- current review verdict uses the latest valid, authority-qualified,
  non-superseded review while preserving older reviews as history.

If qualified sources conflict or do not establish one current answer, do not
guess. Surface `reviewer_required`, `disputed`, `insufficient_authority`, or
`unassessable` as appropriate.

A retrieved `memory.next_step` is a candidate continuation signal only. It does
not grant permission to modify files, commit, push, close issues, upgrade
claims, or bypass current workspace checks.

Current user instruction, current workspace state, dirty-tree status, and
applicable governance rules always supersede memory content. Before acting on
any memory-derived next step, revalidate the current repo state and authority
boundary.

## PLAN Sync Protocol

- `PLAN.md` is mandatory governance state, not optional project notes.
- After each phase completion or milestone transition:
  1. update `PLAN.md` phase status or next milestone;
  2. update memory files;
  3. declare `plan_reconciliation: updated` in the canonical memory entry;
  4. include both in the closeout companion commit, then push and verify the
     remote ref.
- When `plan_reconciliation` is not `updated`, `PLAN.md` must stay outside the
  closeout companion commit.
- `PLAN.md` drift is treated as governance drift.

## Definition Of Done

This section defines delivery completion under the canonical memory workflow,
not a universal task-completion or session-end trigger. Memory updates, session
closeout, and Git delivery are separate events:

- Memory updates follow the existing triggers in `SYSTEM_PROMPT.md` section 6.1
  and this protocol, including review records and PLAN/milestone updates. Task
  completion does not remove those obligations. L0 fast-track is not a memory
  exemption.
- Session closeout follows the defined session-end conditions in root
  `AGENTS.md`. Task completion alone is not session end, and session closeout
  does not authorize commit, push, or a pull request.
- Git delivery follows the applicable delivery workflow and the existing
  authorization boundaries. The delivery steps in this protocol, including
  PLAN sync and the consuming-repo sequence below, do not grant commit or push
  authority.

When a completed implementation is being delivered under this canonical
memory workflow, delivery is complete when:
1. the agreed done-condition for the bounded implementation is met;
2. the bounded implementation is validated and committed;
3. one canonical memory entry bound to that local implementation commit is
   written before the separate closeout companion commit;
4. the implementation and closeout companion commits exist and have been pushed
   with the required authorization;
5. the intended remote ref is verified.

Report the completed local scope, delivery state, and push authorization
separately. If the bounded implementation has been validated and committed but
push is not authorized, report that implementation as complete locally and
delivery as not completed, with push authorization not granted. Lack of push
authorization does not undo completed local work or permit an unauthorized
push. This distinction does not waive applicable memory obligations, pending
companion work, or dirty-workspace reporting requirements; do not claim the
overall task is complete while its required work remains unfinished.

`PLAN.md` sync and structured memory refresh are required when a phase or
milestone transition happened.

The canonical memory entry is not post-push proof. Remote verification is a
separate delivery fact and does not require another memory commit.

## Cross-Agent Closeout Rule

- Framework repo (`ai-governance-framework`): strict mode. Session/workspace
  constraints live in root `AGENTS.md`; final report envelope details live in
  `governance/RESPONSE_ENVELOPE_CONTRACT.md`; executable closeout entrypoints
  are listed below.
- Consuming repos: minimal mode by default (`done-condition met ->
  implementation commit -> canonical memory write -> closeout commit ->
  push both commits -> verify remote ref`).
- Strict closeout is opt-in for consuming repos.

Canonical tools:

```powershell
python -m governance_tools.session_closeout_entry --project-root .
python -m governance_tools.manage_agent_closeout
```

## Non-Claims

This file does not change:
- memory writer schema
- runtime hooks
- validators
- enforcement level
- #17 Copilot memory-authority advisory threshold or any blocking threshold
- historical violation disposition
