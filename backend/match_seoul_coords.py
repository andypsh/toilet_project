"""locations.place_name과 seoul_master.name 매칭해서 좌표 보강.

매칭 방법:
1. 정확 매칭 (place_name == seoul_master.name)
2. 토큰 부분 매칭 (place_name의 핵심 토큰이 seoul_master.name에 포함)
3. 역명 매칭 (place_name이 "OO역 ..." 형태일 때 seoul_master에서 "OO역" 찾기)

좌표가 이미 있는 locations은 스킵.
seoul_master에서 매칭된 row의 도로명 주소도 같이 채움.
"""
from __future__ import annotations

import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

c = sqlite3.connect("bidet.db")
cur = c.cursor()

# 좌표 누락된 locations 가져오기
missing = cur.execute("""
    select id, place_name from locations
    where latitude is null or longitude is null
""").fetchall()

print(f"좌표 누락 locations: {len(missing)}건")

# seoul_master 전부 메모리에 로드 (4,976건이라 부담 없음)
master = cur.execute("""
    select id, name, road_address, jibun_address, latitude, longitude
    from seoul_master
    where latitude is not null and longitude is not null
""").fetchall()
print(f"seoul_master 좌표 보유: {len(master)}건")

# 인덱스: name → row
master_by_name = {row[1]: row for row in master}

# 토큰화 (간단)
def tokens(s: str) -> set[str]:
    """공백 + 특수문자 분리. 2자 이상 토큰만 유효."""
    out = set()
    for tok in re.split(r"[\s,()/·\-]+", s or ""):
        tok = tok.strip()
        if len(tok) >= 2 and not tok.isdigit():
            out.add(tok)
    return out

# 역명 추출 (예: "1·2호선 시청역 장애인화장실" → "시청역")
STATION_RE = re.compile(r"([가-힣A-Za-z0-9]{2,}역)")
HUGE_RE = re.compile(r"([가-힣A-Za-z0-9 ]{2,15}휴게소)")


matched_exact = 0
matched_station = 0
matched_token = 0
unmatched = []

for loc_id, place_name in missing:
    found = None

    # 1) 정확 매칭
    if place_name in master_by_name:
        found = master_by_name[place_name]
        matched_exact += 1

    # 2) 역명 추출 후 매칭
    if not found:
        sm = STATION_RE.search(place_name or "")
        if sm:
            station = sm.group(1)
            # seoul_master에서 이 역명 포함하는 거 찾기
            for m in master:
                if station in m[1]:
                    found = m
                    matched_station += 1
                    break

    # 3) 토큰 매칭 (place_name의 토큰이 seoul_master.name 에 모두 포함)
    if not found:
        loc_tokens = tokens(place_name)
        # 흔한 토큰 제외 (화장실, 비데 등)
        loc_tokens -= {"화장실", "비데", "남자", "여자", "장애인",
                       "어린이", "가족", "공중", "공중화장실"}
        if len(loc_tokens) >= 1:
            for m in master:
                m_tokens = tokens(m[1])
                if loc_tokens.issubset(m_tokens):
                    found = m
                    matched_token += 1
                    break

    if found:
        _, _, road_addr, jibun_addr, lat, lng = found
        addr = road_addr or jibun_addr
        cur.execute("""
            update locations
            set latitude = ?, longitude = ?, address = coalesce(address, ?),
                updated_at = datetime('now')
            where id = ?
        """, (lat, lng, addr, loc_id))
    else:
        unmatched.append((loc_id, place_name))

c.commit()

# After
has_coords_after = cur.execute(
    "select count(*) from locations where latitude is not null"
).fetchone()[0]

print()
print("=== 매칭 결과 ===")
print(f"정확 매칭:   {matched_exact}")
print(f"역명 매칭:   {matched_station}")
print(f"토큰 매칭:   {matched_token}")
print(f"매칭 실패:   {len(unmatched)}")
print()
print(f"좌표 있는 locations: {has_coords_after}건")
print()
print("=== 매칭 실패 샘플 (수동 확인용) ===")
for loc_id, name in unmatched[:10]:
    print(f"  #{loc_id}: {name}")
