import json
from subprocess import CompletedProcess
from xml.etree import ElementTree
from zipfile import ZipFile

import pytest

from notesync import cli
from notesync.adapters import line_navigation, note_ocr
from notesync.domain.models import ContractError
from notesync.exporters.note_xlsx import MAIN


@pytest.mark.parametrize(("status", "payload", "message"), [
    (1, {"error": "loginRequired"}, "手機驗證"),
    (1, {"error": "chatUnavailable"}, "唯一的指定群組"),
    (1, {"error": "notebookUnavailable"}, "新記事本視窗"),
    (0, {"window": True}, "視窗識別無效"),
])
def test_navigation_requires_a_confirmed_window(monkeypatch, status, payload, message):
    calls = []

    def run(arguments, **_options):
        calls.append(arguments)
        if len(calls) == 1:
            return CompletedProcess(arguments, 0, b"", b"")
        return CompletedProcess(arguments, status, json.dumps(payload).encode(), b"")

    monkeypatch.setattr(line_navigation.sys, "platform", "darwin")
    monkeypatch.setattr(line_navigation.subprocess, "run", run)
    with pytest.raises(ContractError, match=message):
        line_navigation.open_notebook("測試 & 親子群")
    assert calls[0] == ["/usr/bin/open", "-b", "jp.naver.line.mac"]
    assert calls[1][0] == "/usr/bin/swift"
    assert calls[1][-1] == "測試 & 親子群"


def test_open_only_never_creates_evidence(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(line_navigation, "open_notebook", lambda _chat: 42)
    assert cli.main(["capture-note", "--chat", "測試群", "--open-only"]) == 0
    assert json.loads(capsys.readouterr().out) == {"notebook_window": 42}
    assert list(tmp_path.iterdir()) == []


def test_unattended_capture_stops_before_launching_line(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(line_navigation, "open_notebook", lambda _chat: pytest.fail("LINE must not launch"))
    with pytest.raises(SystemExit) as error:
        cli.main(["capture-note", "--chat", "測試群"])
    assert error.value.code == 2
    assert "終端機核對留言" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


def test_capture_uses_navigated_window_and_exports_reviewed_quantity(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(note_ocr.sys, "platform", "darwin")
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(line_navigation, "open_notebook", lambda _chat: 42)
    monkeypatch.setattr(note_ocr, "run_native", lambda _args, **_kwargs: b"")
    monkeypatch.setattr(note_ocr, "choose_window", lambda *_args, **_kwargs: pytest.fail("window changed"))
    answers = iter(["", "1", "", ""])
    monkeypatch.setattr(note_ocr, "prompt", lambda _message: next(answers))

    def frame(_native, window, destination):
        assert window == 42
        rows = [("#合成貼文", .18)] if destination.stem == "主題" else [
            ("買家甲", .25), ("+2", .28), ("剛剛", .31),
        ]
        return {"width": 428, "height": 806, "lines": [
            {"text": value, "x": .12, "y": y, "h": .014} for value, y in rows
        ]}

    monkeypatch.setattr(note_ocr, "capture_frame", frame)
    assert cli.main(["capture-note", "--chat", "測試群", "--subject", "#合成貼文"]) == 0
    output = capsys.readouterr().out
    result = json.loads(output[output.index("{"):])
    assert result["comments"] == 1
    with ZipFile(result["excel"]) as workbook:
        rows = ElementTree.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
        assert rows.find(f".//{{{MAIN}}}c[@r='B3']/{{{MAIN}}}v").text == "2"
