"""Append the Mei import sheets to a reconciled, explicitly selected weekly series."""

from collections import Counter
from hashlib import sha256
from io import BytesIO
import os
from pathlib import Path, PurePosixPath
import re
from tempfile import TemporaryDirectory
from xml.dom.minidom import Element as DomElement, parseString
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo

from notesync.domain.models import ContractError
from notesync.exporters.mei_notebook import HEADERS, limited_text
from notesync.exporters.note_xlsx import DOC_REL as RELATIONSHIPS, MAIN as SPREADSHEET, Worksheet, sheet_xml
from notesync.service import encoded


_MIB = 1024 * 1024
_MAX_UNITS = 2**53 - 1
_WORKBOOK = "xl/workbook.xml"
_RELS = "xl/_rels/workbook.xml.rels"
_TYPES = "[Content_Types].xml"
_OVERVIEW = "週報總覽"
_NS = {"s": SPREADSHEET}
_WORKSHEET = f"{RELATIONSHIPS}/worksheet"
SHEET_NAMES = ("包書明細", "匯入資訊")


def _xml(book: ZipFile, part: str) -> ET.Element:
    contents = book.read(part)
    if b"<!DOCTYPE" in contents or b"<!ENTITY" in contents:
        raise ContractError("週報含有不支援的 XML 宣告")
    return ET.fromstring(contents)


def _text(node: ET.Element) -> str:
    return "".join(part.text or "" for part in (*node.findall("s:t", _NS), *node.findall("s:r/s:t", _NS)))


def _worksheet_rows(book: ZipFile, part: str) -> dict[int, dict[str, ET.Element]]:
    rows = {}
    for row in _xml(book, part).findall("s:sheetData/s:row", _NS):
        index = int(row.attrib["r"])
        if index in rows or not 1 <= index <= 5000:
            raise ContractError("週報有重複列，或超過 5000 列")
        cells = {}
        for cell in row.findall("s:c", _NS):
            address = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]*)", cell.attrib["r"])
            if not address or int(address[2]) != index or address[1] in cells:
                raise ContractError("週報儲存格位置不一致")
            cells[address[1]] = cell
        rows[index] = cells
    return rows


def _value(row: dict[str, ET.Element], column: str, shared: list[str]) -> str | int | None:
    cell = row.get(column)
    if cell is None:
        return None
    if cell.find("s:f", _NS) is not None:
        raise ContractError("週報的核對欄位需使用固定值")
    kind = cell.get("t", "n")
    if kind == "inlineStr":
        inline = cell.find("s:is", _NS)
        return _text(inline).strip() if inline is not None else None
    raw = cell.findtext("s:v", default="", namespaces=_NS)
    if not raw:
        return None
    if kind == "s" and re.fullmatch(r"[0-9]+", raw):
        return shared[int(raw)].strip()
    if kind == "str":
        return raw.strip()
    if kind == "n" and re.fullmatch(r"[0-9]+", raw):
        return int(raw)
    raise ContractError("週報的核對欄位格式不符")


def _counts(rows: dict[int, dict[str, ET.Element]], name: str, shared: list[str]) -> dict[str, int]:
    if _value(rows.get(1, {}), "A", shared) != name or (
        _value(rows.get(2, {}), "A", shared), _value(rows.get(2, {}), "B", shared)
    ) != ("暱稱", "數量"):
        raise ContractError("系列明細的標題或「暱稱／數量」表頭不符")
    result = {}
    for index, row in sorted(rows.items()):
        if index <= 2:
            continue
        nickname, quantity = (_value(row, column, shared) for column in ("A", "B"))
        if nickname in (None, "") and quantity is None:
            continue
        if not isinstance(nickname, str) or not isinstance(quantity, int) or not 1 <= quantity <= _MAX_UNITS:
            raise ContractError(f"系列明細第 {index} 列需要暱稱與正整數數量")
        limited_text(nickname, 120)
        if nickname in result:
            raise ContractError(f"系列明細第 {index} 列暱稱重複，請先核對")
        result[nickname] = quantity
    return result


def _sheet_parts(sheets: ET.Element, relationships: ET.Element) -> dict[str, str]:
    worksheet_targets = {
        rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships
        if rel.get("Type") == _WORKSHEET and rel.get("TargetMode", "Internal") == "Internal"
    }
    parts = {}
    for sheet in sheets:
        name = sheet.attrib["name"]
        if name in parts:
            raise ContractError("週報工作表名稱重複")
        target = worksheet_targets[sheet.attrib[f"{{{RELATIONSHIPS}}}id"]]
        path = PurePosixPath(target.lstrip("/") if target.startswith("/") else f"xl/{target}")
        if path.parent != PurePosixPath("xl/worksheets"):
            raise ContractError("週報工作表路徑不符")
        parts[name] = str(path)
    return parts


