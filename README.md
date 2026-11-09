# line-note-order-sync

LINE Note Order Synchronizer

A local-first tool that captures LINE Note comments, parses group-buy orders,
detects changes, and exports auditable order reports.

目標是整理 LINE 記事本商品貼文中的喊單留言，建立能核對與追溯的團購訂單資料。
上方英文描述是專案目標，尚未代表已有這些功能。

## 目前狀態

2026-11-05：PR #1、#2 已合併，PR #3 的 S00 仍待 review。
相依 POC 分支已實作手動 JSON 匯入、嚴格解析、SQLite、人工核對、接受快照及 CSV／HTML 報表。
手動訂單流程使用合成資料展示。本機擷取分支可讀取 Mac LINE 視窗的輔助使用文字，
也可保存手動複製的 UTF-8 文字。所測 Mac LINE 版本的展開留言作者及正文
未出現在輔助使用介面，實測範圍見擷取操作文件。

已導入 repo 層級 AI Governance 設定；安裝、驗證與能力界線見
[治理導入說明](docs/GOVERNANCE_ONBOARDING.md)，目前執行範圍見 [PLAN.md](PLAN.md)。

- [可行性與範圍評估](docs/ASSESSMENT.md)
- [開發 PLAN](docs/PLAN.md)
- [SLICE 工作清單與驗收](docs/SLICES.md)
- [S00 PRD](docs/PRD.md)
- [資料契約與輸入格式](docs/DATA_CONTRACT.md)
- [LINE 記事本擷取操作與實機驗收](docs/CAPTURE_FEASIBILITY.md)
- [手動功能 POC：展示與操作](docs/MANUAL_POC.md)

## 建議起點

先看 POC 的實際報表，再 review S00 與相依功能 PR。
要在 Mac 整理一篇記事本，可在專案根目錄執行
`.venv/bin/python -m notesync capture-note --chat 'LINE 群組完整名稱'`。
指令會啟動 LINE 並嘗試開啟指定群組的記事本。選好貼文、確認留言範圍後，程式自動取圖，
輸出逐則原文、可匯入 Google 試算表的兩欄 Excel，以及供網站交接的擷取 JSON。
已手動開啟記事本時可使用 `capture-note --auto`。
要整理 Mei 版媽近 7 天的已結團記事本，執行
`.venv/bin/python -m notesync capture-week`。也可用 `--from` 和 `--to` 指定發文日期。
Excel 在同一主題內依暱稱加總明確的獨立喊單；待判讀的改單、取消及不明商品編號保留空白。
要交接到團購網站，請參照 [Mei 後台記事本匯入](docs/MEI_NOTEBOOK_IMPORT.md)。

技術基線為 Python 3.12、SQLite、pytest。Mac 視窗擷取使用 Swift 與 macOS 輔助使用介面。
本機指令可為既有 Mei 後台匯入預覽產生檔案；上傳 Google Sheets 與保存網站草稿仍由操作者執行。

## 安裝並看 POC

Python 3.12／3.13；下列為 Windows PowerShell。產品沒有 runtime 第三方相依或 Windows UIA 相依。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\notesync.exe --help
.\.venv\Scripts\python.exe -m notesync --version
.\.venv\Scripts\python.exe -m notesync demo
.\.venv\Scripts\python.exe -m pytest
```

`demo` 回傳可直接開啟的 HTML 路徑，展示問句阻擋、人工核對、重匯、部分拒絕與快照替換。
CLI 支援 `parse`、`import`、`inspect`、`review`、`accept`、`export`；細節見 POC 操作文件。
商品設定暫用 `config/products.example.json`，範例均為合成資料；YAML／真實 TXT 尚不支援。
治理檢查需另裝 `requirements-governance.txt`，操作見治理導入說明。

## 資料與開源

測試資料使用合成資料。實際留言、買家資料、資料庫、UIA 傾印、截圖與匯出檔應存於
Git 忽略的本機目錄。目前 GitHub repo 為公開，提交內容僅含合成案例與開發檔案。
尚未選定 LICENSE 或發布軟體版本；加入程式與測試資料時，仍需確認授權與敏感資料。
