"""Application use cases connecting pure parser, manual adapter and SQLite."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

from notesync.adapters.manual_import import load_json, validate_snapshot
from notesync.domain.models import ContractError, ProductConfig, nonempty
from notesync.parser.order_parser import PARSER_VERSION, parse_order
from notesync.storage.sqlite import Store


def encoded(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row(conn, query: str, values: tuple):
    row = conn.execute(query, values).fetchone()
    if row is None:
        raise ContractError("找不到指定版本")
    return row


def import_snapshot(store: Store, raw: bytes, config_raw: bytes, *, operator: str,
                    independent_occurrences: bool = False) -> dict:
    nonempty(operator)
    if type(independent_occurrences) is not bool:
        raise ContractError("獨立 occurrence 確認須為布林")
    digest = hashlib.sha256(raw).hexdigest()
    try:
        doc = validate_snapshot(raw)
        config = ProductConfig.from_document(load_json(config_raw))
        if (config.scope_key, config.note_key) != (doc["source"]["scope_key"], doc["source"]["note_key"]):
            raise ContractError("商品設定與來源社群／記事本不符")
    except ContractError as exc:
        with store.transaction() as conn:
            conn.execute("INSERT INTO rejected_inputs(raw_sha256,raw,reason,operator,created_at) VALUES(?,?,?,?,?)",
                         (digest, raw, str(exc), operator, now()))
        raise
    config_json = encoded(config.document)
    config_hash = hashlib.sha256(config_json.encode("utf-8")).hexdigest()
    source = doc["source"]
    duplicates = Counter((r["display_name"].strip(), r["text"]) for r in doc["comments"])
    source_ids = Counter(r["source_comment_id"] for r in doc["comments"] if r["source_comment_id"])
    with store.transaction() as conn:
        conn.execute("INSERT OR IGNORE INTO notes(kind,scope_key,note_key) VALUES(?,?,?)",
                     (source["kind"], source["scope_key"], source["note_key"]))
        note_id = _row(conn, "SELECT id FROM notes WHERE kind=? AND scope_key=? AND note_key=?",
                       (source["kind"], source["scope_key"], source["note_key"]))[0]
        conn.execute("INSERT OR IGNORE INTO batches(note_id,raw_sha256,raw,captured_at,imported_at) VALUES(?,?,?,?,?)",
                     (note_id, digest, raw, doc["captured_at"], now()))
        batch_id = _row(conn, "SELECT id FROM batches WHERE note_id=? AND raw_sha256=?", (note_id, digest))[0]
        conn.execute("INSERT OR IGNORE INTO configs(sha256,document) VALUES(?,?)", (config_hash, config_json))
        config_id = _row(conn, "SELECT id FROM configs WHERE sha256=?", (config_hash,))[0]
        existing = conn.execute("SELECT id FROM runs WHERE batch_id=? AND config_id=? AND parser_version=? AND independent_confirmed=?",
                                (batch_id, config_id, PARSER_VERSION, int(independent_occurrences))).fetchone()
        if existing:
            return {"note_id": note_id, "batch_id": batch_id, "run_id": existing[0], "reused": True}
        run_id = conn.execute("INSERT INTO runs(batch_id,config_id,parser_version,independent_confirmed,operator,created_at) VALUES(?,?,?,?,?,?)",
                              (batch_id, config_id, PARSER_VERSION, int(independent_occurrences), operator, now())).lastrowid
        for row in doc["comments"]:
            parsed = parse_order(row["text"], config)
            flags = []
            if not row["display_name"].strip():
                flags.append("missing_buyer")
            if duplicates[(row["display_name"].strip(), row["text"])] > 1 and not independent_occurrences:
                flags.append("overlap_unconfirmed")
            if row["source_comment_id"] and source_ids[row["source_comment_id"]] > 1:
                flags.append("duplicate_source_comment_id")
            result = {"position": row["position"], "display_name": row["display_name"], "text": row["text"],
                      "status": parsed.status, "items": parsed.items, "reason": parsed.reason,
                      "buyer_label": row["display_name"].strip(), "flags": flags, "reviewed": False,
                      "source_comment_id": row["source_comment_id"], "source_author_id": row["source_author_id"]}
            conn.execute("INSERT INTO results(run_id,position,value) VALUES(?,?,?)", (run_id, row["position"], encoded(result)))
    return {"note_id": note_id, "batch_id": batch_id, "run_id": run_id, "reused": False}


def inspect_run(store: Store, run_id: int) -> dict:
    conn = store.conn
    info = dict(_row(conn, """SELECT runs.*, batches.note_id,batches.raw_sha256,batches.raw,
      configs.sha256 AS config_sha256,configs.document AS config_document
      FROM runs JOIN batches ON runs.batch_id=batches.id JOIN configs ON runs.config_id=configs.id WHERE runs.id=?""", (run_id,)))
    source = validate_snapshot(bytes(info.pop("raw")))
    info["source"] = source["source"]
    info["captured_at"] = source["captured_at"]
    info["completeness"] = source["completeness"]
    info["config_document"] = json.loads(info["config_document"])
    info["comments"] = [json.loads(r[0]) for r in conn.execute("SELECT value FROM results WHERE run_id=? ORDER BY position", (run_id,))]
    info["reviews"] = [dict(r) for r in conn.execute("SELECT * FROM reviews WHERE run_id=? ORDER BY id", (run_id,))]
    info["revision"] = len(info["reviews"])
    info["blocking"] = [r["position"] for r in info["comments"] if r["status"] in ("NEEDS_REVIEW", "INVALID") or r["flags"]]
    return info


def review_comment(store: Store, run_id: int, position: int, *, operator: str, reason: str,
                   items: dict | None = None, buyer_label: str | None = None) -> None:
    nonempty(operator)
    nonempty(reason)
    with store.transaction() as conn:
        run = inspect_run(store, run_id)
        original = json.loads(_row(conn, "SELECT value FROM results WHERE run_id=? AND position=?", (run_id, position))[0])
        config = ProductConfig.from_document(run["config_document"])
        result = dict(original)
        if items is None:
            result.update(status="NON_ORDER", items={}, flags=[], reason=reason, reviewed=True)
        else:
            if not isinstance(items, dict) or not items:
                raise ContractError("人工訂單需至少一個 SKU；不訂購請使用 exclude")
            for sku, quantity in items.items():
                if sku not in config.limits or type(quantity) is not int or not 1 <= quantity <= config.limits[sku]:
                    raise ContractError("人工數量／SKU 不符合商品設定")
            label = nonempty(buyer_label if buyer_label is not None else result["buyer_label"]).strip()
            result.update(status="PARSED", items=dict(items), buyer_label=label, flags=[], reason=reason, reviewed=True)
        conn.execute("INSERT INTO reviews(run_id,position,before_value,after_value,operator,reason,created_at) VALUES(?,?,?,?,?,?,?)",
                     (run_id, position, encoded(original), encoded(result), operator, reason, now()))
        conn.execute("UPDATE results SET value=? WHERE run_id=? AND position=?", (encoded(result), run_id, position))


def accept_snapshot(store: Store, run_id: int, *, operator: str) -> dict:
    nonempty(operator)
    with store.transaction() as conn:
        run = inspect_run(store, run_id)
        complete = run["completeness"]
        if complete["status"] != "DECLARED_COMPLETE":
            raise ContractError("手動 POC 只接受具人工宣告的完整快照；不授予機器驗證完整性")
        if not complete["operator"] or not complete["declared_at"] or not complete["evidence_refs"]:
            raise ContractError("人工完整宣告缺少操作者、時間或證據")
        if run["blocking"]:
            raise ContractError(f"尚有待核對留言：{run['blocking']}")
        existing = conn.execute("SELECT id FROM acceptances WHERE run_id=? AND revision=?", (run_id, run["revision"])).fetchone()
        if existing:
            # Re-selecting a historical version is explicit, never import-time behavior.
            acceptance_id = existing[0]
        else:
            for row in run["comments"]:
                if row["status"] != "PARSED":
                    continue
                s = run["source"]
                conn.execute("INSERT OR IGNORE INTO buyer_groups(kind,scope_key,label) VALUES(?,?,?)",
                             (s["kind"], s["scope_key"], row["buyer_label"]))
                group_id = _row(conn, "SELECT id FROM buyer_groups WHERE kind=? AND scope_key=? AND label=?",
                                (s["kind"], s["scope_key"], row["buyer_label"]))[0]
                row["buyer_key"] = f"buyer-{group_id}"
            run["accepted_by"] = operator
            run["accepted_at"] = now()
            acceptance_id = conn.execute("INSERT INTO acceptances(note_id,run_id,revision,payload,operator,accepted_at) VALUES(?,?,?,?,?,?)",
                                         (run["note_id"], run_id, run["revision"], encoded(run), operator, run["accepted_at"])).lastrowid
        conn.execute("INSERT INTO current_acceptances(note_id,acceptance_id) VALUES(?,?) ON CONFLICT(note_id) DO UPDATE SET acceptance_id=excluded.acceptance_id",
                     (run["note_id"], acceptance_id))
    return {"note_id": run["note_id"], "run_id": run_id, "acceptance_id": acceptance_id}


def accepted_payload(store: Store, note_id: int) -> dict:
    row = _row(store.conn, """SELECT a.id,a.payload FROM current_acceptances c
      JOIN acceptances a ON a.id=c.acceptance_id WHERE c.note_id=?""", (note_id,))
    payload = json.loads(row["payload"])
    payload["acceptance_id"] = row["id"]
    return payload


def totals(payload: dict) -> dict[str, int]:
    result: Counter = Counter()
    for row in payload["comments"]:
        if row["status"] == "PARSED" and not row["flags"]:
            result.update(row["items"])
    return dict(sorted(result.items()))
