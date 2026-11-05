---
audience: agent-on-demand
authority: reference
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# AI Governance Update Protocol

Status: extracted from AGENTS.md
Semantic change: no
Runtime behavior change: no
Enforcement change: no

## Purpose

This protocol distinguishes AI Governance check/update intent from ordinary
instruction-file synchronization.

Do not treat `AGENTS.md`, `AGENTS.base.md`, or local governance instruction-file
sync as proof that the AI Governance Framework itself is current.

For the map of where update and review instructions reach different agent
surfaces, see `docs/governance/agent-instruction-surface-map.md`.

## Update Intent Rule

When the user asks to "Update AI Governance to latest" or equivalent Chinese
update wording, first determine whether the repository consumes AI Governance
through a registered submodule. Common paths include:
- `ai-governance-framework`
- `.ai-governance-framework`

Repos may also use a repo-specific path such as
`external/ai-governance-framework`; the updater should discover these through
`.gitmodules` entries whose URL points at an `ai-governance-framework`
repository.

If a governance submodule exists, the request maps to the governed submodule
update workflow. Compare the nested governance HEAD with the approved target
upstream HEAD, preferably through the governed submodule updater dry-run path.

Do not claim AI Governance is already current based only on:
- `AGENTS.md` unchanged
- `AGENTS.base.md` unchanged
- parent repository `HEAD == origin/main`
- `git pull --ff-only` reporting already up to date
- clean parent repository working tree

## Valid Already-Current Evidence

A valid `already_current` conclusion for a submodule consumer must include:
- governance submodule path
- nested governance HEAD
- target upstream framework HEAD
- dry-run update result

Required technical evidence shape (after the plain-language opening defined
below; not a replacement for the complete adoption table):

```text
AI Governance update check: <already_current | update_available | updated | manual_update | destructive_manual_update | not_submodule_consumer | not_verified>
ai_governance_update_result: REPORTED | NOT REPORTED
governance submodule path: <path | NOT FOUND | NOT CHECKED>
nested governance HEAD: <sha | NOT CHECKED>
target framework HEAD: <sha | NOT CHECKED>
dry-run: PASS | FAIL | NOT RUN
update mode: already_current | fast_forward | detached_target_checkout | NOT CLAIMED
parent repo commit: <hash | NOT NEEDED | NOT CREATED>
governance maturity summary: RUN | NOT RUN | NOT AVAILABLE
user-facing adoption status: <minimal | partial | full_candidate | not_governed | unknown | NOT REPORTED>
framework topology: <copy_based | repo_owned_framework_path | submodule_consumer | unknown | NOT REPORTED>
static self-contained: yes | no | unknown | NOT REPORTED
runtime capable: not_checked | <other explicit value | NOT REPORTED>
hook framework root: inside_repo | external | absent | unknown | NOT REPORTED
framework pin freshness: <current_vs_local_tracking | behind_local_tracking | ahead_or_diverged_vs_local_tracking | unknown | not_applicable | NOT REPORTED>
repo-specific rules: true | false | NOT REPORTED
domain contract: true | false | NOT REPORTED
validator surface: true | false | not_checked | NOT REPORTED
memory workflow surface: <value from summary | NOT REPORTED>
adoption cannot claim: <short cannot-claim list from the summary | NOT REPORTED>
human_readable_adoption_summary: REPORTED | NOT REPORTED
```

If the session only updates instruction files, report that as an
instruction-file update and mark the AI Governance Framework update as
`not_verified`.

Invalid conclusion:

```text
AGENTS.md was updated and the parent repo is up to date, so AI Governance is current.
```

Valid partial conclusion:

