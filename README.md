# line-note-order-sync

LINE Note Order Synchronizer

A local-first tool that captures LINE Note comments, parses group-buy orders,
detects changes, and exports auditable order reports.

目標是整理 LINE 記事本商品貼文中的喊單留言，建立能核對與追溯的團購訂單資料。
上方英文描述是專案目標，尚未代表已有這些功能。

## 目前狀態

2026-11-05：完成初步評估與開發切片規劃；尚無應用程式、資料庫或實機擷取結果。
Windows UIA 留言擷取能力為 `NOT_EVALUATED`。

已導入 repo 層級 AI Governance 設定；安裝、驗證與能力界線見
[治理導入說明](docs/GOVERNANCE_ONBOARDING.md)，目前執行範圍見 [PLAN.md](PLAN.md)。

- [可行性與範圍評估](docs/ASSESSMENT.md)
- [開發 PLAN](docs/PLAN.md)
- [SLICE 工作清單與驗收](docs/SLICES.md)

## 建議起點

先執行 S00，確定單篇記事本的資料契約與驗收案例，再執行 S01 的限時擷取驗證。
手動匯入核心可沿 S02–S06 完成；S01 不可行時仍保有可用的本機工具。

技術基線為 Python 3.12、SQLite、pytest；Windows 擷取套件獨立為選用相依。
現階段不含定期同步、Google Sheets、網站後台、付款或物流。

## 資料與開源

測試資料使用合成資料。實際留言、買家資料、資料庫、UIA 傾印、截圖與匯出檔應存於
Git 忽略的本機目錄。目前 GitHub repo 為公開，本 PR 僅提供規劃文件。
尚未選定 LICENSE 或發布軟體版本；加入程式與測試資料時，仍需確認授權與敏感資料。
