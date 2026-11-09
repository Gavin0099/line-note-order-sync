from hashlib import sha256
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pytest

from notesync.adapters.note_ocr import Comment, export_capture
from notesync.domain.models import ContractError
from notesync.exporters.mei_notebook import export_mei, workbook_rows
from notesync.exporters.note_xlsx import MAIN


SUBJECT = '合成親子書團'
PRODUCTS = {'subject': SUBJECT, 'default_item': 'A', 'items': {
    'A': {'title': '故事書', 'list_price': 120, 'price': 100},
    '2': {'title': '釣魚書', 'list_price': None, 'price': 150.5},
}}


def data(value):
    return json.dumps(value, ensure_ascii=False).encode('utf-8')


def capture(*rows, expected=None):
    return data({'format_version': 1, 'subject': SUBJECT, 'expected_comments': len(rows) if expected is None else expected,
                 'comments': [{'nickname': name, 'body': body} for name, body in rows]})


def review(raw, comments):
    return data({'capture_sha256': sha256(raw).hexdigest(), 'comments': comments})


def test_ocr_capture_to_website_preview_keeps_repeats_and_separates_products(tmp_path):
    saved = export_capture(tmp_path, SUBJECT, [Comment('007', '+1'), Comment('007', '+1'),
        Comment('=甲', '兩組'), Comment('007', '2+3'), Comment('版媽', '結團')], 5)
    raw = Path(saved['capture']).read_bytes()
    assert saved['capture_sha256'] == sha256(raw).hexdigest()
    assert Path(saved['text']).read_text().count('007\n+1') == 2
    products = tmp_path / 'products.json'
    products.write_bytes(data(PRODUCTS))
    output = tmp_path / 'mei.xlsx'
    with pytest.raises(ContractError, match='人工核對'):
        export_mei(Path(saved['capture']), products, None, output, confirmed=False)
    assert not output.exists()
    result = export_mei(Path(saved['capture']), products, None, output, confirmed=True)
    assert result == {'excel': str(output), 'website_preview_only': True, 'buyers': 2,
                      'items': 3, 'quantity': 7, 'amount': '851.50'}
    with ZipFile(output) as archive:
        definition = ET.fromstring(archive.read('xl/workbook.xml'))
        sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
    namespace = {'x': MAIN}
    assert definition.find('.//x:sheet', namespace).attrib['name'] == '包書明細'
    assert sheet.find(".//x:c[@r='B5']/x:is/x:t", namespace).text == '007'
    assert sheet.find(".//x:c[@r='G5']/x:v", namespace).text == '2'
    assert sheet.find(".//x:c[@r='G6']/x:v", namespace).text == '3'
    assert sheet.find(".//x:c[@r='B7']/x:is/x:t", namespace).text == '=甲'
    assert sheet.find(".//x:c[@r='J4']/x:is/x:t", namespace).text == '商品代號'
    assert sheet.find(".//x:c[@r='J6']/x:is/x:t", namespace).text == '2'
    assert sheet.find('.//x:f', namespace) is None
    before = output.read_bytes()
    with pytest.raises(FileExistsError):
        export_mei(Path(saved['capture']), products, None, output, confirmed=True)
    assert output.read_bytes() == before


def test_review_binds_sequence_and_can_split_same_name_or_replace_a_prior_order():
    raw = capture(('合成同名', '+1'), ('合成同名', '改成3'), ('合成同名', '+2'))
    decisions = {'1': {'reason': '原單已改', 'items': {}},
                 '2': {'reason': '核對改為三本', 'items': {'A': 3}, 'buyer_group': 'one'},
                 '3': {'reason': '第二個同名買家', 'items': {'A': 2}, 'buyer_group': 'two'}}
    with pytest.raises(ContractError, match='留言序號：2'):
        workbook_rows(raw, data(PRODUCTS))
    rows, totals = workbook_rows(raw, data(PRODUCTS), review(raw, decisions))
    assert [(row[0], row[1], row[6]) for row in rows[4:]] == [
        ('LINE-001', '合成同名', 3), ('LINE-002', '合成同名', 2)]
    assert totals['quantity'] == 5 and totals['amount'] == '500.00'
    with pytest.raises(ContractError, match='另一份擷取'):
        workbook_rows(raw, data(PRODUCTS), review(capture(('合成', '+1')), decisions))


def test_multi_item_comment_keeps_codes_for_same_name_and_price():
    products = {'subject': SUBJECT, 'default_item': None, 'items': {
        'A': {'title': '合成同名品項', 'list_price': None, 'price': 240},
        'B': {'title': '合成同名品項', 'list_price': None, 'price': 240},
    }}
    raw = capture(('合成買家', 'ａ＋１ b+2'), ('合成買家', 'A+2'))
    rows, totals = workbook_rows(raw, data(products))
    assert rows[3][-1] == '商品代號'
    assert [(row[0], row[6], row[-1]) for row in rows[4:]] == [('LINE-001', 3, 'A'), ('LINE-001', 2, 'B')]
    assert totals == {'buyers': 1, 'items': 2, 'quantity': 5, 'amount': '1200.00'}


@pytest.mark.parametrize(('raw', 'products', 'error'), [
    (capture(('甲', '+1'), expected=2), PRODUCTS, '總數不符'),
    (capture(('甲', 'Z+1'), ('乙', '取消'), ('丙', '+0')), PRODUCTS, '留言序號：1, 2, 3'),
    (capture(('甲', '1+1')), PRODUCTS, '留言序號：1'),
    (capture(('甲', '+1  A+1')), PRODUCTS, '留言序號：1'),
    (capture(('甲', '+1')), {**PRODUCTS, 'subject': '其他主題'}, '主題'),
    (capture(('甲', '+1')), {**PRODUCTS, 'items': {'A': {'title': '書', 'list_price': None, 'price': True}}}, '團價'),
    (capture(('甲', '結團')), PRODUCTS, '沒有可匯入'),
])
def test_website_export_rejects_partial_unknown_or_invalid_input_without_output(tmp_path, raw, products, error):
    capture_path, product_path = tmp_path / 'capture.json', tmp_path / 'products.json'
    capture_path.write_bytes(raw)
    product_path.write_bytes(data(products))
    with pytest.raises(ContractError, match=error):
        export_mei(capture_path, product_path, None, tmp_path / 'mei.xlsx', confirmed=True)
    assert {x.name for x in tmp_path.iterdir()} == {'capture.json', 'products.json'}


def test_website_package_limit_rejects_instead_of_truncating():
    rows = [(f'合成買家{i}', '+1') for i in range(101)]
    assert workbook_rows(capture(*rows[:100]), data(PRODUCTS))[1]['buyers'] == 100
    with pytest.raises(ContractError, match='100 個買家'):
        workbook_rows(capture(*rows), data(PRODUCTS))


def test_named_product_requires_exact_mapping_before_counting():
    raw = capture(('合成買家', '道具組*1\nA+2'))
    with pytest.raises(ContractError, match='留言序號：1'):
        workbook_rows(raw, data(PRODUCTS))
    products = {**PRODUCTS, 'items': {**PRODUCTS['items'], '道具組': {
        'title': '合成道具組', 'list_price': None, 'price': 180,
    }}}
    rows, totals = workbook_rows(raw, data(products))
    assert [(row[3], row[6]) for row in rows[4:]] == [('合成道具組', 1), ('故事書', 2)]
    assert totals['amount'] == '380.00'
