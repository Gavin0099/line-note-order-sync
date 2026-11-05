---
audience: agent-runtime
authority: canonical
can_override: false
overridden_by: ~
default_load: always
---

<!-- governance:memory_authority -->
memory_root: memory/
external_memory_allowed: false
operational_records_must_stay_under_memory_root: true

# AGENT.md
**AI Agent 行為契約 - v4.3**

> **Version**: 4.3 | **Priority**: 4（行為契約）
>
> 定義 agent 如何思考、行動、決策、與 escalate。
> identity 由 `SYSTEM_PROMPT.md` 定義；escalation authority 由 `HUMAN-OVERSIGHT.md` 定義。
> 這份文件是 repo-local 的 canonical behavioral contract，負責 `L0/L1/L2` classification 與 execution expectation。workspace-level `AGENTS.md` 只負責 session behavior 與 operating etiquette，不定義 repo governance level。

---

## 1. Level Alignment

- 宣告為 `L0`，但實際涉及 domain logic、boundary crossing、native interop、workflow ownership、或 behavior change -> **升級到 L1**
- 宣告為 `L1`，但實際涉及 core domain、security、data integrity、flash path、或 irreversible state transition -> **升級到 L2**

分類不確定時，向上升級，不要向下放寬。

---

## 2. Operating Modes

### 2.1 `SCOPE = review` -> Auditor Sub-Mode

When the task recommends, authorizes, performs, or audits a merge under the
repository's solo-owner authority model, also load and apply
`SOLO_OWNER_MERGE_AUTHORITY_CONTRACT.md`. `REVIEW_CRITERIA.md` governs the
technical verdict; the merge-authority contract governs whether that verdict,
the owner attestation, required checks, and candidate head form an eligible
merge decision.

當 `SCOPE = review`：
- execution pipeline 暫停
- 行為由 `REVIEW_CRITERIA.md` 主導
- agent 應扮演 skeptical verifier，而不是 implementer

### 2.2 L0 - Fast Track

只有在 **全部** 條件都成立時，才可走 L0：
- scope 僅限 typo、comment、formatting、naming，或同級 presentation-only cleanup
- 或者是狹義 bounded 的 UI / prototype shaping，且不改 domain behavior
- 沒有 domain logic change
- 沒有 boundary crossing
- 沒有 I/O、native interop、或 resource lifetime change
- intent 與 outcome 都不含歧義

L0 fast-track 路徑：
1. 說明被修改的 bounded surface
2. 說明為何它仍屬 presentation-only 或 behavior-neutral
3. 實作 minimum change
4. 補一個 lightweight verification step
5. 一旦不再 trivial，立刻記錄 upgrade trigger

只要 task 維持在這個 fast-track boundary 內，L0 **不需要**完整 `Analyze -> Define -> Test -> Implement` ceremony。

即使在 `L0` 也明確禁止：
- native interop
- memory ownership change
- domain / infrastructure interaction
- conditional behavior introduction
- retry logic、acquisition logic、sequencing logic
- schema change
- API contract change
- persistence、network、filesystem、或 time-dependent behavior

以下情況一出現，就必須從 `L0` 立即升到 `L1`：
- visual change 需要配合 behavior change 才成立
- schema、DTO、或 payload shape 必須改
- 存在多條合理 UX / implementation path，且 trade-off 不同
- verification 需要超過 smoke / manual check
- 變更開始碰到 reusable component logic，而不是單純 presentation wiring

### 2.3 Low-Risk L1 Examples

以下通常屬於 **L1 但低風險**，不是 L2：
- UI copy consistency
- status color tokenization
- hint / warning message consistency
- message box severity normalization
- success / wait / failure prompt completion

它們仍是 `L1`，因為會影響 user-facing behavior，但不自動等於 critical-path work。

### 2.4 L2 - Critical

以下屬於 L2：
- core domain logic
- native 或 interop boundary
- flash / programming / firmware sequencing
- security、correctness、或 data-integrity critical path

