"""Strict JSON adapter. It cannot establish native LINE completeness or IDs."""

from __future__ import annotations

from datetime import datetime
import json

from notesync.domain.models import ContractError, nonempty, require_keys


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("JSON 含重複欄位")
        result[key] = value
    return result


def _reject_constant(value: str):
    raise ContractError("不接受非有限數值")


def load_json(raw: bytes) -> dict:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ContractError("需提供有效 UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ContractError("JSON 根節點必須是物件")
    pending = [value]
    while pending:
        part = pending.pop()
        if isinstance(part, dict):
            pending.extend(part.keys())
            pending.extend(part.values())
        elif isinstance(part, list):
            pending.extend(part)
        elif isinstance(part, str):
            try:
                part.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise ContractError("JSON 含無效 Unicode 字元") from exc
    return value


def timestamp(value: object) -> str:
    value = nonempty(value)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ContractError("時間需為含時區的 ISO 8601") from exc
    if parsed.utcoffset() is None:
        raise ContractError("時間不得缺少時區")
    return value


def validate_snapshot(raw: bytes) -> dict:
    doc = load_json(raw)
    require_keys(doc, {"format_version", "source", "captured_at", "adapter_version", "completeness", "comments"})
    if type(doc["format_version"]) is not int or doc["format_version"] != 1:
        raise ContractError("快照格式版本必須是整數 1")
    require_keys(doc["source"], {"kind", "scope_key", "note_key"})
    if doc["source"]["kind"] not in ("line_group_note", "line_openchat_note"):
        raise ContractError("來源種類不支援")
    nonempty(doc["source"]["scope_key"])
    nonempty(doc["source"]["note_key"])
    timestamp(doc["captured_at"])
    nonempty(doc["adapter_version"])
    complete = doc["completeness"]
    require_keys(complete, {"status", "method", "operator", "declared_at", "evidence_refs"})
    if complete["status"] not in ("VERIFIED_COMPLETE", "DECLARED_COMPLETE", "PARTIAL", "UNKNOWN"):
        raise ContractError("完整性狀態無效")
    nonempty(complete["method"])
    if complete["operator"] is not None:
        nonempty(complete["operator"])
    if complete["declared_at"] is not None:
        timestamp(complete["declared_at"])
    if not isinstance(complete["evidence_refs"], list):
        raise ContractError("證據參照必須是清單")
    for ref in complete["evidence_refs"]:
        nonempty(ref)
    # Missing declaration evidence is retained as a blocking state, not invented.
    if not isinstance(doc["comments"], list):
        raise ContractError("comments 必須是清單")
    for index, row in enumerate(doc["comments"]):
        require_keys(row, {"position", "display_name", "text", "source_comment_id", "source_author_id", "source_created_at"})
        if type(row["position"]) is not int or row["position"] != index:
            raise ContractError("留言 position 必須從 0 連續排列")
        if not isinstance(row["display_name"], str) or not isinstance(row["text"], str):
            raise ContractError("作者及原文必須是文字")
        for key in ("source_comment_id", "source_author_id"):
            if row[key] is not None:
                nonempty(row[key])
        if row["source_created_at"] is not None:
            timestamp(row["source_created_at"])
    return doc
