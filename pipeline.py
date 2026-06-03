"""파이프라인 오케스트레이터.

전체 흐름:
    [수집] collectors/* → raw_documents (+ 공공데이터는 locations 직접)
        ↓
    [정제] extractor → LLM/룰베이스로 raw_documents 에서 추출 → locations + sources
        ↓
    [좌표화] geocoder → locations.lat/lon 보강
        ↓
    [표시] export → 앱에서 쓸 JSON 산출

CLI 사용:
    python pipeline.py init                 # DB 초기화만
    python pipeline.py collect-naver "키워드1" "키워드2"
    python pipeline.py collect-public       # 공공데이터 수집
    python pipeline.py extract              # raw → locations
    python pipeline.py geocode              # 주소 → 좌표
    python pipeline.py export               # 앱용 JSON 출력
    python pipeline.py run "키워드"         # 위 단계 전부 실행
"""
from __future__ import annotations

import _console  # noqa: F401

import argparse
import json
import sys
from pathlib import Path

from collectors import collect_naver_search, collect_public_toilet, collect_user_report
from db import connect, init_db
from extractor import extract_from_unprocessed
from geocoder import geocode_missing


def cmd_init(_: argparse.Namespace) -> None:
    init_db()
    print("[init] DB 초기화 완료.")


def cmd_collect_naver(args: argparse.Namespace) -> None:
    init_db()
    with connect() as conn:
        added = collect_naver_search(conn, args.queries, per_query=args.per_query)
    print(f"[naver] 새 raw_documents {added}건 적재.")


def cmd_collect_public(args: argparse.Namespace) -> None:
    init_db()
    with connect() as conn:
        added = collect_public_toilet(conn, max_pages=args.pages)
    print(f"[public] locations {added}건 적재 (비데설치=Y).")


def cmd_collect_user(args: argparse.Namespace) -> None:
    init_db()
    with connect() as conn:
        loc_id = collect_user_report(
            conn,
            place_name=args.place_name,
            address=args.address,
            has_bidet=not args.no_bidet,
            user_id=args.user_id,
            note=args.note,
        )
    print(f"[user] location id={loc_id} 적재.")


def cmd_extract(args: argparse.Namespace) -> None:
    with connect() as conn:
        n = extract_from_unprocessed(conn, limit=args.limit)
    print(f"[extract] {n}개의 location-source 쌍 생성.")


def cmd_geocode(args: argparse.Namespace) -> None:
    with connect() as conn:
        n = geocode_missing(conn, batch=args.batch)
    print(f"[geocode] {n}건 좌표 보강.")


def cmd_export(args: argparse.Namespace) -> None:
    """앱이 바로 소비할 형태로 locations + 출처 목록을 한 JSON에 묶어 출력."""
    out_path = Path(args.out)
    with connect() as conn:
        locs = conn.execute("""
            SELECT id, place_name, address, latitude, longitude,
                   place_type, has_bidet, confidence
            FROM locations
            WHERE has_bidet = 1
            ORDER BY confidence DESC, id
        """).fetchall()
        data = []
        for r in locs:
            row = dict(r)
            srcs = conn.execute("""
                SELECT source_type, source_url, excerpt, confidence
                FROM sources WHERE location_id = ?
                ORDER BY confidence DESC
            """, (r["id"],)).fetchall()
            row["sources"] = [dict(s) for s in srcs]
            data.append(row)
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[export] {len(data)}개 location → {out_path}")


def cmd_run(args: argparse.Namespace) -> None:
    """수집→정제→좌표화→내보내기 한번에."""
    init_db()
    with connect() as conn:
        if args.queries:
            try:
                naver_added = collect_naver_search(conn, args.queries, per_query=args.per_query)
                print(f"[naver] +{naver_added}")
            except Exception as exc:
                print(f"[naver] 스킵: {exc}")
        try:
            public_added = collect_public_toilet(conn, max_pages=args.pages)
            print(f"[public] +{public_added}")
        except Exception as exc:
            print(f"[public] 스킵: {exc}")
        pairs = extract_from_unprocessed(conn, limit=args.extract_limit)
        print(f"[extract] +{pairs} location-source 쌍")
        geo = geocode_missing(conn, batch=args.batch)
        print(f"[geocode] +{geo}")
    cmd_export(args)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="비데앱 데이터 수집 파이프라인")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)

    sp = sub.add_parser("collect-naver")
    sp.add_argument("queries", nargs="+")
    sp.add_argument("--per-query", type=int, default=30)
    sp.set_defaults(func=cmd_collect_naver)

    sp = sub.add_parser("collect-public")
    sp.add_argument("--pages", type=int, default=5)
    sp.set_defaults(func=cmd_collect_public)

    sp = sub.add_parser("collect-user")
    sp.add_argument("--place-name", required=True)
    sp.add_argument("--address", default=None)
    sp.add_argument("--user-id", default=None)
    sp.add_argument("--note", default=None)
    sp.add_argument("--no-bidet", action="store_true", help="비데 없음 제보")
    sp.set_defaults(func=cmd_collect_user)

    sp = sub.add_parser("extract")
    sp.add_argument("--limit", type=int, default=50)
    sp.set_defaults(func=cmd_extract)

    sp = sub.add_parser("geocode")
    sp.add_argument("--batch", type=int, default=50)
    sp.set_defaults(func=cmd_geocode)

    sp = sub.add_parser("export")
    sp.add_argument("--out", default="locations.json")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("run")
    sp.add_argument("queries", nargs="*",
                    help="네이버 검색 키워드 (없으면 네이버 단계 스킵)")
    sp.add_argument("--per-query", type=int, default=30)
    sp.add_argument("--pages", type=int, default=5)
    sp.add_argument("--extract-limit", type=int, default=200)
    sp.add_argument("--batch", type=int, default=50)
    sp.add_argument("--out", default="locations.json")
    sp.set_defaults(func=cmd_run)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
