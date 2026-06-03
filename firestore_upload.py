"""firebase-admin 으로 Firestore `toilets` 컬렉션에 적재.

사용:
    pip install firebase-admin
    # Firebase Console → 프로젝트 설정 → 서비스 계정 → '새 비공개 키 생성'
    # 받은 JSON 을 service-account.json 으로 프로젝트 루트에 저장
    python firestore_upload.py

옵션:
    python firestore_upload.py --json firestore_toilets.json --key service-account.json --dry-run
"""
from __future__ import annotations

import _console  # noqa: F401

import argparse
import json
import sys
from pathlib import Path


def main(json_path: str, key_path: str, dry_run: bool) -> int:
    docs_path = Path(json_path)
    if not docs_path.exists():
        print(f"[upload] {json_path} 없음 — 먼저 `python firestore_adapter.py` 실행")
        return 1
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    print(f"[upload] {len(docs)}개 doc 적재 준비")

    if dry_run:
        print("[upload] dry-run — 적재 SKIP")
        return 0

    key = Path(key_path)
    if not key.exists():
        print(
            f"[upload] {key_path} 없음.\n"
            f"  Firebase Console → 프로젝트 설정 → 서비스 계정 → '새 비공개 키 생성' 후 저장.\n"
            f"  또는 --dry-run 으로 적재 없이 검증만 가능."
        )
        return 1

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        print("[upload] firebase-admin 미설치. `pip install firebase-admin` 후 재실행.")
        return 1

    cred = credentials.Certificate(str(key))
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    batch = db.batch()
    col = db.collection("toilets")
    for i, d in enumerate(docs, 1):
        doc_id = d.pop("id")
        batch.set(col.document(doc_id), d)
        if i % 400 == 0:  # Firestore batch limit = 500
            batch.commit()
            batch = db.batch()
            print(f"[upload] {i}건 커밋")
    batch.commit()
    print(f"[upload] 총 {len(docs)}건 toilets 컬렉션 적재 완료")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--json", default="firestore_toilets.json")
    p.add_argument("--key",  default="service-account.json")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    sys.exit(main(args.json, args.key, args.dry_run))
