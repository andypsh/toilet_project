"""임시 상태 확인 스크립트."""
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

c = sqlite3.connect("bidet.db")

print("=== 카운트 ===")
print(f"locations: {c.execute('select count(*) from locations').fetchone()[0]}")
print(f"좌표 있음: {c.execute('select count(*) from locations where latitude is not null').fetchone()[0]}")
print(f"좌표 없음: {c.execute('select count(*) from locations where latitude is null').fetchone()[0]}")

print("\n=== 좌표 있는 locations (지도 표시 가능) ===")
for r in c.execute("""
    select id, place_name, address, latitude, longitude, has_bidet
    from locations
    where latitude is not null
    order by id
"""):
    bidet = "✓" if r[5] == 1 else ("✗" if r[5] == 0 else "?")
    print(f"  #{r[0]:3} [{bidet}] {r[1]}")
    if r[2]: print(f"        주소: {r[2]}")
    print(f"        ({r[3]}, {r[4]})")

print("\n=== 좌표 없는 locations (매칭 실패) ===")
for r in c.execute("""
    select id, place_name from locations
    where latitude is null
    order by id
"""):
    print(f"  #{r[0]:3} {r[1]}")

print("\n=== seoul_master 카테고리 통계 ===")
print("총 seoul_master:", c.execute('select count(*) from seoul_master').fetchone()[0])
print("좌표 있는 seoul_master:", c.execute('select count(*) from seoul_master where latitude is not null').fetchone()[0])
print("\n시설 카테고리 분포 (이름 끝 단어):")
for r in c.execute("""
    select case
        when name like '%역%' then '역'
        when name like '%공원%' then '공원'
        when name like '%광장%' then '광장'
        when name like '%마을%' then '마을'
        when name like '%산%' then '산'
        when name like '%주차장%' then '주차장'
        when name like '%휴게소%' then '휴게소'
        else '기타'
    end as cat, count(*)
    from seoul_master
    group by cat
    order by count(*) desc
"""):
    print(f"  {r[0]}: {r[1]}")