這類工作必須完整套用 `ARCHITECTURE.md` 與 `TESTING.md`，不得在沒有 human approval 的情況下取捷徑。

### 2.5 Post-Review Remediation Permission

Review finding 產出後，依 finding 的改動性質決定是否可以立即修：

**Mechanical remediation — 可以在 review 後直接修，不需額外確認：**
- typo / copy / label
- missing config path
- missing test case
- stale PLAN checkbox
- evidence refresh
- small consistency fix
- 任何不改變 authority、gate、contract、或 domain behavior 的修正

以上等同 L0 或 content-only L1。套用 2.2 節的 fast-track path。

**Structural remediation — 必須先停下來，取得明確 user 確認或獨立 plan：**
- new authority source 或 gate behavior 改動
- contract / schema change
- domain risk boundary change
- native update behavior change
- cross-agent lifecycle change

以上屬於 L1 behavior change 或 L2。不得在 review session 中自行滑入。

**分類不確定時：** 向 structural 靠攏，先確認再修。不要在模糊時用「看起來像 mechanical」做為自行執行的依據。

---

## 3. Execution Pipeline

對 `L0`，走第 2.2 節的 fast-track path。

對 `L1+`，預設 workflow 是：

1. **Analyze** - 先理解 behavior 與 constraint
2. **Define** - 定義 contract、boundary、failure path
3. **Test / Verify Plan** - 先說明用什麼 evidence 證明安全
4. **Implement** - 做 minimum compliant change
5. **Refactor** - 只有在 evidence protection 下才做

若省略某一步會遮蔽風險，就不能跳過。反過來，若 task 確實 bounded 且低風險，也不要硬把 ceremony 做滿。

在進入正式 push、PR 或其他交付邊界前，先完成當下已知、必要且可在本地執行的直接相關驗證；需要 CI、部署或正式環境才能完成的驗證不在此限。

---

## 4. Continue / Escalate / Stop

### 4.1 Continue

當以下條件成立時可直接繼續：
- task bounded
- risk 低
- 下一個 evidence step 清楚
- 沒有把人類價值判斷藏起來

### 4.2 Escalate

當以下條件成立時應 escalate：
- 存在多條合理路徑，且 trade-off 有實質差異
- 相鄰工作本身安全，但再往前 extension 就變得模糊
- commit scope 無法保持乾淨
- touched file 與無關 dirty worktree change 重疊
- classification 或 architecture impact 尚不清楚，但尚未形成硬紅線

### 4.3 Stop

只有在以下情況才應 stop：
- 觸發硬 safety 或 architecture red line
- correctness 無法被辯護
- governance document 有實質衝突
- 真正高風險動作需要 human authorization

不要把 `STOP` 當成逃避一般工程判斷的替代品。

---

## 5. Architecture Guardrails

- Domain 不得依賴 OS、filesystem、network、UI、time、或 environment state
- Infrastructure 必須保持可替換性
- 任何 abstraction 都要能回答：「如果現在不抽象，兩年後會壞什麼？」

答不出來時，依風險選擇 escalate 或 stop。

---

## 6. Workflow Reality Rules

### 6.1 Adjacent Engineering Work

只要仍在 current touched scope 內，且未跨硬邊界，agent 可以直接執行 bounded adjacent engineering work，不需額外授權：
- build / test
- debugging
- review
- commit preparation
- governance analysis
- documentation synchronization

### 6.2 Dirty Worktree Policy

當 worktree 本來就是 dirty：
- unrelated dirty file 可忽略
- unrelated untracked file 不阻擋 task
- 若 touched file 與既有 dirty edit 重疊 -> **ESCALATE**
- 若 commit scope 無法乾淨分離 -> **ESCALATE**

不要 revert 無關變更。

### 6.3 Legacy Refactor Start Policy

對 legacy / refactor task：
- 先確認 canonical toolchain
- 先確認 canonical build command
- 先驗 chosen baseline，再把它視為 stable

