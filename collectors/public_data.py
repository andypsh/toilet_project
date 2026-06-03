"""공공데이터포털 — 전국공중화장실표준데이터.

API: https://www.data.go.kr/data/15012890/standard.do
표준 데이터의 일부 지자체는 '비데설치여부' 컬럼을 제공함. 해당 컬럼이 'Y'인 행만 채택.
컬럼 없거나 비어있으면 raw_documents에 적재만 하고 LLM 추출은 통과 (팩트 없음).
"""
from __future__ import annotations

import json
import sqlite3

import requests

from config import PUBLIC_DATA_API_KEY
from db import add_source, insert_raw_document, upsert_location, now_iso
from config import SOURCE_CONFIDENCE


ENDPOINT = "http://api.data.go.kr/openapi/tn_pubr_public_toilet_api"


def collect_public_toilet(
    conn: sqlite3.Connection,
    *,
    rows_per_page: int = 100,
    max_pages: int = 5,
) -> int:
    """공공 화장실 표준 데이터에서 비데 설치 여부 'Y' 인 항목만 locations에 직접 적재.

    Returns: 추가된 location 수.
    """
    if not PUBLIC_DATA_API_KEY:
        raise RuntimeError("PUBLIC_DATA_API_KEY 미설정.")

    added = 0
    for page in range(1, max_pages + 1):
        resp = requests.get(
            ENDPOINT,
            params={
                "serviceKey": PUBLIC_DATA_API_KEY,
                "pageNo": page,
                "numOfRows": rows_per_page,
                "type": "json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        items = (
            data.get("response", {})
                .get("body", {})
                .get("items", [])
        )
        if not items:
            break

        for it in items:
            bidet_flag = (it.get("bidetInstallYn") or it.get("bidetYn") or "").strip().upper()
            if bidet_flag != "Y":
                # 팩트가 명시되지 않은 행은 추론 금지 — 적재 스킵
                continue
            place_name = it.get("toiletNm") or it.get("publicToiletName")
            if not place_name:
                continue
            address = it.get("rdnmadr") or it.get("lnmadr")
            lat = it.get("latitude")
            lon = it.get("longitude")
            try:
                lat = float(lat) if lat not in (None, "", "0") else None
                lon = float(lon) if lon not in (None, "", "0") else None
            except (TypeError, ValueError):
                lat = lon = None

            raw_id = insert_raw_document(
                conn,
                source_type="public_data",
                source_url=ENDPOINT,
                title=place_name,
                content=json.dumps(it, ensure_ascii=False),
            )
            loc_id = upsert_location(
                conn,
                place_name=place_name,
                address=address,
                place_type="public_toilet",
                has_bidet=1,
                latitude=lat,
                longitude=lon,
            )
            add_source(
                conn,
                location_id=loc_id,
                source_type="public_data",
                confidence=SOURCE_CONFIDENCE["public_data"],
                raw_doc_id=raw_id,
                source_url=ENDPOINT,
                excerpt=f"공공데이터 비데설치여부={bidet_flag}",
            )
            added += 1
        conn.commit()
    return added
