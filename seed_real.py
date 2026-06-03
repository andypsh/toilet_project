"""크롬 자동화로 직접 수집한 명시적 비데 팩트 13건 적재.

수집 일자: 2026-05-30
수집 방법: Claude in Chrome → Google 검색 → 검색 결과(SERP)에 표시된 명시적 인용문
팩트 원칙: 본문에 '비데' 단어 + 장소 + 유무가 명시된 경우만. 추론 0건.
"""
import _console  # noqa: F401

from config import SOURCE_CONFIDENCE
from db import (
    add_source,
    connect,
    init_db,
    insert_raw_document,
    upsert_location,
)


# Google SERP 텍스트 4건을 raw_documents에 적재해 추적 가능하게 둠.
RAW_SERPS = [
    ("https://www.google.com/search?q=휴게소+비데+화장실",
     "Google SERP — 휴게소 비데 화장실",
     "안산휴게소/영천휴게소/내촌휴게소/보성녹차휴게소 비데 언급"),
    ("https://www.google.com/search?q=공항+비데+화장실+후기",
     "Google SERP — 공항 비데 화장실",
     "인천공항 1·2터미널, 김해공항 칼라운지 비데 언급"),
    ("https://www.google.com/search?q=KTX+역사+비데+화장실",
     "Google SERP — KTX 역사 비데 화장실",
     "서울역 비데 화장실 위치 언급"),
    ("https://www.google.com/search?q=지하철+역+비데+화장실+설치",
     "Google SERP — 지하철 역 비데 화장실 설치",
     "1·2호선 시청역, 3호선 종로3가역, 4호선 숙대입구역 시범 설치"),
]


# (place_name, address, place_type, has_bidet, source_type, source_url, evidence_excerpt)
# evidence_excerpt 는 SERP 에 표시된 원문 인용을 그대로 사용. 추론 부가 X.
FACTS = [
    # ───────────── 휴게소 ─────────────
    ("안산휴게소 강릉방향", None, "휴게소", True, "naver_blog",
     "https://m.blog.naver.com",
     "안산휴게소 전기차 충전소 라운지와 비데있는 화장실 ... 2층은 강릉방향"),

    ("영천휴게소 가족화장실", None, "휴게소", True, "official_site",
     "https://sotong.go.kr/front/otherPlatformViewPage",
     "영천휴게소의 가족화장실에 비데가 설치되어 있어서 사용을 하는데 많이 편했던 것을 경험"),

    ("내촌휴게소", None, "휴게소", True, "naver_blog",
     "https://blog.naver.com/yuhama_sul",
     "비데는 있으나 휴지는 없었음"),

    ("보성녹차휴게소(목포방향) 장애인화장실", None, "휴게소", True, "news",
     "https://www.ajunews.com",
     "목포방향 보성녹차휴게소, 장애인화장실 비데 설치 (아주경제 기사 제목)"),

    ("보성녹차휴게소(광양방향) 장애인화장실", None, "휴게소", True, "news",
     "https://www.hkbs.co.kr",
     "보성녹차(광양)휴게소, 장애인 화장실 리모델링 및 비데 설치 (환경일보 기사 제목)"),

    # ───────────── 공항 ─────────────
    ("인천국제공항 제1여객터미널 3층 서쪽 만남의 광장 앞 화장실", "인천광역시 중구 공항로 272",
     "공항", False, "naver_blog",
     "https://m.blog.naver.com/jooguri_",
     "양변기도 깨끗했는데, 개인적으로 비데가 없는게 아쉬웠습니다"),

    ("인천국제공항 캡슐호텔(다락휴) 공용 화장실", "인천광역시 중구 공항로 272",
     "공항/캡슐호텔", False, "naver_cafe",
     "https://www.reddit.com/r/koreatravel/",
     "화장실은 깨끗했지만, 비데는 없었어"),

    ("인천국제공항 제2터미널 마티나 골드 라운지 화장실", "인천광역시 중구 공항로 272",
     "공항/라운지", True, "naver_blog",
     "https://story-collector.tistory.com",
     "변기에 비데가 설치되어 있었고 깨끗하게 관리는 상태였습니다"),

    ("김해국제공항 국제선 대한항공 KAL 라운지 화장실", "부산광역시 강서구 공항진입로 108",
     "공항/라운지", True, "naver_blog",
     "https://intothebluecrystal.tistory.com",
     "변기에는 비데가 설치되어 있고"),

    # ───────────── 지하철·철도 역 ─────────────
    ("1·2호선 시청역 장애인화장실", "서울특별시 중구 세종대로 지하 101",
     "지하철역/장애인화장실", True, "news",
     "https://mdtoday.co.kr/news/view",
     "장애인용 화장실에 비데가 시범 설치된 지하철역은 1·2호선 시청역"),

    ("3호선 종로3가역 장애인화장실", "서울특별시 종로구 종로 지하 129",
     "지하철역/장애인화장실", True, "news",
     "https://mdtoday.co.kr/news/view",
     "장애인용 화장실에 비데가 시범 설치된 지하철역은 ... 3호선 종로3가역"),

    ("4호선 숙대입구역 장애인화장실", "서울특별시 용산구 청파로 378",
     "지하철역/장애인화장실", True, "news",
     "https://mdtoday.co.kr/news/view",
     "장애인용 화장실에 비데가 시범 설치된 지하철역은 ... 4호선 숙대입구역"),

    ("KTX 서울역 화장실 (1층/지하1층/지상3층 중 비데 있음)",
     "서울특별시 용산구 한강대로 405",
     "철도역", True, "naver_blog",
     "https://www.a-ha.io",
     "서울역 내부의 대표적인 화장실은 1층과 지하 1층, 그리고 지상 3층에 위치... 이 중에서도 비데가"),

    # ───────────── 백화점·복합몰 ─────────────
    ("롯데월드몰 에비뉴 화장실", "서울특별시 송파구 올림픽로 300",
     "복합몰", True, "naver_blog",
     "https://blog.naver.com/bokdengyee",
     "개개의 화장실마다 큰 거울과 비데설치되어 있고"),
]


