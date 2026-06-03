"""사용자 제보 입력 (API 또는 CLI 백엔드).

앱에서 호출할 인터페이스를 가정한 함수. 단일 제보 1건을 받아 직접 locations에 적재.
"""
from __future__ import annotations

import sqlite3

from config import SOURCE_CONFIDENCE
from db import add_source, upsert_location


def collect_user_report(
    conn: sqlite3.Connection,
    *,
    place_name: str,
    address: str | None,
    has_bidet: bool,
    user_id: str | None = None,
    note: str | None = None,
) -> int:
    """사용자 제보 1건 적재. Returns: location id."""
    loc_id = upsert_location(
        conn,
        place_name=place_name,
        address=address,
        place_type=None,
        has_bidet=1 if has_bidet else 0,
    )
    add_source(
        conn,
        location_id=loc_id,
        source_type="user_report",
        confidence=SOURCE_CONFIDENCE["user_report"],
        excerpt=note or (f"제보자={user_id}" if user_id else "사용자 제보"),
    )
    conn.commit()
    return loc_id
