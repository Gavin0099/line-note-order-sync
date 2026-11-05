---
audience: agent-on-demand
authority: reference
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# F-7 Full Update

Status: extracted from AGENTS.md
Semantic change: no
Runtime behavior change: yes — submodule consumer apply path now refreshes memory workflow router coverage, managed hook advisory coverage, and explicit response-envelope version compatibility.
Enforcement change: no

## Purpose

F-7 is the AI Governance Full Update workflow. A governed submodule pointer
update is Stage 1 of F-7, not the whole workflow.

When the user asks to update or adopt the latest AI Governance, including
"幫我更新最新版 AI Governance" and equivalent natural-language wording, the
request routes to F-7 even when the user does not name F-7. F-7 must execute the
full adoption/update workflow or explicitly report a blocker.

A submodule pointer update alone is insufficient and must be reported as
`partially_updated`, not completed.

## Required Stages

1. framework pointer update
2. repo-local instruction refresh
3. response-envelope surface compatibility check
4. memory writer coverage check
5. hook / validator coverage check
6. existing memory normalization status check
7. final adoption status report backed by `governance_maturity_summary`

## Layered Status Fields

```text
framework_pointer: updated | already_current | blocked | not_present | not_verified
repo_local_instruction: updated | already_current | blocked | missing | not_verified
memory_writer_coverage: verified | updated | blocked | missing | not_applicable | not_verified
hook_validator_enforcement: verified | updated | blocked | missing | not_applicable | not_verified
existing_memory_normalization: completed | needed | blocked | not_applicable | not_verified
response_envelope_surface: verified | conflict | not_verified
governance_maturity_summary: present | not_available | not_run
human_readable_adoption_summary: reported | not_reported
ai_governance_update_result: reported | not_reported
final_status: full_update_completed | already_current | partially_updated | manual_update | destructive_manual_update | blocked | not_submodule_consumer | not_verified
```

`full_update_completed` may be used only when every required stage is
`updated`, `already_current`, `verified`, `completed`, or `not_applicable`.

If any required surface is `missing`, `needed`, `blocked`, `conflict`, or `not_verified`,
the final status must not be `full_update_completed`.

Manual pointer, gitlink, checkout, or lock-file edits that bypass F-7 may be
reported as `manual_update`, but must not be reported as
`full_update_completed`, `already_current`, or `updated`. If that manual path
discarded local framework checkout state, report `destructive_manual_update`
and include the discarded modified and untracked path inventory in the final
operator-facing report.

This is the F-7-specific projection of the canonical manual-update reporting
vocabulary in `governance/AI_GOVERNANCE_UPDATE_PROTOCOL.md`. Do not treat this
file as an independent source for `manual_update` or
`destructive_manual_update` definitions.

The final adoption status report must follow the canonical adoption-summary
relay contract in `governance/AI_GOVERNANCE_UPDATE_PROTOCOL.md`. The concrete
table and final-report projection are produced by
`governance_tools/governance_update_reporting.py`; F-7 must not maintain a
separate copy of the table rows or header here. Operationally, when
`human_readable_adoption_summary` is present, relay the table rows as a table,
not only as machine-readable status fields.

Start the owner-facing report with the plain-language opening defined in
`governance/AI_GOVERNANCE_UPDATE_PROTOCOL.md#plain-language-opening-for-update-reports`.
Explain local completion, delivery state, and the important unverified behavior
before the full table. Expanded reporting requires the complete evidence, not
a jargon-heavy opening; it does not permit dropping table rows or limitations.
Apply that same section's deduplication rule: opening, complete table, then
only evidence and disclosures not already covered with their required meaning
and binding. Do not add a duplicate technical-status checklist. Keep decisive
limitations prominent; unrelated untouched files remain in the required
dirty-state disclosure. Required fields and table-unavailable fallbacks remain.

`adoption_doctor: findings 0`, `governance_version_check: compatible`, a clean
build, or a framework pointer update is not a substitute for the final adoption
status report. If `governance_maturity_summary` cannot be produced, F-7 must
report `governance_maturity_summary: not_available` or
`governance_maturity_summary: not_run` with the reason and must not claim that
the operator was shown complete adoption status.

If the machine-readable summary is available but the table cannot be relayed,
F-7 must report `human_readable_adoption_summary: not_reported` with the reason
and must not claim that the operator was shown the complete human-readable
feature adoption table.

