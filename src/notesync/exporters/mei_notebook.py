"""Build the workbook consumed by Mei's existing, browser-only notebook preview."""

from collections import Counter
from decimal import Decimal
from hashlib import sha256
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from notesync.adapters.manual_import import load_json
from notesync.domain.models import MAX_NOTE_COMMENTS, ContractError, nonempty, require_keys
from notesync.exporters.note_xlsx import write_worksheet
from notesync.parser.note_quantity import MAX_AMOUNT, configured_pattern, note_items, valid_code


HEADERS = ('包裹編號', '媽媽', '開團／訂單', '商品', '定價', '團價', '數量', '金額', '包書確認', '商品代號')
MAX_BUYERS, MAX_ITEMS = 100, 1000
MAX_PRICE = Decimal('99999999.99')


def limited_text(value: object, limit: int) -> str:
    value = nonempty(value).strip()
    if len(value.encode('utf-16-le')) // 2 > limit or '\x00' in value:
        raise ContractError(f'文字欄位超出 {limit} 字或含無效字元')
    return value


def price(value: object) -> Decimal:
    if type(value) not in (int, float):
        raise ContractError('定價和團價須為數值；只有定價可留空')
    number = Decimal(str(value))
    if not number.is_finite() or not 0 <= number <= MAX_PRICE or number != round(number, 2):
        raise ContractError('價格須為 0–99999999.99，最多兩位小數')
    return number


def products_for(config: dict, subject: str) -> tuple[dict, str | None]:
    require_keys(config, {'subject', 'default_item', 'items'})
    if config['subject'] != subject:
        raise ContractError('商品設定的主題與擷取檔不符')
    if not isinstance(config['items'], dict) or not 1 <= len(config['items']) <= MAX_ITEMS:
        raise ContractError('商品設定須有 1–1000 個品項')
    products = {}
    for code, product in config['items'].items():
        if not valid_code(code):
            raise ContractError('商品代號須為英數或中文品名（英文字母大寫，不含空格）')
        require_keys(product, {'title', 'list_price', 'price'})
        products[code] = (limited_text(product['title'], 240),
                          None if product['list_price'] is None else price(product['list_price']),
                          price(product['price']))
    default = config['default_item']
    if default is not None and (not isinstance(default, str) or default not in products):
        raise ContractError('預設商品須為已設定的商品代號或 null')
    return products, default


def resolve_overrides(review_raw: bytes | None, capture_raw: bytes, expected: int) -> dict:
    if review_raw is None:
        return {}
    review = load_json(review_raw)
    require_keys(review, {'capture_sha256', 'comments'})
    if review['capture_sha256'] != sha256(capture_raw).hexdigest():
        raise ContractError('人工核對檔對應另一份擷取，請重新核對留言序號')
    overrides = review['comments']
    if not isinstance(overrides, dict) or any(not re.fullmatch(r'[1-9][0-9]{0,3}', pos)
                                              or int(pos) > expected for pos in overrides):
        raise ContractError('核對檔留言序號超出擷取範圍')
    for decision in overrides.values():
        if not isinstance(decision, dict) or not {'reason', 'items'} <= set(decision) <= {
                'reason', 'items', 'buyer_group', 'buyer_name'}:
            raise ContractError('核對決定須有 reason、items，可另填 buyer_group 或 buyer_name')
        nonempty(decision['reason'])
        if not isinstance(decision['items'], dict):
            raise ContractError('核對品項須為物件；空物件代表排除該則')
        for field in ('buyer_group', 'buyer_name'):
            if field in decision:
                limited_text(decision[field], 120)
    return overrides