def _reconcile(book: ZipFile, parts: dict[str, str], series: str) -> tuple[dict[str, dict[str, int]], bool]:
    shared = ([_text(node) for node in _xml(book, "xl/sharedStrings.xml").findall("s:si", _NS)]
              if "xl/sharedStrings.xml" in book.namelist() else [])
    overview = _worksheet_rows(book, parts[_OVERVIEW])
    headings = {column: _value(overview.get(2, {}), column, shared) for column in ("A", "D", "F", "G")}
    if headings != {"A": "商品／貼文", "D": "擷取狀態", "F": "確認數量", "G": "暱稱／數量待核對"}:
        raise ContractError("週報總覽表頭不符")
    selected = [row for index, row in overview.items() if index > 2 and _value(row, "A", shared) == series]
    if len(selected) != 1 or _value(selected[0], "D", shared) != "已擷取":
        raise ContractError("週報總覽需要一筆相符且已擷取的系列")
    requested_titles = {series, f"{series} A款", f"{series} B款"}
    detail = {}
    for name, part in parts.items():
        if name == _OVERVIEW:
            continue
        rows = _worksheet_rows(book, part)
        title = _value(rows.get(1, {}), "A", shared)
        if title in requested_titles:
            if title in detail:
                raise ContractError("週報有多張相同標題的系列明細，請先核對")
            detail[title] = _counts(rows, title, shared)
    if detail.keys() != requested_titles:
        raise ContractError("週報缺少系列總表、A 款或 B 款")
    variants = {sku: detail[f"{series} {sku}款"] for sku in ("A", "B")}
    series_totals = detail[series]
    combined = Counter(variants["A"]) + Counter(variants["B"])
    units = sum(combined.values())
    if not combined or combined != series_totals or _value(selected[0], "F", shared) != units:
        raise ContractError("A、B 款的暱稱或數量與系列總表或週報總覽不符")
    if len(combined) > 100 or units > _MAX_UNITS:
        raise ContractError("週報超過網站匯入的買家或數量上限")
    unresolved = _value(selected[0], "G", shared)
    return variants, unresolved not in (None, "", 0, "0")


def _append_element(parent: DomElement, name: str, attributes: dict[str, str]) -> DomElement:
    tag = f"{parent.prefix}:{name}" if parent.prefix else name
    element = parent.ownerDocument.createElementNS(parent.namespaceURI, tag)
    for key, value in attributes.items():
        element.setAttribute(key, value)
    parent.appendChild(element)
    return element


def _append_sheets(book: ZipFile, sheets: ET.Element, rels: ET.Element, additions: list[Worksheet]) -> bytes:
    _xml(book, _TYPES)
    # Keep the source namespaces on package manifests for Excel and the website reader.
    manifests = {part: parseString(book.read(part)) for part in (_WORKBOOK, _RELS, _TYPES)}
    workbook_sheets = manifests[_WORKBOOK].getElementsByTagNameNS(SPREADSHEET, "sheets")[0]
    next_id = max(int(sheet.attrib["sheetId"]) for sheet in sheets) + 1
    new_parts = {}
    for index, addition in enumerate(additions, next_id):
        name = addition.title
        path = f"xl/worksheets/notesync-weekly-{index}.xml"
        rel_id = f"rIdNotesyncWeekly{index}"
        if path in book.namelist() or any(rel.get("Id") == rel_id for rel in rels):
            raise ContractError("週報的匯入工作表已存在")
        attributes = {"name": name, "sheetId": str(index)}
        if addition.hidden:
            attributes["state"] = "hidden"
        sheet = _append_element(workbook_sheets, "sheet", attributes)
        sheet.setAttribute("xmlns:r", RELATIONSHIPS)
        sheet.setAttributeNS(RELATIONSHIPS, "r:id", rel_id)
        _append_element(manifests[_RELS].documentElement, "Relationship", {
            "Id": rel_id, "Type": _WORKSHEET, "Target": f"/{path}",
        })
        _append_element(manifests[_TYPES].documentElement, "Override", {
            "PartName": f"/{path}", "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml",
        })
        new_parts[path] = sheet_xml(addition.values, addition.widths, addition.header_row, addition.merge_title).encode("utf-8")
    updates = {path: document.toxml(encoding="utf-8") for path, document in manifests.items()}
    output = BytesIO()
    with ZipFile(output, "w") as result:
        for part in book.infolist():
            result.writestr(part, updates[part.filename] if part.filename in updates else book.read(part))
        for path, contents in new_parts.items():
            result.writestr(ZipInfo(path), contents, compress_type=ZIP_DEFLATED)
    return output.getvalue()


