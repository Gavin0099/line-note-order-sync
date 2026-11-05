---
audience: agent-on-demand
authority: reference
can_override: false
overridden_by: AGENT.md
default_load: on-demand
---

# TESTING.md
**測試策略與品質門檻 - v4.4**

> **Version**: 4.4 | **Priority**: 6（品質守門）
>
> 定義在什麼條件下，我們可以合理相信一段程式碼。
> 測試是 guardrail，不是 KPI。

---

## 1. 核心哲學

- 保護行為
- 防止 regression
- 支持安全 refactoring
- 偏好有意義的 evidence，而不是儀式化 checklist

Coverage 本身不是品質指標。

---

## 2. 測試層級

### L0 - 最低信心

只在 scope 確實很小、rollback 成本也很低時使用。

可接受的 evidence：
- smoke test
- manual checklist
- characterization check
- presentation-only work 的視覺確認
- 有需要時的 before / after screenshot 或同等輕量 UI evidence

`L0` 不得被用來逃避本來就需要的 verification。

對 `L0 fast-track` 工作：
- 只要 task 維持 presentation-only，一個輕量 verification step 就夠
- 除非 task 升出 `L0`，否則不必要求完整 regression matrix
- 一旦變更開始影響 behavior、schema、async flow、或 shared logic，就必須升到 `L1`

### L1 - 可維護

一般工作的預設門檻。

預期 evidence 應包含適用的子集合：
- unit test
- characterization test
- contract test
- build verification
- failure-path evidence

不是每個 task 都需要每一種 test，但每個 task 都要有足夠 evidence 來為其安全性辯護。

### L2 - 關鍵層

必須在以下面向都有強 evidence：
- behavior
- boundary
- integration
- regression
- human-reviewable acceptance criteria

---

## 3. Mandatory Failure-Path Thinking

對 `L1+`，至少要在適用時提供以下 evidence：
- 一個 invalid input 或 invalid state
- 一個 boundary value
- 一條 failure path

若某類別不適用，必須明說。

### 3.1 Critical Function Test Quality

coverage 可以很高，但測試品質仍然很弱。AI 特別擅長把 coverage 灌高，卻避開最難測、也最決策相關的路徑。

當任一條件成立時，該 function 應視為 **critical**：
- 會改變 state（write、delete、command dispatch、irreversible transition）
- 會和 external system 互動（USB、file I/O、network、device API）
- 是其他模組依賴的接縫（public interface、adapter layer、shared entrypoint）
- 曾經是 bug surface，或過去發生過 regression

對 critical function：
- `L1` work 必須涵蓋適用子集合：
  - normal path
  - failure path
  - boundary input
  - invalid input 或 invalid state
- `L2` work 應把這四類視為預設期待，除非某類別明確不適用

若缺任何一類，除非有明講且合理說明，否則不能稱作「fully tested」。

建議命名格式：
- `test_[function]_[scenario]_[expected_outcome]`

較好的例子：
- `test_parse_version_empty_string_returns_none`
- `test_send_command_device_disconnected_raises_error`
- `test_update_firmware_checksum_mismatch_aborts`

避免隱藏意圖的命名：
- `test_case_1`
- `test_parse_version_2`
- `testSendCommand`

### 3.2 Independent Expected-Value Rule

expected result 必須來自 spec、固定範例、invariant、或 independent fixture，**不能**在 test 裡重寫一遍 production algorithm 來算 expected value。

若 test 用與 production 相同的邏輯計算 expected value，兩邊就可能一起錯，測試不再具備獨立驗證價值。這是 AI 最常用來膨脹 coverage、卻沒有增加防禦力的方式之一。

若無法導出 independent expected value，必須明確把這個 test 標成 characterization test 或 weak coverage，而不能把它當 behavior proof。

在 test 內重寫 production logic 是禁止的。

### 3.3 Test Sensitivity and Mutation Thinking

如果一個 test 在合理的邏輯錯誤下仍然會 pass，它就沒有保護力。高 coverage 但低 sensitivity，比低 coverage 但高 sensitivity 更糟，因為它會製造假信心。

對 critical function 與 regression-sensitive path，test 至少要能在合理的邏輯 mutation 下失敗，例如：
- boundary flip（`>` 被改成 `>=`）
- reversed condition
- removed guard clause
- loop bound 的 off-by-one

