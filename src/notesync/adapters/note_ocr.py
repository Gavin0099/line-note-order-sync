"""Capture a selected Mac LINE Note and prepare a reviewable transcription."""

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory, mkdtemp
from time import monotonic, sleep

from notesync.adapters.manual_import import load_json
from notesync.domain.models import MAX_NOTE_COMMENTS, ContractError, nonempty, normalized
from notesync.exporters.note_xlsx import write_note_xlsx
from notesync.parser.note_quantity import incomplete_nickname, nickname_totals, note_increment, observed_item_codes


TIMESTAMP = re.compile(
    r"(?:剛剛|[\dOBIl]+\s*(?:秒|分鐘?|小?時|小小時|天|週|月|年)\s*(?:之)?前"
    r"|(?:今天|昨天|前天)?\s*(?:上午|下午)?\s*\d{1,2}[:：]\d{2}"
    r"|(?:\d{4}年\s*)?\d{1,2}月\s*\d{1,2}日(?:\s*(?:上午|下午)?\s*\d{1,2}[:：]\d{2})?"
    r"|\d{1,4}[./-]\d{1,2}(?:[./-]\d{1,2})?(?:\s*(?:上午|下午)?\s*\d{1,2}[:：]\d{2})?)"
)


class CaptureCancelled(ContractError):
    pass


@dataclass(frozen=True)
class Comment:
    nickname: str
    body: str
    timestamp: str = field(default="", compare=False)
    confidence: float = field(default=1.0, compare=False)


def read_comments(frame: dict, *, resolve_gap: Callable[[Comment, str], Comment | None] | None = None) -> list[Comment]:
    """Read visible nickname/body groups anchored to LINE's timestamp line."""
    aspect = frame["height"] / frame["width"]
    lines = sorted(
        (line for line in frame["lines"] if .095 <= line["x"] <= .21 and .088 <= line["y"]
         and line["y"] + line["h"] <= .993),
        key=lambda line: line["y"],
    )
    comments = []
    group = []
    confidence = []
    separated = []
    last_y = -1.0
    for line in lines:
        if (line["y"] - last_y) * aspect > .078:
            if len(group) >= 2:
                separated.append(Comment(group[0], "\n".join(group[1:]), confidence=min(confidence)))
            group.clear()
            confidence.clear()
        last_y = line["y"]
        value = line["text"]
        if TIMESTAMP.fullmatch(value.strip()):
            timestamp = "".join(normalized(value).split())
            if len(group) >= 2:
                comments.append(Comment(group[0], "\n".join(group[1:]), timestamp, min(confidence)))
            elif separated and resolve_gap is not None:
                if len(separated) == 1 and (confirmed := resolve_gap(separated[0], value)) is not None:
                    comments.append(replace(confirmed, timestamp=timestamp))
            group.clear()
            confidence.clear()
            separated.clear()
        else:
            group.append(value)
            confidence.append(line.get("confidence", 1.0))
    return comments