```text
結果：這次只更新了指令文件，尚不能確認治理框架更新完成；沒有建立提交，上傳與合併狀態未確認。
原因：治理框架的版本與導入狀態尚未檢查。
下一步：先檢查框架版本及導入狀態，再判定是否需要更新；不因此取得更新或上傳授權。

AI Governance update check: not_verified
governance submodule path: NOT CHECKED
nested governance HEAD: NOT CHECKED
target framework HEAD: NOT CHECKED
dry-run: NOT RUN
update mode: NOT CLAIMED
parent repo commit: NOT CREATED
governance maturity summary: NOT RUN
user-facing adoption status: NOT REPORTED
human_readable_adoption_summary: NOT REPORTED
```

## Check Vs Update Intent

Classify the user's wording before acting.

Check intent examples:
- "檢查 AI Governance 是否最新"
- "確認 AI Governance 有沒有更新"
- "verify AI Governance version"
- "check whether AI Governance is up to date"

Action: verify only. Do not update the submodule pointer.

Update intent examples:
- "幫我更新最新版 AI Governance"
- "把 AI Governance 更新到最新"
- "更新 AI Governance 到最新版"
- "Update AI Governance to latest"

Action: route the request to `governance_tools.f7_full_update` as the primary
orchestrator. This applies to "幫我更新最新版 AI Governance" and equivalent
natural-language update requests even when the user does not name F-7. The
governed submodule updater is an F-7 backend/stage, not a substitute for the
complete F-7 report.

For update intent, do not stop after direct HEAD comparison when nested
governance HEAD differs from target framework HEAD. A direct HEAD comparison
may establish `update_available`, but it is not a completed update.

If the repository is a submodule consumer and no blocker exists, continue from
`update_available` to the governed update step.

Ask for confirmation only when the user intent is ambiguous or when a blocker
requires a user decision.

## Fixed Status Values

AI Governance update status must use one of these fixed values:
- `already_current`: nested governance HEAD already matches target framework HEAD.
- `update_available`: nested governance HEAD differs from target framework HEAD, but update has not yet been applied.
- `updated`: governed update flow completed and nested governance HEAD now matches target framework HEAD.
- `manual_update`: the agent changed a governance submodule pointer, gitlink,
  framework checkout, or lock file without governed updater/F-7 evidence. This
  may report what changed, but must not accompany `already_current`,
  `updated`, `completed`, `latest`, or full-adoption claims.
- `destructive_manual_update`: a `manual_update` path that discarded local
  framework checkout state, such as nested worktree changes or untracked files.
  The final report must list the discarded modified and untracked paths.
- `blocked`: update could not proceed due to dirty worktree, staged changes, dirty nested submodule, dry-run failure, missing path, or explicit blocker.
- `not_submodule_consumer`: repository does not consume AI Governance through a submodule.
- `not_verified`: the agent could not safely determine current or target governance state.

For update intent, `update_available` is an intermediate state, not a final
successful outcome. Final response must be one of:
`already_current | updated | manual_update | destructive_manual_update | blocked | not_submodule_consumer | not_verified`.

This file is the canonical source for the `manual_update` and
`destructive_manual_update` reporting vocabulary, templates, and claim
boundaries. Consumer instruction baselines and F-7 documentation may project
this vocabulary into their local execution surfaces, but must not become
independent definitions of these states.

Updating the governance submodule pointer does not automatically authorize a
parent repository commit or push unless the user explicitly requested
commit/push or the active workflow already defines commit/push as part of the
governed update task.

If no parent repo commit is created, report:

```text
parent repo commit: NOT CREATED
```

## Manual Update Reporting

Manual update paths are allowed only as an honest fallback report. They are not
evidence that the governed update flow ran.

Manual update conclusion template:

```text
AI Governance update check: manual_update
ai_governance_update_result: REPORTED
framework_update_status: manual_update
governance maturity summary: <RUN | NOT RUN | NOT AVAILABLE>
adoption_status: <from maturity summary | unknown>
human_readable_adoption_summary: <REPORTED | NOT REPORTED>
reason: governed updater/F-7 was not used
claim boundary: manual pointer/lock/checkout changes may be reported; do not claim completed/latest/full adoption
```

