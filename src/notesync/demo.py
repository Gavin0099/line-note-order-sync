"""Replayable synthetic demonstration using the real application use cases."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from html import escape
import json
from pathlib import Path
import uuid

from notesync.domain.models import ContractError
from notesync.exporters.csv_exporter import export_report, page
from notesync.service import accept_snapshot, accepted_payload, encoded, import_snapshot, inspect_run, review_comment, totals
from notesync.storage.sqlite import Store


def sample_data() -> tuple[dict, dict]:
    config = {"format_version": 1, "scope_key": "demo-community", "note_key": "demo-note", "default_sku": None,
              "products": [{"sku": sku, "name": f"合成商品 {sku}", "aliases": [], "max_quantity": 99} for sku in ("A", "B")]}
    snapshot = {"format_version": 1, "source": {"kind": "line_openchat_note", "scope_key": "demo-community", "note_key": "demo-note"},
                "captured_at": "2026-11-05T12:00:00+08:00", "adapter_version": "manual-json-v1",
                "completeness": {"status": "DECLARED_COMPLETE", "method": "合成示範：固定四則獨立留言，非 LINE 實際擷取或真人完整性驗證。",
                                 "operator": "合成示範操作者", "declared_at": "2026-11-05T12:05:00+08:00", "evidence_refs": ["synthetic:four-independent-rows"]},
                "comments": []}
    for position, (name, text) in enumerate((("合成買家甲", "A+1 B+2"), ("合成買家乙", "Ａ＋２"),
                                            ("合成買家甲", "A+1"), ("合成買家丙", "A+1？"))):
        snapshot["comments"].append({"position": position, "display_name": name, "text": text,
                                     "source_comment_id": None, "source_author_id": None, "source_created_at": None})
    return config, snapshot


def run_demo(output: Path | None = None) -> dict:
    root = (output or Path("exports") / f"poc-{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}").resolve()
    if root.exists() and any(root.iterdir()):
        raise ContractError("示範需使用全新或空白目錄，不覆寫既有檔案")
    root.mkdir(parents=True, exist_ok=True)
    config, snapshot = sample_data()
    config_raw, raw = encoded(config).encode("utf-8"), encoded(snapshot).encode("utf-8")
    (root / "products.json").write_bytes(config_raw)
    (root / "snapshot.json").write_bytes(raw)
    steps = []
    with Store(root / "orders.sqlite3", create=True) as store:
        imported = import_snapshot(store, raw, config_raw, operator="合成示範操作者")
        candidate = inspect_run(store, imported["run_id"])
        if candidate["blocking"] != [3] or totals(candidate) != {"A": 4, "B": 2}:
            raise ContractError("示範初始解析與固定人工答案不符")
        draft = export_report(candidate, root / "reports", draft=True)
        steps.append(("匯入與解析", "四則留言保留；問句 A+1？進待核對，有效候選 A=4、B=2。"))
        try:
            accept_snapshot(store, imported["run_id"], operator="合成示範操作者")
        except ContractError:
            steps.append(("未決資料阻擋", "有問句時拒絕接受正式快照。"))
        else:
            raise ContractError("示範失敗：未決資料未被擋下")
        review_comment(store, imported["run_id"], 3, operator="合成示範操作者", reason="示範人工核對：此句為詢問，不是確定訂購")
        first = accept_snapshot(store, imported["run_id"], operator="合成示範操作者")
        first_payload = accepted_payload(store, first["note_id"])
        if totals(first_payload) != {"A": 4, "B": 2}:
            raise ContractError("示範結果與固定人工答案不符")
        first_report = export_report(first_payload, root / "reports")
        steps.append(("人工核對後接受", "問句排除，正式示範版本 A=4、B=2；理由可追溯。"))
        repeated = import_snapshot(store, raw, config_raw, operator="合成示範操作者")
        repeat_accept = accept_snapshot(store, repeated["run_id"], operator="合成示範操作者")
        if not repeated["reused"] or repeat_accept["acceptance_id"] != first["acceptance_id"]:
            raise ContractError("示範失敗：重匯產生重複版本")
        steps.append(("重匯不重計", "相同輸入仍為同一 run／接受版本，沒有加倍。"))
        partial = deepcopy(snapshot)
        partial["captured_at"] = "2026-11-05T13:00:00+08:00"
        partial["completeness"].update(status="PARTIAL", method="合成示範：刻意只保留一則留言")
        partial["comments"] = partial["comments"][:1]
        partial_run = import_snapshot(store, encoded(partial).encode("utf-8"), config_raw, operator="合成示範操作者")
        try:
            accept_snapshot(store, partial_run["run_id"], operator="合成示範操作者")
        except ContractError:
            if accepted_payload(store, first["note_id"])["acceptance_id"] != first["acceptance_id"]:
                raise ContractError("示範失敗：部分資料改變了正式版本")
            steps.append(("部分資料拒絕", "PARTIAL 不能接受；原 A=4、B=2 保留，不推定漏單是取消。"))
        else:
            raise ContractError("示範失敗：部分資料未被擋下")
        newer = deepcopy(snapshot)
        newer["captured_at"] = "2026-11-05T14:00:00+08:00"
        newer["completeness"].update(method="合成示範：第二份完整快照，固定一則留言；未宣稱來源改單事件。",
                                    declared_at="2026-11-05T14:05:00+08:00", evidence_refs=["synthetic:one-independent-row"])
        newer["comments"] = [{**snapshot["comments"][0], "text": "A+3 B+1"}]
        new_run = import_snapshot(store, encoded(newer).encode("utf-8"), config_raw, operator="合成示範操作者")
        latest = accept_snapshot(store, new_run["run_id"], operator="合成示範操作者")
        current = accepted_payload(store, latest["note_id"])
        if totals(current) != {"A": 3, "B": 1}:
            raise ContractError("示範失敗：新快照被錯誤累加")
        latest_report = export_report(current, root / "reports")
        steps.append(("新快照替換", "選定第二份完整快照，現在 A=3、B=1；不與舊版相加，歷史保留。"))
    links = [("先看：有問句的核對草稿", draft), ("人工核對後：A=4、B=2", first_report), ("目前選定版本：A=3、B=1", latest_report)]
    link_html = "".join(f'<p><a href="{escape((folder / "index.html").relative_to(root).as_posix(), quote=True)}">{escape(label)} →</a></p>' for label, folder in links)
    timeline = "".join(f'<tr><td>{i}</td><td>{escape(title)}</td><td>{escape(detail)}</td><td>通過</td></tr>' for i, (title, detail) in enumerate(steps, 1))
    body = f'''<p>LINE Note Order Sync · 功能 POC</p><h1>從喊單到可核對訂單</h1>
<span class="tag">合成資料示範 · 未連接 LINE</span><p>以下結果由實際 parser、SQLite、審核及匯出流程產生。</p>
<div class="cards"><div class="card">目前商品 A<span class="number">3</span>件</div>
<div class="card">目前商品 B<span class="number">1</span>件</div><div class="card">展示流程<span class="number">6</span>步驟完成</div></div>
<section><h2>直接看報表</h2>{link_html}</section><section><h2>已實際執行的流程</h2>
<div class="scroll"><table><tr><th>#</th><th>功能</th><th>實際結果</th><th>狀態</th></tr>{timeline}</table></div></section>
<section><h2>你可以接著試</h2><p>用 notesync import／inspect／review／accept／export 操作合成 JSON。
每筆訂單保留原文、批次、規則版本與人工理由；CSV 可在 Excel 開啟。</p>
<p>這版支援手動 JSON。LINE 擷取、真實 TXT、YAML 載入、排程、付款及物流尚未實作。</p>
<p>示範用獨立 orders.sqlite3；沒有讀取 LINE 或其他訂單資料庫。</p></section>'''
    (root / "index.html").write_text(page("LINE 訂單功能 POC", body), encoding="utf-8")
    result = {"report": str(root / "index.html"), "database": str(root / "orders.sqlite3"), "totals": totals(current),
              "steps_passed": len(steps), "synthetic": True, "line_capture": "NOT_EVALUATED"}
    (root / "demo-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
