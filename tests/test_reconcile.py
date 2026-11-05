from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from notesync.domain.models import ContractError
from notesync.service import accept_snapshot, accepted_payload, encoded, import_snapshot, inspect_run, review_comment, totals
from notesync.storage.sqlite import Store


def importing(store, doc, config_doc, **kwargs):
    return import_snapshot(store, encoded(doc).encode("utf-8"), encoded(config_doc).encode("utf-8"), operator="test-operator", **kwargs)


def test_restart_repeat_import_and_accept_preserve_one_version(tmp_path, snapshot, config_doc):
    path = tmp_path / "orders.sqlite3"
    raw = encoded(snapshot).encode("utf-8")
    with Store(path, create=True) as store:
        first = importing(store, snapshot, config_doc)
        accepted = accept_snapshot(store, first["run_id"], operator="reviewer")
        for _ in range(3):
            repeat = importing(store, snapshot, config_doc)
            assert repeat["reused"] is True
            assert repeat["run_id"] == first["run_id"]
            assert accept_snapshot(store, repeat["run_id"], operator="reviewer") == accepted
    with Store(path) as store:
        payload = accepted_payload(store, first["note_id"])
        assert totals(payload) == {"A": 3, "B": 2}
        assert store.conn.execute("SELECT COUNT(*) FROM acceptances").fetchone()[0] == 1
        assert store.conn.execute("SELECT raw FROM batches").fetchone()[0] == raw
        assert payload["raw_sha256"] == hashlib.sha256(raw).hexdigest()
        assert payload["comments"][1]["text"] == "Ａ＋２"
        assert payload["comments"][1]["source_comment_id"] is None


def test_new_snapshot_replaces_without_adding_and_old_file_does_not_auto_select(tmp_path, snapshot, config_doc):
    snapshot["comments"] = [{**snapshot["comments"][0], "text": "A+2"}]
    with Store(tmp_path / "db", create=True) as store:
        first = importing(store, snapshot, config_doc)
        old = accept_snapshot(store, first["run_id"], operator="reviewer")
        newer = deepcopy(snapshot)
        newer["captured_at"] = "2026-11-05T14:00:00+08:00"
        newer["comments"][0]["text"] = "A+3"
        run = importing(store, newer, config_doc)
        assert totals(accepted_payload(store, first["note_id"])) == {"A": 2}
        latest = accept_snapshot(store, run["run_id"], operator="reviewer")
        assert latest["acceptance_id"] != old["acceptance_id"]
        assert totals(accepted_payload(store, first["note_id"])) == {"A": 3}
        importing(store, snapshot, config_doc)
        assert accepted_payload(store, first["note_id"])["acceptance_id"] == latest["acceptance_id"]
        historical = json.loads(store.conn.execute("SELECT payload FROM acceptances WHERE id=?", (old["acceptance_id"],)).fetchone()[0])
        assert totals(historical) == {"A": 2}


@pytest.mark.parametrize("status", ["PARTIAL", "UNKNOWN", "VERIFIED_COMPLETE"])
def test_manual_adapter_cannot_accept_partial_unknown_or_self_claimed_verified(tmp_path, snapshot, config_doc, status):
    with Store(tmp_path / "db", create=True) as store:
        first = importing(store, snapshot, config_doc)
        accepted = accept_snapshot(store, first["run_id"], operator="reviewer")
        newer = deepcopy(snapshot)
        newer["completeness"]["status"] = status
        newer["comments"] = newer["comments"][:1]
        run = importing(store, newer, config_doc)
        with pytest.raises(ContractError):
            accept_snapshot(store, run["run_id"], operator="reviewer")
        assert accepted_payload(store, first["note_id"])["acceptance_id"] == accepted["acceptance_id"]


@pytest.mark.parametrize("missing", ["operator", "declared_at", "evidence_refs"])
def test_missing_human_declaration_evidence_blocks_acceptance(tmp_path, snapshot, config_doc, missing):
    snapshot["completeness"][missing] = [] if missing == "evidence_refs" else None
    with Store(tmp_path / "db", create=True) as store:
        run = importing(store, snapshot, config_doc)
        with pytest.raises(ContractError):
            accept_snapshot(store, run["run_id"], operator="reviewer")
        assert store.conn.execute("SELECT COUNT(*) FROM acceptances").fetchone()[0] == 0


