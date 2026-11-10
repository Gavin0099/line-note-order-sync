from datetime import date, datetime
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

import pytest

from notesync.adapters import note_week
from notesync.adapters.note_auto import Footer
from notesync.adapters.note_ocr import Comment
from notesync.domain.models import ContractError
from notesync.exporters.note_xlsx import MAIN
from notesync.parser.note_dates import TAIPEI, deadline_from_text, publication_date, report_dates


TODAY = date(2026, 11, 9)
NOW = datetime(2026, 11, 9, 18, tzinfo=TAIPEI)
POSTED = date(2026, 11, 6)
NS = {"x": MAIN}


@pytest.mark.parametrize(("text", "expected"), [
    ("#1110結團", datetime(2026, 11, 11, tzinfo=TAIPEI)),
    ("#1109結團", datetime(2026, 11, 10, tzinfo=TAIPEI)),
    ("#20261109中午12點結單", datetime(2026, 11, 9, 12, tzinfo=TAIPEI)),
    ("結束日期：11/9 下午6:30", datetime(2026, 11, 9, 18, 30, tzinfo=TAIPEI)),
    ("#1109結團\n11/9 下午6:30截止", datetime(2026, 11, 9, 18, 30, tzinfo=TAIPEI)),
    ("#1109結團 #1110結團", None),
    ("#1109結團，結單延期", None),
    ("出貨 11/10，限量售完", None),
    ("#1105結團", None),
    ("截止：11/31", None),
])
def test_deadlines_use_the_source_text_and_do_not_guess(text, expected):
    assert deadline_from_text(text, published=POSTED) == expected


def test_inclusive_range_and_relative_date_boundary():
    assert report_dates(None, None, today=TODAY) == (date(2026, 11, 3), TODAY)
    assert report_dates("2026-11-03", "2026-11-05", today=TODAY) == (date(2026, 11, 3), date(2026, 11, 5))
    with pytest.raises(ContractError):
        report_dates("2026-11-03", None, today=TODAY)
    with pytest.raises(ContractError):
        report_dates("2026-11-06", "2026-11-10", today=TODAY)
    assert publication_date("16小時前", now=NOW) == TODAY
    assert publication_date("2025.9.29下午12:20", now=NOW) == date(2025, 9, 29)
    assert publication_date("18小時前", now=NOW) is None


def post(title, text):
    footer = Footer("11月6日上午1:27", .13, .75, .78, 2)
    return note_week.Post(title, "Mei版媽", True, POSTED, text, footer, Path("fixture.png"), 620)


def cells(archive, sheet_number):
    xml = ElementTree.fromstring(archive.read(f"xl/worksheets/sheet{sheet_number}.xml"))
    return {cell.attrib["r"]: "".join(cell.itertext()) for cell in xml.findall(".//x:c", NS)}


def test_workbook_splits_items_and_never_combines_unconfirmed_nicknames(tmp_path):
    destination = tmp_path / "report.xlsx"
    rows = [
        note_week.WeekRow(post("合成商品", "#1108結團"), NOW, "已擷取",
                          [("甲", "A+1B+2"), ("甲", "A+1（共2）"), ("測試...", "C+9"), ("測試...", "C+9")]),
        note_week.WeekRow(post("未結團", "#1110結團"), NOW, "尚未結團，未擷取", []),
    ]
    assert note_week.weekly_workbook(destination, POSTED, TODAY, rows) == {"included_series": 0, "units": 0}
    with ZipFile(destination) as archive:
        sheets = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        assert [s.attrib["name"] for s in sheets.findall(".//x:sheet", NS)] == [
            "週報總覽", "合成商品", "合成商品 A款", "合成商品 B款", "合成商品 C款",
        ]
        assert cells(archive, 1)["F3"] == "4"
        assert cells(archive, 1)["G3"] == "2"
        assert "F4" not in cells(archive, 1)
        assert cells(archive, 2)["A4"] == cells(archive, 2)["A5"] == "測試...（暱稱待核對）"
        assert "B4" not in cells(archive, 2) and "B5" not in cells(archive, 2)
        assert cells(archive, 3)["B3"] == cells(archive, 4)["B3"] == "2"
        assert cells(archive, 5)["A3"] == cells(archive, 5)["A4"] == "測試...（暱稱待核對）"
        assert "B3" not in cells(archive, 5) and "B4" not in cells(archive, 5)


