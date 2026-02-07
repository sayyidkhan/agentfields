from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


SCHEMA_VERSION = 1


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, default=str)


@dataclass
class SqliteDB:
    path: Path

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def migrate(self) -> None:
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT NOT NULL)"
            )
            row = conn.execute("SELECT v FROM meta WHERE k='schema_version'").fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO meta (k, v) VALUES ('schema_version', ?)",
                    (str(SCHEMA_VERSION),),
                )
            # v1 tables
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                  case_id TEXT PRIMARY KEY,
                  asset TEXT NOT NULL,
                  persona_id TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  inputs_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                  event_id TEXT PRIMARY KEY,
                  case_id TEXT NOT NULL,
                  asset TEXT NOT NULL,
                  occurred_at TEXT NOT NULL,
                  event_json TEXT NOT NULL,
                  FOREIGN KEY(case_id) REFERENCES cases(case_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                  decision_id TEXT PRIMARY KEY,
                  case_id TEXT NOT NULL,
                  asset TEXT NOT NULL,
                  as_of TEXT NOT NULL,
                  guard_json TEXT NOT NULL,
                  audit_id TEXT NOT NULL,
                  FOREIGN KEY(case_id) REFERENCES cases(case_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audits (
                  audit_id TEXT PRIMARY KEY,
                  case_id TEXT NOT NULL,
                  asset TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  inputs_json TEXT NOT NULL,
                  memory_reads_json TEXT NOT NULL,
                  memory_writes_json TEXT NOT NULL,
                  reasoner_outputs_json TEXT NOT NULL,
                  selected_actions_json TEXT NOT NULL,
                  citations_json TEXT NOT NULL,
                  FOREIGN KEY(case_id) REFERENCES cases(case_id)
                )
                """
            )
            # Memory: KV + vectors
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_kv (
                  scope TEXT NOT NULL,
                  k TEXT NOT NULL,
                  v_json TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  PRIMARY KEY (scope, k)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_vectors (
                  vector_id TEXT PRIMARY KEY,
                  scope TEXT NOT NULL,
                  text TEXT NOT NULL,
                  embedding_json TEXT NOT NULL,
                  metadata_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                )
                """
            )


def insert_case(conn: sqlite3.Connection, *, case_id: str, asset: str, persona_id: str, created_at: str, inputs: dict[str, Any]) -> None:
    conn.execute(
        "INSERT INTO cases(case_id, asset, persona_id, created_at, inputs_json) VALUES(?,?,?,?,?)",
        (case_id, asset, persona_id, created_at, _json_dumps(inputs)),
    )


def get_case(conn: sqlite3.Connection, case_id: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()


def insert_event(conn: sqlite3.Connection, *, event_id: str, case_id: str, asset: str, occurred_at: str, event: dict[str, Any]) -> None:
    conn.execute(
        "INSERT INTO events(event_id, case_id, asset, occurred_at, event_json) VALUES(?,?,?,?,?)",
        (event_id, case_id, asset, occurred_at, _json_dumps(event)),
    )


def insert_decision(conn: sqlite3.Connection, *, decision_id: str, case_id: str, asset: str, as_of: str, guard: dict[str, Any], audit_id: str) -> None:
    conn.execute(
        "INSERT INTO decisions(decision_id, case_id, asset, as_of, guard_json, audit_id) VALUES(?,?,?,?,?,?)",
        (decision_id, case_id, asset, as_of, _json_dumps(guard), audit_id),
    )


def get_latest_decision(conn: sqlite3.Connection, asset: str) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM decisions WHERE asset=? ORDER BY as_of DESC LIMIT 1",
        (asset,),
    ).fetchone()


def insert_audit(conn: sqlite3.Connection, *, audit_id: str, case_id: str, asset: str, created_at: str, report: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO audits(
          audit_id, case_id, asset, created_at,
          inputs_json, memory_reads_json, memory_writes_json,
          reasoner_outputs_json, selected_actions_json, citations_json
        ) VALUES(?,?,?,?,?,?,?,?,?,?)
        """,
        (
            audit_id,
            case_id,
            asset,
            created_at,
            _json_dumps(report.get("inputs", {})),
            _json_dumps(report.get("memory_reads", [])),
            _json_dumps(report.get("memory_writes", [])),
            _json_dumps(report.get("reasoner_outputs", [])),
            _json_dumps(report.get("selected_actions", [])),
            _json_dumps(report.get("citations", [])),
        ),
    )


def get_audit(conn: sqlite3.Connection, audit_id: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM audits WHERE audit_id=?", (audit_id,)).fetchone()


def get_case_audits(conn: sqlite3.Connection, case_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM audits WHERE case_id=? ORDER BY created_at ASC",
        (case_id,),
    ).fetchall()

