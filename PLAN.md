# PLAN.md

> **最後更新**: 2026-11-05
> **Owner**: Gavin0099
> **Freshness**: Sprint (7d)

## Current Phase

- [x] Phase G0 : PR #1、#2 已依序修正、審查與合併；PR #2 final-head 兩平台 CI 通過。
- [>] Phase M0 : S00 資料契約、合成案例與開發骨架；另開 PR review。
- [ ] Phase M1 : S01 Windows UIA 單篇擷取驗證。
- [ ] Phase M2 : S02–S05 手動匯入 MVP。
- [ ] Phase M3 : S06 Windows 試用與交付。

本檔是目前 phase、scope 與 anti-goals 的唯一狀態入口。
[docs/PLAN.md](docs/PLAN.md) 保存架構與里程碑設計；
[docs/SLICES.md](docs/SLICES.md) 保存產品切片的依賴與驗收細節，兩者不另行授權執行。

## Active Sprint

- [x] PR #1 審查修正：暱稱彙總、S08 完整性／多篇／結團、人工宣告標記與效益量測。
- [x] PR #2 獨立 final-head 審查及 Windows／Linux CI；main 合併結果與已審 tree 一致。
- [x] S00 PRD／資料契約、商品設定、合成正反案例、擷取模板與可安裝 CLI 骨架。
- [ ] S00 以本機／CI 驗證並交付獨立 PR；保留真實 TXT／實機能力未確認。

本次 DONE 條件：兩個 PR 合併，完成 S00 的契約、驗收案例與可安裝骨架並另開 PR 交付。
S00 沒有訂單 parser、SQLite schema 或擷取；不把 CLI smoke 當作後續 slice 的驗收。

## Backlog

- P0: S00 交付後進入限時 S01，再完成 S02–S06；後者尚未實作。
- P1: S07 改單／取消、S08 定期擷取、S09 Google Sheets，依能力條件另行驗收。
- P2: Web 後台、付款與物流暫緩。

## Decision Log

- 2026-11-05：產品基線為 Python 3.12、SQLite、pytest；本機治理驗證實際使用 Python 3.13。
- 2026-11-05：依 owner 指定完整導入 AI Governance，以 repo 內 pinned submodule 提供工具，
  使用框架既有安裝、F-7、記憶與驗證流程，不修改上游框架或另建治理規則體系。
- 2026-11-05：Owner 選定中風險，理由為處理買家資料與叫貨數量，需完整性檢查與人工核對。
- 2026-11-05：Owner 接受 MVP 同社群暱稱彙總及同名／改名風險，保留 occurrence 與人工修正。
- 2026-11-05：Owner 授權依序處理兩個 PR、條件式合併，再開始 S00；暫停新增治理範圍。
- 2026-11-05：PR #1 merge=0a36de7；PR #2 merge=cb04aaf，已審 head=93c5ce3，CI run=42013777278 成功。
- 2026-11-05：S01 首個候選為 line_openchat_note，實際來源由本人於實測時確認；TXT 樣本尚缺。

## Known Risks

- 僅有 S00 CLI 骨架與其 smoke 測試；尚無訂單 parser、SQLite schema 或訂單行為測試。
- Windows LINE 的 UIA 擷取、穩定留言 ID 與每批完整性均為 NOT_EVALUATED。
- repo 為公開；實際留言、買家資料、登入資訊與本機傾印不得提交。
- 缺少來源身分時不得推定改單或取消；部分／未知快照不得成為正式叫貨報表依據。
- 安裝 agent instruction／lifecycle 檔不代表目前 Codex desktop 或其他 host 已實際觸發，
  runtime fixture smoke、Git hook trigger、原生 host lifecycle 分開記錄。

## Anti-Goals

- 本次僅實作 S00，不操作 LINE、不匯入真實買家資料，不開始 S01–S09。
- 不修改 framework submodule 內容，不調降驗證、證據或 fail-closed 標準。
- 不變更 repo 可見性或 branch protection，不發布軟體版本或部署；S00 另開 PR 交付。
