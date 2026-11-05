# AI Governance 導入與重現

日期：2026-11-05。此文件描述 repo 導入，驗證結果以提交的證據與實際 PR checks 為準。

## 來源與範圍

- Canonical source：https://github.com/Gavin0099/ai-governance-framework
- 拓撲：repo 內的 `ai-governance-framework/` git submodule；初始 pin 為 `1f5b09e221096b3b4494d12e1db9e233e1c8de62`。
- Owner 指定領域為 LINE 記事本團購訂單整理，風險為 medium；完整性與人工核對是產品要求。
- 導入既有契約、規則、agent instructions、Git hooks、memory workflow 與 CI；不修改上游框架。
- 本次沿 PR #1 的規劃分支另開治理 PR，未合併前不代表 `main` 已接受這些設定。

## 新 clone 的安裝

Python 3.12+ 與 Git 為前置需求；Windows 的 Git hooks 需要 Git for Windows 的 shell。
框架核心與本 repo 的治理檢查使用標準函式庫，不需安裝應用程式依賴。

```powershell
git submodule update --init --recursive
$env:PYTHONPATH = (Resolve-Path ai-governance-framework).Path
$env:PYTHONUTF8 = '1'
python -m governance_tools.hook_installer --repo . --framework-root ai-governance-framework
python scripts/check_governance.py
```

Git 不會把 `.git/hooks/` 跟著 clone。每個 clone 都要執行 installer；
CI 在一次性 runner 上做同樣安裝與檢查，不假設開發者機器已有 hooks。

## 驗證與證據

`scripts/check_governance.py` 只串接 pinned framework 既有檢查：contract、drift、
hook validation、readiness、memory authority guard，以及 Codex adapter 的
session_start／pre_task／post_task fixture smoke，沒有另訂 framework gate 或放寬規則。

診斷輸出位於忽略的 `artifacts/runtime/governance-onboarding/`；
可提交的導入證據另存 `artifacts/evidence/governance-onboarding/`。
CI 上傳的紀錄可由 PR 的 Governance checks 查閱。
驗證清單與結果需分開辨識：有檢查設定不等於已在遠端執行，也不等於 merge protection。

## 後續治理更新

在完成導入的乾淨 checkout，先 dry-run，再依輸出的 blocker 決定是否 apply：

```powershell
$env:PYTHONPATH = (Resolve-Path ai-governance-framework).Path
python -m governance_tools.f7_full_update --repo . --framework-root ai-governance-framework --fetch-remote origin --fetch-ref main --format human
python -m governance_tools.f7_full_update --repo . --framework-root ai-governance-framework --fetch-remote origin --fetch-ref main --apply --format human
```

不以直接修改 gitlink 或 lock 代替 F-7。Apply 後若有待提交變更，保留輸出的 partial 狀態，
依目前 owner 授權交付並重驗；不能從 framework 指標或版本一致推論所有能力已通過。

## Memory 與 session 邊界

`memory/02_workflow.md` 記錄 owner 已提供的產品事實。
Daily、active-state 與 review 的 session-derived 紀錄使用 canonical `memory_record`；
作出完成宣稱前執行 `memory_workflow --check --repo . --run-guard`。
Implementation 與其 memory companion 分開提交、維持同一 PR。

本次任務完成不是 session end。只有已確認的 host session-end 事件或 owner 明確結束 session，
才觸發 closeout；尚未確認的每回合 Stop 不當作 session end。
本次不安裝會把 Codex 每回合 Stop 直接映射成 session-end 的設定。
沒有可用的原生接線時，可在真正 session end 用既有工具顯示手動操作：

```powershell
python -m governance_tools.manage_agent_closeout --project-root . print-manual --agent codex
```

## 驗收界線

- Git hooks 的真實觸發、人工執行的 runtime fixture smoke、host 自動 lifecycle 各自記錄。
- 原生 Codex desktop／Copilot lifecycle 尚未經真實 session-end 驗證。
- Contract 宣告的 validator 是框架既有架構檢查；尚無訂單領域 validator 或產品測試。
- LINE 擷取、訂單正確性、資料遷移、版本發布與 merge enforcement 都不是本次導入證明。
