"""LLM 추출 단계.

raw_documents의 unprocessed 항목에서:
  - 장소명 (place_name)
  - 주소 (address) — 텍스트에 있으면
  - 비데 유무 (has_bidet: 1/0/None)
  - 명시적 근거 문장 (evidence excerpt)

을 추출. ANTHROPIC_API_KEY 있으면 Claude 사용. 없으면 룰베이스 폴백
('비데' 키워드 + 부정어 검출)로 동작.

⚠ 팩트 원칙: 텍스트에 비데 유무가 **명시적**으로 드러난 경우만 추출.
   추론(카테고리/통계 기반 추정) 절대 금지. LLM 프롬프트에도 강제.

룰베이스는 다음을 자동 제외:
  - 제품 광고 (비데물티슈, 휴대용비데, 브랜드명)
  - 개인 공간 (안방, 본가, 시골집, 아파트)
  - 모호한 표현 ('엉 화장실' 같은 일반어)
  - 너무 일반적 장소 ('KTX 역' 단독, '공중화장실' 등)
"""
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

from config import ANTHROPIC_API_KEY, SOURCE_CONFIDENCE
from db import add_source, fetch_unprocessed, mark_processed, upsert_location


SYSTEM_PROMPT = """너는 한국 화장실 비데 정보 추출기다. 주어진 텍스트(블로그/카페 글)에서
**명시적으로 언급된** 화장실 비데 정보만 추출한다.

엄격한 규칙:
1. 텍스트에 '비데' 라는 단어가 명시적으로 등장하고, 어느 장소의 화장실에
   비데가 있다/없다가 분명하게 드러난 경우에만 항목을 만든다.
2. "백화점이니까/호텔이니까/지하철역이니까 비데가 있을 것" 같은 추론은 절대 금지.
3. 장소가 특정되지 않으면(예: "여행 갔는데 비데가 있더라" — 어디인지 불명) 무시.
4. 한 텍스트에서 여러 장소가 나오면 각각 별도 항목.
5. 비데 물티슈/휴대용 비데/제품 광고 글은 추출하지 않는다 (장소 비데가 아님).
6. 개인 집/사무실의 비데 설치 후기도 추출하지 않는다 (공중 X).

JSON 으로만 응답. 스키마:
{
  "extractions": [
    {
      "place_name": "장소명 (예: 강남역 2번 출구 화장실, 신세계백화점 강남점 5층 화장실)",
      "address": "주소 또는 null",
      "has_bidet": true | false,
      "evidence": "근거가 된 원문 문장 그대로 (40자 이내로 트림)"
    }
  ]
}

추출할 항목이 없으면 {"extractions": []} 만 응답."""


