from xml.etree import ElementTree
from zipfile import ZipFile

import pytest

from notesync.adapters import note_ocr
from notesync.adapters.note_ocr import Comment, choose_subject, export_capture, join_page, read_comments
from notesync.domain.models import ContractError
from notesync.exporters.note_xlsx import MAIN, comment_quantity, write_note_xlsx
from notesync.parser.note_quantity import nickname_totals


def line(text, y, x=0.12):
    return {"text": text, "x": x, "y": y / 806, "h": 12 / 806}


def test_ocr_uses_timestamp_anchors_and_keeps_multiline_bodies():
    frame = {"width": 428, "height": 806, "lines": [
        line("記事本", 46, 0.45), line("畫面裁切的留言", 65),
        line("+1", 90), line("昨天 上午 9:12", 113),
        line("買家甲", 160), line("A+1", 185), line("備註保留", 203), line("10月23日", 228),
        line("買家乙", 270), line("+2謝謝", 294), line("2026年 11月 5日 下午 9:12", 318),
        line("買家丙", 364), line("+3", 389),
    ]}
    comments = read_comments(frame)
    assert comments == [Comment("買家甲", "A+1\n備註保留"), Comment("買家乙", "+2謝謝")]
    assert [row.timestamp for row in comments] == ["10月23日", "2026年11月5日下午9:12"]


def test_ocr_subject_requires_expected_author_and_title():
    frame = {"lines": [line("測試作者", 100), line("#合成主題", 130)]}
    assert choose_subject(frame, author="測試 作者", expected_subject="#合成主題") == "#合成主題"
    with pytest.raises(ContractError, match="作者"):
        choose_subject(frame, author="另一位", expected_subject="#合成主題")
    with pytest.raises(ContractError, match="主題"):
        choose_subject(frame, author="測試作者", expected_subject="#另一篇")


def test_attachment_gap_requires_confirmation_without_treating_image_text_as_order():
    frame = {"width": 428, "height": 806, "lines": [
        line('甲', 329), line('底板一組', 350), line('2', 398, 0.148), line('10月21日 上午 10:03', 507),
        line('乙', 560), line('+1', 584), line('10月21日 上午 10:05', 607),
    ]}
    assert read_comments(frame) == [Comment('乙', '+1')]
    assert read_comments(frame, resolve_gap=lambda _row, _time: None) == [Comment('乙', '+1')]
    reviewed = []

    def confirm(row, time):
        reviewed.append((row, time))
        return Comment('甲', '底板+1')

    assert read_comments(frame, resolve_gap=confirm) == [Comment('甲', '底板+1'), Comment('乙', '+1')]
    assert reviewed == [(Comment('甲', '底板一組'), '10月21日 上午 10:03')]


def test_auto_waits_for_note_window_and_samples_without_page_prompts(tmp_path, monkeypatch):
    window_results = iter([b'{"windows":[]}', b'{"windows":[{"id":9,"width":428,"height":806}]}'])
    monkeypatch.setattr(note_ocr, "run_native", lambda _args: next(window_results))
    monkeypatch.setattr(note_ocr, "sleep", lambda _seconds: None)
    frames = iter([
        {"lines": [line("測試作者", 100), line("#合成主題", 130)]},
        {"width": 428, "height": 806, "lines": [
            line("甲", 100), line("+1", 124), line("剛剛", 147),
            line("乙", 185), line("+2", 209), line("剛剛", 232),
        ]},
        {"width": 428, "height": 806, "lines": [
            line("甲", 100), line("+1", 124), line("剛剛", 147),
            line("乙", 185), line("+2", 209), line("剛剛", 232),
            line("丙", 270), line("+3", 294), line("剛剛", 317),
        ]},
    ])
    windows_seen = []

    def capture(_native, window, _destination):
        windows_seen.append(window)
        return next(frames)

    monkeypatch.setattr(note_ocr, "capture_frame", capture)
    answers = iter(["", "3", "", ""])
    monkeypatch.setattr(note_ocr, "prompt", lambda _message: next(answers))
    subject, comments, count = note_ocr.collect_live(
        tmp_path / "probe", tmp_path, automatic=True,
        author="測試作者", expected_subject="#合成主題",
    )
    assert (subject, comments, count) == (
        "#合成主題", [Comment("甲", "+1"), Comment("乙", "+2"), Comment("丙", "+3")], 3,
    )
    assert windows_seen == [9, 9, 9]


