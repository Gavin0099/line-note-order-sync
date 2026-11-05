# PLAN.md

> **最後更新**: 2026-11-05
> **Owner**: Gavin0099
> **Freshness**: Sprint (7d)

## Current Phase

- [>] Phase G0 : 導入 AI Governance；尚未開始產品功能 S00–S09。
- [ ] Phase M0 : S00 資料契約與開發骨架。
- [ ] Phase M1 : S01 Windows UIA 單篇擷取驗證。
- [ ] Phase M2 : S02–S05 手動匯入 MVP。
- [ ] Phase M3 : S06 Windows 試用與交付。

本檔是目前 phase、scope 與 anti-goals 的唯一狀態入口。
[docs/PLAN.md](docs/PLAN.md) 保存架構與里程碑設計；
[docs/SLICES.md](docs/SLICES.md) 保存產品切片的依賴與驗收細節，兩者不另行授權執行。

## Active Sprint

- [x] 評估 repo 與上游導入文件，確認採 submodule consumer 路徑。
- [x] Owner 選定 domain 為 LINE 記事本團購訂單整理，risk 為 medium。
- [ ] 建立 repo 專屬契約、AGENTS、記憶骨架與 framework lock。
- [ ] 安裝並驗證 Git hooks、agent instruction surfaces 與 runtime smoke。
- [ ] 驗證漂移、readiness、memory workflow 與 CI，交付獨立治理 PR。

本次 DONE：導入適用的 framework surfaces，完成本機直接相關驗證與實際 commit/push hook
試驗，將結果及未驗證能力交付 review。保留原規劃 PR #1；不合併 PR。

## Backlog

- P0: 依序執行 S00、限時 S01，再完成 S02–S06；目前均尚未實作。
- P1: S07 改單／取消、S08 定期擷取、S09 Google Sheets，依能力條件另行驗收。
- P2: Web 後台、付款與物流暫緩。

## Decision Log

- 2026-11-05：產品基線為 Python 3.12、SQLite、pytest；本機治理驗證實際使用 Python 3.13。
- 2026-11-05：依 owner 指定完整導入 AI Governance，以 repo 內 pinned submodule 提供工具，
  使用框架既有安裝、F-7、記憶與驗證流程，不修改上游框架或另建治理規則體系。
- 2026-11-05：Owner 選定中風險，理由為處理買家資料與叫貨數量，需完整性檢查與人工核對。

## Known Risks

- 尚無應用程式、訂單 parser、SQLite schema 或產品測試；治理驗證不代表產品驗證。
- Windows LINE 的 UIA 擷取、穩定留言 ID 與每批完整性均為 NOT_EVALUATED。
- repo 為公開；實際留言、買家資料、登入資訊與本機傾印不得提交。
- 缺少來源身分時不得推定改單或取消；部分／未知快照不得成為正式叫貨報表依據。
- 安裝 agent instruction／lifecycle 檔不代表目前 Codex desktop 或其他 host 已實際觸發，
  runtime fixture smoke、Git hook trigger、原生 host lifecycle 分開記錄。

## Anti-Goals

- 本次不實作 S00–S09 產品功能，不操作 LINE，不匯入真實買家資料。
- 不修改 framework submodule 內容，不調降驗證、證據或 fail-closed 標準。
- 不變更 repo 可見性或 branch protection，不合併、發布軟體版本或部署。
