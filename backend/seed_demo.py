"""데모 시드 — API 키 없이도 파이프라인 흐름을 확인하기 위한 가짜 raw_documents.

실제 블로그/카페 글의 톤을 따라한 합성 텍스트. 추출 단계(룰베이스 폴백) 동작 확인용.
"""
import _console  # noqa: F401  (Windows cp949 콘솔 utf-8 재설정)

from db import connect, init_db, insert_raw_document
from collectors.user_report import collect_user_report
from extractor import extract_from_unprocessed
from geocoder import geocode_missing


SAMPLE_BLOGS = [
    {
        "url": "https://example-blog.test/1",
        "title": "강남역 부근 화장실 후기",
        "content": "어제 강남역 2번 출구 근처 화장실에 갔는데 비데까지 깔끔하게 설치돼 있어서 놀랐어요.",
    },
    {
        "url": "https://example-blog.test/2",
        "title": "신세계백화점 강남점 다녀옴",
        "content": "신세계백화점 강남점 5층 화장실에 비데가 있더라구요. 위생 상태도 양호.",
    },
    {
        "url": "https://example-blog.test/3",
        "title": "여행 가서 화장실 갔는데",
        "content": "어디였더라 화장실에 비데 있길래 신기했음. 어디였는지 기억 안남ㅋㅋ",
        # 장소 미상 → 추출 스킵되어야 함
    },
    {
        "url": "https://example-blog.test/4",
        "title": "OO휴게소 짜증",
        "content": "행담도휴게소 갔는데 비데 없어서 좀 아쉬웠음. 화장실은 그래도 깨끗.",
    },
    {
        "url": "https://example-blog.test/5",
        "title": "추론용 글 — 추출되면 안 됨",
        "content": "롯데호텔이면 당연히 비데 있겠지~ 가본 적은 없는데.",
        # '비데' 키워드는 있지만 "비데가 있다/없다"의 명시적 팩트가 아닌 추론
        # 룰베이스로는 잡힐 수도 있음 — LLM이면 거름. 한계 케이스로 노출.
    },
]


def seed():
    init_db()
    with connect() as conn:
        # raw_documents 시드
        new = 0
        for s in SAMPLE_BLOGS:
            rid = insert_raw_document(
                conn,
                source_type="naver_blog",
                source_url=s["url"],
                title=s["title"],
                content=s["content"],
            )
            if rid:
                new += 1
        conn.commit()
        print(f"[seed] raw_documents 신규 {new}건")

        # 사용자 제보 1건도 추가
        collect_user_report(
            conn,
            place_name="인천공항 제2터미널 3층 동편 화장실",
            address="인천광역시 중구 공항로 272",
            has_bidet=True,
            user_id="demo-user",
            note="제2터미널 3층 동편 — 직접 사용 확인",
        )

        # 정제(추출)
        pairs = extract_from_unprocessed(conn)
        print(f"[extract] {pairs}개 location-source 쌍 생성")

        # 좌표화 (키 없으면 skip)
        n = geocode_missing(conn)
        print(f"[geocode] 좌표 보강 {n}건")


if __name__ == "__main__":
    seed()