def test_page_overlap_preserves_identical_comments_outside_the_overlap():
    first = Comment("小華", "+1")
    second = Comment("買家乙", "+2")
    third = Comment("買家丙", "+3")
    assert join_page([first, second, third], [second, third, first]) == [first, second, third, first]


def test_page_merge_rejects_missing_or_ambiguous_overlap():
    a, b = Comment("甲", "+1"), Comment("乙", "+2")
    with pytest.raises(ContractError, match="重疊"):
        join_page([a, b], [b, a])
    with pytest.raises(ContractError, match="重疊"):
        join_page([a, b, a, b], [a, b, a, b])
    with pytest.raises(ContractError, match="重疊"):
        join_page([Comment("Anna", "+1"), b], [Comment("anna", "+1"), b])


def test_conflicting_overlap_requires_original_body_review_without_double_counting():
    a, b = Comment('甲', '+1'), Comment('乙', '1+12+1')
    corrected, c = Comment('乙', '1+1、2+1'), Comment('甲', '+1')
    with pytest.raises(ContractError, match='重疊'):
        join_page([a, b], [a, corrected, c])
    reviewed = []

    def resolve(left, right):
        reviewed.append((left.body, right.body))
        return Comment(left.nickname, '1+1\n2+1')

    assert join_page([a, b], [a, corrected, c], resolve_overlap=resolve) == [
        a, Comment('乙', '1+1\n2+1'), c,
    ]
    assert reviewed == [('1+12+1', '1+1、2+1')]
    with pytest.raises(ContractError, match='重疊'):
        join_page([a, b], [Comment('甲', '+2'), corrected, c], resolve_overlap=resolve)
    assert len(reviewed) == 1


def test_overlap_reviews_nickname_typos_without_merging_separate_orders():
    first_order = Comment("買家甲", "C+1", "上午9:12")
    one = Comment("買家乙", "A+1", "上午9:13")
    two = Comment("買家丙", "C+1", "上午9:14")
    second_order = Comment("買家甲", "C+1（共2）", "上午9:15")
    misread = Comment("買家申", second_order.body, second_order.timestamp)
    last = Comment("買家丁", "C+1", "上午9:16")
    previous = [first_order, one, two, misread]
    current = [one, two, second_order, last]
    with pytest.raises(ContractError, match="對照原畫面"):
        join_page(previous, current)

    reviewed = []

    def resolve(left, right):
        reviewed.append((left, right))
        return right

    merged = join_page(previous, current, resolve_overlap=resolve)
    assert merged == [first_order, one, two, second_order, last]
    assert reviewed == [(misread, second_order)]
    assert dict(nickname_totals([(row.nickname, row.body) for row in merged]))["買家甲"] == 2


@pytest.mark.parametrize("timestamp", ["上午9:16", "昨天", ""])
def test_overlap_refuses_a_nickname_typo_without_the_same_clock(timestamp):
    one = Comment("買家甲", "C+1", "上午9:12")
    two = Comment("買家乙", "A+1", "上午9:13")
    before = Comment("買家丙", "C+1", "上午9:14")
    after = Comment("買家丁", "C+1", timestamp)
    with pytest.raises(ContractError, match="重疊"):
        join_page([one, two, before], [one, two, after, two],
                  resolve_overlap=lambda *_: pytest.fail("沒有足夠證據可以核對"))


