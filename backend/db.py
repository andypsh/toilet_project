"""SQLite 스키마 + 헬퍼.

테이블:
  - raw_documents     : 수집 단계 결과 (정제 전 원본)
  - locations         : 정제 후 화장실 위치
  - sources           : location 1건의 근거(여러 출처 N:1)
  - user_verifications: 사용자 검증 버튼 결과
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_documents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_url  TEXT,
    title       TEXT,
    content     TEXT NOT NULL,
    fetched_at  TEXT NOT NULL,
    processed   INTEGER NOT NULL DEFAULT 0,
    UNIQUE(source_type, source_url, title)
);

CREATE TABLE IF NOT EXISTS locations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    place_name  TEXT NOT NULL,
    address     TEXT,
    latitude    REAL,
    longitude   REAL,
    place_type  TEXT,
    has_bidet   INTEGER,
    confidence  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    UNIQUE(place_name, address)
);

CREATE TABLE IF NOT EXISTS sources (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id  INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    raw_doc_id   INTEGER REFERENCES raw_documents(id) ON DELETE SET NULL,
    source_type  TEXT NOT NULL,
    source_url   TEXT,
    excerpt      TEXT,
    confidence   INTEGER NOT NULL,
    collected_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_verifications (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id  INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    vote         INTEGER NOT NULL,
    user_id      TEXT,
    verified_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_locations_geo
    ON locations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_sources_loc
    ON sources(location_id);
CREATE INDEX IF NOT EXISTS idx_raw_unprocessed
    ON raw_documents(processed);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | str | None = None) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def insert_raw_document(
    conn: sqlite3.Connection,
    source_type: str,
    content: str,
    *,
    source_url: str | None = None,
    title: str | None = None,
) -> int | None:
    """중복(source_type+url+title) 이면 None 반환."""
    cur = conn.execute(
        """INSERT OR IGNORE INTO raw_documents
           (source_type, source_url, title, content, fetched_at)
           VALUES (?, ?, ?, ?, ?)""",
        (source_type, source_url, title, content, now_iso()),
    )
    return cur.lastrowid if cur.rowcount else None


def upsert_location(
    conn: sqlite3.Connection,
    *,
    place_name: str,
    address: str | None,
    place_type: str | None,
    has_bidet: int | None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> int:
    ts = now_iso()
    cur = conn.execute(
        "SELECT id FROM locations WHERE place_name = ? AND IFNULL(address,'') = IFNULL(?,'')",
        (place_name, address),
    )
    row = cur.fetchone()
    if row:
        conn.execute(
            """UPDATE locations
               SET has_bidet = COALESCE(?, has_bidet),
                   latitude  = COALESCE(?, latitude),
                   longitude = COALESCE(?, longitude),
                   place_type= COALESCE(?, place_type),
                   updated_at= ?
               WHERE id = ?""",
            (has_bidet, latitude, longitude, place_type, ts, row["id"]),
        )
        return row["id"]
    cur = conn.execute(
        """INSERT INTO locations
           (place_name, address, latitude, longitude, place_type,
            has_bidet, confidence, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)""",
        (place_name, address, latitude, longitude, place_type,
         has_bidet, ts, ts),
    )
    return cur.lastrowid


def add_source(
    conn: sqlite3.Connection,
    *,
    location_id: int,
    source_type: str,
    confidence: int,
    raw_doc_id: int | None = None,
    source_url: str | None = None,
    excerpt: str | None = None,
) -> None:
    conn.execute(
        """INSERT INTO sources
           (location_id, raw_doc_id, source_type, source_url,
            excerpt, confidence, collected_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (location_id, raw_doc_id, source_type, source_url,
         excerpt, confidence, now_iso()),
    )
    # location.confidence = max(sources.confidence)
    conn.execute(
        """UPDATE locations
           SET confidence = (
               SELECT MAX(confidence) FROM sources WHERE location_id = ?
           )
           WHERE id = ?""",
        (location_id, location_id),
    )


def mark_processed(conn: sqlite3.Connection, raw_doc_id: int) -> None:
    conn.execute(
        "UPDATE raw_documents SET processed = 1 WHERE id = ?", (raw_doc_id,)
    )


def fetch_unprocessed(conn: sqlite3.Connection, limit: int = 50):
    return conn.execute(
        """SELECT id, source_type, source_url, title, content
           FROM raw_documents WHERE processed = 0 LIMIT ?""",
        (limit,),
    ).fetchall()
