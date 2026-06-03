"""잘 알려진 7개 시설 좌표 fill (공개 정보 기반).

휴게소 4개는 좌표 미보유 → 카카오 로컬 API 키 추가 후 `pipeline.py geocode`로 자동 보강.
"""
import _console  # noqa: F401

from db import connect, now_iso


# place_name 부분 매칭 → (lat, lng)
KNOWN_COORDS = {
    "인천국제공항 제2터미널":  (37.4691, 126.4498),
    "김해국제공항":            (35.1796, 128.9385),
    "1·2호선 시청역":          (37.5641, 126.9774),
    "3호선 종로3가역":         (37.5705, 126.9920),
    "4호선 숙대입구역":        (37.5443, 126.9714),
    "KTX 서울역":              (37.5547, 126.9707),
    "롯데월드몰":              (37.5132, 127.1028),
    # has_bidet=False 인 항목도 좌표는 채워둠 (참고용)
    "인천국제공항 제1여객터미널": (37.4602, 126.4407),
    "인천국제공항 캡슐호텔":    (37.4602, 126.4407),
}


def main():
    ts = now_iso()
    updated = 0
    with connect() as conn:
        for fragment, (lat, lng) in KNOWN_COORDS.items():
            cur = conn.execute(
                """UPDATE locations
                   SET latitude = ?, longitude = ?, updated_at = ?
                   WHERE place_name LIKE ?
                     AND (latitude IS NULL OR longitude IS NULL)""",
                (lat, lng, ts, f"{fragment}%"),
            )
            updated += cur.rowcount
        conn.commit()
        no_coord = conn.execute(
            "SELECT place_name FROM locations WHERE latitude IS NULL AND has_bidet = 1"
        ).fetchall()
    print(f"[coords] {updated}건 좌표 fill")
    if no_coord:
        print(f"[coords] 좌표 미보유 (카카오 키 발급 후 geocode 필요):")
        for r in no_coord:
            print(f"   - {r['place_name']}")


if __name__ == "__main__":
    main()
