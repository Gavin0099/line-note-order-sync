import json
import os
from pathlib import Path
import subprocess
import sys

from notesync.demo import run_demo
from notesync.domain.models import ContractError
from notesync.service import accepted_payload, totals
from notesync.storage.sqlite import Store
import pytest


def test_demo_executes_real_workflow_and_keeps_both_accepted_versions(tmp_path):
    result = run_demo(tmp_path / "demo")
    assert result["totals"] == {"A": 3, "B": 1}
    assert result["steps_passed"] == 6
    assert result["synthetic"] is True
    assert result["line_capture"] == "NOT_EVALUATED"
    root = Path(result["report"]).parent
    assert "未連接 LINE" in Path(result["report"]).read_text(encoding="utf-8")
    manifests = [json.loads(p.read_text(encoding="utf-8")) for p in root.glob("reports/*/manifest.json")]
    assert sorted(m["totals"]["A"] for m in manifests if m["mode"] == "HUMAN_DECLARED") == [3, 4]
    assert sum(m["mode"] == "DRAFT" for m in manifests) == 1
    with Store(result["database"]) as store:
        assert store.conn.execute("SELECT COUNT(*) FROM acceptances").fetchone()[0] == 2
        assert totals(accepted_payload(store, 1)) == {"A": 3, "B": 1}
    before = Path(result["database"]).read_bytes()
    with pytest.raises(ContractError):
        run_demo(root)
    assert Path(result["database"]).read_bytes() == before


def test_cli_demo_and_read_commands_do_not_create_unrequested_databases(tmp_path):
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    def command(*args):
        return subprocess.run([sys.executable, "-m", "notesync", *map(str, args)], cwd=tmp_path,
                              env=env, capture_output=True, encoding="utf-8", check=False)
    output = tmp_path / "demo"
    result = command("demo", "--output", output)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["steps_passed"] == 6
    listing = command("inspect", "--db", output / "orders.sqlite3")
    assert listing.returncode == 0
    assert len(json.loads(listing.stdout)["runs"]) == 3
    missing = tmp_path / "not-created.sqlite3"
    rejected = command("inspect", "--db", missing)
    assert rejected.returncode == 2
    assert not missing.exists()


def test_cli_import_review_accept_and_export_are_operable(tmp_path, snapshot, config_doc):
    snapshot["comments"][1]["text"] = "A+1？"
    source = tmp_path / "snapshot.json"
    products = tmp_path / "products.json"
    source.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
    products.write_text(json.dumps(config_doc, ensure_ascii=False), encoding="utf-8")
    db = tmp_path / "orders.sqlite3"
    def command(*args):
        return subprocess.run([sys.executable, "-m", "notesync", *map(str, args)], cwd=tmp_path,
                              capture_output=True, encoding="utf-8", check=False)
    parsed = command("parse", "--products", products, "--text", "Ａ＋１")
    assert parsed.returncode == 0, parsed.stderr
    assert json.loads(parsed.stdout)["items"] == {"A": 1}
    imported = command("import", source, "--products", products, "--db", db, "--operator", "importer")
    assert imported.returncode == 0, imported.stderr
    run = json.loads(imported.stdout)["run_id"]
    rejected = command("accept", "--db", db, "--run", run, "--operator", "reviewer")
    assert rejected.returncode == 2
    assert "Traceback" not in rejected.stderr
    reviewed = command("review", "--db", db, "--run", run, "--position", 1, "--action", "set",
                       "--items", '{"A":4}', "--buyer", "合成測試😀", "--operator", "reviewer", "--reason", "confirmed quantity")
    assert reviewed.returncode == 0, reviewed.stderr
    accepted = command("accept", "--db", db, "--run", run, "--operator", "reviewer")
    assert accepted.returncode == 0, accepted.stderr
    assert json.loads(accepted.stdout)["totals"] == {"A": 5, "B": 2}
    exported = command("export", "--db", db, "--note", 1, "--output", tmp_path / "export")
    assert exported.returncode == 0, exported.stderr
    assert Path(json.loads(exported.stdout)["report"]).is_file()
    inspected = command("inspect", "--db", db, "--run", run)
    assert "合成測試😀" in inspected.stdout
