"""Local capture evidence and manual-order POC commands."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from importlib.metadata import version
import json
from pathlib import Path
import sqlite3
import sys

from notesync.adapters.capture import SOURCE_KINDS, capture_macos, capture_text, save_capture
from notesync.adapters.manual_import import load_json
from notesync.domain.models import ContractError, ProductConfig, nonempty
from notesync.exporters.csv_exporter import export_report
from notesync.parser.order_parser import parse_order
from notesync.service import accept_snapshot, accepted_payload, import_snapshot, inspect_run, review_comment, totals
from notesync.storage.sqlite import Store


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="notesync", description="Manual order POC and LINE Note capture probe.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {version('line-note-order-sync')}")
    commands = parser.add_subparsers(dest="command")
    line = commands.add_parser("capture-line", help="唯讀擷取 Mac LINE 視窗可讀文字")
    target = line.add_mutually_exclusive_group(required=True)
    target.add_argument("--list-windows", action="store_true", help="列出目前可選的 LINE 視窗")
    target.add_argument("--window", type=int, help="要擷取的視窗編號")
    note = commands.add_parser("capture-note", help="Mac LINE 截圖辨識並輸出文字與 Excel")
    note.add_argument("--auto", action="store_true", help="等待 LINE 記事本，選定後自動分段取圖")
    note.add_argument("--chat", help="啟動 Mac LINE 並開啟完整名稱符合的群組記事本，自動分段取圖")
    note.add_argument("--post", help="搜尋這個貼文名稱，自動展開、擷取留言及匯出 Excel")
    note.add_argument("--open-only", action="store_true", help="搭配 --chat，只開啟記事本，不進行 OCR 或輸出")
    note.add_argument("--pages", nargs="+", type=Path, help="依順序重播現有的留言截圖")
    note.add_argument("--author", help="限定貼文畫面上顯示的作者")
    note.add_argument("--subject", help="限定貼文主題，或提供重播時已核對的主題")
    note.add_argument("--count", type=int, help="重播時提供畫面顯示的留言數")
    note.add_argument("--review-transcription", action="store_true", help="重播時逐筆核對並修正暱稱或正文")
    note.add_argument("--item-codes", nargs="+", help="已在本文核對的商品代號或中文品名，供兩欄 Excel 計算")
    week = commands.add_parser("capture-week", help="擷取 Mei 版媽已結團貼文並匯出同一份 Excel")
    week.add_argument("--from", dest="start_date", help="發文起日 YYYY-MM-DD，含當日")
    week.add_argument("--to", dest="end_date", help="發文迄日 YYYY-MM-DD，含當日")
    week.add_argument("--chat", help="LINE 群組完整名稱，預設使用本機設定")
    week.add_argument("--output", type=Path, help="尚未存在的 .xlsx 路徑")
    mei = commands.add_parser("export-mei", help="產生 Mei 後台記事本可預覽的 Excel（不寫入網站）")
    mei.add_argument("capture", type=Path, help="capture-note 產出的 LINE記事本留言.json")
    mei.add_argument("--products", required=True, type=Path, help="本篇商品、代號與團價 JSON")
    mei.add_argument("--review", type=Path, help="依原留言序號記錄人工核對決定的 JSON")
    mei.add_argument("--confirm-reviewed", action="store_true", help="確認完整範圍、數量與同名買家均已人工核對")
    mei.add_argument("--output", required=True, type=Path)
    copied = commands.add_parser("capture-text", help="保存從記事本複製的 UTF-8 文字")
    copied.add_argument("input", type=Path, help="文字檔路徑，或用 - 從標準輸入讀取")
    for command in (line, copied):
        command.add_argument("--kind", choices=SOURCE_KINDS, help="已知時填一般群組或社群記事本")
        command.add_argument("--scope-key", help="群組／社群的本機代號")
        command.add_argument("--note-key", help="該篇記事本的本機代號")
    parse = commands.add_parser("parse", help="解析一則明確喊單（不寫 DB）")
    parse.add_argument("--products", required=True, type=Path)
    parse.add_argument("--text", required=True)
    importing = commands.add_parser("import", help="匯入 JSON 快照並解析")
    importing.add_argument("snapshot", type=Path)
    importing.add_argument("--products", required=True, type=Path)
    importing.add_argument("--independent-occurrences", action="store_true", help="操作者確認每列是獨立 occurrence，已排除複製重疊")
    inspect = commands.add_parser("inspect", help="檢視批次與待核對清單")
    inspect.add_argument("--run", type=int)
    review = commands.add_parser("review", help="追加一筆人工判讀或買家分組修正")
    review.add_argument("--run", required=True, type=int)
    review.add_argument("--position", required=True, type=int)
    review.add_argument("--action", required=True, choices=("set", "exclude"))
    review.add_argument("--items", help='set 時必填，例如 {"A":2}')
    review.add_argument("--buyer", help="人工買家分組標籤；可拆分同名或合併改名")
    review.add_argument("--reason", required=True)
    accept = commands.add_parser("accept", help="人工選定完整且無阻擋的訂單快照")
    accept.add_argument("--run", required=True, type=int)
    export = commands.add_parser("export", help="匯出固定版本的 CSV／HTML 報表套件")
    target = export.add_mutually_exclusive_group(required=True)
    target.add_argument("--note", type=int, help="匯出這篇目前已接受的正式版本")
    target.add_argument("--run", type=int, help="只供 --draft 核對")
    export.add_argument("--draft", action="store_true")
    export.add_argument("--output", required=True, type=Path)
    for command in (importing, inspect, review, accept, export):
        command.add_argument("--db", required=True, type=Path)
    for command in (importing, review, accept):
        command.add_argument("--operator", required=True)
    demo = commands.add_parser("demo", help="執行合成資料 POC 並產生可看的報表")
    demo.add_argument("--output", type=Path, help="全新／空白目錄；預設 exports/poc-時間-隨機碼")
    args = parser.parse_args(argv)
    try:
        result = dispatch(args)
    except (ContractError, OSError, sqlite3.Error) as exc:
        parser.exit(2, f"notesync: {exc}\n")
    if result is None:
        parser.print_help()
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def dispatch(args: argparse.Namespace):
    if args.command is None:
        return None
    if args.command == "demo":
        from notesync.demo import run_demo
        return run_demo(args.output)
    if args.command == "capture-week":
        from notesync.adapters.note_week import capture_week
        return capture_week(args.start_date, args.end_date, args.chat, args.output)
    if args.command == "capture-note":
        from notesync.adapters.note_ocr import capture_note
        if args.post is not None:
            if args.open_only or args.pages is not None or args.count is not None or args.author is not None or args.review_transcription:
                raise ContractError("--post 不能搭配 --open-only、--author 或截圖重播選項")
            post = nonempty(args.post).strip()
            if len(post) > 200 or any(ord(character) < 32 for character in post):
                raise ContractError("貼文名稱須為 1 到 200 字的單行文字")
            from notesync.adapters.line_navigation import default_chat, open_notebook
            window = open_notebook(args.chat if args.chat is not None else default_chat(), reuse=True)
            return capture_note(automatic=True, pages=None, author=None, subject=args.subject, count=None,
                                item_codes=args.item_codes, window=window, post=post)
        if args.open_only and args.chat is None:
            raise ContractError("--open-only 需搭配 --chat")
        if args.open_only and any(value is not None for value in (args.author, args.subject, args.item_codes)):
            raise ContractError("--open-only 只開啟記事本，請移除貼文及商品選項")
        window = None
        if args.chat is not None:
            from notesync.adapters.line_navigation import open_notebook
            if args.pages is not None or args.count is not None or args.review_transcription:
                raise ContractError("--chat 不能搭配重播截圖選項")
            for label in (args.author, args.subject):
                if label is not None:
                    nonempty(label)
            if not args.open_only and not sys.stdin.isatty():
                raise ContractError("此擷取流程需要在終端機核對留言。只開記事本可加 --open-only")
            window = open_notebook(args.chat)
            if args.open_only:
                return {"notebook_window": window}
        return capture_note(
            automatic=args.auto or window is not None, pages=args.pages, author=args.author,
            subject=args.subject, count=args.count, item_codes=args.item_codes,
            review_transcription=args.review_transcription, window=window,
        )
    if args.command == "export-mei":
        from notesync.exporters.mei_notebook import export_mei
        return export_mei(args.capture, args.products, args.review, args.output, confirmed=args.confirm_reviewed)
    if args.command == "capture-line" and args.list_windows:
        return capture_macos(None)
    if args.command in ("capture-line", "capture-text"):
        scope_key = nonempty(args.scope_key) if args.scope_key is not None else None
        note_key = nonempty(args.note_key) if args.note_key is not None else None
        if args.command == "capture-line":
            if args.window < 1:
                raise ContractError("請輸入 --list-windows 列出的視窗編號")
            method, evidence = "macos_accessibility", capture_macos(args.window)
        else:
            method, evidence = "manual_copy", {"text": capture_text(args.input)}
        return save_capture(kind=args.kind, scope_key=scope_key, note_key=note_key,
                            method=method, evidence=evidence)
    if args.command == "parse":
        config = ProductConfig.from_document(load_json(args.products.read_bytes()))
        parsed = parse_order(args.text, config)
        return {"status": parsed.status, "items": parsed.items, "reason": parsed.reason}
    if args.command == "import":
        raw, config = args.snapshot.read_bytes(), args.products.read_bytes()
        with Store(args.db, create=True) as store:
            return import_snapshot(store, raw, config, operator=args.operator,
                                   independent_occurrences=args.independent_occurrences)
    writable = args.command in ("review", "accept")
    with Store(args.db, writable=writable) as store:
        if args.command == "inspect":
            if args.run is not None:
                return inspect_run(store, args.run)
            return {"runs": [dict(r) for r in store.conn.execute("SELECT id,batch_id,parser_version,operator,created_at FROM runs ORDER BY id")],
                    "current": [dict(r) for r in store.conn.execute("SELECT * FROM current_acceptances ORDER BY note_id")]}
        if args.command == "review":
            if args.action == "set" and args.items is None:
                raise ContractError("set 需提供 --items")
            if args.action == "exclude" and (args.items is not None or args.buyer is not None):
                raise ContractError("exclude 不接受 items 或 buyer")
            items = load_json(args.items.encode("utf-8")) if args.action == "set" else None
            review_comment(store, args.run, args.position, operator=args.operator,
                           reason=args.reason, items=items, buyer_label=args.buyer)
            return {"run_id": args.run, "blocking": inspect_run(store, args.run)["blocking"]}
        if args.command == "accept":
            result = accept_snapshot(store, args.run, operator=args.operator)
            result["totals"] = totals(accepted_payload(store, result["note_id"]))
            return result
        if args.command == "export":
            if args.draft != (args.run is not None):
                raise ContractError("--run 必須搭配 --draft；正式匯出請用 --note")
            payload = inspect_run(store, args.run) if args.draft else accepted_payload(store, args.note)
            folder = export_report(payload, args.output, draft=args.draft)
            return {"report": str(folder / "index.html"), "totals": totals(payload), "draft": args.draft}
    raise ContractError("命令未支援")