def weekly_import_sheets(series: list[tuple[str, dict[str, dict[str, int]]]], *,
                         verified_note: str | None = None) -> tuple[list[Worksheet], dict]:
    """Build a single import sheet from already reconciled A/B series."""
    status = "DECLARED_COMPLETE" if verified_note else "PARTIAL"
    note_id = sha256(encoded(["weekly-note", verified_note or [title for title, _ in series]]).encode("utf-8")).hexdigest()
    snapshot = sha256(encoded([series, note_id, status]).encode("utf-8")).hexdigest()
    label = "LINE 週報 · 人工核對完整" if verified_note else "LINE 週報 · 待核對草稿"
    rows: list[tuple] = [(label,), (), (), HEADERS]
    packages: dict[str, str] = {}
    units: Counter = Counter()
    for index, (title, variants) in enumerate(series, 1):
        for code, counts in variants.items():
            sku = code if len(series) == 1 else f"{index:03d}-{code}"
            for nickname, quantity in counts.items():
                limited_text(nickname, 120)
                package = packages.setdefault(nickname, f"{len(packages) + 1:03}")
                rows.append((package, nickname, "記事本", limited_text(f"{title} {code}款", 240),
                             None, None, quantity, None, None, sku))
                units[code] += quantity
    total = units.total()
    if not units or len(packages) > 100 or len(rows) - 4 > 1000 or total > _MAX_UNITS:
        raise ContractError("週報明細無有效品項，或超過網站的買家、品項或數量上限")
    metadata = [("格式", "LINE_NOTE_ORDER_SYNC_V1"), ("完整性", status),
                ("快照", f"sha256:{snapshot}"), ("記事本識別", f"sha256:{note_id}")]
    sheets = [
        Worksheet("包書明細", rows, (14, 22, 16, 42, 12, 12, 12, 12, 14, 16), 4),
        Worksheet("匯入資訊", metadata, (14, 85), 1, hidden=True),
    ]
    return sheets, {"completeness": status, "units_by_variant": dict(units), "units": total,
                    "buyer_packages": len(packages), "item_rows": len(rows) - 4}


def export_weekly_excel(source: Path, output: Path, series: str, *, verified_note: str | None = None) -> dict:
    series = limited_text(series, 237)
    if verified_note is not None:
        verified_note = limited_text(verified_note, 240)
    if source.suffix.lower() != ".xlsx" or output.suffix.lower() != ".xlsx":
        raise ContractError("週報來源與輸出須使用 .xlsx")
    if output.exists():
        raise ContractError("輸出檔已存在，請指定新的 .xlsx 路徑")
    if source.stat().st_size > 5 * _MIB:
        raise ContractError("週報來源超過 5 MiB")
    try:
        with ZipFile(source) as book:
            parts = book.infolist()
            if (len(parts) > 498 or len(set(book.namelist())) != len(parts)
                or sum(part.file_size for part in parts) > 39 * _MIB
                or any(part.file_size > 20 * _MIB or part.flag_bits & 1
                       or part.compress_type not in (0, ZIP_DEFLATED) for part in parts)):
                raise ContractError("週報壓縮檔格式或大小不符")
            workbook, rels = _xml(book, _WORKBOOK), _xml(book, _RELS)
            sheets = workbook.find("s:sheets", _NS)
            if sheets is None:
                raise ContractError("週報缺少工作表")
            sheet_parts = _sheet_parts(sheets, rels)
            if any(name in sheet_parts for name in SHEET_NAMES):
                raise ContractError("週報已含網站匯入工作表，請用原始週報重新匯出")
            variants, unresolved = _reconcile(book, sheet_parts, series)
            if verified_note and unresolved:
                raise ContractError("所選系列仍有待核對留言，僅能匯出草稿")
            additions, summary = weekly_import_sheets([(series, variants)], verified_note=verified_note)
            data = _append_sheets(book, sheets, rels, additions)
    except ContractError:
        raise
    except (BadZipFile, ET.ParseError, KeyError, IndexError, ValueError) as exc:
        raise ContractError("週報無法讀取或缺少系列總表、A 款、B 款") from exc
    if len(data) > 5 * _MIB:
        raise ContractError("匯出結果超過網站上限 5 MiB")
    with TemporaryDirectory(prefix=".notesync-weekly-", dir=output.parent) as staging:
        complete = Path(staging) / "weekly.xlsx"
        complete.write_bytes(data)
        os.link(complete, output)
    return {"website_excel": str(output), **summary}
