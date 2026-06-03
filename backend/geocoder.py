"""주소 → 좌표 변환 (카카오 로컬 API).

locations 에서 lat/lon 이 NULL 이고 address가 있는 행을 골라 보강.
키 없으면 그냥 skip (raise X).
"""
from __future__ import annotations

import sqlite3
import time

import requests

from config import KAKAO_REST_API_KEY
from db import now_iso


KAKAO_ENDPOINT = "https://dapi.kakao.com/v2/local/search/address.json"


def _geocode_one(address: str) -> tuple[float, float] | None:
    resp = requests.get(
        KAKAO_ENDPOINT,
        headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
        params={"query": address},
        timeout=8,
    )
    resp.raise_for_status()
    docs = resp.json().get("documents", [])
    if not docs:
        return None
    d = docs[0]
    return float(d["y"]), float(d["x"])  # (lat, lon)


def geocode_missing(conn: sqlite3.Connection, *, batch: int = 50, sleep: float = 0.1) -> int:
    """좌표 없는 row 들에 대해 카카오 로컬 API 호출. Returns: 성공 건수."""
    if not KAKAO_REST_API_KEY:
        print("[geocoder] KAKAO_REST_API_KEY 미설정 - 스킵.")
        return 0

    rows = conn.execute(
        """SELECT id, address FROM locations
           WHERE (latitude IS NULL OR longitude IS NULL)
             AND address IS NOT NULL AND address != ''
           LIMIT ?""",
        (batch,),
    ).fetchall()

    success = 0
    for row in rows:
        try:
            coords = _geocode_one(row["address"])
        except Exception as exc:
            print(f"[geocoder] {row['address']!r} 실패: {exc}")
            coords = None
        if coords:
            lat, lon = coords
            conn.execute(
                "UPDATE locations SET latitude=?, longitude=?, updated_at=? WHERE id=?",
                (lat, lon, now_iso(), row["id"]),
            )
            success += 1
        time.sleep(sleep)
    conn.commit()
    return success
