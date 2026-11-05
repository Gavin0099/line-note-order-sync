# AGENTS.md
<!-- governance-baseline: overridable -->
<!-- baseline_version: 1.0.0 -->
<!-- This file is repo-specific. Edit freely. -->
<!-- DO NOT edit AGENTS.base.md — it is a protected framework file. -->

This file extends `AGENTS.base.md`.
All rules in `AGENTS.base.md` are non-negotiable and apply to this repo unconditionally.

Add repo-specific rules below.
Fill in each section below, or write `N/A` if the section is not applicable to this repo.

Quick start:

1. Start with the top 1-3 risky paths in this repo, not a full policy rewrite.
2. If you already have a checklist / runbook / test convention, copy that wording here instead of inventing new terms.
3. If a section truly does not apply, keep `N/A` and move on.

---

## AI Governance Update Intent Rule

This is the ALWAYS-READ F-7 routing and truthfulness boundary. The complete
work instructions, result vocabulary, evidence shapes, stage details and
reporting examples live in the canonical pinned framework documents:
- `governance/AI_GOVERNANCE_UPDATE_PROTOCOL.md`
- `governance/F7_FULL_UPDATE.md`
- `governance/RESPONSE_ENVELOPE_CONTRACT.md`

Resolve these against the consumer's installed governance documents or the
active, pinned framework checkout (which may be a submodule). Do not consult
an unrelated version and assume it matches the current consumer. For F-7
updates, load the canonical update and F-7 documents before acting or
claiming completion. Missing instructions or unverified evidence mean
`not_verified` / `blocked`, **not** `updated` or `already_current`.
On-demand documents cannot authorize commit, push, release or destructive
work that the current Owner has not authorized.

### AI Governance Check Vs Update Intent

- For `check` intent (e.g., 「檢查 AI Governance 是否最新」), verify only.
  Never update the framework pointer.
- For `update` intent (e.g., 「幫我更新最新版 AI Governance」 or
  "Update AI Governance to latest"), invoke
  `governance_tools.f7_full_update` as the primary orchestrator.
  The submodule updater alone is only one stage, not complete F-7.
  Do not repeat a request for authorization already granted within the
  approved scope; stop only for a real blocker or an Owner-gated action.

Never claim `already_current` solely from `AGENTS.md` unchanged,
`AGENTS.base.md` unchanged, clean parent git status, parent
`HEAD == origin/main`, or `git pull --ff-only`. A defensible
submodule status requires the actual governance submodule path,
nested framework HEAD, target approved framework HEAD, and governed
updater dry-run result. `update_available` is not a completed update.

Full technical shape and terminal report definitions must come from the
canonical docs above. Status line (never fabricate values):

```text
AI Governance update check: <already_current | update_available | updated | manual_update | destructive_manual_update | not_submodule_consumer | not_verified>
```

This baseline is a propagated, managed consumer instruction copy of the
canonical manual-update reporting vocabulary in
`governance/AI_GOVERNANCE_UPDATE_PROTOCOL.md`. The canonical file is the
authority; this compact copy is an execution entrypoint, not another status
definition. `manual_update` and `destructive_manual_update` are truthful
fallbacks for pointer/lock/checkout changes without the governed F-7 path,
**never** evidence for completed/latest/full adoption. Disclose discarded
modified and untracked paths before claiming destructive cleanup; obtain
Owner authorization before discarding anything. If a parent repo commit
was not created, report `parent repo commit: NOT CREATED`.

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

### Response Envelope Boundary

- Response envelope contract version: v0.8. Compact human responses are the default.
- Failed/partial work and owner decisions may remain compact if the
  blocker, ability to proceed, risk, claim boundary and Owner choice are clear.
  Expand when canonical evidence is unavailable, an explanation cannot be
  preserved briefly, or full evidence is requested.
- Keep all raw fields in canonical evidence; use plain-language meanings for
  decision-relevant status tokens.
- For review, diagnosis and concepts, use Engineering Explanation
  without forcing an irrelevant next action.
- For completion or partial-completion F-7 reports, retain the first three
  non-empty lines as 結果 / 原因 / 下一步 (translated in other session
  languages). Explain local completion, commit/push/merge state and important
  unverified behavior in plain language before the complete adoption table;
  suggested actions do not grant
authorization.

If the session only updates `AGENTS.md` or other local instruction files,
mark governance framework status `not_verified` and do not claim a complete
update. The examples below remain an explicit negative/positive boundary.

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

