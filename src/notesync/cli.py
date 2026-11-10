"""Local manual-order POC commands. No LINE automation or network access."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from importlib.metadata import version
import json
from pathlib import Path
import sqlite3
import sys

from notesync.adapters.manual_import import load_json
from notesync.domain.models import ContractError, ProductConfig
from notesync.exporters.csv_exporter import export_report
from notesync.parser.order_parser import parse_order
from notesync.service import accept_snapshot, accepted_payload, import_snapshot, inspect_run, review_comment, totals
from notesync.storage.sqlite import Store


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="notesync", description="Manual order POC. LINE capture is not implemented.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {version('line-note-order-sync')}")
    commands = parser.add_subparsers(dest="command")
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
