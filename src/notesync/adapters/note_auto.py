"""Navigate one visually identified LINE notebook post and collect its comments."""

from dataclasses import dataclass, replace
from pathlib import Path
import re
from time import sleep

from notesync.adapters.line_navigation import notebook_action
from notesync.adapters.manual_import import load_json
from notesync.adapters.note_ocr import (
    TIMESTAMP, Comment, attachment_reviewer, capture_frame, header_key, join_page,
    prompt, read_comments, review_overlap, review_uncertain, run_native,
)
from notesync.domain.models import MAX_NOTE_COMMENTS, ContractError


@dataclass(frozen=True)
class Footer:
    timestamp: str
    x: float
    y: float
    date_bottom: float
    count: int | None


def footer_candidates(frame: dict, *, width: float, height: float, top: float) -> list[Footer]:
    result = []
    for line in frame["lines"]:
        if (not 9 <= line["x"] * width <= 24 or line["y"] < top + 34 / height
                or not TIMESTAMP.fullmatch(line["text"].strip())):
            continue
        x = (line["x"] * width + 38) / width
        y = line["y"] - 21 / height
        numbers = [
            match for row in frame["lines"]
            if x - 10 / width <= row["x"] <= x + 24 / width
            and abs(row["y"] + row["h"] / 2 - y) <= 8 / height
            for match in re.findall(r"[0-9]{1,4}", row["text"])
        ]
        count = int(numbers[0]) if len(numbers) == 1 and 0 < int(numbers[0]) <= MAX_NOTE_COMMENTS else None
        result.append(Footer(header_key(line["text"]), x, y, line["y"] + line["h"], count))
    return result


def composer_y(frame: dict) -> float | None:
    hints = [
        row["y"] for row in frame["lines"]
        if row["x"] < .24 and row["y"] > .45
        and "寫下" in header_key(row["text"]) and header_key(row["text"]).endswith("留言")
    ]
    candidates = [
        row["y"] for row in frame["lines"]
        if row["x"] > .78 and (row["text"] == "貼文" or (
            row["text"] in {"貼", "帖文", "貼又"} and any(
                hint["x"] < .25 and "留言" in hint["text"] and abs(hint["y"] - row["y"]) < .025
                for hint in frame["lines"]
            )
        ))
    ]
    if len(candidates) == 1:
        return candidates[0]
    return hints[0] if len(hints) == 1 else None


def post_heading(frame: dict, post: str, *, top: float, height: float) -> bool:
    key = header_key(post)
    return any(any(key in header_key(text) for text in [line["text"], *line.get("alternatives", [])])
               and line["x"] < .34
               and top + 18 / height <= line["y"] <= top + 210 / height
               for line in frame["lines"])


@dataclass
class NotebookViewport:
    native: Path
    controls: Path
    folder: Path
    window: int
    width: float
    height: float
    top: float
    frame_number: int = 0

    def capture(self) -> tuple[dict, Path]:
        sleep(.25)
        self.frame_number += 1
        path = self.folder / f"記事本-{self.frame_number:03}.png"
        return capture_frame(self.native, self.window, path), path

    def scroll(self, points: int) -> None:
        notebook_action(self.controls, self.window, "scroll", ".56", ".52", str(points))

    def click(self, x: float, y: float) -> None:
        notebook_action(self.controls, self.window, "click", str(x), str(y))

    def resume(self) -> None:
        notebook_action(self.controls, self.window, "resume")

    def footers(self, frame: dict, image: Path) -> list[Footer]:
        matched = []
        for entry in footer_candidates(frame, width=self.width, height=self.height, top=self.top):
            for shift in (0, 7, 11, 15, 19, 23, 27):
                x = entry.x + shift / self.width
                result = run_native([str(self.native), "bubble", str(image), str(x), str(entry.y),
                                     str(frame["width"] / self.width)])
                if load_json(result)["visible"]:
                    matched.append(replace(entry, x=x, count=entry.count if shift == 0 else None))
                    break
        return matched

    def movement(self, previous: Path, current: Path, expected: int | None = None) -> int | None:
        arguments = [str(self.native), "motion", str(previous), str(current)]
        if expected is not None:
            arguments.append(str(expected))
        return load_json(run_native(arguments))["shift"]