def workbook_rows(capture_raw: bytes, config_raw: bytes, review_raw: bytes | None = None) -> tuple[list[tuple], dict]:
    capture = load_json(capture_raw)
    require_keys(capture, {'format_version', 'subject', 'expected_comments', 'comments'})
    if type(capture['format_version']) is not int or capture['format_version'] != 1:
        raise ContractError('不支援的 LINE 擷取格式')
    subject = limited_text(capture['subject'], 500)
    expected, comments = capture['expected_comments'], capture['comments']
    if (type(expected) is not int or not 0 <= expected <= MAX_NOTE_COMMENTS
            or not isinstance(comments, list) or len(comments) != expected):
        raise ContractError('留言筆數與 LINE 顯示的總數不符')
    products, default = products_for(load_json(config_raw), subject)
    overrides = resolve_overrides(review_raw, capture_raw, expected)
    pattern = configured_pattern(products)

    buyers: dict[tuple[str, str], tuple[str, Counter]] = {}
    pending = []
    for index, row in enumerate(comments, 1):
        require_keys(row, {'nickname', 'body'})
        if not isinstance(row['nickname'], str) or not isinstance(row['body'], str):
            raise ContractError(f'第 {index} 則留言欄位無效')
        decision = overrides.get(str(index), {})
        items = decision['items'] if decision else note_items(row['body'], pattern=pattern)
        if items == {}:
            continue
        if items is None:
            pending.append(index)
            continue
        resolved = {}
        for code, qty in items.items():
            sku = code if code or decision else default
            if sku not in products or sku in resolved or type(qty) is not int or not 1 <= qty <= MAX_AMOUNT:
                pending.append(index)
                break
            resolved[sku] = qty
        else:
            name = limited_text(decision.get('buyer_name', row['nickname']), 120)
            key = ('manual', decision['buyer_group'].strip()) if 'buyer_group' in decision else ('nickname', name)
            old_name, counts = buyers.setdefault(key, (name, Counter()))
            if old_name != name:
                raise ContractError(f'第 {index} 則的買家分組名稱不一致')
            counts.update(resolved)
    if pending:
        raise ContractError('有未對應商品或待核對數量，請檢查留言序號：' + ', '.join(map(str, pending)))
    if not buyers:
        raise ContractError('沒有可匯入網站的記事本品項')
    if len(buyers) > MAX_BUYERS or sum(len(counts) for _, counts in buyers.values()) > MAX_ITEMS:
        raise ContractError('超出網站每份 100 個買家區塊／1000 筆品項的上限，請分開核對')
    rows = [(subject,), (), (), HEADERS]
    total_quantity = 0
    total_amount = Decimal(0)
    for index, (buyer, counts) in enumerate(buyers.values(), 1):
        for sku, qty in counts.items():
            title, list_price, unit_price = products[sku]
            total_quantity += qty
            total_amount += unit_price * qty
            # Mei recomputes money from price and quantity. Leave the optional amount cell blank.
            rows.append((f'LINE-{index:03d}', buyer, '記事本', title, list_price, unit_price, qty, None, '□', sku))
    if total_amount * 100 > 2**53 - 1:
        raise ContractError('金額超出可安全計算範圍')
    return rows, {'buyers': len(buyers), 'items': len(rows) - 4, 'quantity': total_quantity,
                  'amount': format(total_amount, '.2f')}


def export_mei(capture: Path, products: Path, review: Path | None, output: Path, *, confirmed: bool) -> dict:
    if not confirmed:
        raise ContractError('先人工核對 LINE 原文、數量及同名買家，再加上 --confirm-reviewed')
    if output.suffix.lower() != '.xlsx':
        raise ContractError('網站匯入檔名須以 .xlsx 結尾')
    rows, totals = workbook_rows(capture.read_bytes(), products.read_bytes(), review.read_bytes() if review else None)
    with TemporaryDirectory(dir=output.parent, prefix='.mei-export-') as temp:
        staged = Path(temp) / 'preview.xlsx'
        write_worksheet(staged, '包書明細', rows, widths=(14, 22, 16, 42, 12, 12, 12, 12, 14, 16), header_row=4)
        staged.chmod(0o600)
        os.link(staged, output)  # Atomic, and never overwrites an earlier export.
    return {'excel': str(output.resolve()), 'website_preview_only': True, **totals}
