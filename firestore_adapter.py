"""SQLite locations → Firestore `toilets` 컬렉션 스키마 변환.

안드로이드 모델 `com.bidet.app.data.model.Toilet` 과 1:1 매칭.
좌표 누락 행은 자동 제외 (lat/lng=0,0 인도양 마커 방지).

산출물:
  - firestore_toilets.json : 적재 가능한 JSON dump
  - firestore_upload.py    : firebase-admin 으로 toilets 컬렉션 적재
"""
from __future__ import annotations

import _console  # noqa: F401

import json
import sys
import time
from pathlib import Path

from db import connect


# ─────────── Geohash (안드로이드 Geohash.kt 와 동일 알고리즘) ───────────
BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash_encode(lat: float, lng: float, precision: int = 9) -> str:
    lat_range = [-90.0, 90.0]
    lng_range = [-180.0, 180.0]
    out: list[str] = []
    is_even = True
    bit = 0
    ch = 0
    while len(out) < precision:
        if is_even:
            mid = (lng_range[0] + lng_range[1]) / 2
            if lng >= mid:
                ch |= (1 << (4 - bit))
                lng_range[0] = mid
            else:
                lng_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat >= mid:
                ch |= (1 << (4 - bit))
                lat_range[0] = mid
            else:
                lat_range[1] = mid
        is_even = not is_even
        if bit < 4:
            bit += 1
        else:
            out.append(BASE32[ch])
            bit = 0
            ch = 0
    return "".join(out)


# ─────────── 우리 enum → 안드로이드 enum 매핑 ───────────
CATEGORY_MAP = {
    "휴게소":                  "REST_AREA",
    "공항":                    "AIRPORT",
    "공항/캡슐호텔":           "AIRPORT",
    "공항/라운지":             "AIRPORT",
    "지하철역/장애인화장실":   "SUBWAY",
    "철도역":                  "TRAIN_STATION",
    "복합몰":                  "SHOPPING_MALL",
    "백화점":                  "DEPARTMENT_STORE",
    "카페":                    "CAFE",
    "public_toilet":           "PUBLIC",
    None:                      "UNKNOWN",
}

# 우리 source_type → SourceType enum (안드로이드 정의)
SOURCE_TYPE_MAP = {
    "public_data":     "PUBLIC_DATA",
    "info_disclosure": "INFORMATION_DISCLOSURE",
    "official_site":   "OFFICIAL_WEBSITE",
    "news":            "NEWS",
    "user_report":     "USER_REPORT",
    "naver_blog":      "BLOG_REVIEW",
    "naver_cafe":      "BLOG_REVIEW",
}


def _category(place_type: str | None) -> str:
    return CATEGORY_MAP.get(place_type, "UNKNOWN")


def _accessible(place_name: str, place_type: str | None) -> bool:
    return "장애인" in (place_name or "") or "장애인" in (place_type or "")


def export_toilets() -> list[dict]:
    """SQLite locations(has_bidet=1, lat/lng 보유) → Toilet dict 리스트."""
    now_ms = int(time.time() * 1000)
    docs: list[dict] = []

    with connect() as conn:
        rows = conn.execute(
            """SELECT id, place_name, address, latitude, longitude,
                      place_type, has_bidet, confidence,
                      created_at, updated_at
               FROM locations
               WHERE has_bidet = 1
                 AND latitude IS NOT NULL AND longitude IS NOT NULL
               ORDER BY confidence DESC, id"""
        ).fetchall()

        for r in rows:
            lat = float(r["latitude"])
            lng = float(r["longitude"])
            srcs = conn.execute(
                """SELECT source_type, source_url, excerpt, confidence,
                          collected_at
                   FROM sources WHERE location_id = ?
                   ORDER BY confidence DESC""",
                (r["id"],),
            ).fetchall()

            doc = {
                "id":            f"loc_{r['id']:04d}",
                "name":          r["place_name"],
                "address":       r["address"] or "",
                "lat":           lat,
                "lng":           lng,
                "geohash":       geohash_encode(lat, lng),
                "category":      _category(r["place_type"]),
                "hasBidet":      True,
                "bidetVerified": r["confidence"] >= 80,
                "bidetCount":    0,
                "gender":        "UNKNOWN",
                "accessible":    _accessible(r["place_name"], r["place_type"]),
                "openHours":     None,
                "is24h":         False,
                "isFree":        True,
                "rating":        0.0,
                "reviewCount":   0,
                "photoUrls":     [],
                "sources": [
                    {
                        "type":        SOURCE_TYPE_MAP.get(s["source_type"], "UNKNOWN"),
                        "url":         s["source_url"],
                        "description": s["excerpt"],
                        "collectedAt": now_ms,
                    }
                    for s in srcs
                ],
                "createdAt": now_ms,
                "updatedAt": now_ms,
            }
            docs.append(doc)
    return docs


def main(out_path: str = "firestore_toilets.json"):
    docs = export_toilets()
    Path(out_path).write_text(
        json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[firestore] {len(docs)}개 toilet → {out_path}")
    for d in docs:
        verified = "✓ verified" if d["bidetVerified"] else "(blog)"
        print(f"   - {d['id']:<10} {d['name'][:40]:<40} [{d['category']:<14}] {verified}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "firestore_toilets.json")
