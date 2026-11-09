"""Read the LINE notebook feed, then collect comments from eligible cards."""

from dataclasses import dataclass, replace
from datetime import date, datetime
import os
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory, mkdtemp
from time import sleep

from notesync.adapters.line_navigation import default_chat, notebook_action, open_notebook
from notesync.adapters.note_auto import Footer, NotebookViewport, collect_comments, footer_candidates
from notesync.adapters.note_ocr import CaptureCancelled, capture_frame, header_key, prompt, run_native
from notesync.domain.models import MAX_NOTE_COMMENTS, ContractError
from notesync.exporters.note_xlsx import Worksheet, write_workbook
from notesync.parser.note_dates import TAIPEI, deadline_from_text, publication_date, report_dates, reviewed_cutoff
from notesync.parser.note_quantity import buyer_item_totals, incomplete_nickname, observed_item_codes


@dataclass(frozen=True)
class Post:
    title: str
    author: str
    possible_mei: bool
    published: date
    text: str
    footer: Footer
    image: Path
    position: float


@dataclass(frozen=True)
class WeekRow:
    post: Post
    ends: datetime | None
    status: str
    comments: list[tuple[str, str]]


def title_from_lines(lines: list[dict]) -> str:
    for line in lines[:10]:
        text = line["text"].strip()
        for tag in re.findall(r"#([^#＃\s]+)", text.replace("＃", "#")):
            if not re.search(r"結團|結單|截止|收單|^[0-9]|^限時快閃$|^客製化(?:商品)?$|^常態團$|滿千|買一送一|^CHERRY客製化",
                             tag, re.IGNORECASE):
                return tag[:120]
        if (not text.startswith(("#", "＃", "常態團")) and len(text) >= 4
                and not re.fullmatch(r"[0-9\s月團圆圓]+", text)):
            return text[:120]
    return "未辨識商品"


def identify_post(lines: list[dict], *, width: float, first: bool) -> tuple[str, bool, list[dict]]:
    """Find the author row immediately following the previous card's footer."""
    if not lines:
        return "", False, []
    baseline = lines[0]["world"]
    candidates = [
        (i, line) for i, line in enumerate(lines)
        if 36 <= line["x"] * width <= 90
        and (re.fullmatch(r"[^\s#]{1,18}版媽(?:小幫手[^\s]*)?", line["text"])
             or any(header_key(alt) == "mei版媽" for alt in line.get("alternatives", [])))
    ]
    if len(candidates) > 1 and candidates[-1][1]["world"] - candidates[0][1]["world"] > 12:
        raise ContractError("兩個貼文作者之間的發文日期讀不到，未輸出週報")
    if candidates:
        index, row = candidates[0]
        if not first and row["world"] >= baseline + 95:
            return "", False, lines
        labels = {header_key(text) for text in (row["text"], *row.get("alternatives", []))}
        if "mei版媽" in labels:
            return "Mei版媽", True, lines[index + 1:]
        return row["text"], bool(labels & {"mel版媽", "me1版媽"}), lines[index + 1:]
    # The original author can be reviewed from the saved card screenshots.
    return "", False, lines