def join_page(previous: list[Comment], current: list[Comment], *,
              resolve_overlap: Callable[[Comment, Comment], Comment] | None = None) -> list[Comment]:
    if not current:
        raise ContractError("這個畫面沒有辨識到完整的留言列")
    if not previous:
        return list(current)

    candidates = []
    for size in range(2, min(len(previous), len(current)) + 1):
        pairs = list(zip(previous[-size:], current[:size]))
        if any(":" in left.timestamp and ":" in right.timestamp and left.timestamp != right.timestamp
               for left, right in pairs):
            continue
        anchors = {left for left, right in pairs if left == right}
        if not anchors or len(set(current[:size])) < 2:
            continue
        # A clock label alone cannot identify a comment. A nickname disagreement
        # requires the same text and clock plus two distinct unchanged neighbors.
        nickname_changes = [(left, right) for left, right in pairs if left.nickname != right.nickname]
        if nickname_changes:
            if len(anchors) < 2 or any(left.body != right.body or ":" not in left.timestamp
                                       or left.timestamp != right.timestamp for left, right in nickname_changes):
                continue
        elif any(left != right for left, right in pairs) and len({row.nickname for row in current[:size]}) < 2:
            continue
        candidates.append(pairs)

    if len(candidates) != 1:
        raise ContractError("無法確認分頁重疊，請回捲並保留至少兩則辨識一致的留言")
    pairs = candidates[0]
    size = len(pairs)
    if any(left != right for left, right in pairs) and resolve_overlap is None:
        raise ContractError("分頁重疊的留言辨識不同，請對照原畫面核對")
    reviewed = []
    for left, right in pairs:
        if left == right:
            row = replace(left, confidence=max(left.confidence, right.confidence))
        else:
            row = resolve_overlap(left, right)
            row = replace(row, nickname=nonempty(row.nickname), body=nonempty(row.body), confidence=1.0)
        reviewed.append(replace(row, timestamp=right.timestamp or left.timestamp))
    return previous[:-size] + reviewed + current[size:]


