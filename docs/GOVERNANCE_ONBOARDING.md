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
目前 pinned framework 的 runtime phase policy 會載入 PyYAML；
`requirements-governance.txt` 固定已驗證的版本，與未來產品相依分開。

```powershell
git -c core.longpaths=true submodule update --init --recursive
python -m pip install -r requirements-governance.txt
Push-Location ai-governance-framework
try {
    python -X utf8 -m governance_tools.hook_installer --repo .. --framework-root .
} finally {
    Pop-Location
}
python scripts/check_governance.py
```

Git 不會把 `.git/hooks/` 跟著 clone。每個 clone 都要執行 installer；
CI 在一次性 runner 上做同樣安裝與檢查，不假設開發者機器已有 hooks。
Windows CI 在 checkout 前只替一次性 runner 設定 Git longpaths；未修改開發者機器的系統設定。
此安裝方式不在目前 PowerShell 留下 `PYTHONPATH`，避免 Windows 路徑被 Git Bash
當成不同分隔規則的搜尋路徑串接。檢查腳本只替自己的子程序設定 module 搜尋路徑。

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
python -X utf8 ai-governance-framework/governance_tools/f7_full_update.py --repo . --framework-root ai-governance-framework --fetch-remote origin --fetch-ref main --format human
python -X utf8 ai-governance-framework/governance_tools/f7_full_update.py --repo . --framework-root ai-governance-framework --fetch-remote origin --fetch-ref main --apply --format human
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
Push-Location ai-governance-framework
try {
    python -m governance_tools.manage_agent_closeout --project-root .. print-manual --agent codex
} finally {
    Pop-Location
}
```

## 本機結果與仍待驗證的部分

- `python scripts/check_governance.py` 的八項檢查通過，Codex adapter 的三個事件分別執行。
- 在 framework 工作目錄執行四個相關測試檔，89 passed；首次在 consumer 目錄執行時有
  三個案例因相對 fixture 路徑不存在失敗，改用正確 cwd 後重跑，沒有修改上游測試。
- F-7 已執行 apply；初始 lock 記錄實際 pin，後續 apply receipt 確認 lock 與 checkout 一致，
  乾淨索引的 dry-run 回報 `full_update_completed`。這是該次更新檢查的狀態，不是完整治理保證。
- `external_repo_smoke` 的 session_start、pre_task 通過，並留有三項 assumption 的 report-only
  advisory；它沒有本 repo 的 post-task fixture，所以 `post_task_ok` 保留 null。
  post_task 由另一條 Codex adapter fixture smoke 驗證，不改寫外部 smoke receipt。
- 真實 pre-commit 已觸發；pre-push 與遠端 CI 在交付時另行驗證，狀態看 PR 與交付報告。
- 原生 host lifecycle、merge protection、LINE 操作與訂單功能保持未驗證。
- 首輪遠端 CI 暴露 Windows submodule 長路徑與 Linux 缺少 PyYAML，已在同一 PR
  補上 checkout 前置設定與 pinned runtime dependency；是否修復由後續 CI 結果確認。

## 驗收界線

- Git hooks 的真實觸發、人工執行的 runtime fixture smoke、host 自動 lifecycle 各自記錄。
- 原生 Codex desktop／Copilot lifecycle 尚未經真實 session-end 驗證。
- Contract 宣告的 validator 是框架既有架構檢查；尚無訂單領域 validator 或產品測試。
- LINE 擷取、訂單正確性、資料遷移、版本發布與 merge enforcement 都不是本次導入證明。