For every F-7 terminal result, relay actual
`[human_readable_adoption_summary]` rows as a TABLE. A clean build,
`adoption_doctor: findings 0` or a pointer update is no substitute.
If the real table cannot be produced or relayed, report
`human_readable_adoption_summary: NOT REPORTED` and the reason;
also set `update_report_complete=false` and
`completion_claim_allowed=false`. Never fabricate rows or claim complete
adoption. Report completeness is separate from update success.

### Test Quality Expectations

Non-trivial changes require evidence beyond happy-path-only tests:
bug regressions where feasible, independently sourced expected results,
and validator pass/fail cases. Mock-only success and
`test_signal_quality_audit` are not proof of correctness or enforcement.
Read the detailed `governance/TESTING.md` for testing decisions.

### F-7 Full Update Semantics

F-7 has six necessary stages: framework pointer, repo-local instructions,
memory writer coverage, hook/validator coverage, existing memory
normalization status, and user-facing maturity/adoption report. A raw
submodule pointer update alone is `partially_updated`, not completed.

`full_update_completed` is permitted only when every required stage is
actually verified as updated, already_current, verified, completed or
not_applicable. Missing, needed, blocked or not_verified surfaces are NOT
complete. Read `governance/F7_FULL_UPDATE.md` for the layered status
fields and the exact final adoption report. Successful structural checks
do not prove real-session hook execution or that legacy memory was
normalized.


## AI Governance Memory Workflow Router
<!-- governance:key=memory_workflow -->

- Before claiming completion for any change touching `memory/**`, run `python -m governance_tools.memory_workflow --check --repo .`.
- For memory completion claims, run `python -m governance_tools.memory_workflow --check --repo . --run-guard` and report blockers before claiming DONE.
- Use the canonical memory writer (`memory_record`) for session-derived records (daily, review log, active-task summary); do not hand-edit them. A root-caused bug-fix gotcha may be written directly to `memory/03_knowledge_base.md` (or the adopted alias) only as a `CANDIDATE / UNREVIEWED` entry with root cause, fix, fix commit and test evidence, paired with a canonical daily record for the same fix commit; it never claims promotion or `Approved by`.
- Canonical writer signal: `governance_tools.memory_record` / `memory_record.py`.

## Repo-Specific Risk Levels
<!-- governance:key=risk_levels -->

<!-- Define what makes a change HIGH / MEDIUM / LOW risk in this repo.
Example:
- HIGH: any change to auth, payment, or data migration paths
- MEDIUM: adding a new API endpoint or external dependency
- LOW: documentation, config comments, test-only changes

Prompt yourself:
- What changes in this repo can corrupt state, break compatibility, or cause production downtime?
- What changes are review-heavy but still reversible?
- What changes are safe enough to keep in a fast path?
-->

- Owner-selected project posture: MEDIUM, because buyer data and procurement quantities require completeness checks and human reconciliation.
- HIGH / L2: changes to snapshot acceptance, buyer identity, deduplication, cancellation, schema migration, credentials, or writes to external order systems.
- MEDIUM / L1: parsing rules, capture adapters, import/export formats, dependencies and governance integration.
- LOW: wording and formatting that do not change behavior, authorization or evidence rules.

## Must-Test Paths
<!-- governance:key=must_test_paths -->

<!-- List modules or code paths that require tests before merge.
Example:
- src/auth/       any change here needs integration tests
- src/migrations/ schema changes need a rollback test

Prompt yourself:
- Which files or directories would you never want changed without a test?
- Which paths are easy to break with static changes alone?
- Which user-visible or hardware-facing flows need explicit coverage?
-->

- `src/notesync/parser/`: explicit orders, full-width forms, unknown SKU, questions and cancellation text; expected values come from S02 fixtures.
- `src/notesync/storage/` and `reconcile/`: transaction rollback, restart, repeat import, same-name buyers, partial snapshots and version selection.
- `src/notesync/exporters/`: totals agree with reviewed detail, source traceability, UTF-8 and CSV formula safety.
- Governance wiring: pinned submodule, drift/readiness, hook validation, target-repo runtime smoke and memory workflow. These checks do not validate product behavior.

## L1 → L2 Escalation Triggers
<!-- governance:key=escalation_triggers -->

<!-- When does this repo's work need the full L2 evidence checklist?
Example:
- Changing shared database schema
- Modifying public API contracts
- Any change touching >3 modules simultaneously

