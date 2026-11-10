# LINE 喊單交接到 Mei 後台

一篇 LINE 記事本輸出一份兩欄核對表和逐則原文。需要把品項放進 Mei 的月份記事本時，另產生網站專用 Excel。兩欄表沒有商品、團價及買家區塊，不能直接用作網站匯入檔。

1. 開啟該篇 LINE 記事本，在本專案目錄執行 `.venv/bin/python -m notesync capture-note --auto`。若已確認本文的商品代號，例如 `1`、`2` 或中文品名，可在指令加 `--item-codes 1 2`，讓兩欄表加總這些品項。依提示確認主題與留言總數，載入較早留言後捲動；跨圖辨識不一致、或正文與時間被附圖分開時，依原畫面核對。逐筆確認暱稱、正文和數量。輸出中的 `capture` 是後續要使用的 JSON 路徑。
2. 依貼文設定商品和團價。在 `local-evidence/` 建立 `products.json`，主題必須與擷取檔一致。以下是假資料；商品代號也可用實際留言中的中文品名。`default_item` 是單寫 `+1`、`*1`、`一組` 時要用的品項。若這種喊法的商品不固定，請設 `null`，由人工核對。

   ```json
   {
     "subject": "合成親子書團",
     "default_item": "A",
     "items": {
       "A": {"title": "故事書", "list_price": 120, "price": 100},
       "2": {"title": "釣魚書", "list_price": null, "price": 150}
     }
   }
   ```

3. 逐筆核對商品與數量後匯出。指令會列出未對應商品、問句、改單或取消等須核對的留言序號；有未解決的序號時不會產生網站檔。

   ```sh
   .venv/bin/python -m notesync export-mei "擷取輸出資料夾/LINE記事本留言.json" \
     --products local-evidence/products.json --confirm-reviewed \
     --output local-evidence/Mei記事本匯入.xlsx
   ```

4. 開啟 [Mei 後台的 Excel 整理頁](https://meiandraybook.readwithus.workers.dev/admin/order-batches?view=excel)，選擇要整理的月份，在「LINE 截圖 → 核對 → Excel 匯入」選檔。核對買家、件數和金額，再選擇要對應的網站買家或記事本買家。比對先前已匯入的品項後，才追加到草稿；保存是後台另一個步驟。

`+1`、`+2` 兩則獨立留言，在同一暱稱、同一商品下是 3。`A+1 2+3` 在兩個代號都有商品設定時保留各自的件數。跨截圖的重疊列不重複加總；位置只供核對同一份擷取，不能當作 LINE 留言 ID。重新擷取或匯入同一篇時，請比較整份版本，並使用後台的重複品項核對；不要把新版總數直接加到舊版。

`A+1 B+2` 在網站用 Excel 中是同一個買家區塊下的兩列，每列帶自己的商品代號、數量和團價。新版後台「商品分析」可按代號、品名及團價查看總量與商品小計。記事本只有團價時，定價可留空，商品小計按團價計算。

用 `--pages` 重播已保存的截圖時，可加 `--review-transcription` 修正容易誤辨的暱稱、表情符號與正文。

需要更正時，可加 `--review local-evidence/review.json`。把擷取指令輸出的 `capture_sha256` 貼入核對檔，`comments` 用 **從 1 開始**的原文序號。例如第 1 則原為 `+1`，第 2 則說「改成 3」：核對第 1 則已被取代後，將第 1 則排除、第 2 則填 `A: 3`。

```json
{
  "capture_sha256": "貼上本次擷取的 capture_sha256",
  "comments": {
    "1": {"reason": "已由第 2 則改單取代", "items": {}},
    "2": {"reason": "LINE 已確認改為三本", "items": {"A": 3}}
  }
}
```

`buyer_group` 可選填：同名但確定是不同買家時，為各買家所屬留言設定不同分組；同一分組的 `buyer_name`（若需修正）要一致。暱稱與包裹編號只用於本次檔案，網站買家對應由後台選擇。原文及核對檔留在本機。若要回顧舊 Google 試算表，請對照原留言再修改，不從原表空白欄推算。
