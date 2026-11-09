"""One worksheet per note with a title and reviewable quantities."""

from dataclasses import dataclass
from pathlib import Path
import re
from xml.sax.saxutils import escape, quoteattr
from zipfile import ZIP_DEFLATED, ZipFile

from notesync.domain.models import ContractError
from notesync.parser.note_quantity import comment_quantity as comment_quantity, nickname_totals


MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT = "http://schemas.openxmlformats.org/package/2006/content-types"
INVALID_XML = re.compile(r"[^\x09\x0a\x0d\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]")


@dataclass(frozen=True)
class Worksheet:
    title: str
    values: list[tuple]
    widths: tuple[int, ...]
    header_row: int
    merge_title: bool = False


def text_cell(address: str, value: str) -> str:
    if INVALID_XML.search(value) or len(value.encode("utf-16-le")) > 65534:
        raise ContractError("留言文字超出 Excel 儲存格支援範圍")
    protected = re.sub(r"_(?=x[0-9a-fA-F]{4}_)", "_x005F_", value)
    literal = escape(protected).replace("\r", "&#13;")
    return f'<c r="{address}" t="inlineStr"><is><t xml:space="preserve">{literal}</t></is></c>'


def write_note_xlsx(path: Path, subject: str, comments: list[tuple[str, str]], *,
                    item_codes: list[str] | None = None) -> None:
    write_worksheet(path, subject, [(subject,), ("暱稱", "數量"), *nickname_totals(comments, item_codes=item_codes)],
                    widths=(44, 14), header_row=2, merge_title=True)


def write_worksheet(path: Path, subject: str, values: list[tuple], *, widths: tuple[int, ...],
                    header_row: int, merge_title: bool = False) -> None:
    write_workbook(path, [Worksheet(subject, values, widths, header_row, merge_title)])


def sheet_xml(values: list[tuple], widths: tuple[int, ...], header_row: int, merge_title: bool) -> str:
    rows = []
    for row, columns in enumerate(values, 1):
        cells = []
        for index, value in enumerate(columns):
            address = f"{chr(65 + index)}{row}"
            if isinstance(value, str):
                cells.append(text_cell(address, value))
            elif value is not None:
                cells.append(f'<c r="{address}" t="n"><v>{value}</v></c>')
        rows.append(f'<row r="{row}">{"".join(cells)}</row>')

    end_column = chr(64 + len(widths))
    cols = ''.join(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>'
                   for i, width in enumerate(widths, 1))
    merge = '<mergeCells count="1"><mergeCell ref="A1:B1"/></mergeCells>' if merge_title else ''
    return f'<worksheet xmlns="{MAIN}">' + (
        f'<dimension ref="A1:{end_column}{len(rows)}"/>'
        f'<sheetViews><sheetView workbookViewId="0"><pane ySplit="{header_row}" topLeftCell="A{header_row + 1}" '
        'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        f'<cols>{cols}</cols>'
        f'<sheetData>{"".join(rows)}</sheetData>'
        f'<autoFilter ref="A{header_row}:{end_column}{len(rows)}"/>'
        f'{merge}</worksheet>'
    )


def write_workbook(path: Path, worksheets: list[Worksheet]) -> None:
    names = set()
    sheets, relationships, types = [], [], []
    for index, sheet in enumerate(worksheets, 1):
        root = re.sub(r"[\\/?:*\[\]]", " ", sheet.title)
        root = " ".join(root.split())[:31].strip(" '") or "LINE 留言"
        name, repeat = root, 1
        while name.casefold() in names:
            repeat += 1
            suffix = f" ({repeat})"
            name = root[:31 - len(suffix)] + suffix
        names.add(name.casefold())
        sheets.append(f'<sheet name={quoteattr(name)} sheetId="{index}" r:id="rId{index}"/>')
        relationships.append(f'<Relationship Id="rId{index}" Type="{DOC_REL}/worksheet" '
                             f'Target="worksheets/sheet{index}.xml"/>')
        types.append(f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
                     'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
    with ZipFile(path, "x", ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", (
            f'<Types xmlns="{CONTENT}">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            + ''.join(types) + '</Types>'
        ))
        workbook.writestr("_rels/.rels", (
            f'<Relationships xmlns="{PKG_REL}"><Relationship Id="rId1" '
            f'Type="{DOC_REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
        ))
        workbook.writestr("xl/workbook.xml", (
            f'<workbook xmlns="{MAIN}" xmlns:r="{DOC_REL}"><sheets>'
            + ''.join(sheets) + '</sheets></workbook>'
        ))
        workbook.writestr("xl/_rels/workbook.xml.rels", (
            f'<Relationships xmlns="{PKG_REL}">' + ''.join(relationships) + '</Relationships>'
        ))
        for index, sheet in enumerate(worksheets, 1):
            workbook.writestr(f"xl/worksheets/sheet{index}.xml",
                             sheet_xml(sheet.values, sheet.widths, sheet.header_row, sheet.merge_title))
