# 手動快照資料契約 v1

日期：2026-11-05。這是 S02–S05 的實作契約；S00 尚無 importer、parser 或 SQLite schema。
後續手動 POC 已實作 JSON 路徑，支援限制與命令見 [MANUAL_POC](MANUAL_POC.md)；
手動 adapter 不接受 VERIFIED_COMPLETE，YAML／TXT、來源能力驗證與排程仍待後續切片。
輸入範例：`tests/fixtures/manual_snapshot.example.json`；合成資料不得替代實際擷取證據。

## 輸入封套

UTF-8 JSON object；`format_version` 固定整數 `1`，不接受布林或未知版本。
JSON 重複 key、未知欄位、錯誤型別、無效編碼與不含時區的時間一律拒絕，
保留可回查錯誤，不建立可接受批次。時間為 ISO 8601 含 offset／Z，內部可轉 UTC。

| 欄位 | 型別／語意 |
| --- | --- |
| `format_version` | integer `1` |
| `source.kind` | `line_openchat_note` 或 `line_group_note` |
| `source.scope_key` | 非空字串；人工登記的單一社群範圍，不用社群名稱自動猜 |
| `source.note_key` | 範圍內唯一的非空字串；人工登記，不從文章標題推定 |
| `captured_at` | 這份來源快照的觀察時間，含時區；不是匯入時間 |
| `adapter_version` | 非空字串；格式／來源整理工具版本 |
| `completeness` | 下表的狀態與證據物件 |
| `comments` | 按觀察順序排列的 occurrence 陣列，允許空陣列但仍須完整性證據 |

`scope_key` 的語意包含 `source.kind`；不同來源種類不共用身分命名空間。
資料庫內的 Note 鍵為 `(source.kind, scope_key, note_key)`。
所有輸入字串保留原值；商品文字只在 parser 副本正規化。
匯入器自行記錄 `imported_at`、原始 bytes、SHA-256 及內部 batch ID，不信任輸入自報 hash。

## 留言 occurrence

每筆必備以下欄位；可缺失來源 ID／時間以 JSON `null` 表示，不填推測值。

| 欄位 | 型別／約束 |
| --- | --- |
| `position` | 從 0 起連續 integer，依 comments 順序，不接受 bool |
| `display_name` | string；保留原值，空白作者標示進阻擋審核，不猜作者 |
| `text` | string，可為空白；保留多行及符號，不在 import 時刪除 |
| `source_comment_id` | 非空 string 或 null；存在不等於已證明穩定 |
| `source_author_id` | 非空 string 或 null；存在不等於已證明身分作用域／穩定性 |
| `source_created_at` | 含時區時間或 null |

內部 occurrence ID 只識別 `(batch, position)`。相同原文多筆仍分開保存；
沒有穩定原生 ID 時，不靠文字 hash、位置、UIA RuntimeId 或暱稱跨快照追蹤事件。
疑似複製重疊而無法證明兩筆獨立時，進阻擋審核，不默默去重或相加。

## 買家彙總與修正

優先使用經證明範圍及穩定性的原生作者 ID；未具證據時依 `(source.kind, scope_key, nickname)`
分組。`nickname` 僅對原始 display_name 做首尾空白移除；不做大小寫、全形或模糊合併。
相同暱稱可彙總同篇的獨立明確喊單；跨篇只作買家顯示分組，SKU／數量仍按 Note 分開。
同名誤併與改名拆分是 owner 已接受的 MVP 風險。缺 ID 本身不阻擋，也不需逐則 mapping。

內部 `buyer_key` 是程式管理的分組鍵，不冒充 LINE user ID。
人工可對指定 occurrence 拆分或合併買家，保留原值、新值、理由、操作者、時間與目標 parse run。
新快照／新 parse run 不自動移植修正；原文與原始作者標示不可覆寫。
同來源留言 ID 重複卻內容／邊界矛盾時先待審，不推定哪則有效；同作者多則獨立喊單則可累加。

## 完整性與正式輸出

`completeness` 固定包含 `status`、`method`、`operator`、`declared_at`、`evidence_refs`；
method 為非空字串，operator／declared_at 允許 null（唯 DECLARED_COMPLETE 必填），
evidence_refs 為字串陣列，記錄本機證據參照，不嵌入真實證據於公開 repo。

