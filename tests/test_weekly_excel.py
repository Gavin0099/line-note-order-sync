import json
from pathlib import Path
from xml.dom.minidom import parseString
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pytest

from notesync.cli import main
from notesync.domain.models import ContractError
from notesync.exporters.note_xlsx import MAIN as SPREADSHEET, Worksheet, write_workbook
from notesync.exporters.weekly_excel import export_weekly_excel


SERIES = "合成發條救援"
WEBSITE_BUYER = "合成網站買家"
NS = {"s": SPREADSHEET}


def write_weekly_source(path: Path, *, series=SERIES, overview_total=21, wrong_buyer=False, pending=None, a_units=7):
    names = ("週報總覽", series, f"{series} A款", f"{series} B款")
    sheets = (
        [["合成週報"], ["商品／貼文", "發文日期", "結團截止（台北）", "擷取狀態", "已讀留言", "確認數量", "暱稱／數量待核對"],
         ["別的系列", "2026-11-04", None, "尚未結團，未擷取"],
         [series, "2026-11-05", None, "已擷取", 4, overview_total, pending]],
        [[series], ["暱稱", "數量"], [WEBSITE_BUYER, 9], ["合成買家甲", a_units], ["合成買家乙", 5]],
        [[names[2]], ["暱稱", "數量"], [WEBSITE_BUYER, 5], ["另一位同量買家" if wrong_buyer else "合成買家甲", a_units]],
        [[names[3]], ["暱稱", "數量"], [WEBSITE_BUYER, 4], ["合成買家乙", 5]],
    )
    write_workbook(path, [Worksheet(name, [tuple(row) for row in rows], (20,) * len(rows[1]), 2)
                          for name, rows in zip(names, sheets, strict=True)])
    return path


def read_cells(book, part):
    result = {}
    for cell in ET.fromstring(book.read(part)).findall(".//s:c", NS):
        result[cell.get("r")] = cell.findtext("s:v", namespaces=NS) if cell.get("t") == "n" else cell.findtext("s:is/s:t", namespaces=NS)
    return result


def test_weekly_cli_preserves_source_and_appends_only_variant_rows(tmp_path, capsys):
    source = write_weekly_source(tmp_path / "weekly.xlsx")
    original = source.read_bytes()
    output = tmp_path / "website.xlsx"
    assert main(["weekly-export", str(source), "--series", SERIES, "--output", str(output)]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "website_excel": str(output), "completeness": "PARTIAL", "units_by_variant": {"A": 12, "B": 9},
        "units": 21, "buyer_packages": 3, "item_rows": 4,
    }
    assert source.read_bytes() == original
    with ZipFile(source) as old, ZipFile(output) as new:
        for path in old.namelist():
            if path not in {"[Content_Types].xml", "xl/workbook.xml", "xl/_rels/workbook.xml.rels"}:
                assert new.read(path) == old.read(path)
        sheets = ET.fromstring(new.read("xl/workbook.xml")).findall("s:sheets/s:sheet", NS)
        assert [(sheet.get("name"), sheet.get("state")) for sheet in sheets[-2:]] == [("包書明細", None), ("匯入資訊", "hidden")]
        package_links = parseString(new.read("xl/_rels/workbook.xml.rels")).getElementsByTagName("Relationship")
        assert package_links[-2].getAttribute("Target") == "/xl/worksheets/notesync-weekly-5.xml"
        cells = read_cells(new, "xl/worksheets/notesync-weekly-5.xml")
        assert [(cells[f"A{i}"], cells[f"D{i}"], cells[f"G{i}"], cells[f"J{i}"]) for i in range(5, 9)] == [
            ("001", f"{SERIES} A款", "5", "A"), ("002", f"{SERIES} A款", "7", "A"),
            ("001", f"{SERIES} B款", "4", "B"), ("003", f"{SERIES} B款", "5", "B"),
        ]
        assert all(f"{column}{i}" not in cells for column in ("F", "H") for i in range(5, 9))
        assert read_cells(new, "xl/worksheets/notesync-weekly-6.xml")["B2"] == "PARTIAL"
    same = tmp_path / "repeat.xlsx"
    export_weekly_excel(source, same, SERIES)
    assert same.read_bytes() == output.read_bytes()
    with pytest.raises(ContractError, match="輸出檔已存在"):
        export_weekly_excel(source, output, SERIES)
    with pytest.raises(ContractError, match="已含網站匯入工作表"):
        export_weekly_excel(output, tmp_path / "duplicate.xlsx", SERIES)


@pytest.mark.parametrize("overrides", [{"wrong_buyer": True}, {"overview_total": 22}])
def test_conflicting_breakdown_refuses_even_with_manual_confirmation(tmp_path, overrides):
    source = write_weekly_source(tmp_path / "weekly.xlsx", **overrides)
    output = tmp_path / "website.xlsx"
    with pytest.raises(ContractError, match="暱稱或數量"):
        export_weekly_excel(source, output, SERIES, verified_note="fixture-post")
    assert not output.exists()


def test_uses_original_series_title_when_tab_names_are_sanitized_and_shortened(tmp_path):
    series = "合成/需要縮短的系列：" + "長" * 35
    source = write_weekly_source(tmp_path / "weekly.xlsx", series=series)
    output = tmp_path / "website.xlsx"
    assert export_weekly_excel(source, output, series)["units"] == 21


def test_pending_counts_allow_draft_but_block_declared_complete(tmp_path):
    source = write_weekly_source(tmp_path / "weekly.xlsx", pending=1)
    assert export_weekly_excel(source, tmp_path / "draft.xlsx", SERIES)["completeness"] == "PARTIAL"
    complete = tmp_path / "verified.xlsx"
    with pytest.raises(ContractError, match="仍有待核對留言"):
        export_weekly_excel(source, complete, SERIES, verified_note="fixture-post")
    assert not complete.exists()


def test_verified_export_keeps_note_identity_when_quantities_change(tmp_path):
    first = write_weekly_source(tmp_path / "first.xlsx")
    second = write_weekly_source(tmp_path / "second.xlsx", overview_total=22, a_units=8)
    outputs = [tmp_path / "website1.xlsx", tmp_path / "website2.xlsx"]
    metadata = []
    for source, output in zip((first, second), outputs, strict=True):
        export_weekly_excel(source, output, SERIES, verified_note="fixture-post")
        with ZipFile(output) as book:
            metadata.append(read_cells(book, "xl/worksheets/notesync-weekly-6.xml"))
    assert [row["B2"] for row in metadata] == ["DECLARED_COMPLETE", "DECLARED_COMPLETE"]
    assert metadata[0]["B4"] == metadata[1]["B4"]
    assert metadata[0]["B3"] != metadata[1]["B3"]