對 bug fix：新增的 test 必須能在原 bug 被重新引入時失敗。若這次修改裡沒有任何 test 能抓到原 defect 的回歸，就不能說 fix 已有 regression protection。

若無法證明 test sensitivity，coverage claim 必須降級。

Mutation testing 是這條規則的可執行化手段：故意把 production code 改成一個合理的小錯誤，再確認 test 是否失敗。它回答的是「如果這段 behavior 壞了，會不會有人發現」，不是「這段 code 有沒有被跑到」。

使用 mutation testing 時必須保持 scope-aware：
- 優先用在 critical path、regression-sensitive path、或本次 diff 觸及的高風險行為；不要預設全 repo 跑。
- 存活的 mutant 是 reviewer aid 和 test-improvement prompt，代表這裡可能缺少有牙齒的 assertion；它不是自動 blocking gate。
- mutation score 不得變成 KPI。追求漂亮分數會把團隊推向垃圾測試，並破壞這個 signal 的價值。
- 對 AI 生成測試，surviving mutant 可以回饋給 agent，要求它補一個會在該 mutation 下失敗的 test；這比籠統要求「提高 coverage」更可驗證。

### 3.4 Stateful and Sequence Behavior

對 stateful 或 workflow-driven code，只做單點 function test 是不夠的。這類系統最常見的失敗，不是出在單一 function call，而是出在一連串操作之間。

對 stateful 或 multi-step code，應加入 sequence test，驗證：
- 完整 sequence 後的 final state 是否正確
- sequence 中途失敗時行為如何
- retry、rollback、recovery path 後的一致性

依 side-effect 類型還要補：
- external write（DB、file、device）：要 assert persisted state，不只驗證 write function 被呼叫
- shared / global state modification：要有明確 cleanup 或 restoration verification
- async dispatch：要有 completion behavior 與 failure-path evidence；不能把 fire-and-forget 當 fully tested

### 3.5 Pure Function and Never-Raises Contracts

宣告了「never raises」或「always returns well-formed output」保證的函式，需要專屬測試策略。保證本身必須由測試來持守，不能只靠文件說明。

**Never-raises 保證**的測試要求：
- 每種異常輸入類型（`None`、空值、格式錯誤、schema 違反）都必須有獨立測試案例
- 測試必須 assert 回傳值的結構與 status，不能只驗證「未拋例外」
- 最壞情況（完全無效輸入）仍必須回傳有用的 degraded output；測試必須明確斷言這個 degraded output 的形狀

**Graceful degradation**（失敗時回傳 `inject=False` 或等效降級結果）的測試要求：
- 必須覆蓋：目錄不存在、檔案不可讀、JSON 解析失敗、必要欄位缺失
- 每個失敗路徑的測試都必須 assert 降級回傳值的完整結構，不只確認 flag 值
- 降級後的回傳值必須符合與正常路徑相同的 key contract

若一個 function 宣稱 never-raises，但測試套件中沒有針對異常輸入的測試，這個保證不能算已驗證。

---

## 4. Repo-Aware Build Policy

### 4.1 Authoritative Build Config

每個 repo 至少應宣告一個 **authoritative** 或 **known-good** build configuration。

每個 task 的最低期待：
- 驗至少一個 known-good config

### 4.2 Phase-Based Matrix

build breadth 應隨 task risk 調整：

| Task Type | Minimum Build Expectation |
|---|---|
| 低風險 UI / wording / presentation | Known-good config |
| 一般 feature / bugfix / refactor | Known-good config，再加 touched path 需要的驗證 |
| 關鍵邊界 / release / L2 | 擴大到與 boundary risk 相稱的 matrix |

當 repo 現實 baseline 本來就不支持 full Debug / Release 或跨平台 matrix 時，不要硬性要求完整矩陣。

### 4.3 Warning Policy

採用 **baseline-aware** warning policy：
- touched file 不得引入新 warning
- 不得在沒有明確說明的情況下惡化既有 warning baseline
- 若 legacy warning 沒變，不必自動阻擋完成

### 4.4 stdlib-Only Testing Constraints

本專案僅使用 Python stdlib（不允許 `pip install`）。測試必須遵守相同限制：

**允許**：
- `unittest.mock`（stdlib）
- `tempfile`、`pathlib`、`os`、`io` 等 stdlib 模組做 fixture isolation
- `pytest` 作為測試執行器（工具，非 production dependency）

