# 手動訂單功能 POC

這份 POC 實際使用 parser、SQLite、人工審核與報表匯出；不是模擬訂單結果的展示網頁。
使用合成資料，尚未連接 LINE。產品範圍是 S02–S05 的手動 JSON 路徑，沒有完成 S01 或 S06 試用。
它基於 PR #3 的 S00 契約，另開相依 PR，未自動合併。

## 先看功能

在 repo 根目錄，用 Python 3.12／3.13：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m notesync demo
```

命令回傳 `report` 路徑，開啟該 `index.html` 即可看展示；不需要網站伺服器或 LINE 登入。
每次使用新的 `exports/poc-時間-隨機碼/`，含合成輸入、獨立 DB、三份報表及 demo-result。
也可指定 `--output exports/my-poc`，該目錄必須全新或空白，既有資料不覆寫。

固定人工答案及實際展示順序：

| 步驟 | 可看到的行為 |
| --- | --- |
| 匯入／解析 | `A+1 B+2`、`Ａ＋２`、另一則 `A+1`；候選 A=4、B=2 |
| 未決資料阻擋 | 第四則 `A+1？` 待核對，接受失敗 |
| 人工核對 | 明確排除問句，保存理由，接受 A=4、B=2 |
| 重匯 | 同一輸入仍為同一 run／接受版本，數量不加倍 |
| 部分資料 | PARTIAL 被拒絕，原已接受版本保留 |
| 替換快照 | 人工選定另一份完整快照後為 A=3、B=1；不是 A=7、B=3，歷史仍在 |

HTML 頁面連至核對草稿、第一個接受版本及目前版本。可下載買家彙總、留言明細、
商品總量、待核對清單 CSV；manifest 保留來源、時間、hash、版本及人工宣告。
HTML 是可離線查看的報表，不提供瀏覽器內編輯；人工操作由 CLI 完成。

## 自己操作合成範例

這組命令使用已存在的合成 fixture，並讀取實際回傳 ID，不假設 run／note 永遠為 1：

```powershell
$pocPython = (Resolve-Path .venv/Scripts/python.exe).Path
$pocImport = & $pocPython -m notesync import tests/fixtures/manual_snapshot.example.json --products config/products.example.json --db data/my-poc.sqlite3 --operator '示範操作者' | ConvertFrom-Json
& $pocPython -m notesync inspect --db data/my-poc.sqlite3 --run $pocImport.run_id
$pocAccept = & $pocPython -m notesync accept --db data/my-poc.sqlite3 --run $pocImport.run_id --operator '示範操作者' | ConvertFrom-Json
& $pocPython -m notesync export --db data/my-poc.sqlite3 --note $pocAccept.note_id --output exports/my-poc-report
```

此 fixture 的人工答案為 A=3、B=2。匯出目錄存在時不覆寫，重做時換另一個輸出根目錄。
任一命令失敗需先處理錯誤，不繼續使用空的回傳 ID。

其他命令範例（ID 請用 inspect 實際輸出）：

```powershell
# 只解析，不建立 DB
& $pocPython -m notesync parse --products config/products.example.json --text 'A+1 B+2'
# 明確排除一則留言；原文不變、原因追加保存
& $pocPython -m notesync review --db data/my-poc.sqlite3 --run 1 --position 0 --action exclude --operator '示範操作者' --reason '已確認非訂單'
# 人工判定數量／買家分組；商品數量仍須符合設定
& $pocPython -m notesync review --db data/my-poc.sqlite3 --run 1 --position 0 --action set --items '{"A":2}' --buyer '人工分組名稱' --operator '示範操作者' --reason '買家確認數量'
# 未接受／未知資料只可匯出 DRAFT 核對，不可叫貨
& $pocPython -m notesync export --db data/my-poc.sqlite3 --run 1 --draft --output exports/my-review-draft
```

review 改變候選版本，不會立即改動已接受的報表；需重新 accept 才切換。
同名拆分可用不同 `--buyer` 標籤；確認改名後可指定同一標籤合併，原暱稱仍保留。
新快照／新設定不自動繼承舊人工決定。

## 完整性與重複留言

- POC 只接受 `DECLARED_COMPLETE`，需宣告人、時間、方法與證據參照，再由操作者明確 accept。
  參照是供人工核對的記錄，不宣稱軟體已驗證外部證據內容。
- 輸入自報 `VERIFIED_COMPLETE` 也不能在這個手動 adapter 取得機器驗證資格。
- PARTIAL／UNKNOWN 可保存與產生 DRAFT，不改已接受版本。
- 同暱稱且原文完全相同的多筆先標記疑似重疊，全部 occurrence 保留。
  匯入時加 `--independent-occurrences` 表示操作者已逐列確認為獨立留言；
  確認值與操作者存在 parse run，與未確認版本分開，不是自動推定。
- 50 筆無 ID fixture 只需這個批次級確認，不需 50 次買家映射。同名／改名風險仍由 owner 接受。
- 重複 source comment ID 或缺作者標示仍阻擋，不能被上述確認旗標蓋過。
- 接受切換與匯入均用 SQLite transaction；正式輸出讀已保存的固定接受版本。
  DB 不存在時 inspect／export 會失敗，不偷偷建立空白 DB；既有未知 DB 不自動遷移。

## 解析／輸出支援範圍

商品設定用 `config/products.example.json`，欄位對應既有 YAML 範例；POC 不解析 YAML。
ASCII SKU／別名最多 32 字元、數量上限設定 1–999999，範例上限 99。
未知文字保守進待核對；只有空白、謝謝／感謝／THANKS／THANK YOU／[貼圖] 白名單是 NON_ORDER。
缺原生身分驗證能力時依同社群暱稱分組；保留來源 ID 但不視為已證明穩定。
CSV 使用 UTF-8 BOM 與公式字首防護；原始資料不因輸出改動。CSV 檔名包含 HUMAN_DECLARED／DRAFT
及來源 UTC 時間，HTML 顯示 Asia/Taipei，manifest 保存原時間含 offset。
報表套件全部寫完才原子搬入完成目錄；失敗不留半份正式套件。既有報表不覆寫。

尚未支援：LINE／UIA、真實 TXT、穩定來源事件辨識、排程、LOCKED 多篇管理、Sheets、付款／物流。
試用備份恢復、實際來源正確性與節省工時仍需 S01／S06；這不是正式營運驗收或版本發布。

## 開發驗證

```powershell
.\.venv\Scripts\python.exe -m pytest -q
python scripts/check_governance.py
```

本機產品測試包含 S00 的 26 個人工 parser 答案、50 筆無 ID、重匯、版本切換、審核隔離、
真實 SQLite rollback、CSV／HTML 安全、匯出失敗清理及 CLI 全流程。
另外限兩個故障注入檢查，確認「移除完整性阻擋」與「數量上限邊界改錯」會被現有測試抓到；
原始碼已逐位元恢復，不把此有限檢查當作全面 mutation coverage。
遠端結果以相依 PR 的實際 head／CI 為準。