def run_native(arguments: list[str], *, timeout: int = 30) -> bytes:
    try:
        result = subprocess.run(arguments, capture_output=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise ContractError("macOS 截圖或辨識逾時") from exc
    if result.returncode:
        raise ContractError("macOS 截圖或辨識失敗，請檢查螢幕錄製權限、Swift 工具與視窗狀態")
    return result.stdout


def capture_frame(native: Path, window: int, destination: Path) -> dict:
    windows = load_json(run_native([str(native), "windows"]))["windows"]
    if not any(item["id"] == window for item in windows):
        raise ContractError("選定的 LINE 視窗已關閉，請重新開啟後再執行")
    run_native(["/usr/sbin/screencapture", "-x", "-o", f"-l{window}", str(destination)])
    frame = recognize_frame(native, destination)
    def has_title(rows: list[dict]) -> bool:
        return any(text.strip() == "記事本"
                   for row in rows for text in [row["text"], *row.get("alternatives", [])])

    if not has_title([row for row in frame["lines"] if .32 < row["x"] < .68 and row["y"] < .1]):
        if not has_title(recognize_frame(native, destination, header_only=True)["lines"]):
            raise ContractError("截圖中找不到記事本視窗標籤，請確認選中的視窗與螢幕錄製權限")
    return frame


def recognize_frame(native: Path, image: Path, *, header_only: bool = False) -> dict:
    # Vision can write framework diagnostics to stdout. Read only its data file.
    with TemporaryDirectory() as temp:
        result = Path(temp) / "frame.json"
        run_native([str(native), "header" if header_only else "recognize", str(image), str(result)])
        return load_json(result.read_bytes())


def prompt(message: str) -> str:
    try:
        answer = input(message).strip()
    except (EOFError, KeyboardInterrupt) as exc:
        raise CaptureCancelled("已結束擷取") from exc
    if answer == ":q":
        raise CaptureCancelled("已取消擷取")
    return answer


def review_overlap(left: Comment, right: Comment) -> Comment:
    print(f"重疊留言辨識不同（{right.timestamp or left.timestamp}）：\n"
          f"  1. {left.nickname} {left.body!r}\n  2. {right.nickname} {right.body!r}", flush=True)
    value = prompt("請對照原畫面選 1／2，或按 Enter 手動修正（:q 取消）：")
    if value == '1':
        return left
    if value == '2':
        return right
    if value:
        raise ContractError("請輸入 1、2，或按 Enter 手動修正")
    nickname = nonempty(prompt("正確暱稱：")) if left.nickname != right.nickname else left.nickname
    body = nonempty(prompt("正確正文（\\n 換行）：").replace('\\n', '\n')) if left.body != right.body else left.body
    return Comment(nickname, body)


def attachment_reviewer() -> Callable[[Comment, str], Comment | None]:
    decisions: dict[tuple[Comment, str], Comment | None] = {}

    def review(row: Comment, time: str) -> Comment | None:
        key = (row, time)
        if key not in decisions:
            print(f"可能有附圖或空白，請對照 LINE：{row.nickname} {row.body!r}（{time}）", flush=True)
            if prompt("確認暱稱與正文屬於這個時間的同一則留言：輸入 y 核對，Enter 略過：").lower() == 'y':
                nickname = prompt(f"暱稱 [{row.nickname}]：") or row.nickname
                body = prompt(f"正文 [{row.body!r}]（輸入 \\n 表示換行）：")
                decisions[key] = Comment(nickname, body.replace('\\n', '\n') if body else row.body)
            else:
                decisions[key] = None
        return decisions[key]

    return review


def header_key(value: str) -> str:
    return "".join(value.split()).casefold()


def choose_subject(frame: dict, *, author: str | None, expected_subject: str | None) -> str:
    header = [line for line in sorted(frame["lines"], key=lambda row: (row["y"], row["x"]))
              if .083 <= line["y"] <= .56 and line["x"] < .38 and line["text"].strip()]
    if author is not None:
        authors = [line for line in header if header_key(line["text"]) == header_key(author)]
        if len(authors) != 1:
            raise ContractError("畫面須只顯示一個符合的貼文作者，請調整位置後重試")
        author_y = authors[0]["y"]
        header = [line for line in header if 0 < line["y"] - author_y < .16]
    candidates = [line["text"] for line in header[:12]]
    if expected_subject is not None:
        if not any(header_key(line) == header_key(expected_subject) for line in candidates):
            raise ContractError("辨識的貼文主題與 --subject 不符，已停止擷取")
        print(f"已核對貼文主題：{expected_subject}", flush=True)
        return expected_subject
    for index, value in enumerate(candidates, 1):
        print(f"  {index}. {value}")
    selection = prompt("輸入主題的編號，或直接輸入完整主題：")
    if selection.isascii() and selection.isdecimal() and len(selection) <= 2:
        index = int(selection)
        if 1 <= index <= len(candidates):
            return candidates[index - 1]
    return nonempty(selection)


def review_comments(rows: list[Comment]) -> list[Comment]:
    for index, row in enumerate(rows, 1):
        items, declared_total = note_increment(row.body)
        hint = '數量待核對' if items is None else (
            '非喊單' if not items else ', '.join(f'{code or "未標商品"} × {qty}' for code, qty in items.items())
        )
        if declared_total is not None:
            hint += f'，宣告累計 {declared_total}，匯出時與前文核對'
        print(f"{index:>3}  {row.nickname}  {row.body!r}  [{hint}]")
    while (value := prompt("逐筆核對後按 Enter 輸出，或輸入要修正的序號（:q 取消）：")):
        if not value.isascii() or not value.isdecimal() or len(value) > 4 or not 1 <= int(value) <= len(rows):
            print("請輸入畫面中的序號。")
            continue
        index = int(value) - 1
        row = rows[index]
        nickname = prompt(f"暱稱 [{row.nickname}]：") or row.nickname
        body = prompt(f"正文 [{row.body!r}]（輸入 \\n 表示換行）：")
        rows[index] = Comment(nickname, body.replace("\\n", "\n") if body else row.body)
    return rows


def review_uncertain(rows: list[Comment], *, item_codes: list[str] | None, split_items: bool = False) -> list[Comment]:
    pairs = [(row.nickname, row.body) for row in rows]
    quantities = dict(nickname_totals(pairs, item_codes=item_codes))
    multiple = split_items and len(observed_item_codes(pairs)) > 1
    reviewed = []
    for index, row in enumerate(rows, 1):
        if (incomplete_nickname(row.nickname) or row.confidence < .80
                or (multiple and "" in (note_increment(row.body)[0] or {}))
                or (row.nickname.strip() in quantities and quantities[row.nickname.strip()] is None)):
            print(f"第 {index} 則的辨識或數量需要核對：{row.nickname} {row.body!r}", flush=True)
            nickname = prompt(f"暱稱 [{row.nickname}]（Enter 保留）：") or row.nickname
            body = prompt(f"正文 [{row.body!r}]（Enter 保留，\\n 換行）：")
            row = replace(row, nickname=nickname, body=body.replace("\\n", "\n") if body else row.body)
        reviewed.append(row)
    return reviewed


def choose_window(native: Path, *, automatic: bool) -> int:
    if automatic:
        print("等待 LINE 記事本視窗。請開啟 LINE，再打開要擷取的貼文。", flush=True)
    while True:
        windows = load_json(run_native([str(native), "windows"]))["windows"]
        candidates = [item for item in windows if item["width"] < item["height"]]
        if candidates or (windows and not automatic):
            break
        if not automatic:
            raise ContractError("找不到 LINE 記事本視窗")
        sleep(2)
    if len(candidates) == 1:
        return candidates[0]["id"]
    print("可選的 LINE 視窗：" + "、".join(
        f'{item["id"]} ({item["width"]}×{item["height"]})' for item in windows
    ))
    selection = prompt("請輸入記事本視窗編號：")
    if selection not in {str(item["id"]) for item in windows}:
        raise ContractError("視窗編號無效")
    return int(selection)


def collect_live(native: Path, folder: Path, *, automatic: bool, author: str | None,
                 expected_subject: str | None, window: int | None = None) -> tuple[str, list[Comment], int]:
    if window is None:
        window = choose_window(native, automatic=automatic)
    else:
        print("已開啟指定群組的記事本，請選擇要擷取的貼文。", flush=True)
    prompt("請在 LINE 顯示該篇貼文的完整主題，回到這裡按 Enter（:q 取消）：")
    subject = choose_subject(capture_frame(native, window, folder / "主題.png"),
                             author=author, expected_subject=expected_subject)
    count = prompt("輸入這篇貼文在 LINE 顯示的留言總數：")
    if not count.isascii() or not count.isdecimal() or len(count) > 4 or int(count) > MAX_NOTE_COMMENTS:
        raise ContractError(f"請輸入 0 到 {MAX_NOTE_COMMENTS} 的留言數")
    expected = int(count)
    if expected == 0:
        return subject, [], 0

    prompt("展開留言並載入較早留言，讓第一則完整顯示，再按 Enter（:q 取消）：")
    rows: list[Comment] = []
    review_gap = attachment_reviewer()
    last_change = monotonic()
    index = 1
    while len(rows) < expected:
        if index > 1:
            if automatic:
                sleep(2)
                if monotonic() - last_change > 180:
                    raise ContractError("三分鐘未增加可核對的留言，請重新從第一則開始")
            else:
                prompt("向下捲動並保留至少兩則重疊，按 Enter 截圖（:q 取消）：")
        frame = capture_frame(native, window, folder / f"留言-{index:03d}.png")
        index += 1
        try:
            merged = join_page(rows, read_comments(frame, resolve_gap=review_gap), resolve_overlap=review_overlap)
        except CaptureCancelled:
            raise
        except ContractError as exc:
            print(str(exc), flush=True)
            continue
        if len(merged) > expected:
            print("辨識筆數超出原先填寫的總數，請確認未滑到另一篇貼文。", flush=True)
            continue
        if len(merged) > len(rows):
            last_change = monotonic()
            print(f"已辨識 {len(merged)}／{expected} 則。", flush=True)
            if automatic and len(merged) < expected:
                print("請在 LINE 緩慢向下捲動，保持兩則以上重疊。", flush=True)
        rows = merged
    return subject, review_comments(rows), expected


def export_capture(folder: Path, subject: str, rows: list[Comment], expected: int, *,
                   item_codes: list[str] | None = None) -> dict:
    if len(rows) != expected:
        raise ContractError(f"只辨識到 {len(rows)}／{expected} 則，請核對留言範圍")
    destination = folder / "結果"
    with TemporaryDirectory(dir=folder, prefix=".write-") as staging:
        draft = Path(staging) / "結果"
        draft.mkdir(mode=0o700)
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        lines = ["LINE 記事本留言", f"主題：{subject}", f"擷取時間：{timestamp}",
                 f"LINE 顯示 {expected} 則；本機 OCR 紀錄，請與原畫面核對。", ""]
        lines.extend(f"{index:02d}. {row.nickname}\n{row.body}\n" for index, row in enumerate(rows, 1))
        (draft / "LINE記事本留言.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        capture = json.dumps({"format_version": 1, "subject": subject, "expected_comments": expected,
                              "comments": [{"nickname": row.nickname, "body": row.body} for row in rows]},
                             ensure_ascii=False, indent=2).encode("utf-8")
        (draft / "LINE記事本留言.json").write_bytes(capture)
        write_note_xlsx(draft / "LINE記事本留言.xlsx", subject, [(row.nickname, row.body) for row in rows],
                        item_codes=item_codes)
        os.rename(draft, destination)
    return {"text": str(destination / "LINE記事本留言.txt"),
            "excel": str(destination / "LINE記事本留言.xlsx"), "comments": len(rows),
            "capture": str(destination / "LINE記事本留言.json"),
            "capture_sha256": hashlib.sha256(capture).hexdigest()}