**不允許**：
- 任何第三方測試輔助函式庫（`faker`、`factory_boy`、`responses`、`freezegun` 等）
- 任何需要外部服務或 API key 的測試（除非有明確 mock harness）

若某個 test 看起來需要第三方函式庫，這通常是測試設計問題的信號：應以 injection、fixture、或 in-process stub 取代。

注意：test runner（`pytest`）本身不受此限制；限制對象是 production dependency 和 test-helper libraries。

---

## 5. Legacy Refactor Baseline Validation

對 legacy repo 的 refactor，必備 baseline evidence：
- baseline commit 或 rollback point 的 build 結果
- modified state 的 build 結果
- canonical toolchain 與 canonical build command 的確認

若 baseline 本身無法 build，必須明示這次工作是在 unstable baseline 上進行，不能把它表述成 clean、regression-proof 的 refactor。

---

## 6. Evidence Templates

### 6.1 Minimum Refactor Evidence

可接受的 evidence 例如：
- before / after build result
- touched-file diff review
- key call-chain comparison
- characterization 或 smoke verification，證明核心 behavior 未變

### 6.2 High-Risk Rule Evidence

對高風險工作，evidence 應具體且能讓人 review。例子：

| Rule Type | Acceptable Evidence Examples |
|---|---|
| Flash / sequencing safety | before/after diff、ordered call-path list、build pass、explicit unchanged sequence note |
| Layer boundary | touched entrypoint list、dependency-path inspection、確認無 direct forbidden access |
| Thread safety | UI update path list、dispatcher usage 確認、failure-path note |
| Legacy baseline | canonical toolchain、canonical build command、baseline build、modified build |

不要在沒有指出 evidence 的情況下宣稱 `verified`。

### 6.3 Cross-Tool Integration Evidence

當一個 task 修改的 governance tool 與其他工具有跨邊界互動（例如 `session_start` → `session_end` → audit），evidence 必須涵蓋**邊界**，不只是單個工具。

兩個各自通過的 unit test 不等於 integration evidence。

可接受的 integration evidence：
- 涵蓋完整呼叫鏈的 end-to-end test，使用現實輸入
- 跨邊界的 return dict shape 驗證（不只驗單一函式內部）
- producer 輸出降級時，consumer 能正確處理的測試

**不**算 integration evidence：
- 兩個獨立 unit test 各自通過
- 只測試 happy path 的 integration sequence
- mock-only 驗證 downstream function 被呼叫

典型需要 integration evidence 的邊界：
- `session_end` 寫入 canonical → `session_start` 讀取並注入 context
- `write_candidate()` 寫入 → `build_canonical_closeout()` 處理 → `closeout_audit` 聚合
- `pre_task_check` 完成 → `post_task_check` 接收 contract

---

## 7. Hard-to-Test Areas

對 I/O、native、time、environment、或 legacy code：
- 能 isolate 的先 isolate
- 單元級 coverage 不現實時，用 characterization
- 偏好 observed behavior，而不是 mocked fantasy

會遮蔽真實風險的 mocking 是禁止的。

### 7.1 Assertion and Mocking Discipline

每個 test 至少應有一個清楚 assertion，針對：
- output value
- state change
- emitted error 或 failure signal

除非行為本身就是「不拋例外」，且 test name 已明說，否則不能把「沒有 exception」當成唯一通過條件。

較好的 assertion 風格：
- `assert result == expected_value`
- `assert device.state == DeviceState.DISCONNECTED`
- `assert "checksum mismatch" in error_log`

只斷言 collaborator 被呼叫的 mock-only test 不夠。例如：
- 弱：`mock_device.send.assert_called_once()`
- 較強：assert resulting status、emitted output、或 persisted state

測試也必須保持獨立：
- 每個 test 都應可單獨執行
- setup / teardown 必須恢復環境
- mutable state 不得跨 test 洩漏
- device、file、port、或 external resource setup 必須在每個 test 中明確處理

### 7.2 Determinism and Flakiness Control

測試必須 deterministic。若一個 test 多跑幾次結果不一致，它就不是 test，而是雜訊。

除非 nondeterminism 本身就是被測行為，否則避免依賴：
- wall-clock time 或 `datetime.now()`
- 未 seed 的 random
- test 執行順序
- 跨 test 共享的 process state 或 global singleton
- `sleep()` 或 timing-based synchronization

若 system under test 真的牽涉 time、random、或 async scheduling，應透過 injection 控制：fake clock、seeded random、explicit harness control、或 deterministic event replay。