def collect_post(native: Path, controls: Path, folder: Path, window: int, post: str,
                 *, subject: str | None, item_codes: list[str] | None) -> tuple[str, list[Comment], int]:
    preview = capture_frame(native, window, folder / "搜尋前.png")
    labels = [row for row in preview["lines"] if row["x"] < .22 and .08 < row["y"] < .155]
    if len(labels) != 1:
        raise ContractError("無法確認記事本搜尋欄，請保留一般記事本視窗尺寸")
    row = labels[0]
    y = str(row["y"] + row["h"] / 2)
    notebook_action(controls, window, "search-text", ".24", y, post)
    sleep(.25)
    state = notebook_action(controls, window, "state")
    if state["query"] != post:
        typed = capture_frame(native, window, folder / "搜尋文字.png")
        if not any(any(header_key(post) in header_key(text) for text in [line["text"], *line.get("alternatives", [])])
                   and .08 < line["y"] < .155
                   for line in typed["lines"]):
            raise ContractError("搜尋欄的文字與指定貼文名稱不符，已停止")
    notebook_action(controls, window, "submit-search", ".24", y)
    width, height, top = (state[name] for name in ("width", "height", "top"))
    if not (280 <= width <= 620 and 580 <= height <= 1600 and .04 < top < .26):
        raise ContractError("無法確認記事本搜尋範圍，請保留一般記事本視窗尺寸")
    view = NotebookViewport(native, controls, folder, window, width, height, top)
    capture, scroll = view.capture, view.scroll

    def footer(frame: dict, image: Path) -> Footer | None:
        matched = view.footers(frame, image)
        if len(matched) > 1:
            raise ContractError("搜尋結果有多篇貼文，請改用更完整的貼文名稱")
        return matched[0] if matched else None

    frame, image = capture()
    for _ in range(8):
        if post_heading(frame, post, top=top, height=height):
            break
        frame, image = capture()
    else:
        raise ContractError("搜尋結果的貼文正文沒有辨識到指定名稱，請檢查名稱")
    if subject is not None and not post_heading(frame, subject, top=top, height=height):
        raise ContractError("貼文與 --subject 不符")

    for _ in range(12):
        entry = footer(frame, image)
        if entry is not None:
            break
        scroll(-int(height * .52))
        frame, image = capture()
    else:
        raise ContractError("找不到已核對貼文的留言按鈕")

    # The first result must still be the last card after scrolling past its footer.
    scroll(-int(height * .42))
    sleep(.55)
    frame, image = capture()
    tail = footer(frame, image)
    if (tail is None or tail.timestamp != entry.timestamp
            or any(row["y"] > tail.date_bottom + 25 / height for row in frame["lines"])):
        raise ContractError("無法確認搜尋結果只有一篇，請使用更完整的名稱")
    expected = tail.count if tail.count is not None else entry.count
    if tail.count is not None and entry.count is not None and tail.count != entry.count:
        expected = None
    if expected is None:
        value = prompt("留言數辨識不確定，請看 LINE 後輸入總數（:q 取消）：")
        if re.fullmatch(r"[0-9]{1,4}", value) is None or int(value) > MAX_NOTE_COMMENTS:
            raise ContractError("留言數無效")
        expected = int(value)
        notebook_action(controls, window, "resume")

    rows = collect_comments(view, tail, expected, item_codes=item_codes)
    return subject or post, rows, expected


def collect_comments(view: "NotebookViewport", tail: Footer, expected: int,
                     *, item_codes: list[str] | None = None, split_items: bool = False) -> list[Comment]:
    capture, scroll, click = view.capture, view.scroll, view.click
    height, top = view.height, view.top

    def footer(frame: dict, image: Path) -> Footer | None:
        matches = [item for item in view.footers(frame, image) if item.timestamp == tail.timestamp]
        if len(matches) > 1:
            raise ContractError("同一畫面有多個相同的貼文時間，無法確認留言範圍")
        return matches[0] if matches else None

    for _ in range(2):
        click(tail.x, tail.y)
        for _ in range(5):
            frame, image = capture()
            if composer_y(frame) is not None:
                break
        if composer_y(frame) is not None:
            break
        still_closed = footer(frame, image)
        if still_closed is None or still_closed.timestamp != tail.timestamp:
            break
        tail = still_closed
    if composer_y(frame) is None:
        raise ContractError("沒有確認到留言已展開，已停止匯出")
    print(f"找到指定貼文，LINE 顯示 {expected} 則留言。", flush=True)

    for _ in range(65):
        beginning = footer(frame, image)
        if beginning is not None and beginning.timestamp == tail.timestamp:
            earlier = [row for row in frame["lines"] if header_key(row["text"]) in {
                "查看之前的留言", "查看之前留言", "查看先前的留言", "顯示較早留言", "查看更多留言",
            } and beginning.date_bottom < row["y"] < .8]
            if len(earlier) > 1:
                raise ContractError("有多個較早留言入口，無法確認所屬貼文")
            if earlier:
                row = earlier[0]
                click(row["x"] + row["w"] / 2, row["y"] + row["h"] / 2)
                frame, image = capture()
                continue
            if beginning.date_bottom < .43:
                break
            scroll(-int((beginning.date_bottom - .30) * height))
        else:
            scroll(int(height * .32))
        frame, image = capture()
    else:
        raise ContractError("找不到第一則留言，未匯出")

    rows: list[Comment] = []
    review_attachment = attachment_reviewer()
    decisions = {}

    def review_gap(row: Comment, time: str) -> Comment | None:
        result = review_attachment(row, time)
        view.resume()
        return result

    def resolve(left: Comment, right: Comment) -> Comment:
        key = (left.timestamp, right.timestamp, left, right)
        if key not in decisions:
            confirmed = review_overlap(left, right)
            view.resume()
            decisions[key] = confirmed
            decisions[left.timestamp, right.timestamp, confirmed, right] = confirmed
        return decisions[key]

    stalled = 0
    smaller_step = False
    for page in range(240):
        end = composer_y(frame)
        lower = beginning.date_bottom + 8 / height if page == 0 else top
        lines = [line for line in frame["lines"] if lower < line["y"] < (end or .993)]
        visible = read_comments({**frame, "lines": lines}, resolve_gap=review_gap)
        if visible:
            try:
                merged = join_page(rows, visible, resolve_overlap=resolve)
            except CaptureCancelled:
                raise
            except ContractError:
                if smaller_step:
                    raise
                smaller_step = True
                scroll(int(height * .10))
                frame, image = capture()
                continue
            stalled = stalled + 1 if len(merged) == len(rows) else 0
            rows = merged
        else:
            stalled += 1
        if len(rows) > expected or (end is not None and len(rows) != expected):
            raise ContractError(f"畫面留言與 LINE 顯示的總數不符（{len(rows)}／{expected}），未匯出")
        if end is not None and len(rows) == expected:
            return review_uncertain(rows, item_codes=item_codes, split_items=split_items)
        if stalled >= 4:
            break
        scroll(-int(height * (.14 if smaller_step else .22)))
        frame, image = capture()
    raise ContractError(f"無法核對完整留言（{len(rows)}／{expected}），未匯出")
