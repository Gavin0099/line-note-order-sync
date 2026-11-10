"""Publication and cutoff dates displayed by LINE, interpreted in Taipei."""

from datetime import date, datetime, time, timedelta, timezone
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from notesync.domain.models import ContractError, normalized

try:
    TAIPEI = ZoneInfo("Asia/Taipei")
except ZoneInfoNotFoundError:
    # Current LINE posts use UTC+08:00. Windows may have no IANA database.
    TAIPEI = timezone(timedelta(hours=8), "Asia/Taipei")
CLOSE = r"(?:截止收單|收單截止|結團|結單|截單|收單|截止|結束)"
DATE = (
    r"(?:20[0-9]{2}[./年-](?:0?[1-9]|1[0-2])[./月-](?:0?[1-9]|[12][0-9]|3[01])日?"
    r"|(?:0?[1-9]|1[0-2])[/月.-](?:0?[1-9]|[12][0-9]|3[01])日?"
    r"|(?:20[0-9]{2})?(?:0[1-9]|1[0-2])(?:0[1-9]|[12][0-9]|3[01]))"
)
CLOCK = r"(?:上午|下午|早上|中午|晚上|凌晨)?\s*[0-9]{1,2}(?:[:：][0-9]{2}|點(?:[0-9]{1,2}分?|半)?)"
AFTER_DATE = re.compile(rf"(?<![0-9])(?P<day>{DATE})(?![0-9])\s*(?P<clock>{CLOCK})?\s*{CLOSE}")
BEFORE_DATE = re.compile(rf"{CLOSE}(?:日期|時間|日)?\s*(?:到|至|於|為|:|：)?\s*(?P<day>{DATE})(?![0-9])\s*(?P<clock>{CLOCK})?")


def report_dates(start: str | None, end: str | None, *, today: date) -> tuple[date, date]:
    if start is None and end is None:
        return today - timedelta(days=6), today
    try:
        if not start or not end or any(not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v) for v in (start, end)):
            raise ValueError
        first, last = date.fromisoformat(start), date.fromisoformat(end)
    except ValueError as exc:
        raise ContractError("請同時提供 --from 和 --to，格式為 YYYY-MM-DD") from exc
    if not first <= last <= today:
        raise ContractError("起日須早於或等於迄日，且迄日不得晚於今天")
    return first, last


def publication_date(label: str, *, now: datetime) -> date | None:
    label = "".join(normalized(label).split())
    for prefix, days in (("今天", 0), ("昨天", 1), ("前天", 2)):
        if label.startswith(prefix):
            return now.date() - timedelta(days=days)
    if label == "剛剛":
        return now.date() if now.time() >= time(0, 1) else None
    age = re.fullmatch(r"([0-9]+)(秒|分鐘?|小?時|天)(?:之)?前", label)
    if age:
        unit = {"秒": 1, "分": 60, "分鐘": 60, "時": 3600, "小時": 3600, "天": 86400}[age[2]]
        if int(age[1]) * unit > 366 * 86400:
            return None
        days = [(now - timedelta(seconds=(int(age[1]) + i) * unit)).date() for i in (0, 1)]
        return days[0] if days[0] == days[1] else None
    if re.fullmatch(CLOCK, label):
        return now.date()
    match = re.match(r"(?:(20[0-9]{2})[./年-])?([0-9]{1,2})[./月-]([0-9]{1,2})(?=日|上午|下午|中午|晚上|$)", label)
    if not match:
        return None
    year, month, day = match.groups()
    try:
        value = date(int(year or now.year), int(month), int(day))
        if not year and value > now.date():
            value = value.replace(year=value.year - 1)
        return value if value <= now.date() else None
    except ValueError:
        return None


def cutoff(day: date, clock: time | None = None) -> datetime:
    if clock is None:
        return datetime.combine(day + timedelta(days=1), time.min, TAIPEI)
    return datetime.combine(day, clock, TAIPEI)


def deadline_from_text(text: str, *, published: date) -> datetime | None:
    text = normalized(text)
    if re.search(r"(?:改期|延後|延期|延長|提前)", text):
        return None
    matches = list(AFTER_DATE.finditer(text)) + list(BEFORE_DATE.finditer(text))
    dates: dict[date, set[time]] = {}
    for match in matches:
        raw = match["day"]
        if raw.isdecimal():
            parts = [raw[:4], raw[4:6], raw[6:]] if len(raw) == 8 else [raw[:2], raw[2:]]
        else:
            parts = re.findall(r"[0-9]+", raw)
        try:
            if len(parts) == 3:
                day = date(*map(int, parts))
            else:
                month, number = map(int, parts)
                year = published.year + int(published.month == 12 and month == 1)
                day = date(year, month, number)
            if day < published:
                return None
            times = dates.setdefault(day, set())
            if match["clock"]:
                clock = "".join(match["clock"].split())
                chunks = re.findall(r"[0-9]+", clock)
                hour = int(chunks[0])
                minute = 30 if "半" in clock else int(chunks[1]) if len(chunks) == 2 else 0
                if clock.startswith("晚上") and hour == 12:
                    return None
                if clock.startswith(("下午", "中午", "晚上")) and hour < 12:
                    hour += 12
                elif clock.startswith(("上午", "早上", "凌晨")) and hour == 12:
                    hour = 0
                times.add(time(hour, minute))
        except ValueError:
            return None
    if len(dates) != 1:
        return None
    day, times = next(iter(dates.items()))
    return cutoff(day, next(iter(times), None)) if len(times) <= 1 else None


def reviewed_cutoff(value: str, *, published: date) -> datetime:
    try:
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            day = date.fromisoformat(value)
            result = cutoff(day)
        elif re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}", value):
            result = datetime.fromisoformat(value).replace(tzinfo=TAIPEI)
            day = result.date()
        else:
            raise ValueError
        if day < published:
            raise ValueError
        return result
    except ValueError as exc:
        raise ContractError("結團時間須為 YYYY-MM-DD 或 YYYY-MM-DD HH:MM，且不得早於發文日") from exc
