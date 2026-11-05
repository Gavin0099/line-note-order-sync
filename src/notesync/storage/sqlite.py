"""SQLite v1 repository; raw inputs, decisions and accepted payloads persist."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3

from notesync.domain.models import ContractError

SCHEMA = """
BEGIN;
CREATE TABLE notes(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, scope_key TEXT NOT NULL,
 note_key TEXT NOT NULL, UNIQUE(kind,scope_key,note_key));
CREATE TABLE batches(id INTEGER PRIMARY KEY, note_id INTEGER NOT NULL REFERENCES notes(id),
 raw_sha256 TEXT NOT NULL, raw BLOB NOT NULL, captured_at TEXT NOT NULL, imported_at TEXT NOT NULL,
 UNIQUE(note_id,raw_sha256));
CREATE TABLE configs(id INTEGER PRIMARY KEY, sha256 TEXT NOT NULL UNIQUE, document TEXT NOT NULL);
CREATE TABLE runs(id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES batches(id),
 config_id INTEGER NOT NULL REFERENCES configs(id), parser_version TEXT NOT NULL,
 independent_confirmed INTEGER NOT NULL CHECK(independent_confirmed IN (0,1)),
 operator TEXT NOT NULL, created_at TEXT NOT NULL,
 UNIQUE(batch_id,config_id,parser_version,independent_confirmed));
CREATE TABLE results(run_id INTEGER NOT NULL REFERENCES runs(id), position INTEGER NOT NULL,
 value TEXT NOT NULL, PRIMARY KEY(run_id,position));
CREATE TABLE reviews(id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL, position INTEGER NOT NULL,
 before_value TEXT NOT NULL, after_value TEXT NOT NULL, operator TEXT NOT NULL,
 reason TEXT NOT NULL, created_at TEXT NOT NULL,
 FOREIGN KEY(run_id,position) REFERENCES results(run_id,position));
CREATE TABLE buyer_groups(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, scope_key TEXT NOT NULL,
 label TEXT NOT NULL, UNIQUE(kind,scope_key,label));
CREATE TABLE acceptances(id INTEGER PRIMARY KEY, note_id INTEGER NOT NULL REFERENCES notes(id),
 run_id INTEGER NOT NULL REFERENCES runs(id), revision INTEGER NOT NULL,
 payload TEXT NOT NULL, operator TEXT NOT NULL, accepted_at TEXT NOT NULL, UNIQUE(run_id,revision));
CREATE TABLE current_acceptances(note_id INTEGER PRIMARY KEY REFERENCES notes(id),
 acceptance_id INTEGER NOT NULL REFERENCES acceptances(id));
CREATE TABLE rejected_inputs(id INTEGER PRIMARY KEY, raw_sha256 TEXT NOT NULL, raw BLOB NOT NULL,
 reason TEXT NOT NULL, operator TEXT NOT NULL, created_at TEXT NOT NULL);
PRAGMA user_version=1;
COMMIT;
"""


class Store:
    def __init__(self, path: str | Path, *, create: bool = False, writable: bool = False):
        path = Path(path).resolve()
        if create:
            path.parent.mkdir(parents=True, exist_ok=True)
        elif not path.is_file():
            raise ContractError("資料庫不存在；請先匯入快照")
        mode = "rwc" if create else "rw" if writable else "ro"
        self.conn = sqlite3.connect(path.as_uri() + f"?mode={mode}", uri=True, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        try:
            self.conn.execute("PRAGMA foreign_keys=ON")
            version = self.conn.execute("PRAGMA user_version").fetchone()[0]
            if version == 0 and create:
                tables = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                if tables:
                    raise ContractError("不修改未識別的既有資料庫；請選空白 POC DB")
                self.conn.executescript(SCHEMA)
            elif version != 1:
                raise ContractError("資料庫 schema 版本不支援；不自動遷移")
            required = {"notes", "batches", "configs", "runs", "results", "reviews", "buyer_groups",
                        "acceptances", "current_acceptances", "rejected_inputs"}
            present = {r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not required <= present:
                raise ContractError("資料庫不是 notesync v1 schema")
        except BaseException:
            self.conn.close()
            raise

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *args: object) -> None:
        self.conn.close()

    @contextmanager
    def transaction(self):
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
            self.conn.execute("COMMIT")
        except BaseException:
            if self.conn.in_transaction:
                self.conn.execute("ROLLBACK")
            raise