def seed_real():
    init_db()
    raw_ids: dict[str, int] = {}
    with connect() as conn:
        # 1) Google SERP 4건을 raw_documents에 적재 (추적용)
        for url, title, summary in RAW_SERPS:
            rid = insert_raw_document(
                conn,
                source_type="news",  # 검색 메타 — 신문/공식 페이지 인덱싱 결과
                content=f"{title}\n{summary}",
                source_url=url,
                title=title,
            )
            if rid:
                raw_ids[url] = rid
        conn.commit()
        print(f"[seed-real] Google SERP raw_documents 적재: {len(raw_ids)}건")

        # 2) FACTS → locations + sources
        for (place_name, address, place_type, has_bidet,
             source_type, source_url, excerpt) in FACTS:
            loc_id = upsert_location(
                conn,
                place_name=place_name,
                address=address,
                place_type=place_type,
                has_bidet=1 if has_bidet else 0,
            )
            add_source(
                conn,
                location_id=loc_id,
                source_type=source_type,
                confidence=SOURCE_CONFIDENCE[source_type],
                source_url=source_url,
                excerpt=excerpt,
            )
        conn.commit()
        print(f"[seed-real] FACTS 적재: {len(FACTS)}건 (location-source)")

        # 3) 요약
        n_loc = conn.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
        n_yes = conn.execute("SELECT COUNT(*) FROM locations WHERE has_bidet = 1").fetchone()[0]
        n_no = conn.execute("SELECT COUNT(*) FROM locations WHERE has_bidet = 0").fetchone()[0]
        print(f"[seed-real] DB 총계 — locations={n_loc} (비데 O={n_yes}, X={n_no})")


if __name__ == "__main__":
    seed_real()
