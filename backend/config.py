"""환경변수/경로 로딩."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).parent
DB_PATH = ROOT / "bidet.db"

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PUBLIC_DATA_API_KEY = os.getenv("PUBLIC_DATA_API_KEY", "")


# source_type별 기본 신뢰도 (0~100). 사용자 검증 누적되면 동적으로 올라감.
SOURCE_CONFIDENCE = {
    "public_data":     95,  # 공공데이터포털 표준 데이터
    "info_disclosure": 90,  # 정보공개청구 결과
    "official_site":   85,  # 공식 페이지/정부 운영 채널 (소통24 등)
    "news":            80,  # 신문 보도 (기자 확인)
    "user_report":     70,  # 사용자 제보 (단일)
    "naver_blog":      60,  # 블로그
    "naver_cafe":      55,  # 카페/포럼
}
