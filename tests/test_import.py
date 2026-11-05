from copy import deepcopy
import json

import pytest

from notesync.adapters.manual_import import load_json, validate_snapshot
from notesync.domain.models import ContractError


@pytest.mark.parametrize("raw", [b'{"a":1,"a":2}', b'{"a":NaN}', b'{', b'\xff', b'[]', b'{"a":"\\ud800"}'])
def test_invalid_json_is_rejected(raw):
    with pytest.raises(ContractError):
        load_json(raw)


@pytest.mark.parametrize("change", ["bool_version", "bool_position", "unknown_key", "naive_time", "unknown_source", "bad_id", "bad_text", "noncontiguous"])
def test_invalid_snapshot_cannot_form_an_acceptable_batch(snapshot, change):
    doc = deepcopy(snapshot)
    if change == "bool_version":
        doc["format_version"] = True
    elif change == "bool_position":
        doc["comments"][0]["position"] = False
    elif change == "unknown_key":
        doc["trust_me"] = True
    elif change == "naive_time":
        doc["captured_at"] = "2026-11-05T12:00:00"
    elif change == "unknown_source":
        doc["source"]["kind"] = "private_api"
    elif change == "bad_id":
        doc["comments"][0]["source_author_id"] = 123
    elif change == "bad_text":
        doc["comments"][0]["text"] = None
    else:
        doc["comments"][1]["position"] = 5
    with pytest.raises(ContractError):
        validate_snapshot(json.dumps(doc).encode("utf-8"))