def test_50_no_id_occurrences_need_one_overlap_confirmation_not_50_buyer_mappings(tmp_path, config_doc):
    doc = json.loads((Path(__file__).parent / "fixtures/no_id_50.json").read_text(encoding="utf-8"))
    with Store(tmp_path / "db", create=True) as store:
        uncertain = importing(store, doc, config_doc)
        assert len(inspect_run(store, uncertain["run_id"])["blocking"]) == 50
        confirmed = importing(store, doc, config_doc, independent_occurrences=True)
        assert confirmed["batch_id"] == uncertain["batch_id"]
        assert confirmed["run_id"] != uncertain["run_id"]
        accept_snapshot(store, confirmed["run_id"], operator="reviewer")
        payload = accepted_payload(store, confirmed["note_id"])
        assert len(payload["comments"]) == 50
        assert len({r["buyer_key"] for r in payload["comments"]}) == 1
        assert totals(payload) == {"A": 50}
        assert payload["reviews"] == []


def test_review_freezes_accepted_version_and_does_not_carry_to_new_config(tmp_path, snapshot, config_doc):
    snapshot["comments"][1]["text"] = "A+1？"
    with Store(tmp_path / "db", create=True) as store:
        run = importing(store, snapshot, config_doc)
        with pytest.raises(ContractError):
            accept_snapshot(store, run["run_id"], operator="reviewer")
        review_comment(store, run["run_id"], 1, operator="reviewer", reason="confirmed non-order")
        accept_snapshot(store, run["run_id"], operator="reviewer")
        old = accepted_payload(store, run["note_id"])
        assert totals(old) == {"A": 1, "B": 2}
        review_comment(store, run["run_id"], 1, operator="reviewer", reason="buyer confirmed four", items={"A": 4})
        assert totals(accepted_payload(store, run["note_id"])) == {"A": 1, "B": 2}
        new = accept_snapshot(store, run["run_id"], operator="reviewer")
        assert new["acceptance_id"] != old["acceptance_id"]
        assert totals(accepted_payload(store, run["note_id"])) == {"A": 5, "B": 2}
        assert inspect_run(store, run["run_id"])["comments"][1]["text"] == "A+1？"
        config_doc["products"][0]["max_quantity"] = 98
        reparse = importing(store, snapshot, config_doc)
        assert reparse["batch_id"] == run["batch_id"]
        assert inspect_run(store, reparse["run_id"])["reviews"] == []
        assert inspect_run(store, reparse["run_id"])["blocking"] == [1]


def test_same_name_split_rename_merge_and_scopes_remain_auditable(tmp_path, snapshot, config_doc):
    snapshot["comments"][0]["text"] = "A+1"
    snapshot["comments"][1].update(display_name=snapshot["comments"][0]["display_name"], text="A+2")
    with Store(tmp_path / "db", create=True) as store:
        run = importing(store, snapshot, config_doc)
        accept_snapshot(store, run["run_id"], operator="reviewer")
        original = accepted_payload(store, run["note_id"])
        assert len({r["buyer_key"] for r in original["comments"]}) == 1
        review_comment(store, run["run_id"], 1, items={"A": 2}, buyer_label="confirmed-other-buyer", operator="reviewer", reason="split same-name buyers")
        accept_snapshot(store, run["run_id"], operator="reviewer")
        split = accepted_payload(store, run["note_id"])
        assert len({r["buyer_key"] for r in split["comments"]}) == 2
        review_comment(store, run["run_id"], 1, items={"A": 2}, buyer_label=original["comments"][0]["buyer_label"], operator="reviewer", reason="merge confirmed rename")
        accept_snapshot(store, run["run_id"], operator="reviewer")
        assert len({r["buyer_key"] for r in accepted_payload(store, run["note_id"])["comments"]}) == 1
        snapshot["source"]["scope_key"] = config_doc["scope_key"] = "another-community"
        other = importing(store, snapshot, config_doc)
        accept_snapshot(store, other["run_id"], operator="reviewer")
        assert other["note_id"] != run["note_id"]
        assert accepted_payload(store, other["note_id"])["comments"][0]["buyer_key"] != original["comments"][0]["buyer_key"]


@pytest.mark.parametrize("defect", ["missing_name", "source_id_collision"])
def test_identity_or_source_ambiguity_is_blocking(tmp_path, snapshot, config_doc, defect):
    if defect == "missing_name":
        snapshot["comments"][0]["display_name"] = " "
    else:
        for row in snapshot["comments"]:
            row["source_comment_id"] = "same-source-comment"
    with Store(tmp_path / "db", create=True) as store:
        run = importing(store, snapshot, config_doc, independent_occurrences=True)
        with pytest.raises(ContractError):
            accept_snapshot(store, run["run_id"], operator="reviewer")