def _extract_with_claude(text: str) -> list[dict[str, Any]]:
    from anthropic import Anthropic

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    body = msg.content[0].text.strip()
    body = re.sub(r"^```(?:json)?\s*|\s*```$", "", body, flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return []
    return parsed.get("extractions", []) if isinstance(parsed, dict) else []


# ─────────────── 룰베이스 ───────────────

_BIDET_RE = re.compile(r"비데")
_NEG_NEAR = re.compile(r"비데[^\.。\n]{0,15}(없|안 ?있|미설치|미비|부재)")

# 제품/광고 글 제외 (브랜드, 제품군, 거래 키워드)
_PRODUCT_BLACKLIST_RE = re.compile(
    r"(베베숲|크리넥스|루헨스|깨끗한나라|코웨이|청호|SK\s*매직|웅진|마이비데|닥터비데|클린비데|"
    r"소중한습관|미마비데|이지데이|이지케어|콜러|"
    r"비데\s*물티슈|휴대용\s*비데|티슈\s*캡형|"
    r"구매\s*후기|할인|특가|쿠폰|sponsored|광고|체험단|공구|공동구매)"
)

# 개인 공간 (공중 화장실 아님)
_PRIVATE_PLACE_RE = re.compile(
    r"(안방|본가|시골집|우리\s*집|친정|주공|.{1,3}동\s*\d+호|.{1,5}아파트|빌라|원룸|"
    r"자취방|사무실\s*비데|회사\s*비데|기숙사)"
)

# 너무 일반적인 단어들 (place_name 거부 리스트)
_GENERIC_PLACE_NAMES = {
    "공중화장실", "비데화장실", "비데 화장실", "비데", "화장실",
    "공중 화장실", "남자 화장실", "여자 화장실", "장애인 화장실",
    "어린이 화장실", "아이들 화장실", "엉 화장실", "겨울철 화장실",
    "공원 화장실", "고속도로 화장실", "지하철 역", "KTX 역", "공항",
    "공항 비데 화장실", "백화점 화장실", "카페 화장실", "마트 화장실",
}

# 진짜 장소 시그널 (이 패턴 매칭되어야 추출)
# 그룹1: "OO역/공항/터미널/휴게소/..." 형태
# 그룹2: 특정 지역 + 화장실
_SPECIFIC_PLACE_RE = re.compile(
    r"([가-힣A-Za-z0-9]{2,15}(?:역|공항|터미널|휴게소|백화점|마트|호텔|병원|대학교|"
    r"도서관|미술관|박물관|타워|광장|공원|시청|구청|아울렛|쇼핑몰|면세점))"
    r"|((?:강남|역삼|논현|신사|압구정|청담|홍대|상수|합정|망원|연남|연희|"
    r"신촌|이대|아현|충정로|시청|광화문|종로|종각|을지로|동대문|종묘|"
    r"명동|회현|남대문|서울역|용산|이태원|한남|녹사평|"
    r"잠실|건대|성수|왕십리|뚝섬|뚝도|구의|"
    r"여의도|영등포|당산|문래|"
    r"강서|발산|마곡|"
    r"안암|고려대|성북|혜화|동대문|길음|미아|"
    r"수원|성남|판교|분당|일산|인천|부천|"
    r"부산|대구|광주|대전|울산|세종|제주)"
    r"[가-힣A-Za-z0-9 ]{0,15}?(?:역|화장실|공원|광장|거리|로|길|동))"
)


def _extract_fallback(text: str) -> list[dict[str, Any]]:
    """API 키 없을 때의 룰베이스. 강화 버전.

    제외 조건:
      1. '비데' 자체가 없음
      2. 제품/광고 키워드 매칭
      3. 개인공간 키워드 매칭
      4. 구체적 장소명 패턴 미매칭
      5. 추출된 place_name 이 generic 리스트에 있음
    """
    if not _BIDET_RE.search(text):
        return []
    if _PRODUCT_BLACKLIST_RE.search(text):
        return []
    if _PRIVATE_PLACE_RE.search(text):
        return []

    m = _SPECIFIC_PLACE_RE.search(text)
    if not m:
        return []
    place_name = (m.group(1) or m.group(2) or "").strip()
    if not place_name:
        return []
    # 너무 일반적인 이름이거나 너무 짧으면 제외
    if place_name in _GENERIC_PLACE_NAMES:
        return []
    if len(place_name) < 4:
        return []
    # "비데"라는 단어가 그대로 place_name 안에 있으면 (제품 잔여) 제외
    if "비데" in place_name:
        return []

    has_bidet = not bool(_NEG_NEAR.search(text))
    idx = text.find("비데")
    excerpt = text[max(0, idx - 30): idx + 30].replace("\n", " ").strip()
    return [{
        "place_name": place_name,
        "address": None,
        "has_bidet": has_bidet,
        "evidence": excerpt[:80],
    }]


def extract_from_unprocessed(
    conn: sqlite3.Connection, limit: int = 500, *, use_llm: bool | None = None
) -> int:
    """unprocessed raw_documents 처리. 추출된 항목들을 locations/sources에 적재.

    Returns: 새로 적재된 location-source 쌍 개수.
    """
    if use_llm is None:
        use_llm = bool(ANTHROPIC_API_KEY)

    rows = fetch_unprocessed(conn, limit=limit)
    extract_fn = _extract_with_claude if use_llm else _extract_fallback
    pairs = 0

    for row in rows:
        try:
            extractions = extract_fn(row["content"])
        except Exception as exc:
            print(f"[extractor] doc#{row['id']} 추출 실패: {exc}")
            continue

        for ext in extractions:
            place_name = (ext.get("place_name") or "").strip()
            if not place_name:
                continue
            has_bidet = ext.get("has_bidet")
            has_bidet_int = (
                1 if has_bidet is True else (0 if has_bidet is False else None)
            )
            loc_id = upsert_location(
                conn,
                place_name=place_name,
                address=ext.get("address"),
                place_type=None,
                has_bidet=has_bidet_int,
            )
            add_source(
                conn,
                location_id=loc_id,
                source_type=row["source_type"],
                confidence=SOURCE_CONFIDENCE.get(row["source_type"], 50),
                raw_doc_id=row["id"],
                source_url=row["source_url"],
                excerpt=(ext.get("evidence") or "")[:200],
            )
            pairs += 1
        mark_processed(conn, row["id"])
        conn.commit()
    return pairs
