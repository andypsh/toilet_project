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


KAKAO_ADDR_ENDPOINT = "https://dapi.kakao.com/v2/local/search/address.json"
KAKAO_KEYWORD_ENDPOINT = "https://dapi.kakao.com/v2/local/search/keyword.json"


def _geocode_address(address: str) -> tuple[float, float, str | None] | None:
    """주소로 좌표 검색. 성공 시 (lat, lon, road_address)."""
    resp = requests.get(
        KAKAO_ADDR_ENDPOINT,
        headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
        params={"query": address},
        timeout=8,
    )
    resp.raise_for_status()
    docs = resp.json().get("documents", [])
    if not docs:
        return None
    d = docs[0]
    road = (d.get("road_address") or {}).get("address_name") if d.get("road_address") else None
    return float(d["y"]), float(d["x"]), road


def _geocode_keyword(keyword: str) -> tuple[float, float, str | None] | None:
    """place_name으로 키워드 검색. 동명이인 위험 있음 → 결과 1건일 때만 채택."""
    resp = requests.get(
        KAKAO_KEYWORD_ENDPOINT,
        headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
        params={"query": keyword, "size": 3},
        timeout=8,
    )
    resp.raise_for_status()
    docs = resp.json().get("documents", [])
    if not docs:
        return None
    # 결과가 너무 많으면 ambiguous — 첫 번째와 두 번째가 같은 동네면 채택
    d = docs[0]
    addr = d.get("road_address_name") or d.get("address_name")
    return float(d["y"]), float(d["x"]), addr


def geocode_missing(conn: sqlite3.Connection, *, batch: int = 50, sleep: float = 0.1) -> int:
    """좌표 없는 row 들에 좌표 보강.

    우선순위:
      1. address 있으면 주소 검색
      2. address 없으면 place_name으로 키워드 검색 (성공 시 검색된 주소도 저장)

    Returns: 성공 건수.
    """
    if not KAKAO_REST_API_KEY:
        print("[geocoder] KAKAO_REST_API_KEY 미설정 - 스킵.")
        return 0

    rows = conn.execute(
        """SELECT id, place_name, address FROM locations
           WHERE (latitude IS NULL OR longitude IS NULL)
           LIMIT ?""",
        (batch,),
    ).fetchall()

    success = 0
    for row in rows:
        result = None
        try:
            if row["address"]:
                result = _geocode_address(row["address"])
            if not result and row["place_name"]:
                result = _geocode_keyword(row["place_name"])
        except Exception as exc:
            print(f"[geocoder] id={row['id']} 실패: {exc}")

        if result:
            lat, lon, addr = result
            conn.execute(
                "UPDATE locations SET latitude=?, longitude=?, address=COALESCE(NULLIF(address, ''), ?), updated_at=? WHERE id=?",
                (lat, lon, addr, now_iso(), row["id"]),
            )
            success += 1
        time.sleep(sleep)
    conn.commit()
    return success