def test_failed_import_rolls_back_every_new_row_and_keeps_current(tmp_path, snapshot, config_doc):
    with Store(tmp_path / "db", create=True) as store:
        run = importing(store, snapshot, config_doc)
        accepted = accept_snapshot(store, run["run_id"], operator="reviewer")
        store.conn.execute("CREATE TRIGGER fail_result BEFORE INSERT ON results WHEN NEW.position=1 BEGIN SELECT RAISE(ABORT,'injected'); END")
        snapshot["comments"][0]["text"] = "A+8"
        with pytest.raises(sqlite3.IntegrityError):
            importing(store, snapshot, config_doc)
        assert store.conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0] == 1
        assert store.conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 1
        assert accepted_payload(store, run["note_id"])["acceptance_id"] == accepted["acceptance_id"]


def test_failed_accept_rolls_back_new_projection_and_acceptance(tmp_path, snapshot, config_doc):
    with Store(tmp_path / "db", create=True) as store:
        run = importing(store, snapshot, config_doc)
        first = accept_snapshot(store, run["run_id"], operator="reviewer")
        review_comment(store, run["run_id"], 0, items={"A": 8}, operator="reviewer", reason="new decision")
        store.conn.execute("CREATE TRIGGER fail_current BEFORE INSERT ON current_acceptances BEGIN SELECT RAISE(ABORT,'injected'); END")
        with pytest.raises(sqlite3.IntegrityError):
            accept_snapshot(store, run["run_id"], operator="reviewer")
        assert store.conn.execute("SELECT COUNT(*) FROM acceptances").fetchone()[0] == 1
        assert accepted_payload(store, run["note_id"])["acceptance_id"] == first["acceptance_id"]
        assert totals(accepted_payload(store, run["note_id"])) == {"A": 3, "B": 2}


def test_rejected_input_is_traceable_without_an_acceptable_batch(tmp_path, config_doc):
    with Store(tmp_path / "db", create=True) as store:
        raw = b'{"invalid":true}'
        with pytest.raises(ContractError):
            import_snapshot(store, raw, encoded(config_doc).encode(), operator="reviewer")
        rejected = store.conn.execute("SELECT raw FROM rejected_inputs").fetchone()[0]
        assert rejected == raw
        assert store.conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0] == 0


@pytest.mark.parametrize("items", [{"A": True}, {"A": 0}, {"A": 100}, {"A": 1.5}, {"X": 1}, {}])
def test_invalid_review_does_not_append_a_decision(tmp_path, snapshot, config_doc, items):
    with Store(tmp_path / "db", create=True) as store:
        run = importing(store, snapshot, config_doc)
        with pytest.raises(ContractError):
            review_comment(store, run["run_id"], 0, items=items, operator="reviewer", reason="bad input")
        assert inspect_run(store, run["run_id"])["reviews"] == []


def test_empty_declared_snapshot_can_be_explicitly_accepted(tmp_path, snapshot, config_doc):
    snapshot["comments"] = []
    with Store(tmp_path / "db", create=True) as store:
        run = importing(store, snapshot, config_doc)
        accept_snapshot(store, run["run_id"], operator="reviewer")
        assert totals(accepted_payload(store, run["note_id"])) == {}


def test_read_missing_and_open_foreign_database_do_not_create_or_migrate(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(ContractError):
        Store(missing)
    assert not missing.exists()
    foreign = tmp_path / "foreign.sqlite3"
    with sqlite3.connect(foreign) as conn:
        conn.execute("CREATE TABLE unrelated(value TEXT)")
    with pytest.raises(ContractError):
        Store(foreign, create=True)
    with sqlite3.connect(foreign) as conn:
        assert [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")] == ["unrelated"]


def test_note_and_source_kind_isolation_and_mismatched_config_rejection(tmp_path, snapshot, config_doc):
    with Store(tmp_path / "db", create=True) as store:
        first = importing(store, snapshot, config_doc)
        other_kind = deepcopy(snapshot)
        other_kind["source"]["kind"] = "line_group_note"
        second = importing(store, other_kind, config_doc)
        assert first["note_id"] != second["note_id"]
        assert first["batch_id"] != second["batch_id"]
        snapshot["source"]["note_key"] = "another-note"
        with pytest.raises(ContractError):
            importing(store, snapshot, config_doc)
        config_doc["note_key"] = "another-note"
        third = importing(store, snapshot, config_doc)
        assert third["note_id"] not in (first["note_id"], second["note_id"])
        assert store.conn.execute("PRAGMA foreign_key_check").fetchall() == []