| status | 必要證據 | 可接受為正式版本 |
| --- | --- | --- |
| `VERIFIED_COMPLETE` | 非空 evidence_refs，限定來源與版本、逐筆基準及當批範圍／一致時間窗；來源聲稱本身不足 | 完成解析與人工接受後可 |
| `DECLARED_COMPLETE` | 非空 operator、含時區 declared_at、人工逐筆方法及非空 evidence_refs | 人工明確接受且報表可見標示後可 |
| `PARTIAL` | method 說明已知缺漏或截斷，可附證據 | 否；僅核對草稿 |
| `UNKNOWN` | method 說明未知原因，可附證據 | 否；僅核對草稿 |

匯入器必須驗證證據條件及來源能力；不因輸入自報 VERIFIED_COMPLETE 就直接授予接受資格。
不得以捲到底、總數一致、前次成功或 mock 測試單獨升格為 VERIFIED_COMPLETE。
正式輸出需已確認 Note、有效商品設定、完整性條件、阻擋異常為零及操作者選定的 batch+parse run。
人工宣告的 manifest 與檔名須包含 `HUMAN_DECLARED` 和 captured_at；manifest 也含宣告資料。
部分／未知的核對輸出一律標 `DRAFT`，不覆寫上一份正式報表或冒充本輪成功。

## 商品設定與 parser 答案

`config/products.example.yaml`：format_version=1、scope_key、note_key、products、default_sku。
products 為非空清單，每筆 sku/name/aliases/max_quantity；sku 在篇內唯一，aliases 不得與
其他 SKU 的代號／別名正規化後衝突。max_quantity 為正整數，範例固定 99。
default_sku 為 null 或存在的 SKU；有多 SKU 仍可明確指定一個預設，不靠順序猜。
設定需另綁 source.kind；跨來源種類使用需明確選定 Note，不能只靠同名設定自動綁定。

S02 的解析副本使用 NFKC、ASCII SKU 大寫、首尾空白移除；允許 token 內空白。
token 以空白／換行、`,`、`，` 或 `、` 分隔；完整 token 為 SKU+正整數。
不允許任意標點、文字殘留或同則重複 SKU。數量範例上限含 99，100 不計入。

- `PARSED`：全文均為允許的明確 token，才產生有效 items。
- `NEEDS_REVIEW`：未知 SKU、問句、條件、引用、改單、取消、追加意圖或重複 SKU；有效 items 為空。
- `INVALID`：看似訂單但數量為 0、負數、小數或超上限；有效 items 為空。
- `NON_ORDER`：空白或無訂單意圖的感謝／貼圖描述；有效 items 為空。

若無效數量與其他歧義同時出現，一律 NEEDS_REVIEW；先拒絕整則採信。
候選 token 可供人工看，但不作已接受訂單。固定預期值見 parser_cases.json；S02 才執行解析測試。

## 重匯、版本與接受交易

1. 同輸入由 `(source.kind, scope_key, note_key, raw_sha256, format_version)` 識別；
   保留完整原始 bytes。不同 Note 即使 bytes／原文相同亦隔離。
2. 相同 batch、parser version、商品設定內容 hash 重跑不增加有效訂單；規則變更另存 parse run。
3. 更換換行可能產生另一待選 batch；不能因而累加到上一 batch。
4. 每篇只選一份 batch+parse run；A=2 換 A=3 後目前為 3，歷史保留 2，不能變成 5。
5. 新匯入時間不代表較新來源；舊檔不能自動覆蓋。部分／未知新批次不影響已接受版本。
6. 人工決定以追加紀錄保存；接受切換用單一 SQLite transaction，失敗維持前版本。
7. 無穩定留言 ID 的差異只稱候選；未出現不等於刪除、改單或取消。
8. S08 的 NoteRegistry 採 OPEN／LOCKED；LOCKED 禁止自動覆寫接受與交付版本，明確人工解鎖留紀錄。

S03 才設計 schema migration 及 import 交易；S04 實作接受／審核；S05 實作固定版本讀取與
報表套件原子完成、UTF-8 BOM、CSV 公式字首防護。內部原文不因匯出防護改動。

## TXT 邊界

`UNCONFIRMED`：尚未取得真實人工複製樣本，S00 不定義 LINE 原生 TXT grammar。
S03 僅在樣本確認作者、時間、多行與分段規則後支援該單一格式；分段不可靠就拒絕，改走 JSON。