Destructive manual update conclusion template:

```text
AI Governance update check: destructive_manual_update
ai_governance_update_result: REPORTED
framework_update_status: destructive_manual_update
discarded_modified_paths: <list | none reported>
discarded_untracked_paths: <list | none reported>
governance maturity summary: <RUN | NOT RUN | NOT AVAILABLE>
human_readable_adoption_summary: <REPORTED | NOT REPORTED>
claim boundary: destructive local cleanup occurred; do not claim completed/latest/full adoption
```

When a manual or destructive manual path is reported, the
`ai_governance_update_result` envelope must remain a disclosure surface:

- `report_only=true`
- `framework_update_status=manual_update` or
  `framework_update_status=destructive_manual_update`
- `adoption_status=not_reported` unless `governance_maturity_summary` was
  explicitly run and relayed
- `human_readable_adoption_summary=not_reported` unless the operator-facing
  table was explicitly produced and relayed
- `cannot_claim` includes that the operation is not a completed governed
  updater/F-7 update and does not prove full adoption or enforcement

Before discarding local state in a nested framework checkout, first inspect and
record the modified and untracked paths that would be discarded. The final
operator-facing report must include that discarded-path inventory. A statement
such as "cleaned the submodule" is not a substitute for the inventory.

## Consuming Repo Reporting Corrections

When reporting AI Governance updates in a consuming repository, keep receipt
integrity, dirty-tree state, build evidence, and memory disposition separate.

### Plain-Language Opening For Update Reports

Before the required adoption table and technical evidence, explain what the
existing results mean for the owner. For completion or partial-completion
reports, retain the existing first three non-empty lines: 結果 / 原因 / 下一步
(translated in other session languages). This does not introduce a paragraph
format exception. Other task classes retain their existing rendering rules.
Select the content of that opening to answer:

- Is the local update complete, incomplete, or not yet verified? State the
  actual blocker when one exists, rather than opening with status tokens.
- Was the change committed, pushed, or merged? Keep these separate; local
  validation does not prove delivery. If delivery was not checked, say unknown.
- What important behavior remains unverified, and what is the next action?
  Preserve any required owner authorization; a suggested action is not permission.

Use ordinary language, not a list of field names followed by translations.
An installed writer or hook does not prove it ran in a real session. Do not
translate `full_candidate` into "fully working", or `not_checked` into a
successful result. Mention exact tokens in the opening only when their exact
value is needed for the current decision; retain them in the technical evidence.

The required response shapes in this protocol remain the detailed evidence
section, not the opening. The complete adoption table, required fields, evidence
references, warnings, discarded-path inventory when applicable, and non-claims
remain in the same final report. This is ordering and wording only: it changes
no completion criteria, authorization, schema, or F-7 expanded-report exception.

For update reports, present the plain-language opening, then the complete
required adoption table, then only the required evidence or disclosures not
already represented. Do not insert an additional technical-status table,
update checklist, or closing recap that merely repeats those facts. The
opening may summarize a decisive fact that also appears in the required table;
do not remove a required table row to avoid that necessary overlap.

The required evidence shapes are coverage requirements, not a demand for a
second field-by-field rendering. A fact already shown in the table or opening
need not be repeated only when its required value, meaning, and evidence
binding are preserved. Add any missing exact HEADs, paths, command/results,
status values, evidence references, warnings, or non-claims once after the
table. Keep the complete canonical machine evidence unchanged. Distinct or
conflicting signals are not duplicates; preserve their difference. An explicit
full-evidence request still receives all requested detail.

Use the opening or an optional 注意 line for the limitation that changes what
the owner may conclude or do next, such as an unverified runtime or a missing
authorization. An unrelated, untouched backup belongs in the required
dirty-state disclosure after the table, not in that prominent warning merely
because it is untracked. If dirty state affects scope, validation, or safe
delivery, keep that impact prominent. Never suppress other decision-relevant
limits to fit one line, or omit required discarded-path or dirty-state records.
The next action must state an action and any needed authorization, not merely
repeat a delivery status such as "not pushed".

