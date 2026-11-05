import json
from pathlib import Path

import pytest

from notesync.domain.models import ContractError, ProductConfig
from notesync.parser.order_parser import parse_order

CASES = json.loads((Path(__file__).parent / "fixtures/parser_cases.json").read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_parser_matches_s00_handwritten_expected_values(case, config_doc):
    config_doc["default_sku"] = case["default_sku"]
    result = parse_order(case["text"], ProductConfig.from_document(config_doc))
    assert result.status == case["expected_status"]
    assert result.items == case["expected_items"]
    assert result.reason


@pytest.mark.parametrize("text", ["A+1B+2", "A+1,", "A+1！", "A+0 A+1", "A+1 / B+2", "我要兩個", "A1"])
def test_unapproved_text_never_partially_becomes_an_order(text, config_doc):
    result = parse_order(text, ProductConfig.from_document(config_doc))
    assert result.status == "NEEDS_REVIEW"
    assert result.items == {}


def test_very_long_quantities_do_not_overflow_or_escape_validation(config_doc):
    config = ProductConfig.from_document(config_doc)
    assert parse_order("A+" + "9" * 10000, config).status == "INVALID"
    assert parse_order("A+" + "0" * 10000 + "1", config).items == {"A": 1}


@pytest.mark.parametrize("change", ["empty", "boolean_limit", "alias_collision", "unknown_default", "duplicate_sku", "extra_key"])
def test_invalid_product_settings_are_rejected(change, config_doc):
    if change == "empty":
        config_doc["products"] = []
    elif change == "boolean_limit":
        config_doc["products"][0]["max_quantity"] = True
    elif change == "alias_collision":
        config_doc["products"][0]["aliases"] = ["B"]
    elif change == "unknown_default":
        config_doc["default_sku"] = "X"
    elif change == "duplicate_sku":
        config_doc["products"][1]["sku"] = "a"
    else:
        config_doc["ignored"] = "must not be ignored"
    with pytest.raises(ContractError):
        ProductConfig.from_document(config_doc)
