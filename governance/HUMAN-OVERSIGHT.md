---
audience: human-only
authority: reference
can_override: false
overridden_by: ~
default_load: never
---

# HUMAN-OVERSIGHT.md
**人類升級與監督協定 - v3.1**

> **Version**: 3.1 | **Priority**: 2（安全閥）
>
> 定義何時可以繼續、何時應該 escalate、何時必須 stop。
> 其他文件中的 escalation 行為，最終都以這份文件為準。

---

## 1. Decision Classes

### 1.1 Continue

當以下條件成立時，agent 可以繼續：
- task 有明確邊界
- risk 低
- evidence 可以在本地蒐集
- 沒有把重要的人類 trade-off 隱藏起來

### 1.2 Escalate

當以下條件成立時，agent 必須 escalate：
- requirement 存在實質歧義
- 有多條合理路徑，且 trade-off 不同
- architecture impact 還不清楚，但尚未踩到硬紅線
- dirty worktree overlap 或 commit scope ambiguity 存在
- 可以先走安全的 partial path，但下一步需要人類方向

### 1.3 Stop

當以下條件成立時，agent 必須 stop：
- 已觸發硬 safety 或 architecture red line
- governance 文件之間存在實質衝突
- correctness 無法被合理辯護
- 高風險動作需要人類授權

> **不要把所有不確定性都當成 stop。除非真的踩到紅線，否則先用 escalate。**

---

## 2. Escalation Procedure

當需要 escalate 時：
1. 說明不清楚的是什麼
2. 說明若不受控繼續，風險在哪裡
3. 提出一到三個具體選項與預期影響
4. 等待人類指示

不要猜測。不要在重大歧義下默默替人類選方向。

---

## 3. Stop Procedure

當需要 stop 時：
1. 指出觸發的規則或紅線
2. 說明為什麼安全繼續已無法辯護
3. 描述最近的安全 rollback 或 containment step
4. 等待人類授權

---

## 4. Authority Boundary

Agent 可以在安全邊界內：
- 分析
- 提案
- 實作
- 驗證
- refactor

只有人類可以在仍有重大不確定性或真實高風險偏離下授權方向。

---

## 5. State Recovery

發生中斷後：
1. 重讀 `memory/01_active_task.md`
2. 重新驗證 `LANG / LEVEL / SCOPE`
3. 在繼續前，先重述上一個已知 task state

不要假設先前的 governance state 仍然有效。

---

## 6. Audit Trail

每個有意義的 task 都應留下人類可讀的 trace，至少包含：
- start / end 或 current status
- `LANG / LEVEL / SCOPE`
- bounded context
- 關鍵決策
- 套用的 guardrail
- trade-off、escalation 或 stop 理由

這些紀錄必須讓人類看得懂，且能對應回 governance 規則。

---

## 7. Final Principle

> **Autonomy 在 accountability 開始的地方結束。**
> **Escalation 是為了處理有意義的不確定性；stop 是給真正無法安全辯護的情況與紅線風險。**
