import pytest

from notesync import cli
from notesync.adapters import line_navigation, note_auto, note_ocr
from notesync.domain.models import ContractError


def line(text, x, y):
    return {"text": text, "x": x, "y": y, "h": .017, "w": .12}


def test_search_bar_cannot_confirm_the_post_title():
    frame = {"lines": [line("搜尋 恩米小黑盒", .06, .12), line("另一個商品", .04, .28)]}
    assert not note_auto.post_heading(frame, "恩米小黑盒", top=.15, height=806)
    frame["lines"].append(line("#恩米小黑盒 11月團", .04, .22))
    assert note_auto.post_heading(frame, "恩米小黑盒", top=.15, height=806)


def test_count_is_anchored_to_the_post_toolbar_and_not_a_comment_timestamp():
    frame = {"lines": [
        line("a8山", .109, .943),
        line("10月31日下午5:17", .035, .979),
        line("10月31日下午5:18", .121, .50),
    ]}
    footer, = note_auto.footer_candidates(frame, width=428, height=806, top=.15)
    assert footer.timestamp == "10月31日下午5:17"
    assert footer.count == 8
    frame["lines"][0] = line("a3 8山", .109, .943)
    assert note_auto.footer_candidates(frame, width=428, height=806, top=.15)[0].count is None


def test_complete_certain_comments_need_no_prompt(monkeypatch):
    monkeypatch.setattr(note_ocr, "prompt", lambda *_: pytest.fail("不應要求逐筆確認"))
    comments = [note_ocr.Comment("甲", "C+1"), note_ocr.Comment("甲", "C+1（共2）")]
    assert note_ocr.review_uncertain(comments, item_codes=["C"]) == comments


def test_only_uncertain_rows_are_reviewed(monkeypatch):
    answers = iter(["正確暱稱", ""])
    monkeypatch.setattr(note_ocr, "prompt", lambda *_: next(answers))
    comments = [note_ocr.Comment("甲", "C+1"), note_ocr.Comment("錯字", "C+1", confidence=.55)]
    assert note_ocr.review_uncertain(comments, item_codes=["C"]) == [
        comments[0], note_ocr.Comment("正確暱稱", "C+1"),
    ]


def test_post_cli_uses_local_default_group_and_passes_verified_window(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    evidence = tmp_path / "local-evidence"
    evidence.mkdir()
    (evidence / "line-chat.txt").write_text("測試社群\n", encoding="utf-8")
    opened = []

    def open_group(chat, *, reuse):
        opened.append((chat, reuse))
        return 19

    def capture(**options):
        assert options["post"] == "合成貼文"
        assert options["window"] == 19
        return {"excel": "test.xlsx"}

    monkeypatch.setattr(line_navigation, "open_notebook", open_group)
    monkeypatch.setattr(note_ocr, "capture_note", capture)
    assert cli.main(["capture-note", "--post", "合成貼文"]) == 0
    assert opened == [("測試社群", True)]
    assert "test.xlsx" in capsys.readouterr().out


def test_missing_post_title_stops_before_any_scroll_or_click(monkeypatch, tmp_path):
    actions = []

    def action(_controls, _window, verb, *_args):
        actions.append(verb)
        return {"width": 428, "height": 806, "top": .15, "query": "合成貼文"}

    frame = {"lines": [line("合成貼文", .08, .12), line("另一篇", .08, .25)]}
    monkeypatch.setattr(note_auto, "notebook_action", action)
    monkeypatch.setattr(note_auto, "capture_frame", lambda *_: frame)
    monkeypatch.setattr(note_auto, "sleep", lambda *_: None)
    with pytest.raises(ContractError, match="貼文正文"):
        note_auto.collect_post(tmp_path, tmp_path, tmp_path, 19, "合成貼文", subject=None, item_codes=None)
    assert actions == ["search-text", "state", "submit-search"]
