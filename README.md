# line-note-order-sync

LINE Note Order Synchronizer

A local-first tool that captures LINE Note comments, parses group-buy orders,
detects changes, and exports auditable order reports.

目標是整理 LINE 記事本商品貼文中的喊單留言，建立能核對與追溯的團購訂單資料。
上方英文描述是專案目標，尚未代表已有這些功能。

## 目前狀態

2026-11-05：PR #1 規劃、PR #2 治理導入已合併。S00 提供資料契約、合成案例與 CLI 骨架；
目前僅有 help／version，尚無 parser、資料庫或實機擷取結果。
Windows UIA 留言擷取能力為 `NOT_EVALUATED`。

已導入 repo 層級 AI Governance 設定；安裝、驗證與能力界線見
[治理導入說明](docs/GOVERNANCE_ONBOARDING.md)，目前執行範圍見 [PLAN.md](PLAN.md)。

- [可行性與範圍評估](docs/ASSESSMENT.md)
- [開發 PLAN](docs/PLAN.md)
- [SLICE 工作清單與驗收](docs/SLICES.md)
- [S00 PRD](docs/PRD.md)
- [資料契約與輸入格式](docs/DATA_CONTRACT.md)
- [S01 擷取實驗模板（尚未實測）](docs/CAPTURE_FEASIBILITY.md)

## 建議起點

先 review S00 的單篇資料契約與驗收案例，再執行 S01 的限時擷取驗證。
手動匯入核心將沿 S02–S06 建立；S01 不可行時仍可繼續完成本機工具。

技術基線為 Python 3.12、SQLite、pytest；Windows 擷取套件獨立為選用相依。
現階段不含定期同步、Google Sheets、網站後台、付款或物流。

## 安裝與骨架驗證

Python 3.12+；下列為 Windows PowerShell。產品骨架沒有 runtime 第三方相依或 Windows UIA 相依。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\notesync.exe --help
.\.venv\Scripts\python.exe -m notesync --version
.\.venv\Scripts\python.exe -m pytest
```

`parse`、`import`、`review`、`accept`、`export` 尚未實作，呼叫會失敗。
目前測試只驗 CLI 骨架，不會解析 `tests/fixtures/` 的訂單案例；案例是後續 slice 的人工答案。
`config/products.example.yaml` 與 JSON 範例都是合成資料。真實 TXT 格式尚未確認，不能直接匯入。
治理檢查需另裝 `requirements-governance.txt`，操作見治理導入說明。

## 資料與開源

測試資料使用合成資料。實際留言、買家資料、資料庫、UIA 傾印、截圖與匯出檔應存於
Git 忽略的本機目錄。目前 GitHub repo 為公開，提交內容僅含合成案例與開發檔案。
尚未選定 LICENSE 或發布軟體版本；加入程式與測試資料時，仍需確認授權與敏感資料。
