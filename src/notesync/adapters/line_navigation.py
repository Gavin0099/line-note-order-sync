"""Open a named chat's notebook using the local LINE app."""

from pathlib import Path
import subprocess
import sys

from notesync.adapters.manual_import import load_json
from notesync.domain.models import ContractError, nonempty, require_keys


def open_notebook(chat: str, *, reuse: bool = False) -> int:
    chat = nonempty(chat).strip()
    if chat.splitlines() != [chat] or any(ord(character) < 32 for character in chat):
        raise ContractError("群組名稱須為單行文字")
    if sys.platform != "darwin":
        raise ContractError("自動開啟 LINE 記事本需在 macOS 執行")

    try:
        launch = subprocess.run(
            ["/usr/bin/open", "-b", "jp.naver.line.mac"], capture_output=True, timeout=10,
        )
        if launch.returncode:
            raise ContractError("無法開啟 Mac LINE，請確認已安裝 LINE")
        print("已啟動 LINE，正在確認登入狀態及尋找指定群組。", file=sys.stderr, flush=True)
        source = Path(__file__).with_name("macos_line_navigation.swift")
        arguments = ["/usr/bin/swift", str(source), chat]
        if reuse:
            arguments.append("--reuse")
        result = subprocess.run(arguments, capture_output=True, timeout=90)
    except subprocess.TimeoutExpired as exc:
        raise ContractError("LINE 導覽逾時，請解鎖 Mac 並確認 LINE 畫面後重試") from exc

    try:
        response = load_json(result.stdout)
    except ContractError as exc:
        raise ContractError("無法啟動 LINE 導覽工具，請確認已安裝 Xcode Command Line Tools") from exc
    if result.returncode:
        messages = {
            "accessibilityDenied": "請在 macOS 輔助使用設定中允許執行指令的終端機",
            "loginRequired": "LINE 正等待登入，請在 LINE 完成登入或手機驗證，再執行指令",
            "mainUnavailable": "找不到已登入的 LINE 主視窗，請解鎖 Mac 並確認 LINE 已登入",
            "chatUnavailable": "無法確認唯一的指定群組，請核對完整群組名稱及 LINE 搜尋結果",
            "notebookUnavailable": "無法確認指定群組的新記事本視窗，請關閉已開啟的記事本後重試",
        }
        error = response.get("error")
        message = messages.get(error) if isinstance(error, str) else None
        raise ContractError(message or "LINE 導覽失敗，請確認 LINE 仍在前景並重試")
    require_keys(response, {"window"})
    window = response["window"]
    if type(window) is not int or window <= 0:
        raise ContractError("LINE 記事本視窗識別無效")
    return window


def notebook_action(native: Path, window: int, verb: str, *arguments: str) -> dict:
    try:
        result = subprocess.run(
            [str(native), "--notebook-action", str(window), verb, *arguments],
            capture_output=True, timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        raise ContractError("LINE 記事本沒有回應，請確認視窗在前景") from exc
    response = load_json(result.stdout)
    if result.returncode:
        messages = {
            "notebookNotFocused": "LINE 記事本不在前景或被遮住，請移開其他視窗再重跑",
            "notebookSearchFailed": "無法確認 LINE 記事本搜尋欄，已停止",
        }
        raise ContractError(messages.get(response.get("error"), "LINE 記事本視窗已變更，已停止"))
    return response


def default_chat() -> str:
    path = Path("local-evidence/line-chat.txt")
    if path.is_file() and not path.is_symlink():
        return nonempty(path.read_text(encoding="utf-8")).strip()
    raise ContractError("請指定 --chat 或在 local-evidence/line-chat.txt 填入預設群組的完整名稱")