def test_identical_text_at_distinct_clock_times_cannot_establish_overlap():
    first = Comment("買家甲", "C+1", "上午9:12")
    second = Comment("買家乙", "A+1", "上午9:13")
    with pytest.raises(ContractError, match="重疊"):
        join_page([first, second], [Comment(first.nickname, first.body, "上午9:14"), second])


def test_export_blocks_count_mismatch_without_outputs(tmp_path):
    with pytest.raises(ContractError, match="1／2"):
        export_capture(tmp_path, "合成主題", [Comment("甲", "+1")], 2)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(("body", "expected"), [
    ("+2謝謝", 2), ("Ａ＋３", 3), ("+1", 1), ("+0", None),
    ("A+1 B+2", 3), ("*1", 1), ("兩組", 2), ("十七本", 17), ("1+2", None),
    ("取消 +2", None), ("改成2", None), ("+2？", None), ("+1.5", None),
    ("+1 B+2", None), ("A+1 A+2", None), ("A+1、B+0", None), ("A+1 B+2、", None),
])
def test_quantity_only_uses_unambiguous_positive_amounts(body, expected):
    assert comment_quantity(body) == expected


def test_configured_note_codes_count_numbered_and_named_variants_and_leave_unknown_blank():
    rows = [('甲', '+1'), ('甲', '2+1'), ('乙', '1+1、2+1'), ('乙', '道具組*2'), ('丙', 'Z+4')]
    assert nickname_totals(rows, item_codes=['1', '2', '道具組']) == [('甲', 2), ('乙', 4), ('丙', None)]
    assert nickname_totals(rows[:2]) == [('甲', None)]


@pytest.mark.parametrize(("bodies", "quantity"), [
    (["C+1", "Ｃ＋１（共２）"], 2),
    (["C+1 A+2", "C+2（共3）", "A+1"], 6),
    (["C+1", "C+1（共3）"], None),
    (["A+1", "C+1（共2）"], None),
    (["C+1（共2）"], None),
    (["C+1", "C+1（共2）", "取消"], None),
    (["C+1", "C+1 A+1（共2）"], None),
])
def test_cumulative_count_checks_prior_orders_of_the_same_item(bodies, quantity):
    assert nickname_totals([("買家甲", body) for body in bodies], item_codes=["A", "C"]) == [
        ("買家甲", quantity),
    ]


def test_excel_exports_one_subject_and_two_columns(tmp_path):
    book = tmp_path / "capture.xlsx"
    write_note_xlsx(book, "#合成主題", [("007", "+2謝謝"), ("=甲", "+2"), ("007", "+2謝謝"),
                                    ("=甲", "取消 +2"), ("版媽", "結團")])
    namespace = {"x": MAIN}
    with ZipFile(book) as archive:
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        definition = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    assert definition.find(".//x:sheet", namespace).attrib["name"] == "#合成主題"
    assert sheet.find(".//x:c[@r='A1']/x:is/x:t", namespace).text == "#合成主題"
    assert sheet.find(".//x:c[@r='A2']/x:is/x:t", namespace).text == "暱稱"
    assert sheet.find(".//x:c[@r='B2']/x:is/x:t", namespace).text == "數量"
    assert sheet.find(".//x:c[@r='A3']/x:is/x:t", namespace).text == "007"
    assert sheet.find(".//x:c[@r='B3']/x:v", namespace).text == "4"
    assert sheet.find(".//x:c[@r='A4']/x:is/x:t", namespace).text == "=甲"
    assert sheet.find(".//x:c[@r='B4']", namespace) is None
    assert sheet.find(".//x:row[@r='5']", namespace) is None
    assert sheet.find(".//x:f", namespace) is None

    empty = tmp_path / "empty.xlsx"
    write_note_xlsx(empty, "空篇", [])
    with ZipFile(empty) as archive:
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    assert sheet.find(".//x:c[@r='A1']/x:is/x:t", namespace).text == "空篇"