def test_capture_week_opens_only_ended_posts(monkeypatch, tmp_path):
    class Clock(datetime):
        @classmethod
        def now(cls, _tz):
            return NOW

    class View:
        def resume(self):
            pass

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(note_week.sys, "platform", "darwin")
    monkeypatch.setattr(note_week, "datetime", Clock)
    monkeypatch.setattr(note_week, "run_native", lambda *args, **kwargs: None)
    monkeypatch.setattr(note_week, "fresh_view", lambda *args: View())
    monkeypatch.setattr(note_week, "inventory", lambda *args: [
        post("仍開團", "#1109結團"),
        post("時間未到", "11/9 下午6:01收單"),
        post("剛截止", "11/9 下午6:00收單"),
        post("日期不明", "售完為止"),
    ])
    monkeypatch.setattr(note_week, "prompt", lambda message: "")
    opened = []

    def locate(_view, selected):
        opened.append(selected.title)
        return selected.footer, Path("fixture.png")

    monkeypatch.setattr(note_week, "locate_post", locate)
    monkeypatch.setattr(note_week, "collect_comments", lambda *_, **_kw: [Comment("甲", "A+5 B+4"), Comment("乙", "A+7 B+5")])
    result = note_week.capture_week(None, None, "測試群", None)
    assert opened == ["剛截止"]
    assert result["posts"] == 4 and result["captured"] == 1 and result["open"] == 2
    assert result["website_import"] == {
        "included_series": 1, "completeness": "PARTIAL", "units_by_variant": {"A": 12, "B": 9},
        "units": 21, "buyer_packages": 2, "item_rows": 4,
    }
    with ZipFile(result["excel"]) as archive:
        assert cells(archive, 1)["F5"] == "21"
        assert cells(archive, 1)["D6"] == "截止日未確認，未擷取"
        packing = cells(archive, 2)
        assert [(packing[f"J{i}"], int(packing[f"G{i}"])) for i in range(5, 9)] == [
            ("A", 5), ("A", 7), ("B", 4), ("B", 5),
        ]
        assert cells(archive, 3)["B2"] == "PARTIAL"


def test_multiple_series_keep_product_codes_separate(tmp_path):
    path = tmp_path / "report.xlsx"
    summary = note_week.weekly_workbook(path, POSTED, TODAY, [
        note_week.WeekRow(post("系列一", ""), NOW, "已擷取", [("甲", "A+1 B+2")]),
        note_week.WeekRow(post("系列二", ""), NOW, "已擷取", [("甲", "A+3 B+4")]),
        note_week.WeekRow(post("系列三待核對", ""), NOW, "已擷取", [("乙...", "A+8 B+8"), ("乙", "A+1 B+1")]),
    ])
    assert summary["included_series"] == 2
    assert summary["units"] == 10
    with ZipFile(path) as archive:
        packing = cells(archive, 2)
        assert [packing[f"J{i}"] for i in range(5, 9)] == ["001-A", "001-B", "002-A", "002-B"]
        assert [packing[f"A{i}"] for i in range(5, 9)] == ["001"] * 4
        assert "J9" not in packing


def test_feed_inventory_walks_through_older_boundary_without_duplicate_posts(monkeypatch):
    def line(text, x, y):
        return {"text": text, "x": x, "y": y, "h": .018, "confidence": .9}

    frames = iter([
        {"height": 806, "lines": [line("Mei版媽", .12, .2), line("#客製化 #商品甲 #1108結團", .04, .26),
                                  line("11月8日 上午9:30", .035, .72)]},
        {"height": 806, "lines": [line("11月8日 上午9:30", .035, .348),
                                  line("Ray版媽", .12, .417), line("#商品乙 #1108結團", .04, .47),
                                  line("11月6日 上午9:30", .035, .79)]},
        {"height": 806, "lines": [line("11月6日 上午9:30", .035, .418),
                                  line("Mei版媽", .12, .48), line("#較早商品一", .04, .53),
                                  line("11月2日 上午9:30", .035, .63),
                                  line("Mei版媽", .12, .71), line("#較早商品二", .04, .76),
                                  line("11月1日 上午9:30", .035, .92)]},
    ])

    class View:
        width, top, height = 428, .09, 806

        def capture(self):
            return next(frames), Path("fixture.png")

    def advance(view, _image):
        frame, image = view.capture()
        return 300, frame, image

    monkeypatch.setattr(note_week, "scroll_feed", advance)
    posts = note_week.inventory(View(), date(2026, 11, 3), TODAY, NOW)
    assert [(row.title, row.author, row.published) for row in posts] == [
        ("商品甲", "Mei版媽", date(2026, 11, 8)),
    ]


def test_locate_post_retries_idle_scroll_without_accepting_another_card(monkeypatch):
    target = post("已結團商品", "#1108結團")
    wrong = Footer(target.footer.timestamp, .13, .75, .78, 7)
    beginning, idle, correct = map(Path, ("before.png", "idle.png", "correct.png"))
    frame = {"height": 806}
    steps = iter([(0, frame, idle), (200, frame, correct)])
    scrolls = []
    checked = []

    class View:
        def capture(self):
            return frame, beginning

        def footers(self, _frame, image):
            return [wrong if image == beginning else target.footer]

        def movement(self, reference, image):
            assert reference == target.image
            checked.append(image)
            return 0 if image == correct else None

    def scroll(_view, image):
        scrolls.append(image)
        return next(steps)

    monkeypatch.setattr(note_week, "scroll_feed", scroll)
    monkeypatch.setattr(note_week, "sleep", lambda _: None)
    assert note_week.locate_post(View(), target) == (target.footer, correct)
    assert scrolls == [beginning, idle]
    assert checked == [beginning, correct]
