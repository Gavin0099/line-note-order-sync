import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def snapshot():
    return json.loads((ROOT / "tests/fixtures/manual_snapshot.example.json").read_text(encoding="utf-8"))


@pytest.fixture
def config_doc():
    return json.loads((ROOT / "config/products.example.json").read_text(encoding="utf-8"))