Prompt yourself:
- What kinds of changes cross system boundaries?
- What changes would require a reviewer to ask for stronger evidence than normal?
- What changes become risky mainly because they are broad, not because they touch one file?
-->

- Changes can silently add, lose or merge orders, or turn partial data into an accepted report.
- A migration changes existing data, a capture path reads credentials/private APIs, or an export writes to an external service.
- Native/UIA behavior is relied on for a completeness or stable-identity claim without a matching local experiment.
- Governance authority, fail-closed behavior or evidence standards would change. Reuse the pinned framework; do not weaken its gates to pass onboarding.

## Repo-Specific Forbidden Behaviors
<!-- governance:key=forbidden_behaviors -->

<!-- Add restrictions beyond the framework baseline.
Example:
- Do not write directly to the production database from tests
- Do not commit .env files even if .gitignored

Prompt yourself:
- What are the easy-to-make mistakes that are specific to this repo?
- Are there tool, environment, hardware, or deployment actions that should never happen casually?
- What "cleanup" or "shortcut" behaviors have already caused pain here?
-->

- MVP may group buyers by nickname within one community (`scope_key`), accepting same-name/rename risk as the owner decided. Preserve occurrences and manual split/merge corrections; absent author IDs alone do not require per-comment mapping.
- Do not use nickname grouping, text hashes, UIA RuntimeId or row positions as proof of stable source-comment identity or edit/cancellation events.
- Do not add totals from successive snapshots or infer cancellation from an incomplete capture.
- Do not issue a formal procurement report from partial/unknown data or unresolved blocking review items.
- Do not collect tokens, use private LINE endpoints, send messages, change notes, or process real buyer data as part of governance onboarding.
- Do not commit buyer data, databases, local evidence, credentials or generated runtime artifacts.
- Do not infer product acceptance, native lifecycle support, branch protection, release readiness or complete governance from a static PASS.

## Project Entry Points

<!-- governance:memory_authority -->
memory_root: memory/
external_memory_allowed: false
operational_records_must_stay_under_memory_root: true

- Read `governance/SYSTEM_PROMPT.md`, `governance/AGENT.md`, root `PLAN.md` and applicable `memory/` files before non-trivial repo work.
- Root `PLAN.md` owns current phase and anti-goals. `docs/PLAN.md` and `docs/SLICES.md` describe the product design and acceptance cases.
- The framework is the pinned `ai-governance-framework/` submodule. Initialize it with `git submodule update --init --recursive`.
- Run `python scripts/check_governance.py` for repo onboarding checks. Install local hooks as described in `docs/GOVERNANCE_ONBOARDING.md`; cloning alone does not install them.
- The Python order application is not implemented. Governance checks and their fixtures are not order-parser tests.

<!-- AI Governance Framework: agent-contract BEGIN -->
<!-- AI Governance Framework: agent-contract v1.1 -->
<!-- Source: ai-governance-framework/governance/agent-contract-template.md -->
<!-- Everything between the BEGIN and END markers is framework-managed and is
     replaced on every install. Repository-specific rules belong outside this
     block; the installer preserves them. -->

## Governance Contract Output (MANDATORY)

The rules below are projected verbatim from the canonical source named in the
projection header, which carries the projection version and the content digest
of that canonical section. Do not edit them here; they are replaced on install.

<!-- ai-governance:checkpoint-projection BEGIN version=1.1 source=governance/SYSTEM_PROMPT.md#2.8 sha256=bde31e2dbdfbb3b07421248db57e202f52cf9f20523094ea390b8913817a80bf -->
### 2.8 Governance Contract Output

在以下時點輸出此 block：
- task 開始
- milestone 完成
- scope 改變
- stop / escalation 事件
- 任何 contract 欄位發生實質變化時

若只是 routine progress commentary 且 state 未變，可省略。

```text
[Governance Contract]
LANG     = <value>
LEVEL    = <value>
SCOPE    = <value>
PLAN     = <current phase> / <sprint> / <task>
LOADED   = <comma-separated list of loaded governance docs>
CONTEXT  = <context name> -> <responsible for X>; NOT: <not responsible for Y>
PRESSURE = <SAFE|WARNING|CRITICAL|EMERGENCY> (<line count>/200)
         # 或 <LEVEL> (<line count>/200 lines; <char count> chars)
AGENT_ID = <agent-id>       # optional; required in multi-agent sessions
SESSION  = <YYYY-MM-DD-NN>  # optional; required when AGENT_ID is present
```

