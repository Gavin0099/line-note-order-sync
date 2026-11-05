"""Strict whole-comment grammar. Expected values live in S00 fixtures."""

from __future__ import annotations

import re

from notesync.domain.models import ParseResult, ProductConfig, normalized

PARSER_VERSION = "strict-v1"
TOKEN = re.compile(r"(?P<sku>[A-Z][A-Z0-9_-]*)?\s*\+\s*(?P<qty>-?[0-9]+(?:\.[0-9]+)?)")
SEPARATOR = re.compile(r"[\s,、]+")
NON_ORDER_TEXT = {"謝謝", "感謝", "THANKS", "THANK YOU", "[貼圖]"}


def parse_order(text: str, config: ProductConfig) -> ParseResult:
    value = normalized(text)
    if not value:
        return ParseResult("NON_ORDER", {}, "空白留言")
    tokens = []
    cursor = 0
    while cursor < len(value):
        match = TOKEN.match(value, cursor)
        if match is None:
            break
        tokens.append(match.groupdict())
        cursor = match.end()
        if cursor == len(value):
            break
        separator = SEPARATOR.match(value, cursor)
        if separator is None:
            break
        cursor = separator.end()
        # A trailing comma is not an order token.
        if cursor == len(value):
            return ParseResult("NEEDS_REVIEW", {}, "分隔符後缺少喊單")
    if not tokens or cursor != len(value):
        if not tokens and value in NON_ORDER_TEXT:
            return ParseResult("NON_ORDER", {}, "已知的非喊單文字")
        return ParseResult("NEEDS_REVIEW", {}, "全文文法不明確，需人工核對")

    items: dict[str, int] = {}
    seen: set[str] = set()
    ambiguous = False
    invalid = False
    for token in tokens:
        sku = config.aliases.get(token["sku"]) if token["sku"] else config.default_sku
        if sku is None or sku in seen:
            ambiguous = True
            continue
        seen.add(sku)
        quantity = token["qty"]
        if "-" in quantity or "." in quantity:
            invalid = True
            continue
        digits = quantity.lstrip("0") or "0"
        if len(digits) > 6 or not 1 <= int(digits) <= config.limits[sku]:
            invalid = True
            continue
        items[sku] = int(digits)
    if ambiguous:
        return ParseResult("NEEDS_REVIEW", {}, "未知／缺預設 SKU 或同則重複商品")
    if invalid:
        return ParseResult("INVALID", {}, "數量需為設定上限內的正整數")
    return ParseResult("PARSED", items, "明確獨立喊單")
