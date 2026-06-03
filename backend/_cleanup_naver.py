"""기존 네이버 출처 노이즈 정리.

1. naver_blog/naver_cafe 출처의 sources 모두 삭제
2. 소속 sources가 모두 사라진 locations 삭제 (고립 위치)
3. naver_blog/naver_cafe raw_documents 의 mark_processed 리셋
   → 재추출 시 강화된 룰로 다시 시도

기존 휴게소 등 'news'/'official_site' 출처 데이터는 보존.
"""
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

c = sqlite3.connect("bidet.db")
cur = c.cursor()

# Before
before_loc = cur.execute("select count(*) from locations").fetchone()[0]
before_src = cur.execute("select count(*) from sources").fetchone()[0]

# 1) 네이버 출처 sources 삭제
deleted_src = cur.execute(
    "delete from sources where source_type in ('naver_blog', 'naver_cafe')"
).rowcount
print(f"sources 삭제 (naver): {deleted_src}")

# 2) sources가 0인 locations 삭제 (고립)
deleted_loc = cur.execute("""
    delete from locations
    where id not in (select distinct location_id from sources)
""").rowcount
print(f"고립 locations 삭제: {deleted_loc}")

# 3) naver raw_documents mark_processed 리셋 (재추출 가능하게)
reset = cur.execute("""
    update raw_documents set processed = 0
    where source_type in ('naver_blog', 'naver_cafe')
""").rowcount
print(f"raw_documents 재처리 마킹: {reset}")

c.commit()

# After
after_loc = cur.execute("select count(*) from locations").fetchone()[0]
after_src = cur.execute("select count(*) from sources").fetchone()[0]

print()
print(f"=== 정리 결과 ===")
print(f"locations: {before_loc} → {after_loc}")
print(f"sources:   {before_src} → {after_src}")
