---
audience: agent-on-demand
authority: reference
can_override: false
overridden_by: SYSTEM_PROMPT.md
default_load: on-demand
---

# ARCHITECTURE.md
**架構治理與邊界規則 - v4.3**

> **Version**: 4.3 | **Priority**: 5（結構紅線）
>
> 定義系統如何切分、哪些地方可以改、哪些邊界屬於硬紅線。

---

## 0. 載入條件

- 遇到新功能、refactor、邊界調整、或其他非 trivial 的 L1/L2 工作時載入
- 只要可能有 architecture impact，就應載入；不要等到已經證明出事才載入

---

## 1. 核心原則

### 1.1 Architecture Before Implementation

在實作擴張前，必須先能說清楚：
- 邊界在哪裡
- 責任怎麼分
- 資料怎麼流動

如果連 architecture 都無法清楚表述，實作就還不具備可辯護性。

### 1.2 Explicit Boundaries

每個被碰到的 component 都應能被歸類為以下其中之一：
- Domain
- Application
- Adapter
- Infrastructure

每個 component 都應回答：
- 自己負責什麼
- 自己**明確不負責**什麼

### 1.3 Governance Goal

architecture governance 的目的，是防止災難性耦合與隱性邊界侵蝕。

它應該降低風險，而不是懲罰 trivial、低風險工作。

### 1.4 Framework Operational Posture

本 framework 的目前架構身分是 **audit-first**：核心可辯護能力是讓
AI-assisted engineering 的工作軌跡、證據、claim ceiling 與 closeout 可被
reviewer 稽核與追溯；它不是 security boundary，也不以現有證據宣稱會穩定
改善 agent 行為或交付結果。

runtime treatment（session_start、pre/post-task checks、adapters 與
instruction injection）是實驗性或手動交付能力，不是目前已部署的常態控制。
2026-07-12 live-invoker census 只觀察到 closeout chain 有本機 configured
invoker；treatment 層及 adapter pre/post paths 仍只由 manual、campaign、smoke、
example 或 test 路徑觸發。v3 比較在其單一 task class 的四個 mechanical counts
未觀察到穩定 Arm B advantage。

這是目前 evidence-bound 的架構定位，不改變 runtime、hook、schema、gate 或
enforcement semantics。未來若要主張 treatment 是常態控制或具有 outcome effect，
必須另有已部署的 invoker 與對應的行為／結果證據。

Evidence sources:

- `docs/governance/runtime-treatment-census-live-invoker-check-2026-07-12.md`
- `docs/status/no-governance-baseline-v3-scoring-2026-07-11.md`
- `README.md` trust-model statement

---

## 2. Bounded Context

### 2.1 L1+ 必答問題

在任何 boundary-sensitive work 前，先回答：
- 這件事屬於哪個 bounded context
- 是否涉及 native API、platform variance、或 external system
- 是否需要 Anti-Corruption Layer（ACL）

### 2.2 Continue / Escalate / Stop

- **Continue**：context 與 ownership 清楚
- **Escalate**：大致清楚，但 boundary choice 或 abstraction choice 存在多個可辯護方案
- **Stop**：提議變更已跨越硬邊界，或根本無法一致分類

不要因為需要設計判斷就直接 stop；除非已經踩線，否則先 escalate。

### 2.3 L0 例外

L0 仍只限於 presentation-only 或 trivial edit，條件是：
- 不跨 Domain / Infrastructure
- 不涉及 native / I/O / state interaction
- 不帶隱性行為變更

典型 L0 例子：
- copy 與 wording cleanup
- spacing / layout polish
- 不改 semantic state 的 color / token 對齊
- prototype-only UI composition 調整，且不需要動 domain 或 API

L0 不再只限於 typo-level edit，但只要碰到真實行為或邊界影響，就必須升到 L1。

不確定時，升級到 L1。

---

## 3. Domain vs Infrastructure

### 3.1 Domain 硬紅線

Domain **不得**：
- 直接呼叫 native API
- 依賴 `.dll`、`.so`、`.dylib`、`.framework` 或同類 runtime binding
- 依賴 UI、OS、filesystem、network、time、或 environment state

Domain 應只透過明確、穩定的 interface 消費 capability。

### 3.2 Infrastructure Anti-False-Positive Rule

以下情況**不應自動**被判成 infrastructure leakage：
- pure data transformation
- OS-agnostic utility
- compile-time constant
- presentation-only state mapping

不要用教條式過度擴張，去否定實際上有效的低風險設計。

---

## 4. Anti-Corruption Layer（ACL）

### 4.1 何時必須有 ACL

當以下任一條件成立時，ACL 屬於必需：
- native 或 external model 與 domain language 不一致
- 邊界攜帶 state、side effect、async behavior 或 unstable semantic
- 需要 translation、validation、caching 或 error conversion

### 4.2 何時通常不需要 ACL

- 行為穩定、pure、stateless
- 程式只做運算
- 邊界風險本身不具實質意義

`replaceable` 不等於 `立刻抽象一切`。

---

## 5. Interface Rules

以下情況應引入 explicit interface：
- platform behavior 存在差異
- resource lifetime 不 trivial
- ABI 或 binary stability 很重要
- 邊界預期會獨立於 caller 變動

如果 abstraction cost 大於 boundary risk，就不要引入 speculative interface。

---

## 6. ADR Rules

### 6.1 ADR Trigger

當決策影響以下任何一項時，應建立或更新 ADR：
- memory ownership strategy
- cross-platform loading strategy
- ABI 或 calling convention
- boundary partitioning
- long-lived interface placement

### 6.2 Conflict Check

新增 ADR 前先做：
1. 列出 `docs/adr/` 中相關標題
2. 找出是否有衝突
3. 若有歧義，明確標記 supersession 或 escalate
4. 在新紀錄中連結相關 ADR

沒有做 conflict review 就產出 ADR，屬於 governance failure。

---

## 7. Build Boundary Addendum

build-system wiring 是 architecture 的一部分，不只是 tooling 細節。

硬規則：
- project 只能 include 自己樹內的 header，以及明確核准的 shared layer
- project **不得**把 peer project 的 private directory 加進 include-search settings
- build 成功 **不代表** boundary violation 被合理化
- 如果多個 project 需要同一個 header，應把它移到有明確 ownership 的 shared boundary layer

cross-project private include access 屬於 architecture violation，因為它隱藏耦合並繞過 ownership boundary。

---

## 8. Legacy 與 Refactor 解讀

對 legacy repo 與大型 refactor：
- 隱藏的歷史耦合是風險，不是藉口
- baseline instability 要被顯性指出
- boundary judgment 應以 canonical build environment 為準，不是被隨機 toolchain noise 牽著走

如果 repo 現況讓邊界本身不清楚，就應帶證據 escalate，而不是假裝 architecture 很明顯。

---

## 9. Evidence Expectations

可接受的 architecture evidence 包括：
- touched-layer list
- dependency path 或 include path inspection
- entrypoint / call-path summary
- before / after boundary diff
- 明說哪些東西刻意保持不變

不要在沒有明講 evidence 的情況下宣稱 `architecture-safe`。

---

## 10. Final Principle

> **Architecture 的工作，是防止災難性錯誤，不是阻止正常進度。**
> **硬違規才用 hard stop；真正的設計歧義才用 escalation。**
