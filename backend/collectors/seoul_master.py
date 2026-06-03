"""@dododo9511 가 수집한 서울시 공중화장실 마스터 CSV → SQLite seoul_master 테이블.

CSV 출처: 행안부 공중화장실 표준 데이터 (서울특별시), 5,656건.
인코딩: EUC-KR (cp949).

목적:
  1) 별도 마스터 테이블에 적재 (locations 테이블과 분리)
  2) 우리 locations 의 좌표를 정확한 행정 좌표로 보강 (지하철역 등)
  3) 추후 사용자 제보 시 자동완성 후보로 활용 가능
"""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

SEOUL_CSV = (
    Path(__file__).parent.parent
    / "dodo_data" / "메인자료" / "공중화장실정보_서울특별시.csv"
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS seoul_master (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    road_address  TEXT,
    jibun_address TEXT,
    latitude      REAL,
    longitude     REAL,
    manager_name  TEXT,
    open_hours    TEXT,
    UNIQUE(name, road_address)
);
CREATE INDEX IF NOT EXISTS idx_seoul_master_name ON seoul_master(name);
"""


def _f(s: str | None) -> float | None:
    if not s:
        return None
    try:
        v = float(s)
        return v if v != 0 else None
    except (TypeError, ValueError):
        return None


def load_seoul_master(
    conn: sqlite3.Connection,
    csv_path: Path | str | None = None,
) -> int:
    """CSV 적재. Returns: 신규 적재 행 수."""
    conn.executescript(SCHEMA)
    path = Path(csv_path or SEOUL_CSV)
    if not path.exists():
        raise FileNotFoundError(f"{path} 없음. backend/dodo_data/ 확인.")

    inserted = 0
    with open(path, encoding="cp949", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("화장실명") or "").strip()
            if not name:
                continue
            cur = conn.execute(
                """INSERT OR IGNORE INTO seoul_master
                   (name, road_address, jibun_address, latitude, longitude,
                    manager_name, open_hours)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    name,
                    (row.get("소재지도로명주소") or "").strip() or None,
                    (row.get("소재지지번주소") or "").strip() or None,
                    _f(row.get("WGS84위도")),
                    _f(row.get("WGS84경도")),
                    (row.get("관리기관명") or "").strip() or None,
                    (row.get("개방시간") or "").strip() or None,
                ),
            )
            if cur.rowcount:
                inserted += 1
    conn.commit()
    return inserted


# place_name 의 핵심 키워드 → seoul_master 매칭용
MATCH_KEYWORDS = [
    "시청역", "종로3가역", "종로3가", "숙대입구역", "숙대입구",
    "서울역", "롯데월드몰", "롯데월드", "강남역",
]


def match_coords_from_master(conn: sqlite3.Connection) -> int:
    """우리 locations 의 좌표를 seoul_master 정확 좌표로 갱신.

    locations.place_name 안에 MATCH_KEYWORDS 중 하나가 포함되면,
    seoul_master.name LIKE '%키워드%' 의 첫 매치 좌표로 update.
    """
    from db import now_iso

    rows = conn.execute(
        "SELECT id, place_name FROM locations WHERE has_bidet = 1"
    ).fetchall()
    updated = 0
    for r in rows:
        name = r["place_name"] or ""
        for kw in MATCH_KEYWORDS:
            if kw in name:
                m = conn.execute(
                    """SELECT name, latitude, longitude FROM seoul_master
                       WHERE name LIKE ? AND latitude IS NOT NULL
                       LIMIT 1""",
                    (f"%{kw}%",),
                ).fetchone()
                if m:
                    conn.execute(
                        """UPDATE locations
                           SET latitude = ?, longitude = ?, updated_at = ?
                           WHERE id = ?""",
                        (m["latitude"], m["longitude"], now_iso(), r["id"]),
                    )
                    updated += 1
                    print(
                        f"  ↳ {name[:40]:<40} ← '{m['name']}' "
                        f"({m['latitude']:.5f}, {m['longitude']:.5f})"
                    )
                break
    conn.commit()
    return updated


if __name__ == "__main__":
    import _console  # noqa: F401
    from db import connect, init_db

    init_db()
    with connect() as c:
        n = load_seoul_master(c)
        print(f"[seoul-master] CSV 적재: {n}건")
        total = c.execute("SELECT COUNT(*) FROM seoul_master").fetchone()[0]
        print(f"[seoul-master] DB 총 마스터: {total}건")
        print(f"[seoul-master] 좌표 매칭 시작 ...")
        u = match_coords_from_master(c)
        print(f"[seoul-master] {u}건 좌표 갱신 (마스터 정확 좌표로 보강)")