def capture_note(*, automatic: bool, pages: list[Path] | None, author: str | None,
                 subject: str | None, count: int | None, item_codes: list[str] | None = None,
                 review_transcription: bool = False, window: int | None = None,
                 post: str | None = None) -> dict:
    if sys.platform != "darwin":
        raise ContractError("本機截圖辨識需在 macOS 執行")
    if post is not None and (window is None or pages is not None):
        raise ContractError("指定貼文自動擷取需有已核對的記事本視窗")
    if pages is not None:
        if automatic or author is not None or subject is None or count is None or not 0 <= count <= MAX_NOTE_COMMENTS:
            raise ContractError("重播截圖需提供 --subject 和 --count，並單獨使用 --pages")
        nonempty(subject)
    elif count is not None:
        raise ContractError("--count 僅供 --pages 重播截圖")
    for label in (author, subject):
        if label is not None:
            nonempty(label)

    root = Path("local-evidence")
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink():
        raise ContractError("local-evidence 必須是工作目錄下的本機資料夾")
    folder = Path(mkdtemp(dir=root.resolve(), prefix="line-note-"))
    try:
        with TemporaryDirectory() as tool_directory:
            native = Path(tool_directory) / "note-ocr"
            source = Path(__file__).with_name("macos_note_ocr.swift")
            run_native(["/usr/bin/xcrun", "swiftc", str(source), "-o", str(native)], timeout=90)
            if post is not None:
                from notesync.adapters.note_auto import collect_post
                controls = Path(tool_directory) / "note-controls"
                source = Path(__file__).with_name("macos_line_navigation.swift")
                run_native(["/usr/bin/xcrun", "swiftc", str(source), "-o", str(controls)], timeout=90)
                subject, rows, count = collect_post(
                    native, controls, folder, window, post, subject=subject, item_codes=item_codes,
                )
            elif pages is None:
                subject, rows, count = collect_live(
                    native, folder, automatic=automatic, author=author, expected_subject=subject, window=window,
                )
            else:
                rows = []
                review_gap = attachment_reviewer()
                for path in pages:
                    frame = recognize_frame(native, path.resolve())
                    rows = join_page(rows, read_comments(frame, resolve_gap=review_gap), resolve_overlap=review_overlap)
                if review_transcription and len(rows) == count:
                    rows = review_comments(rows)
            return export_capture(folder, subject, rows, count, item_codes=item_codes)
    except KeyboardInterrupt as exc:
        raise ContractError("已取消擷取") from exc
