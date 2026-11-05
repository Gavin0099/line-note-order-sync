"""Atomic, version-fixed CSV/HTML report bundles with visible trust labels."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
import json
from pathlib import Path
import tempfile

from notesync.domain.models import ContractError
from notesync.service import now, totals


def safe_cell(value: object) -> object:
    if not isinstance(value, str):
        return value
    stripped = value.lstrip(" \t\r\n\ufeff")
    if stripped.startswith(("=", "+", "-", "@")) or (value and (ord(value[0]) < 32 or value[0] == "\ufeff")):
        return "'" + value
    return value


def _csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: safe_cell(row.get(key, "")) for key in fields})


def page(title: str, body: str) -> str:
    return f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><style>
body{{font:16px/1.6 system-ui,sans-serif;background:#f2f5f4;color:#19332d;margin:0}}
main{{max-width:1100px;margin:40px auto;padding:0 24px 50px}}h1{{font-size:32px;margin-bottom:8px}}
.tag{{display:inline-block;background:#e4ba62;color:#362b13;padding:5px 12px;border-radius:6px;font-weight:700}}
.cards{{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}}.card{{background:white;padding:20px 28px;border-radius:12px;min-width:130px}}
.number{{display:block;font-size:36px;font-weight:700}}section{{background:white;padding:24px;border-radius:12px;margin:20px 0}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:12px;border-bottom:1px solid #dce5df;text-align:left;vertical-align:top}}
td{{white-space:pre-wrap;overflow-wrap:anywhere}}a{{color:#086754}}code{{overflow-wrap:anywhere}}small{{color:#536a62}}
.scroll{{overflow-x:auto}}details{{margin:14px 0}}.warning{{border-left:5px solid #d9a441;padding-left:16px}}
</style><main>{body}</main></html>'''


def buyer_totals(payload: dict) -> list[dict]:
    grouped: Counter = Counter()
    for row in payload["comments"]:
        if row["status"] == "PARSED" and not row["flags"]:
            for sku, quantity in row["items"].items():
                grouped[(row.get("buyer_key", ""), row["buyer_label"], sku)] += quantity
    return [{"buyer_key": key, "buyer_label": label, "sku": sku, "quantity": quantity}
            for (key, label, sku), quantity in sorted(grouped.items())]


def report_html(payload: dict, manifest: dict) -> str:
    def e(value: object) -> str:
        return escape(str(value))
    amounts = totals(payload)
    labels = {"PARSED": "已解析", "NEEDS_REVIEW": "待核對", "NON_ORDER": "非訂單", "INVALID": "數量無效"}
    flag_labels = {"missing_buyer": "缺少買家標示", "overlap_unconfirmed": "尚未排除複製重疊", "duplicate_source_comment_id": "來源留言 ID 重複"}
    source_time = datetime.fromisoformat(payload["captured_at"]).astimezone(timezone(timedelta(hours=8))).isoformat()
    cards = "".join(f'<div class="card">商品 {e(sku)}<span class="number">{qty}</span>件</div>' for sku, qty in amounts.items())
    rows = "".join(
        "<tr>" + "".join(f"<td>{e(value)}</td>" for value in
        (row["position"], row.get("buyer_key", "—"), row["buyer_label"], row["text"],
         labels[row["status"]], "、".join(f"{s} × {q}" for s, q in row["items"].items()),
         "、".join(flag_labels[f] for f in row["flags"]), row["reason"])) + "</tr>"
        for row in payload["comments"])
    buyers = "".join("<tr>" + "".join(f"<td>{e(r[key])}</td>" for key in ("buyer_key", "buyer_label", "sku", "quantity")) + "</tr>" for r in buyer_totals(payload))
    reviews = "".join(f'<li>留言 {e(r["position"])}：{e(r["operator"])} — {e(r["reason"])}</li>' for r in payload["reviews"])
    source = payload["source"]
    body = f'''<p>LINE Note Order Sync · 本機手動匯入</p><h1>訂單核對報表</h1>
<span class="tag">{'核對草稿' if manifest['mode'] == 'DRAFT' else '人工宣告完整'} · {e(manifest['mode'])}</span>
<p class="warning">{'草稿：未接受或有未決資料，不可作叫貨依據。' if manifest['mode'] == 'DRAFT' else '完整性由操作者人工宣告；此報表不是 LINE 自動同步成功證明。'}
同社群暱稱彙總接受同名／改名風險；所有原始 occurrence 均保留。</p>
<p>社群：{e(source['scope_key'])} ／ 記事本：{e(source['note_key'])}<br>
來源時間（Asia/Taipei）：{e(source_time)} ／ 接受版本：{e(payload.get('acceptance_id', '未接受'))}</p>
<p>版本接受人：{e(payload.get('accepted_by', '未接受'))} ／ 目前選用人：{e(payload.get('selection', {}).get('operator', '未選定'))}<br>
選用時間：{e(payload.get('selection', {}).get('selected_at', '未選定'))}</p>
<div class="cards">{cards or '<div class="card">目前無有效訂單</div>'}
<div class="card">待核對<span class="number">{len(payload['blocking'])}</span>則</div></div>
<p><a href="{e(manifest['files']['details'])}">留言明細 CSV</a> · <a href="{e(manifest['files']['buyers'])}">買家彙總 CSV</a> · <a href="{e(manifest['files']['totals'])}">商品統計 CSV</a> · <a href="manifest.json">來源 manifest</a></p>
<section><h2>買家彙總</h2><div class="scroll"><table><tr><th>買家鍵</th><th>彙總名稱</th><th>SKU</th><th>數量</th></tr>{buyers}</table></div></section>
<section><h2>原始留言與處理結果</h2><div class="scroll"><table><thead><tr>
<th>位置</th><th>買家鍵</th><th>彙總名稱</th><th>原文</th><th>狀態</th><th>商品候選</th><th>阻擋原因</th><th>理由</th>
</tr></thead><tbody>{rows}</tbody></table></div></section>
<section><h2>人工核對紀錄</h2><ul>{reviews or '<li>無人工改判</li>'}</ul>
<details><summary>追溯資訊</summary><p>batch {e(payload['batch_id'])} / run {e(payload['id'])} / parser {e(payload['parser_version'])}<br>
輸入 SHA-256：<code>{e(payload['raw_sha256'])}</code><br>設定 SHA-256：<code>{e(payload['config_sha256'])}</code><br>
宣告人：{e(payload['completeness']['operator'])}；宣告時間：{e(payload['completeness']['declared_at'])}<br>
方法：{e(payload['completeness']['method'])}</p></details></section>'''
    return page("訂單核對報表", body)


def export_report(payload: dict, root: str | Path, *, draft: bool = False) -> Path:
    if not draft and (not payload.get("acceptance_id") or not payload.get("selection") or payload["blocking"] or payload["completeness"]["status"] != "DECLARED_COMPLETE"):
        raise ContractError("正式匯出需固定的已接受、無阻擋且人工宣告完整版本")
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    mode = "DRAFT" if draft else "HUMAN_DECLARED"
    # Safe filename uses database integers plus a compact source timestamp.
    stamp = datetime.fromisoformat(payload["captured_at"]).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    identifier = payload["id"] if draft else payload["acceptance_id"]
    suffix = str(int(identifier)) if draft else f"accept-{int(identifier)}_selection-{int(payload['selection']['id'])}"
    destination = root / f"note-{int(payload['note_id'])}_{stamp}_{mode}_{suffix}"
    if destination.exists():
        raise ContractError("報表目錄已存在；請指定另一個輸出根目錄，原報表不覆寫")
    manifest = {"mode": mode, "generated_at": now(), "source": payload["source"],
                "captured_at": payload["captured_at"], "completeness": payload["completeness"],
                "acceptance_id": payload.get("acceptance_id"), "batch_id": payload["batch_id"],
                "run_id": payload["id"], "revision": payload["revision"], "parser_version": payload["parser_version"],
                "input_sha256": payload["raw_sha256"], "config_sha256": payload["config_sha256"],
                "accepted_by": payload.get("accepted_by"), "accepted_at": payload.get("accepted_at"),
                "selection": payload.get("selection"), "storage_schema_version": payload["storage_schema_version"],
                "blocking_positions": payload["blocking"], "totals": totals(payload),
                "identity_mode": "community_nickname_grouping_not_stable_identity",
                "files": {key: f"{mode}_{stamp}_{key}.csv" for key in ("details", "buyers", "totals", "review")}}
    details = []
    for row in payload["comments"]:
        for sku, quantity in (row["items"].items() if row["status"] == "PARSED" and not row["flags"] else [("", "")]):
            details.append({"batch_id": payload["batch_id"], "run_id": payload["id"], "position": row["position"],
                            "buyer_key": row.get("buyer_key", ""), "display_name": row["display_name"],
                            "buyer_label": row["buyer_label"], "sku": sku, "quantity": quantity,
                            "status": row["status"], "original_text": row["text"], "reason": row["reason"], "flags": ",".join(row["flags"]),
                            "source_kind": payload["source"]["kind"], "scope_key": payload["source"]["scope_key"], "note_key": payload["source"]["note_key"]})
    with tempfile.TemporaryDirectory(prefix=".notesync-staging-", dir=root) as temporary:
        staging = Path(temporary)
        fields = ["source_kind", "scope_key", "note_key", "batch_id", "run_id", "position", "buyer_key", "display_name", "buyer_label", "sku", "quantity", "status", "original_text", "flags", "reason"]
        _csv(staging / manifest["files"]["details"], fields, details)
        _csv(staging / manifest["files"]["buyers"], ["buyer_key", "buyer_label", "sku", "quantity"], buyer_totals(payload))
        _csv(staging / manifest["files"]["totals"], ["sku", "quantity"], [{"sku": s, "quantity": q} for s, q in totals(payload).items()])
        _csv(staging / manifest["files"]["review"], fields, [r for r in details if r["status"] in ("NEEDS_REVIEW", "INVALID") or r["flags"]])
        (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (staging / "index.html").write_text(report_html(payload, manifest), encoding="utf-8")
        staging.rename(destination)
    return destination
