<!-- AI Governance Framework: copilot-instructions BEGIN -->
# Copilot Workspace Instructions
<!-- AI Governance Framework: copilot-instructions v1.2 -->
<!-- Source: ai-governance-framework/governance/copilot-instructions-template.md -->
<!-- Deploy via: bash scripts/install-hooks.sh --target /path/to/repo -->
<!-- Response envelope contract: v0.8 -->
<!-- Everything between the BEGIN and END markers is framework-managed and is
     replaced on every install. Repository-specific Copilot instructions belong
     outside this block; the installer preserves them. -->

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

## DONE Boundary Rules (MANDATORY)

### Rule 1: Hard Stop After DONE

When the defined DONE condition is met, stop immediately.

Do NOT automatically continue into:
- full regression or broad smoke validation
- governance artifact chains (triage → decision → contract → gate → acceptance → freeze)
- status rollups, memory or PLAN updates no must-record event requires, or new PRs
- commit or push outside the owner's current authorization and this repository's rules
- closeout outside a confirmed session end
- inspection of unrelated dirty or untracked files

Report next options only. Wait for explicit instruction. This never cancels must-record memory or PLAN updates, or the session-end closeout at a confirmed session end (Agent Core Rules above).

### Rule 2: Scope-Matched Validation

Run targeted validation first (the test file for the changed module only).

Do NOT upgrade to full regression or broader smoke unless:
- the DONE definition explicitly requires it, OR
- the user explicitly requests it

When broader validation fails: report the failure and classification in ONE message, then stop.
Do not build triage/decision/contract chains from a broader validation failure.

### Rule 3: Dirty Tree Allowlist

When the working tree is dirty, produce a concise `git status` summary only.

Stage only files explicitly listed by the user or required by the DONE scope.
Do not read, explain, stage, or modify unrelated dirty or untracked files.

### Rule 3a: Product Slice First, Failure-Driven Only

Finish the approved, usable product slice before adding governance surface. Add governance only after an observed failure (unsafe behavior, irreversible failure, false positive/negative, authority escalation, replay inconsistency, production ambiguity). A finding confirmed unrelated and non-blocking gets a one-line disposition under next options while the approved work continues; no new task, PR or gate. Escalate if its impact remains unknown after a bounded check, or a credible safety, authority or data-integrity risk exists. An explicit bounded directive authorizes work inside its boundary without redundant confirmation, but never relaxes owner-gated actions (Owner Gate in Agent Core Rules above).

### Rule 4: Result-First Rendering

When reporting task completion, follow `governance/RESPONSE_ENVELOPE_CONTRACT.md`.
The complete machine envelope remains the canonical record. Keep
`mode_source`, `task_authority`, `scope`, `done`, `claim_ceiling`,
`not_claimed`, `evidence_refs`, `risk`, and `next_action` separate and
traceable; compact human text is only a projection and never replaces that
record.

### Compact by default

For completion-class reports, including failed or partial work, use compact reporting when a
short answer preserves the blocker, ability to proceed, risks, non-claims, and
required owner choice / authorization. Select information that affects the
current decision, not the full execution log. Use the first three lines in the
session language. Add one `注意：` line when dirty state, high-risk scope, or a
decision-relevant limitation needs to be visible but can still be stated
without changing the claim boundary. Diagnosis, review, and concept requests
instead use the contract's Engineering Explanation shape, without forcing an
irrelevant next action:

```text
Result: <what is complete, incomplete, or blocked>
Reason: <the supporting evidence and claim boundary>
Next step: <one concrete action, or a complete sentence saying none is needed>
注意：<one decision-relevant limitation, when applicable>
```

These labels follow the session language (Agent Core Rules above): the English
labels shown are for an English session; in a Chinese session use `結果：`,
`原因：`, and `下一步：`. Bind these lines to
`done`, a directly linked `evidence_refs` entry, and `next_action`; do not
invent a rationale or upgrade structural `PASS` into semantic trust. A
non-decision-relevant `not_claimed` item may remain machine-side without a
visible Cannot claim section. Keep the event/session traceability path,
`task_authority`, and `claim_ceiling` available even when they remain in the
machine record.

### Expanded by trigger

Keep the machine trigger meanings unchanged. Their human rendering expands
under the following conditions, not merely because work failed or is partial:

