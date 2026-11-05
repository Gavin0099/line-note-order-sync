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
