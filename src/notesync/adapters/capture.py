"""Local evidence from a LINE window or text copied by the operator."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from notesync.adapters.manual_import import load_json
from notesync.domain.models import ContractError, nonempty, require_keys


SOURCE_KINDS = ("line_group_note", "line_openchat_note")
MAX_TEXT_BYTES = 2 * 1024 * 1024


def capture_text(path: Path) -> str:
    if path == Path("-"):
        raw = sys.stdin.buffer.read(MAX_TEXT_BYTES + 1)
    else:
        with path.open("rb") as stream:
            raw = stream.read(MAX_TEXT_BYTES + 1)
    if len(raw) > MAX_TEXT_BYTES:
        raise ContractError("單次文字擷取上限為 2 MiB，請分段儲存")
    try:
        return nonempty(raw.decode("utf-8-sig"))
    except UnicodeDecodeError as exc:
        raise ContractError("請提供 UTF-8 純文字") from exc


def capture_macos(window: int | None) -> dict:
    if sys.platform != "darwin":
        raise ContractError("LINE 視窗擷取需在 macOS 執行，可用 capture-text 保存複製的文字")
    script = Path(__file__).with_name("macos_ax_probe.swift")
    arguments = ["/usr/bin/swift", str(script), "list" if window is None else str(window)]
    try:
        result = subprocess.run(arguments, capture_output=True, timeout=60, check=False)
    except subprocess.TimeoutExpired as exc:
        raise ContractError("macOS 輔助使用讀取逾時，請確認記事本視窗後重試") from exc
    if result.returncode:
        try:
            error = load_json(result.stdout).get("error")
        except ContractError:
            error = None
        messages = {
            "lineNotRunning": "找不到執行中的 Mac LINE，請開啟 LINE 並登入後再試",
            "accessibilityDenied": "請在「系統設定 → 隱私權與安全性 → 輔助使用」允許執行指令的終端機",
            "noWindows": "LINE 沒有可讀的視窗，請展開記事本並重試",
            "invalidWindow": "視窗編號已失效，請重新執行 --list-windows",
            "elementUnavailable": "LINE 視窗已更新，請重新列出視窗並重試",
            "readFailed": "無法讀取 LINE 視窗，請確認記事本仍開啟後重試",
        }
        message = messages.get(error) if isinstance(error, str) else None
        raise ContractError(message or "無法啟動 macOS 擷取程式，請確認已安裝 Xcode Command Line Tools")
    evidence = load_json(result.stdout)
    if window is None:
        require_keys(evidence, {"windows"})
        if not isinstance(evidence["windows"], list):
            raise ContractError("macOS 輔助使用視窗結果無效")
        return evidence
    require_keys(evidence, {"window", "window_title", "elements", "incomplete_read"})
    if (type(evidence["window"]) is not int or evidence["window"] != window
            or not isinstance(evidence["window_title"], str)
            or type(evidence["incomplete_read"]) is not bool
            or not isinstance(evidence["elements"], list)):
        raise ContractError("macOS 輔助使用擷取結果無效")
    if not evidence["elements"]:
        raise ContractError("找不到可讀文字，請展開記事本留言後重試或使用 capture-text")
    return evidence


def save_capture(
    *, kind: str | None, scope_key: str | None, note_key: str | None, method: str, evidence: dict,
) -> dict:
    completeness = "PARTIAL" if evidence.get("incomplete_read") else "UNKNOWN"
    record = {
        "capture_format_version": 1,
        "source": {"kind": kind, "scope_key": scope_key, "note_key": note_key},
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "completeness": completeness,
        "evidence": evidence,
    }
    output = Path("local-evidence")
    output.mkdir(mode=0o700, exist_ok=True)
    if output.is_symlink():
        raise ContractError("local-evidence 必須是工作目錄下的本機資料夾")
    with tempfile.TemporaryDirectory(dir=output, prefix="line-note-") as staging:
        staging = Path(staging)
        payload = staging / "capture.json"
        payload.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        destination = output / staging.with_suffix(".json").name
        # Publish only a complete file and never replace a prior capture.
        os.link(payload, destination)
    return {"capture": str(destination), "completeness": completeness}