def scroll_feed(view: NotebookViewport, image: Path) -> tuple[int, dict, Path]:
    points = int(view.height * .40)
    view.scroll(-points)
    frame, next_image = view.capture()
    expected = int(points * frame["height"] / view.height)
    moved = view.movement(image, next_image, expected)
    if moved is None:
        # Back up part of the wheel step and re-measure against the same frame.
        view.scroll(points // 2)
        frame, next_image = view.capture()
        moved = view.movement(image, next_image, expected // 2)
    if moved is None or moved < 0:
        raise ContractError("無法確認記事本捲動前後的重疊，未輸出週報。請保持視窗在前景後重跑")
    return moved, frame, next_image


def advance_feed(view: NotebookViewport, image: Path) -> tuple[int, dict, Path]:
    moved, frame, image = scroll_feed(view, image)
    if moved == 0:
        # A wheel event can briefly leave the LINE viewport unchanged mid-feed.
        sleep(.5)
        return scroll_feed(view, image)
    return moved, frame, image


def inventory(view: NotebookViewport, start: date, end: date, now: datetime) -> list[Post]:
    """Walk a single contiguous feed from its top to the older date boundary."""
    frame, image = view.capture()
    offset = 0
    boundary = -1.0
    lines: list[dict] = []
    selected: list[Post] = []
    older = 0
    last_day = None
    for _ in range(400):
        height = frame["height"]
        for row in frame["lines"]:
            y = offset + row["y"] * height
            if not .088 < row["y"] < .982 or y <= boundary + 14:
                continue
            match = next((i for i, old in enumerate(lines)
                          if abs(old["world"] - y) <= 4 and abs(old["x"] - row["x"]) * view.width <= 12), None)
            item = {**row, "world": y}
            if match is None:
                lines.append(item)
            elif item.get("confidence", 0) > lines[match].get("confidence", 0):
                lines[match] = item

        # Dates delimit the cards in the inventory. Before acting on any card,
        # locate_post also verifies the bubble and matches the recorded image.
        footers = footer_candidates(frame, width=view.width, height=view.height, top=view.top)
        for entry in sorted(footers, key=lambda item: item.y):
            position = offset + entry.date_bottom * height
            if position <= boundary + 18:
                continue
            card = sorted((row for row in lines if boundary + 14 < row["world"] < position - 30),
                          key=lambda row: (row["world"], row["x"]))
            first = boundary < 0
            boundary = position
            lines = [row for row in lines if row["world"] > boundary + 14]
            published = publication_date(entry.timestamp, now=now)
            if published is None:
                answer = prompt(f"發文日期無法確認（{entry.timestamp}，{image.name}），輸入 YYYY-MM-DD（:q 取消）：")
                try:
                    published = date.fromisoformat(answer)
                    if published > now.date():
                        raise ValueError
                except ValueError as exc:
                    raise ContractError("發文日期無效，未輸出週報") from exc
                view.resume()
            if last_day is not None and published > last_day:
                raise ContractError("記事本發文日期出現非倒序，無法確認完整範圍，未輸出週報")
            last_day = published
            older = older + 1 if published < start else 0
            if older == 2:
                return selected
            if not start <= published <= end:
                continue
            author, possible_mei, body = identify_post(card, width=view.width, first=first)
            if author and not possible_mei:
                continue
            selected.append(Post(title_from_lines(body), author, possible_mei, published,
                                 "\n".join(line["text"] for line in body), entry, image, position))
        moved, frame, image = advance_feed(view, image)
        if moved == 0:
            if any(row["world"] > boundary + 75 for row in lines):
                raise ContractError("清單底部仍有未確認發文日期的內容，未輸出週報")
            return selected
        offset += moved
    raise ContractError("已達掃描上限且尚未確認日期邊界，請縮短日期範圍")


def fresh_view(native: Path, controls: Path, folder: Path, chat: str, previous: NotebookViewport | None) -> NotebookViewport:
    if previous is None:
        window = open_notebook(chat, reuse=True)
        capture_frame(native, window, folder / "原記事本.png")
    else:
        window = previous.window
        previous.resume()
    notebook_action(controls, window, "close")
    sleep(.35)
    window = open_notebook(chat, reuse=True)
    state = notebook_action(controls, window, "state")
    if state["query"]:
        raise ContractError("新記事本仍在搜尋模式，無法確認週報範圍")
    view = NotebookViewport(native, controls, folder, window, state["width"], state["height"], .09)
    frame, _ = view.capture()
    if not any(.08 < row["y"] < .155 and row["x"] < .24 and "搜尋" in row["text"] for row in frame["lines"]):
        raise ContractError("無法確認記事本位於未搜尋的清單起點")
    return view


def locate_post(view: NotebookViewport, post: Post) -> tuple[Footer, Path]:
    frame, image = view.capture()
    offset = 0
    for _ in range(400):
        height = frame["height"]
        for entry in view.footers(frame, image):
            position = offset + entry.date_bottom * height
            if entry.timestamp != post.footer.timestamp or abs(position - post.position) > height * .4:
                continue
            motion = view.movement(post.image, image)
            predicted = (post.footer.y - entry.y) * height
            if motion is not None and abs(motion - predicted) <= 8:
                return entry, image
        if offset > post.position or (moved := advance_feed(view, image))[0] == 0:
            break
        delta, frame, image = moved
        offset += delta
    raise ContractError("貼文清單已變更或定位不確定，未展開這篇留言")


def weekly_workbook(path: Path, start: date, end: date, rows: list[WeekRow]) -> None:
    overview: list[tuple] = [
        (f"Mei 版媽｜{start} 至 {end}",),
        ("商品／貼文", "發文日期", "結團截止（台北）", "擷取狀態", "已讀留言", "確認數量", "暱稱／數量待核對"),
    ]
    sheets = []
    for entry in rows:
        unresolved = sum(incomplete_nickname(name) for name, _ in entry.comments)
        pairs = [(name, body) for name, body in entry.comments if not incomplete_nickname(name)]
        totals = buyer_item_totals(pairs)
        codes = sorted(observed_item_codes(entry.comments))
        if len(codes) > 1:
            totals = {name: counts if counts is None or "" not in counts else None for name, counts in totals.items()}
        pending = unresolved + sum(counts is None for counts in totals.values())
        quantity = sum(counts.total() for counts in totals.values() if counts is not None)
        status = entry.status if not pending else "部分待核對"
        overview.append((entry.post.title, str(entry.post.published),
                         entry.ends.strftime("%Y-%m-%d %H:%M") if entry.ends else None, status,
                         len(entry.comments) if entry.status == "已擷取" else None,
                         quantity if entry.status == "已擷取" else None, pending or None))
        if entry.status != "已擷取":
            continue
        heading = [(entry.post.title,), ("暱稱", "數量")]
        rows_by_buyer = [(name, counts.total() if counts is not None else None) for name, counts in totals.items()]
        rows_by_buyer += [(f"{name}（暱稱待核對）", None) for name, _ in entry.comments if incomplete_nickname(name)]
        sheets.append(Worksheet(entry.post.title, heading + rows_by_buyer, (44, 14), 2, True))
        if len(codes) > 1:
            for code in codes:
                suffix = f" {code}款"
                label = entry.post.title + suffix
                tab = entry.post.title[:max(0, 31 - len(suffix))] + suffix if len(suffix) < 31 else suffix.strip()
                detail = [(name, counts[code]) for name, counts in totals.items() if counts is not None and code in counts]
                detail.extend((f"{name}（暱稱待核對）", None) for name, body in entry.comments
                              if incomplete_nickname(name) and code in observed_item_codes([(name, body)]))
                sheets.append(Worksheet(tab, [(label,), ("暱稱", "數量"), *detail], (44, 14), 2, True))
    write_workbook(path, [Worksheet("週報總覽", overview, (39, 15, 23, 22, 15, 15, 22), 2), *sheets])


def capture_week(start: str | None, end: str | None, chat: str | None, output: Path | None) -> dict:
    now = datetime.now(TAIPEI)
    first, last = report_dates(start, end, today=now.date())
    if sys.platform != "darwin":
        raise ContractError("LINE 週報擷取需在 macOS 執行")
    if output is not None and (output.suffix.lower() != ".xlsx" or output.exists() or output.is_symlink()):
        raise ContractError("請指定尚未存在的 .xlsx 輸出路徑")
    root = Path("local-evidence")
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink():
        raise ContractError("local-evidence 必須是工作目錄下的本機資料夾")
    group = chat if chat is not None else default_chat()
    folder = Path(mkdtemp(dir=root.resolve(), prefix="line-week-"))
    destination = output or folder / f"LINE週報_{first}_{last}.xlsx"
    rows = []
    confirmed_aliases = set()
    with TemporaryDirectory() as tools:
        native, controls = Path(tools) / "ocr", Path(tools) / "controls"
        base = Path(__file__).parent
        for source, executable in (("macos_note_ocr.swift", native), ("macos_line_navigation.swift", controls)):
            run_native(["/usr/bin/xcrun", "swiftc", "-O", str(base / source), "-o", str(executable)], timeout=90)
        view = fresh_view(native, controls, folder, group, None)
        posts = inventory(view, first, last, now)
        print(f"日期範圍 {first} 至 {last}，辨識到 {len(posts)} 篇需核對作者或截止日的貼文。", flush=True)
        for index, post in enumerate(posts, 1):
            if post.author != "Mei版媽" and post.author not in confirmed_aliases:
                question = f"{post.title}（{post.published}，{post.image}）的作者顯示為 {post.author or '不明'}。確認是 Mei 版媽？[y／Enter 略過]："
                if prompt(question).lower() != "y":
                    rows.append(WeekRow(post, None, "作者未確認，未擷取", []))
                    continue
                if post.possible_mei and post.author:
                    confirmed_aliases.add(post.author)
            deadline = deadline_from_text(post.text, published=post.published)
            if deadline is None:
                value = prompt(f"{post.title}（{post.image}）結團日不確定。輸入 YYYY-MM-DD 或 YYYY-MM-DD HH:MM，Enter 略過：")
                if not value:
                    rows.append(WeekRow(post, None, "截止日未確認，未擷取", []))
                    continue
                deadline = reviewed_cutoff(value, published=post.published)
            if deadline > now:
                rows.append(WeekRow(post, deadline, "尚未結團，未擷取", []))
                continue
            if post.title == "未辨識商品":
                title = prompt(f"無法確認商品名稱（{post.image}），請輸入名稱，Enter 略過：")
                if not title:
                    rows.append(WeekRow(post, deadline, "商品未確認，未擷取", []))
                    continue
                post = replace(post, title=title)
            print(f"擷取已結團貼文：{post.title}", flush=True)
            capture_folder = folder / f"貼文-{index:03}"
            capture_folder.mkdir(mode=0o700)
            try:
                view = fresh_view(native, controls, capture_folder, group, view)
                footer, image = locate_post(view, post)
                expected = footer.count
                if expected is None:
                    value = prompt(f"{post.title} 的留言數看不清楚（{image}），請輸入 0 到 {MAX_NOTE_COMMENTS}：")
                    if not re.fullmatch(r"[0-9]{1,4}", value) or int(value) > MAX_NOTE_COMMENTS:
                        raise ContractError("留言數無效")
                    expected = int(value)
                    view.resume()
                captured = collect_comments(view, footer, expected, split_items=True) if expected else []
                rows.append(WeekRow(post, deadline, "已擷取", [(row.nickname, row.body) for row in captured]))
            except CaptureCancelled:
                raise
            except ContractError as exc:
                print(f"{post.title}：{exc}", flush=True)
                rows.append(WeekRow(post, deadline, "留言未核對完整", []))
                view = None
    with TemporaryDirectory(dir=destination.parent, prefix=".line-week-") as staging:
        draft = Path(staging) / "週報.xlsx"
        weekly_workbook(draft, first, last, rows)
        os.link(draft, destination)
    return {"excel": str(destination.resolve()), "from": str(first), "to": str(last),
            "posts": len(rows), "captured": sum(row.status == "已擷取" for row in rows),
            "open": sum(row.status == "尚未結團，未擷取" for row in rows)}