Example openings (illustrative inputs, not claims about the current repo):

- Local workflow completed, committed but not pushed; runtime not checked:

  ```text
  結果：本機治理更新已完成，修改已提交，但還沒上傳。
  原因：安裝檢查已通過；實際工作時保護流程是否會觸發，尚未驗證。
  下一步：依目前授權處理上傳；若尚未授權，先請你確認。
  ```

- New files staged, required closeout blocked; no commit or push:

  ```text
  結果：新版檔案已準備好，但更新流程還沒完成，也沒有提交或上傳。
  原因：必要的收尾檢查被尚未提交的變更擋住，不能先當作更新成功。
  下一步：先確認這批檔案符合提交條件且已有授權，再提交並重跑收尾檢查。
  ```

- Summary unavailable:

  ```text
  結果：目前無法確認治理更新是否完整，上傳與合併狀態也未確認。
  原因：導入檢查結果無法取得，不能先當作更新成功。
  下一步：先取得缺少的檢查結果，再判定更新狀態。
  ```

For example acceptance, read only the opening and check that the local result,
delivery state, decisive limitation, and needed owner action are understandable
without knowing the field names. Then compare it with the source evidence:
unknown must remain unknown, blocked must not become complete, and the full
table must still follow. This is a human review, not a new automated gate.

Also review the whole rendered report against the observed consumer case:
local update checked, commit created but not uploaded, runtime unverified,
and an unrelated untouched backup. The opening must make the update, delivery,
runtime limitation, and authorization-dependent next action understandable;
the required table remains complete; a supplemental evidence section preserves
anything the opening/table did not cover, including the backup disposition.
Reject an extra technical-status list that only repeats these sections.
As counterchecks, a dirty file that blocks safe delivery must remain prominent,
and an unavailable table must retain the existing incomplete-report fallback.
These are presentation reviews, not new updater tests or completion criteria.

### Required Adoption Status Summary

This section is the canonical reporting contract for adoption-summary relay.
Concrete tool-output projection lives in
`governance_tools/governance_update_reporting.py`. Secondary surfaces should
point here and to that projection helper instead of restating the table rows or
header.

An AI Governance update report must surface the user-facing adoption status
summary when the framework checkout contains `governance_maturity_summary`.

Do not collapse this into:
- `adoption_doctor: findings 0`;
- `governance_version_check: compatible`;
- `framework.lock.json updated`;
- `dotnet build passed`;
- `submodule updated from <old> to <new>`.

Those signals may be useful evidence, but they do not tell the operator which
governance surfaces are present.

Valid update reports must include the `governance_maturity_summary` fields, or
explicitly state why the summary was not run / not available. At minimum, report:
- user-facing adoption status and one-line meaning;
- framework topology;
- static self-contained status;
- runtime capable status;
- hook framework root;
- framework pin freshness;
- repo-specific rules;
- domain contract;
- validator surface;
- memory workflow surface;
- cannot-claim / claim-boundary summary.

When `human_readable_adoption_summary` is present, the final operator-facing
report must relay that section as a readable Chinese table, not only as
machine-readable fields. The report must include the marker
`[human_readable_adoption_summary]` and the table header:

```text
| 功能 | 狀態 | 這個功能是做什麼 |
```

It is valid to preserve the table verbatim from the tool output or to restate it
faithfully in the final report. It is not valid to report only
`user_facing_status`, `framework_topology`, or other machine field names while
omitting the Chinese feature/status/explanation table. If the table cannot be
produced or relayed, state:

```text
human_readable_adoption_summary: NOT REPORTED
reason: <why the Chinese table was not relayed>
claim boundary: machine-readable adoption fields only; operator-facing feature table was not reported
```