The table relay is required for every terminal F-7 result: updated,
already-current, blocked, and fallback/manual outcomes. Fallback paths should
still run the report-only maturity summary when safe. If table rows are
unavailable, F-7 must report `update_report_complete=false` and
`completion_claim_allowed=false`; it must not fabricate a table or claim a
complete update report. A blocked update may still have a complete update
report when its real adoption table is relayed; report completeness and update
success are separate truths.

## Consumer Test-Quality Expectations

F-7 instruction refresh must keep semantic test-quality expectations visible to
agents that later write feature or bugfix code in the consuming repo.

For non-trivial behavior changes:

- happy-path-only tests are not sufficient evidence;
- reproducible bug fixes need regression tests when feasible;
- expected values must come from a specification, invariant, reviewed fixture,
  or other independent source, not copied production logic;
- mock-only assertions are weak evidence unless the test also asserts
  observable behavior, state, output, or persisted effect;
- domain validators need pass/fail fixtures, and fixture evidence is strongest
  only when a focused harness actually executes the validator against those
  fixtures.

Report-only `test_signal_quality_audit` output can help reviewers find weak
signals. It does not prove tests are industry-grade, does not prove domain
correctness, and does not create enforcement.

F-7 human and JSON outputs must also carry `ai_governance_update_result` as a
report-only presentation and claim-boundary envelope. This envelope must not
replace `final_status`, must not change F-7 completion criteria, and must not
be used as proof of runtime enforcement, full adoption, semantic correctness,
memory completeness, fleet/CI enforcement, domain correctness, or release
readiness.

When F-7 reports `manual_update` or `destructive_manual_update`, the envelope
must preserve that same status as a disclosure state. Manual and destructive
manual states are not successful governed F-7 completions, and destructive
manual reporting must include the discarded modified and untracked path
inventory.

## Implemented Automation

For `submodule_consumer` apply mode, the updater now performs these scoped
surfaces:

- refreshes `AGENTS.base.md`
- refreshes / appends AI Governance update rules in `AGENTS.md`
- ensures an `AGENTS.md` `governance:key=memory_workflow` router section
- installs managed hook advisory files from the governance submodule checkout
- checks explicit response-envelope contract version markers in managed
  instruction surfaces; a legacy marker produces `response_envelope_surface:
  conflict` and prevents `full_update_completed`
- surfaces `governance_maturity_summary` as a report-only adoption visibility
  stage for consuming-repo operators
- reports `full_update_completed` only when memory workflow coverage, hook
  advisory coverage, and normalization status are all eligible
- after installing hooks, verifies the Copilot hooks with the validator of the
  target framework checkout, run in a subprocess, because the installer that ran
  may predate the target. A framework lifecycle bridge still registered in
  `.github/hooks/ai-governance-vscode.json` (the legacy `Stop -> session_end`
  wiring, which closes the session at every agent turn) makes the hook stage
  `blocked` with a `migration_required` error, and the update receipt records
  `blocked`
- in dry-run, reports the hook stage as `missing`, never `verified`, while that
  legacy wiring remains

## Consumer Health Check

Run `python -m governance_tools.external_repo_readiness --repo <consumer>` from a
current framework checkout. The tool then checks the consumer with current
validator code, whatever framework version the consumer pins. Its output opens
with an `AI Governance Health` summary:

- `framework`: `CURRENT`, `OUTDATED` or `INCOMPATIBLE`; only `INCOMPATIBLE`
  blocks readiness. An outdated framework is not by itself unsafe.
- `copilot_hooks`: `SAFE`, `NOT_INSTALLED`, `INCOMPLETE` or
  `MIGRATION_REQUIRED`. Absent hooks do not block readiness; the installed
  legacy `Stop -> session_end` wiring does.
- `memory_lifecycle`: always `NOT_VERIFIED`; this static check cannot observe a
  session start, a session end or memory recovery.

The check reads one repository. It keeps no list of consumers and changes
nothing; migrating is an F-7 run, which needs the owner's authorization.

## Non-Claims

This protocol defines the required F-7 reporting contract. It does not by
itself implement updater automation for all stages.

Not claimed unless separately implemented and validated:
- updater automation performs all F-7 stages for all repo roles
- arbitrary prose contradictions in unmanaged instruction surfaces are detected;
  the compatibility check currently handles explicit contract version markers
- validators changed
- artifact schema changed
- existing memory was normalized
