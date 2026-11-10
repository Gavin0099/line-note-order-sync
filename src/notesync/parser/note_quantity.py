"""Interpret full LINE comments for capture previews, separate from accepted orders."""

import re
from collections import Counter
from collections.abc import Collection

from notesync.domain.models import ContractError, normalized

MAX_AMOUNT = 999_999
ITEM_CODE = r"(?:[A-Z][A-Z0-9_-]{0,31}|[0-9]{1,6})"
NAMED_CODE = r"[\u3400-\u9fff][\u3400-\u9fffA-Z0-9_-]{0,31}"
UNITS = r"(?:本|盒|個|組|套|件|份|包|支|張)"
DIGITS = "一二三四五六七八九"
NUMBER = rf"(?:[0-9]{{1,6}}|[十兩{DIGITS}]{{1,3}})"
NEXT_CODE = r"[A-Z][A-Z0-9_-]{0,31}\s*[+*×]"


def order_pattern(codes: str) -> re.Pattern:
    return re.compile(rf"(?:(?P<code>{codes})?\s*[+*×]\s*(?P<count>{NUMBER})\s*(?:{UNITS})?|(?P<units>{NUMBER})\s*{UNITS})(?=$|[\s,、;]|{NEXT_CODE})")


ORDER = order_pattern(ITEM_CODE)
SEPARATOR = re.compile(r"[\s,、;]+")
POLITE = re.compile(r"(?:\s*[,、.!~]?\s*)(?:謝謝|感謝|THANKS)[!.~]*$")
CUMULATIVE = re.compile(rf"\s*\(共\s*(?P<total>{NUMBER})\s*(?:{UNITS})?\s*\)$")
NON_ORDERS = {"結團", "結單", "截單", "收單", "謝謝", "感謝", "[貼圖]"}
CHINESE = re.compile(rf"(?:(?P<tens>[{DIGITS}])?十(?P<ones>[{DIGITS}])?|(?P<single>[兩{DIGITS}]))")


def incomplete_nickname(name: str) -> bool:
    return not name.strip() or re.search(r"(?:\.{2,}|…|⋯)\s*$", name) is not None


def observed_item_codes(comments: list[tuple[str, str]]) -> set[str]:
    return {code for _, body in comments for code in (note_increment(body)[0] or {}) if code}


def valid_code(code: str) -> bool:
    return re.fullmatch(rf'{ITEM_CODE}|{NAMED_CODE}', code) is not None


def configured_pattern(codes: Collection[str]) -> re.Pattern:
    named = [re.escape(code) for code in sorted(codes) if re.fullmatch(NAMED_CODE, code)]
    return order_pattern('|'.join([ITEM_CODE, *named]))


def amount(text: str) -> int:
    if text.isascii():
        return int(text)
    match = CHINESE.fullmatch(text)
    if not match:
        return 0
    if match['single']:
        return 2 if match['single'] == '兩' else DIGITS.index(match['single']) + 1
    return (DIGITS.index(match['tens']) + 1 if match['tens'] else 1) * 10 + (
        DIGITS.index(match['ones']) + 1 if match['ones'] else 0
    )


def note_items(body: str, *, pattern: re.Pattern = ORDER) -> dict[str, int] | None:
    """Return explicit code/count pairs; '' is the unlabelled item; None needs review."""
    value = normalized(body)
    if value.rstrip('!.~') in NON_ORDERS:
        return {}
    value = POLITE.sub('', value).rstrip()
    if not value:
        return None
    cursor = 0
    items: dict[str, int] = {}
    while cursor < len(value):
        match = pattern.match(value, cursor)
        if not match:
            return None
        code = match['code'] or ''
        quantity = amount(match['count'] or match['units'])
        if code in items or not 1 <= quantity <= MAX_AMOUNT:
            return None
        items[code] = quantity
        cursor = match.end()
        if cursor == len(value):
            return items
        separator = SEPARATOR.match(value, cursor)
        if separator:
            cursor = separator.end()
    return None


def _quantity(items: dict[str, int] | None, codes: set[str] | None) -> int | None:
    if not items or ('' in items and len(items) > 1):
        return None
    if any((code not in codes if codes is not None else code.isdecimal()) for code in items if code):
        return None
    return sum(items.values())


def comment_quantity(body: str) -> int | None:
    return _quantity(note_items(body), None)


def note_increment(body: str, *, pattern: re.Pattern = ORDER) -> tuple[dict[str, int] | None, int | None]:
    """Read an increment and an optional claimed total for one item."""
    value = POLITE.sub('', normalized(body)).rstrip()
    cumulative = CUMULATIVE.search(value)
    if cumulative is None:
        return note_items(body, pattern=pattern), None
    items = note_items(value[:cumulative.start()], pattern=pattern)
    total = amount(cumulative['total'])
    if not items or len(items) != 1 or not 1 <= total <= MAX_AMOUNT:
        return None, None
    return items, total


def nickname_totals(comments: list[tuple[str, str]], *, item_codes: list[str] | None = None) -> list[tuple[str, int | None]]:
    totals = buyer_item_totals(comments, item_codes=item_codes)
    return [(nickname, None if counts is None else counts.total()) for nickname, counts in totals.items()]


def buyer_item_totals(comments: list[tuple[str, str]], *,
                      item_codes: list[str] | None = None) -> dict[str, Counter[str] | None]:
    codes = {normalized(code) for code in item_codes} if item_codes is not None else None
    if codes is not None and (not codes or len(codes) > 1000 or not all(map(valid_code, codes))):
        raise ContractError('商品代號須為英數或中文品名（不含空格，最多 1000 個）')
    pattern = configured_pattern(codes) if codes is not None else ORDER
    totals: dict[str, Counter[str] | None] = {}
    for nickname, body in comments:
        nickname = nickname.strip()
        items, declared_total = note_increment(body, pattern=pattern)
        if items == {}:
            continue
        # A possible change/cancellation makes the whole nickname's total uncertain.
        prior = totals.setdefault(nickname, Counter())
        if prior is None:
            continue
        if not items or _quantity(items, codes) is None:
            totals[nickname] = None
            continue
        if declared_total is not None:
            (code, increment), = items.items()
            if prior[code] + increment != declared_total:
                totals[nickname] = None
                continue
        prior.update(items)
    return totals