This relay requirement applies to every terminal update result, including
`updated`, `already_current`, `blocked`, `manual_update`,
`destructive_manual_update`, `not_submodule_consumer`, and `not_verified`.
Fallback paths must run and relay `governance_maturity_summary` when it is
safely available. If a fallback or blocker prevents the table from being
produced, do not fabricate rows; report:

```text
human_readable_adoption_summary: NOT REPORTED
update_report_complete=false
completion_claim_allowed=false
reason: <why the table was unavailable or omitted>
```

When the table is omitted, the operation status may still be reported, but the
agent must not claim a complete AI Governance update report.

## Consumer Test-Quality Expectations

When an AI Governance update refreshes consumer-facing instruction surfaces,
the resulting instructions must keep test-quality expectations visible to the
agent that later writes feature or bugfix code.

For non-trivial behavior changes:

- do not report happy-path-only tests as sufficient evidence;
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

If the update path used a direct submodule fast-forward plus lock-file update
instead of F-7 or `adopt_governance.py`, run or relay the available
`governance_maturity_summary` before final reporting. If it cannot be run,
state:

```text
governance maturity summary: NOT RUN
reason: <why it was not run>
claim boundary: update commit/build evidence only; adoption completeness was not reported
```

Valid technical evidence excerpt (after the plain-language opening; not a
complete final report):

```text
AI Governance was updated, and the adoption status summary is partial:
framework_topology=submodule_consumer, runtime_capable=not_checked,
repo_specific_rules=false. This is report-only and does not prove runtime
enforcement or complete governance adoption.
```

Invalid wording:

```text
AI Governance was updated and adoption_doctor findings=0, so governance is
fully installed.
```

### Verified Status Claim Ceiling

Note: `not_verified` in the fixed update status list and
`repo_native_verified` in onboarding/readiness output are different axes. The
former is an update-check status; the latter is a receipt/evidence-chain
integrity signal.

`repo_native_verified`, `head_ok`, and `ts_ok` may be reported only as
receipt/evidence-chain integrity signals.

They must not be reported as proof of:
- governance enforcement;
- framework correctness;
- complete governance adoption;
- semantic correctness;
- runtime behavior correctness.

Valid wording:

```text
repo_native_verified means the closeout receipt/evidence-chain head and
timestamp alignment passed for this update check.
It does not prove governance enforcement or framework correctness.
```

Invalid wording:

```text
The repo is now governed / enforcement is active / framework correctness is verified.
```

### Dirty Tree Reporting Separation

If the consuming repository has pre-existing dirty work, the final report must
separate:
- governance apply scope;
- pre-existing user work;
- generated local artifacts or memory files;
- validation run on the combined dirty state.

Do not flatten these into a single "updated and validated" statement.

Required wording pattern when dirty work remains:

```text
Governance apply scope: <files changed by the update>
Pre-existing dirty user work: <paths or summary>
Validation scope: ran on combined dirty working tree
Overall task: NOT DONE until dirty work is audited or explicitly excluded
```

### Build And Smoke Evidence Boundary

Build or CLI smoke checks run after an AI Governance update in a dirty consuming
repo may be reported only as compatibility evidence for the current combined
dirty state.

They must not be reported as proof that:
- the governance update is correct;
- the governance framework is correct;
- governance enforcement is active;
- unrelated user feature work is complete.

### Generated Memory Disposition

Generated memory files in consuming repositories must have an explicit
disposition before the update is reported as cleanly completed.

Allowed dispositions:
- verify the file was produced by the canonical writer and commit it;
- rewrite the record through `governance_tools.memory_record` and commit it;
- explicitly mark it as unresolved dirty work.

Do not leave an untracked generated memory file as a side note while reporting
the update as complete.

## Non-Claims

This file does not change:
- updater behavior
- submodule update semantics
- hooks
- validators
- runtime behavior
- F-7 automation coverage