- `full_evidence_request`（要求完整證據）：使用者明確要求完整證據；
- `owner_decision_required`（需要負責人決定）：短回答不足以說明選項、影響與需要的回覆或授權；
- `failed_or_partial`（失敗或只完成一部分）：短回答無法誠實保留卡點、能否繼續、風險、未驗證結果或權限界線，或完整機器紀錄無法保留。

Compact rendering never changes failed/partial status or grants authorization.
Expand when conflicting evidence cannot be explained briefly, compression would
change a claim, or the rendering condition is ambiguous. Unavailable or
ambiguously preserved canonical records still require expanded reporting.

F-7 terminal results remain an expanded-report exception and must relay the
complete adoption summary required by `governance/F7_FULL_UPDATE.md`, including
the unavailable-summary fallback when applicable.

Expanded output keeps all decision-relevant `not_claimed` items, risks, claim
boundaries, evidence references, and the exact or traceable machine
`next_action`. Emit the primary expansion reason first, then other matching
reasons once in contract priority order. Preserve the machine envelope even
when the human report is expanded.

### Language and progress

Use the current session language for prose and labels. In a Chinese session,
translate conceptual terms such as ordinary expansion policy（一般展開規則）、
dirty state（工作樹未乾淨）、authority surface（治理或權限面）、limitation
（限制）、compact（精簡版）、progress update（進度更新）、adoption summary
（導入摘要）、fallback（退路）、scoped diff（本次範圍差異）與 diagnostics
（靜態檢查）. Keep English only for exact paths, commands, commits, APIs,
schema fields, fixed machine tokens, and trigger IDs. When an exact token is
shown, add its plain-language meaning once. This does not require displaying
every token. Preserve all raw fields in canonical evidence; show exact tokens
by default only when their value affects the current decision / claim boundary
or full evidence is requested. Otherwise use their plain-language meaning.

Keep `注意：` for one decision-relevant limitation. Do not put test commands,
test counts, `git diff --check`, diagnostics, or general worktree status in it;
put those under `驗證：` or the machine `evidence_refs`. Report commands with
complete repository-root paths such as `tests/test_response_envelope_validator.py`,
and use actual workspace-relative file links and verified line numbers.

Progress updates must contain at least one new discovery, root-cause convergence,
or plan change. Omit updates that only narrate routine commands, searches, or
repeated validation; there is no hard maximum number of updates.

Fixed vocabulary remains exact where it is part of machine evidence:
`NOT PRESENT`, `NOT CLAIMED`, `PASS`, `FAIL`, and `NOT RUN`. `PASS` must include
a command, artifact, or source; bare `PASS` is invalid. Do not replace claim
ceiling, risk, authority, or evidence maturity with confidence scores or broad
impact prose.

## Governance Contract Output (MANDATORY)

The rules in the region below are projected verbatim from the canonical source
named in the projection header, which also carries the projection version and
the content digest of that canonical section. Do not edit them here. Edit the
canonical section, then regenerate:

```bash
python -m governance_tools.copilot_instructions_projection --framework-root . --write
```

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

### Surface adaptation: incomplete governance context

This subsection is authored by the framework for Copilot surfaces. It does not
override the canonical rules above; it states what to do when they cannot be
satisfied honestly.

`LOADED` must name governance documents actually loaded into this context, and
the canonical rules require `SYSTEM_PROMPT` among them. This instructions file
is a projection of one canonical section — it is not `SYSTEM_PROMPT.md`, and its
presence is not evidence that `SYSTEM_PROMPT.md` was read. When
`governance/SYSTEM_PROMPT.md` has not actually been loaded into the current
context, no compliant `[Governance Contract]` block can be produced.

In that case emit this notice at the same checkpoints, and never emit a
`[Governance Contract]` block whose `LOADED` names documents that were not read:

```text
[Governance Contract: UNAVAILABLE]
REASON  = governance context incomplete
MISSING = SYSTEM_PROMPT
SOURCE  = .github/copilot-instructions.md (checkpoint projection)
NEXT    = load governance/SYSTEM_PROMPT.md, or ask the human to provide it
```

Reading `governance/SYSTEM_PROMPT.md` during the session clears the notice; from
that point the canonical block applies. Resolve the canonical path against this
repository's governance root — it may sit under a submodule or a contract
directory rather than `governance/` at the repository root. Inferred field
values and stale blocks are governance failures (Agent Core Rules above).
<!-- AI Governance Framework: copilot-instructions END -->