若測試依賴未受控的 time、random、或 execution order，卻仍宣稱 stable，屬於禁止行為。

### 7.3 Trust Boundary Tests

宣告了信任邊界的元件（例如「只讀 canonical，不讀 candidates」）必須有測試驗證該邊界確實被遵守。信任邊界違反是**靜默失敗**：結果看起來有效，但資料來自不受信任的來源。

**Trust boundary test 的要求**：
- 若元件宣稱不讀取路徑 X，測試必須在路徑 X 存在且有資料的情況下，驗證結果不受其影響
- 不能只測試「有讀取路徑 Y」；必須同時測試「沒有讀取路徑 X」
- 每條已宣告的 trust rule 至少對應一個 boundary test

本專案中典型的 trust boundary pattern：

| 元件 | 宣告的信任規則 | Boundary test 驗證方式 |
|---|---|---|
| `closeout_audit` | 只讀 `artifacts/runtime/closeouts/` | 在 candidates dir 放資料，確認 audit 結果不受影響 |
| `_canonical_closeout_context` | 只讀最新 canonical（依 `closed_at`）；不讀 session-index | 在 session-index 放舊資料，確認 context 回傳的是正確 canonical |
| `run_session_end` 整合 | canonical 只由 system 寫入；AI candidate 為 untrusted input | candidate 為 schema invalid 時，canonical status 正確反映，不 propagate candidate 的 fields |

若一個元件宣稱有 trust boundary，但 test suite 中沒有任何 boundary test，這個宣告不能算已驗證。

### 7.4 Behavior Source and Test Plan Requirement

沒有可信 expected behavior source 的 test，不是 test，而是猜測偽裝成 verification。

生成 test 前，先識別 expected behavior 的來源：
- specification 或 design doc
- public contract 或 interface definition
- 具有可重現步驟的 bug report
- reviewer 或 product owner 提供的 acceptance criteria
- known-good output 的 existing characterization baseline
- 明確 reviewer instruction

若沒有可信來源，必須明說，並下調所有產出測試的 confidence label。不能只靠閱讀現有 implementation 並假設它是對的，就當作 expected behavior source。

對 non-trivial work，寫 test code 前先給一個簡短 test plan。至少指出：
- behavior source（誰授權這個 expected behavior）
- risk level 與 task classification
- candidate critical path 與 failure path
- 哪些 category 明確不適用，以及理由

這個順序是為了防止 AI 最常見的失敗模式：在 behavior contract 都還沒立起來前，就先生成大量結構正確但價值很低的測試。

---

## 8. Test Gap Records

當一個有意義的 test 目前做不到時，必須記錄：
- 原因
- 風險
- remediation condition

若沒有 remediation condition，就是隱藏技術債。

### 8.1 Gap Record Format

每筆 gap record 必須自我完備，包含：

```text
GAP: [工具名稱或函式名稱]
REASON: [為何目前無法寫出此測試]
RISK: [哪些失敗模式目前無法被偵測]
REMEDIATION: [什麼條件成立後，這個 gap 應該被關閉]
```

範例：

```text
GAP: linear_integrator API response validation
REASON: 無 test mode 或 mock API key；CI 環境無法連線外部服務
RISK: 格式錯誤的 API response 在 runtime 才會被發現
REMEDIATION: 加入 recorded fixture 或 in-process mock server 後
```

若無法填寫 REMEDIATION，表示此 gap 為**永久技術債**，必須明確標記，不能靜默略過。

Gap records 的位置：直接寫在本節，或寫在對應工具的 `tests/` 目錄下的 `GAPS.md`，兩者選一，保持一致。

---

## 9. Definition of Done

工作完成的條件是：
- 選用的 evidence 與 task risk 相稱
- build verification 符合 repo reality
- relevant failure-path thinking 已套用
- critical function 有真正的 behavior assertion，而不是儀式化 coverage 或 mock-only check
- bug fix 在可重現時，與修復同一 change 中附上 regression test
- 後續 reviewer 能理解為什麼這次變更被視為安全

以下做法明確禁止，無論 test count 或 coverage 百分比多高，都不算 evidence：
- 在 test 中重寫 production logic
- 在沒有 independent expected-value reasoning 下宣稱 fully tested
- 對可重現 bug 沒有 regression test 卻宣稱 regression-safe
- 依賴未受控的 time、random、或 execution order，卻宣稱 stable test
