"""네이버 검색 API (블로그/카페) 수집기.

ToS 안전한 공식 API. 키워드로 검색해서 'description' (요약문)을 raw_documents에 적재.
"""
from __future__ import annotations

import html
import re
import sqlite3
from typing import Iterable

import requests

from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from db import insert_raw_document


NAVER_ENDPOINT = "https://openapi.naver.com/v1/search/{kind}.json"
_TAG_RE = re.compile(r"<[^>]+>")


def _strip(s: str) -> str:
    return _TAG_RE.sub("", html.unescape(s or "")).strip()


def _search(query: str, kind: str, display: int, start: int) -> list[dict]:
    if not (NAVER_CLIENT_ID and NAVER_CLIENT_SECRET):
        raise RuntimeError(
            "NAVER_CLIENT_ID/SECRET 미설정. .env 채우거나 다른 수집기 사용."
        )
    resp = requests.get(
        NAVER_ENDPOINT.format(kind=kind),
        headers={
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        },
        params={"query": query, "display": display, "start": start, "sort": "sim"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("items", [])


def collect_naver_search(
    conn: sqlite3.Connection,
    queries: Iterable[str],
    *,
    kinds: tuple[str, ...] = ("blog", "cafearticle"),
    per_query: int = 30,
) -> int:
    """주어진 쿼리들로 블로그/카페 검색해서 raw_documents에 적재.

    Returns: 새로 적재된 문서 수.
    """
    added = 0
    for query in queries:
        for kind in kinds:
            # API는 1-base, max display=100
            for start in range(1, per_query + 1, 100):
                display = min(100, per_query - start + 1)
                if display <= 0:
                    break
                items = _search(query, kind, display, start)
                for item in items:
                    text = f"{_strip(item.get('title', ''))}\n{_strip(item.get('description', ''))}"
                    src = "naver_blog" if kind == "blog" else "naver_cafe"
                    rid = insert_raw_document(
                        conn,
                        source_type=src,
                        content=text,
                        source_url=item.get("link"),
                        title=_strip(item.get("title", "")),
                    )
                    if rid:
                        added += 1
                if not items:
                    break
        conn.commit()
    return added
