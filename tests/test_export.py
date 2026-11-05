import csv
import json

import pytest

from notesync.domain.models import ContractError
from notesync.exporters import csv_exporter
from notesync.exporters.csv_exporter import export_report, safe_cell
from notesync.service import accept_snapshot, accepted_payload, encoded, import_snapshot, inspect_run
from notesync.storage.sqlite import Store


def payload_for(tmp_path, snapshot, config_doc):
    with Store(tmp_path / "orders.sqlite3", create=True) as store:
        run = import_snapshot(store, encoded(snapshot).encode("utf-8"), encoded(config_doc).encode("utf-8"), operator="importer")
        accept_snapshot(store, run["run_id"], operator="reviewer")
        return accepted_payload(store, run["note_id"])


def test_csv_totals_details_bom_and_visible_provenance_match_manual_answer(tmp_path, snapshot, config_doc):
    payload = payload_for(tmp_path, snapshot, config_doc)
    folder = export_report(payload, tmp_path / "exports")
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "HUMAN_DECLARED"
    assert manifest["captured_at"] == "2026-11-05T12:00:00+08:00"
    assert manifest["completeness"]["operator"] == "synthetic-operator"
    assert manifest["totals"] == {"A": 3, "B": 2}
    for filename in manifest["files"].values():
        assert "HUMAN_DECLARED_20261105T040000Z" in filename
        assert (folder / filename).read_bytes().startswith(b"\xef\xbb\xbf")
    with (folder / manifest["files"]["totals"]).open(encoding="utf-8-sig", newline="") as stream:
        assert list(csv.DictReader(stream)) == [{"sku": "A", "quantity": "3"}, {"sku": "B", "quantity": "2"}]
    with (folder / manifest["files"]["details"]).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 3
    assert rows[-1]["original_text"] == "Ａ＋２"
    assert rows[-1]["position"] == "1"
    assert rows[-1]["batch_id"] == str(payload["batch_id"])
    html = (folder / "index.html").read_text(encoding="utf-8")
    assert "HUMAN_DECLARED" in html
    assert "買家彙總" in html
    assert "Asia/Taipei" in html
    assert "2026-11-05T12:00:00+08:00" in html


@pytest.mark.parametrize("value", ['=HYPERLINK("x")', "+1", "-2", "@SUM(A1)", " \t=1+1", "\ufeff=1+1", "\ntext"])
def test_formula_prefixes_are_neutralized_without_mutating_stored_text(tmp_path, snapshot, config_doc, value):
    snapshot["comments"][0]["display_name"] = value
    payload = payload_for(tmp_path, snapshot, config_doc)
    folder = export_report(payload, tmp_path / "exports")
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    with (folder / manifest["files"]["details"]).open(encoding="utf-8-sig", newline="") as stream:
        first = next(csv.DictReader(stream))
    assert first["display_name"] == "'" + value
    assert payload["comments"][0]["display_name"] == value
    assert safe_cell(value).startswith("'")


def test_report_escapes_html_and_retains_multiline_csv_values(tmp_path, snapshot, config_doc):
    snapshot["comments"][0]["display_name"] = '<script>alert("x")</script>,\n合成測試'
    payload = payload_for(tmp_path, snapshot, config_doc)
    folder = export_report(payload, tmp_path / "exports")
    html = (folder / "index.html").read_text(encoding="utf-8")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    with (folder / manifest["files"]["details"]).open(encoding="utf-8-sig", newline="") as stream:
        assert next(csv.DictReader(stream))["display_name"] == snapshot["comments"][0]["display_name"]


def test_export_is_fixed_version_and_existing_bundle_is_never_overwritten(tmp_path, snapshot, config_doc):
    payload = payload_for(tmp_path, snapshot, config_doc)
    first = export_report(payload, tmp_path / "first")
    second = export_report(payload, tmp_path / "second")
    manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    for filename in manifest["files"].values():
        assert (first / filename).read_bytes() == (second / filename).read_bytes()
    before = (first / "index.html").read_bytes()
    with pytest.raises(ContractError):
        export_report(payload, tmp_path / "first")
    assert (first / "index.html").read_bytes() == before


def test_failed_export_leaves_no_official_or_staging_bundle(tmp_path, snapshot, config_doc, monkeypatch):
    payload = payload_for(tmp_path, snapshot, config_doc)
    original = csv_exporter._csv
    def fail_on_totals(path, fields, rows):
        if path.name.endswith("_totals.csv"):
            raise OSError("injected disk failure")
        return original(path, fields, rows)
    monkeypatch.setattr(csv_exporter, "_csv", fail_on_totals)
    with pytest.raises(OSError):
        export_report(payload, tmp_path / "exports")
    assert list((tmp_path / "exports").iterdir()) == []


def test_unknown_input_exports_visible_draft_but_cannot_be_official(tmp_path, snapshot, config_doc):
    snapshot["completeness"]["status"] = "UNKNOWN"
    snapshot["comments"][0]["text"] = "A+1？"
    with Store(tmp_path / "db", create=True) as store:
        run = import_snapshot(store, encoded(snapshot).encode("utf-8"), encoded(config_doc).encode("utf-8"), operator="importer")
        payload = inspect_run(store, run["run_id"])
        with pytest.raises(ContractError):
            export_report(payload, tmp_path / "official")
        folder = export_report(payload, tmp_path / "draft", draft=True)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "DRAFT"
    assert manifest["acceptance_id"] is None
    assert manifest["blocking_positions"] == [0]
    with (folder / manifest["files"]["review"]).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["status"] == "NEEDS_REVIEW"
    assert rows[0]["quantity"] == ""
    assert "不可作叫貨依據" in (folder / "index.html").read_text(encoding="utf-8")
