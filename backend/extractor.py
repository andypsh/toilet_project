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
    # ```json 펜스 제거
    body = re.sub(r"^```(?:json)?\s*|\s*```$", "", body, flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return []
    return parsed.get("extractions", []) if isinstance(parsed, dict) else []


_BIDET_RE = re.compile(r"비데")
_NEG_NEAR = re.compile(r"비데[^\.。\n]{0,15}(없|안 ?있|미설치|미비|부재)")
_PLACE_HINT_RE = re.compile(
    r"([가-힣A-Za-z0-9 ]{2,30}?(?:화장실|휴게소|역|공항|백화점|마트|카페|호텔|병원|도서관|미술관|박물관|터미널))"
)


def _extract_fallback(text: str) -> list[dict[str, Any]]:
    """API 키 없을 때의 룰베이스. 보수적으로 — 장소 힌트+비데 키워드 동시 충족 시만."""
    if not _BIDET_RE.search(text):
        return []
    place_match = _PLACE_HINT_RE.search(text)
    if not place_match:
        return []
    has_bidet = not bool(_NEG_NEAR.search(text))
    # 근거 문장 = '비데' 기준 ±60자
    idx = text.find("비데")
    excerpt = text[max(0, idx - 30): idx + 30].replace("\n", " ").strip()
    return [{
        "place_name": place_match.group(1).strip(),
        "address": None,
        "has_bidet": has_bidet,
        "evidence": excerpt[:80],
    }]


def extract_from_unprocessed(
    conn: sqlite3.Connection, limit: int = 50, *, use_llm: bool | None = None
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