欄位規則：
- `LANG`: 取自 `C | C++ | C# | ObjC | Swift | JS | Python | Verilog | SystemVerilog | GDScript`。
  單一語言直接填該值；跨語言任務以逗號分隔，每個元素都必須是上列值之一（例：`C, C++`）。
  不得把多個語言寫成單一 token（例：`C/C++`）：`/` 已是 `SCOPE` 的 `I/O` 值的一部分，
  在同一個 block 內不能再兼作清單分隔符。分隔符與 `LOADED` 一致。
- `LEVEL`: 單值，取自 `L0 | L1 | L2`
- `SCOPE`: **單值**，取自 `feature | refactor | bugfix | I/O | tooling | review | governance | kernel-driver`。
  `SCOPE` 會決定 review、testing 與 governance routing；多值會引入未定義的優先序與衝突語義，
  因此不接受清單。任務橫跨多個 scope 時，拆成多個 task 或選擇主導的那一個。
- `PLAN`: 取自 `PLAN.md`；若人類明確授權 governance analysis，可標 `Out-of-scope`
- `LOADED`: must name governance docs actually loaded into the agent context. It must include `SYSTEM_PROMPT`; `HUMAN-OVERSIGHT.md` is human-only authority and must not be listed as loaded unless a human explicitly provides it.
  每個項目以逗號分隔。文件識別採**最後一段路徑、可省略 `.md`**，因此下列四種寫法識別為同一份文件：
  `SYSTEM_PROMPT`、`SYSTEM_PROMPT.md`、`governance/SYSTEM_PROMPT.md`、
  `ai-governance-framework\governance\SYSTEM_PROMPT.md`。
  正規化規則：`\` 一律視為 `/`；取最後一段；**只有 `.md` 可省略**，其他副檔名不得省略；
  比對**區分大小寫**。因此 `SYSTEM_PROMPT.txt`、`MY_SYSTEM_PROMPT.md`、`system_prompt`
  都不是 `SYSTEM_PROMPT`。寫出完整路徑比裸 token 攜帶更多可稽核資訊，兩者同等合法。
- `CONTEXT`: 必須同時包含 `->` 與 `NOT:`
- `PRESSURE`: 必須含 label 與**實際的** line count，兩種形式擇一：
  - `<LEVEL> (<line count>/200)`
  - `<LEVEL> (<line count>/200 lines; <char count> chars)`
  第二種形式存在的理由：§7.4 的判級依據是「行數**或**字元數任一達標」，只寫 line count
  時，因字元數達標而升級的判定在 contract 裡無法被檢視。需要說明判級理由時用第二種。
  兩個數字都必須是實際整數；分母固定 200。`(<line count>/200)` 這種未替換的樣板、
  `(pending exact line count/200)` 這類佔位字串、非數字與負數都屬格式錯誤。
- `SESSION`: 當 `AGENT_ID` 存在時必填

格式錯誤的 contract block 屬於 governance failure。
<!-- ai-governance:checkpoint-projection END -->

### When SYSTEM_PROMPT.md is not loaded

`LOADED` must name governance documents actually loaded into this context, and
the canonical rules require `SYSTEM_PROMPT` among them. This block is a
projection of one canonical section — it is not `SYSTEM_PROMPT.md`, and its
presence is not evidence that `SYSTEM_PROMPT.md` was read.

When the canonical `SYSTEM_PROMPT.md` has not actually been loaded, no compliant
`[Governance Contract]` block can be produced. Emit this notice at the same
checkpoints instead, and never emit a block whose `LOADED` names documents that
were not read:

```text
[Governance Contract: UNAVAILABLE]
REASON  = governance context incomplete
MISSING = SYSTEM_PROMPT
SOURCE  = agent instructions (checkpoint projection)
NEXT    = load the canonical SYSTEM_PROMPT.md, or ask the human to provide it
```

Reading `SYSTEM_PROMPT.md` during the session clears the notice, and that change
to `LOADED` is itself a material contract change — emit the full block at that
point. Resolve the canonical path against this repository's governance root; it
may sit under a submodule or contract directory rather than `governance/` at the
repository root.

<!-- ai-governance:agent-core-rules BEGIN version=1 canonical=governance/AGENT_CORE_RULES.md -->
## Agent Core Rules (MANDATORY)

Identical on every agent surface. Repository rules may add duties; they never relax these.

1. **Owner Gate.** Every agent needs explicit owner approval before merging into main, publishing or releasing, deleting branches, closing another person's PR, any irreversible operation, firmware operations, data-integrity operations, and any high-risk operation this repository's own rules name. No directive, slice approval or protocol relaxes this gate.
2. **Commit and push.** Memory and delivery protocols define order, not git authority. Commit and push follow the owner's current authorization and this repository's rules; inside an owner-authorized slice they may continue without re-asking. If either is missing from your context, ask.
3. **Task DONE is not session end.** After task DONE, stop and do no extra work. A confirmed session end still requires the existing session-end closeout. An ordinary Stop event, a final answer, or a subagent finishing is not session end.
4. **Must-record events.** Memory or PLAN updates these events require are part of that delivery, not extra work. A task limited to named files still includes these records unless the owner explicitly excludes them. After DONE, add no unrelated rollups or new PRs; do not record micro-steps or duplicate a record. Repository-specific record duties still apply. An agent's private or tool-provided memory (for example Claude auto-memory or the Copilot memory tool) may help the agent, but never satisfies these records; only the records named here or by this repository, written through their own contracts, do.

| Event | Record in |
|---|---|
| Architecture decision | `memory/02_workflow.md`; `PLAN.md` only when it changes PLAN scope, phase, anti-goal or another existing PLAN obligation |
| Bug fixed with root cause identified (new gotcha / solution) | `memory/03_knowledge_base.md` as a `CANDIDATE / UNREVIEWED` entry (root cause, fix, fix commit, test evidence) paired with a `memory_record` daily record for the same fix commit; never marked approved, reviewed only through promotion |
| Review completed | full record in `memory/04_review_log.md`, one-line summary in `memory/01_active_task.md` |
| Milestone reached | `memory/01_active_task.md`; `PLAN.md` phase/sprint only when it changes PLAN phase, scope, anti-goal or another existing PLAN obligation |
| Risk or incident encountered | `PLAN.md` risk section + `memory/01_active_task.md` |
| Confirmed session end | canonical `memory/YYYY-MM-DD.md` record through the session-end closeout when it is non-stateless |

Use an alias only when this repository has adopted the `SYSTEM_PROMPT.md` section 6.1 alias schema (`02_project_facts.md`, `03_decisions.md`, `04_validation_log.md`); never assume an alias that does not exist.

5. **No fabricated evidence.** Never claim a document was loaded, an authorization was given, or work was completed without evidence in this context. Filling `LOADED` or any other contract field by inference, or reusing a stale `[Governance Contract]` block such as one from an earlier session, is a governance failure. The block is evidence of what was loaded, not a formatting ritual.
6. **Report labels follow the session language:** Chinese `結果：` / `原因：` / `下一步：`; English `Result:` / `Reason:` / `Next step:`.
7. **Secrets.** Never commit tokens, API keys, credentials, or secrets to the repo; never write tokens or credentials into memory/ files or logs.
<!-- ai-governance:agent-core-rules END -->

## Delivery Convergence (MANDATORY)

1. **Product slice first.** Finish the approved, usable product slice before adding governance surface, unless an observed failure requires it (unsafe behavior, irreversible failure, false positive/negative, authority escalation, replay inconsistency, production ambiguity).
2. **Failure-driven only.** Future extensibility, completeness or "might be useful later" are not triggers. If a finding is confirmed unrelated to the approved slice and non-blocking to the current decision, note a one-line disposition under next options and continue the approved work; do not open a new task, PR or gate. If its current-decision impact remains unknown after a bounded check, or a credible safety, authority or data-integrity risk exists, escalate.
3. **Scope-matched checks.** Validate the changed scope first; no full regression or broad smoke unless DONE or the user requires it. Re-review checks prior blockers and the correction delta; a new HEAD does not reopen subsystem qualification.
4. **Stop at DONE.** Report extra work as next options only. An explicit bounded directive authorizes work inside its stated boundary without redundant confirmation; an ambiguous "continue" without an approved next slice is audit-first.

This never relaxes owner-gated actions or commit and push authority (Agent Core Rules above). It never cancels memory or PLAN updates that this repository's rules explicitly require, or session-end closeout; it does not license other status work after DONE.
<!-- AI Governance Framework: agent-contract END -->
