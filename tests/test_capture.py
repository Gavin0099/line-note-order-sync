"""Capture artifacts preserve evidence and stay outside the order workflow."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from notesync.adapters import capture
from notesync.domain.models import ContractError


SOURCE = ["--kind", "line_group_note", "--scope-key", "group-1", "--note-key", "note-1"]
TEXT = "小美：Ａ＋１\r\n備註\r\n小美：Ａ＋１\r\n"


def run_cli(workspace, *args, stdin=None):
    return subprocess.run(
        [sys.executable, "-m", "notesync", *args],
        cwd=workspace, input=stdin, capture_output=True, check=False,
    )


@pytest.mark.parametrize("from_stdin", [False, True])
def test_capture_text_retains_multiline_chinese_and_repeated_occurrences(tmp_path, from_stdin):
    raw = TEXT.encode("utf-8-sig")
    if from_stdin:
        result = run_cli(tmp_path, "capture-text", "-", *SOURCE, stdin=raw)
    else:
        (tmp_path / "note.txt").write_bytes(raw)
        result = run_cli(tmp_path, "capture-text", "note.txt", *SOURCE)

    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)
    relative_path = Path(receipt["capture"])
    assert relative_path.parent == Path("local-evidence")
    assert relative_path.suffix == ".json"
    assert TEXT.encode("utf-8") not in result.stdout
    capture_file = tmp_path / relative_path
    assert list(capture_file.parent.iterdir()) == [capture_file]
    document = json.loads(capture_file.read_bytes())
    assert document["source"] == {
        "kind": "line_group_note", "scope_key": "group-1", "note_key": "note-1",
    }
    assert document["method"] == "manual_copy"
    assert document["completeness"] == receipt["completeness"] == "UNKNOWN"
    assert document["evidence"] == {"text": TEXT}
    assert "comments" not in document


@pytest.mark.parametrize(
    "raw", [b"  \r\n", b"\xff", b"a" * (2 * 1024 * 1024 + 1)],
    ids=["blank", "invalid-utf8", "oversize"],
)
def test_invalid_text_creates_no_evidence(tmp_path, raw):
    result = run_cli(tmp_path, "capture-text", "-", *SOURCE, stdin=raw)
    assert result.returncode == 2, result.stderr
    assert not result.stdout
    assert list(tmp_path.iterdir()) == []


def test_repeat_capture_keeps_both_observations(tmp_path):
    first = run_cli(tmp_path, "capture-text", "-", *SOURCE, stdin=b"A+1")
    assert first.returncode == 0, first.stderr
    first_file = tmp_path / json.loads(first.stdout)["capture"]
    first_bytes = first_file.read_bytes()
    second = run_cli(tmp_path, "capture-text", "-", stdin=b"A+2")
    assert second.returncode == 0, second.stderr
    second_file = tmp_path / json.loads(second.stdout)["capture"]
    assert first_file != second_file
    assert first_file.read_bytes() == first_bytes
    document = json.loads(second_file.read_bytes())
    assert document["evidence"] == {"text": "A+2"}
    assert document["source"] == {"kind": None, "scope_key": None, "note_key": None}


def test_failed_publish_leaves_no_partial_file(tmp_path, monkeypatch):
    def fail_link(*_args):
        raise OSError("simulated file system failure")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(capture.os, "link", fail_link)
    with pytest.raises(OSError, match="simulated file system failure"):
        capture.save_capture(kind="line_group_note", scope_key="g", note_key="n",
                             method="manual_copy", evidence={"text": TEXT})
    assert list((tmp_path / "local-evidence").iterdir()) == []


def test_native_capture_rejects_wrong_window_without_saving(tmp_path, monkeypatch):
    monkeypatch.setattr(capture.sys, "platform", "darwin")
    probe = b'{"window":42,"window_title":"Note","elements":[{"text":"A+1"}],"incomplete_read":false}'
    monkeypatch.setattr(
        capture.subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, probe, b""),
    )
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ContractError, match="擷取結果無效"):
        capture.capture_macos(41)
    assert list(tmp_path.iterdir()) == []


def test_bounded_probe_output_is_always_partial(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    receipt = capture.save_capture(
        kind="line_openchat_note", scope_key="g", note_key="n", method="macos_accessibility",
        evidence={"window": 42, "window_title": "Note", "elements": [{"text": "A+1"}], "incomplete_read": True},
    )
    assert receipt["completeness"] == "PARTIAL"
    assert json.loads(Path(receipt["capture"]).read_bytes())["completeness"] == "PARTIAL"


def test_native_probe_translates_accessibility_denial(monkeypatch):
    monkeypatch.setattr(capture.sys, "platform", "darwin")
    monkeypatch.setattr(
        capture.subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, b'{"error":"accessibilityDenied"}', b""),
    )
    with pytest.raises(ContractError, match="隱私權與安全性"):
        capture.capture_macos(None)


@pytest.mark.skipif(sys.platform == "darwin", reason="Tests the unsupported-platform path")
def test_native_probe_on_other_platforms_returns_clear_error(tmp_path):
    result = run_cli(tmp_path, "capture-line", "--window", "42", *SOURCE)
    assert result.returncode == 2
    assert "capture-text" in result.stderr.decode("utf-8")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.skipif(sys.platform != "darwin", reason="Requires macOS and the Swift toolchain")
def test_native_probe_rejects_unavailable_window_using_swift(tmp_path):
    toolchain = subprocess.run(["/usr/bin/xcode-select", "-p"], capture_output=True, check=False)
    if toolchain.returncode:
        pytest.skip("Xcode Command Line Tools not installed")
    result = run_cli(tmp_path, "capture-line", "--window", "2147483647", *SOURCE)
    assert result.returncode == 2
    error = result.stderr.decode("utf-8")
    assert any(message in error for message in (
        "找不到執行中的 Mac LINE", "隱私權與安全性", "LINE 沒有可讀的視窗", "視窗編號已失效", "LINE 視窗已更新",
    ))
    assert list(tmp_path.iterdir()) == []