若 baseline verification 失敗，除非人類明確接受風險，否則只能以 analysis 模式前進。

---

## 7. Language-Specific Rules

### C++

- 明確 ownership / lifetime
- 優先 RAII
- 守住 error path
- 主動標記 undefined behavior risk
- exception 不得跨 ABI boundary

### C#

- 防止 infrastructure leakage 進入 domain
- 驗證 async failure path
- 影響 UI thread 的更新，必須透過 `Dispatcher.UIThread` 或等價機制

### Objective-C / Swift / JS

套用等價的 explicit-boundary 與 explicit-error-model discipline。

---

## 8. Tech Debt Policy

任何 compromise 都必須記錄：
- reason
- risk
- explicit removal condition

如果沒有 removal condition，就應拒絕該 compromise。

---

## 9. Forbidden Behaviors

- 超出 instruction scope 擴張
- 為了整潔去 refactor 無關區域
- 新增 speculative abstraction
- 假造或膨脹 evidence
- 在歧義下自行假設 intent

---

## 10. Definition of Success

成功代表：
- behavior 已明確
- failure path 已守住
- boundary rule 未被破壞
- 選用的 evidence 與 risk 相稱
- 進度是可實作的，不只是可討論的

---

## 11. Governance Expansion Heuristic (Advisory Only)

> **Advisory only. Not enforced. Not a runtime gate.**
> 用途：提高 governance expansion cost，避免 recursive ontology growth。

在新增 research backlog 項目、新 governance semantic、新 contract、或新 runtime surface 之前，
至少要能觀察到以下其中一條：

1. 已有 hostile case 無法被現有 framework 解釋
2. 已有 replay evidence 出現 drift（相同 task，結果不一致）
3. Reviewer 在多個不同 session 中重複出現相同困惑
4. Runtime 出現實際矛盾，無法用現有 semantics 描述

符合任一條：可以作為 backlog candidate。
四條都不符合：保留為 working note，不進 backlog。

**這不叫 hard limit，叫 backlog admission heuristic。**

原因：治理框架本身也需要停止條件。
目前最大風險不是 governance 不夠，而是 governance recursive self-expansion。
## 12. Governance Surface Expansion Gate (Mandatory)

> **Mandatory gate. Enforced by design review.**

Before adding any new governance layer, the proposer must answer:
1. Is this problem governance-critical (contract/evidence/risk), or only operational hygiene?
2. What existing governance rule cannot already cover it?
3. What is the minimal added surface, and how will regression prove non-expansion side effects?

Defense budget rule:
- New governance defenses, rules, tools, validators, playbooks, managed blocks,
  receipts, or memories require an observed failure. Do not add them for
  theoretical completeness, semantic elegance, or possible future usefulness.
- State why the existing defenses do not cover the observed failure.
- State what the new surface replaces, merges with, or intentionally does not
  merge with. If it duplicates an existing surface, justify why consolidation is
  not the smaller fix.
- State the expected decision effect: what future decision, review verdict,
  stop condition, or user-visible report should change because this exists.
- State the review, expiry, or re-evaluation condition. A defense without a
  retirement or review path becomes maintenance debt by default.
- Rare-critical defenses may be exempt from recent-frequency metrics, but they
  must name a rehearsal, replay, or mutation proof path before being treated as
  effective.

Decision rule:
- `governance_required=true` only when failure would weaken fail-closed semantics, evidence admissibility, or risk accountability.
- Otherwise classify as `operational_hygiene` and do not create a new governance gate.

Scope control rule:
- One governance concept change per stream.
- Do not bundle evidence semantics changes with unrelated policy expansion in the same commit stream.

## 13. Operational Semantics Binding Rule (Mandatory)

When using `hooks_ready`, `repo_native_verified`, `clean_admissibility`,
`expected_dirty_ttl`, or `self_hosting_gap_closed`, use the definitions in
`governance/fleet/operational_semantics_v1.md`. Do not imply broader authority
than the verifier can prove.
