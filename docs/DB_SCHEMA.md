# Firestore DB 스키마 명세 (다음 프롬프트에서 구현)

이 문서는 **다음 프롬프트에서 DB를 구성할 때 따라야 할 명세서**. 앱 코드의 `data/model/*.kt` 와 1:1 매칭됨.

---

## 컬렉션 4개

### 1. `toilets/{toiletId}`
화장실 정보 (앱의 메인 데이터)

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string (auto) | 문서 ID |
| `name` | string | 장소명 (예: "신촌 스타벅스 2호점") |
| `address` | string | 도로명 주소 |
| `lat` | double | 위도 |
| `lng` | double | 경도 |
| `geohash` | string (9자) | 지오해시 (반경 쿼리용) |
| `category` | string | enum: `PUBLIC`, `DEPARTMENT_STORE`, `MART`, `CAFE` 등 |
| `hasBidet` | bool | 비데 보유 여부 (반드시 true인 경우만 표시) |
| `bidetVerified` | bool | 검증된 팩트 여부 (사용자 2명 이상 확인 또는 공식자료) |
| `bidetCount` | int | 비데 개수 (선택) |
| `gender` | string | enum: `MEN_ONLY`, `WOMEN_ONLY`, `BOTH`, `UNISEX`, `UNKNOWN` |
| `accessible` | bool | 장애인용 |
| `openHours` | string? | 운영시간 (텍스트) |
| `is24h` | bool | 24시간 운영 |
| `isFree` | bool | 무료 여부 |
| `rating` | double | 평균 평점 (0~5) |
| `reviewCount` | int | 리뷰 수 |
| `photoUrls` | array<string> | Storage URL |
| `sources` | array<object> | **데이터 출처 (팩트 추적용, 필수)** |
| `createdAt` | long | epoch ms |
| `updatedAt` | long | epoch ms |

`sources[]` 객체:
```json
{
  "type": "BLOG_REVIEW",
  "url": "https://blog.naver.com/xxx",
  "description": "2024-03 방문, 비데 있다고 명시",
  "collectedAt": 1709123456789
}
```
`type` enum: `PUBLIC_DATA`, `OFFICIAL_WEBSITE`, `BLOG_REVIEW`, `MAP_REVIEW`, `USER_REPORT`, `INFORMATION_DISCLOSURE`, `UNKNOWN`

**인덱스 필요:**
- `hasBidet ASC, geohash ASC` (반경 검색)
- `hasBidet ASC, name ASC` (이름 검색)
- `hasBidet ASC, category ASC, geohash ASC` (필터+반경)

---

### 2. `reviews/{reviewId}`
사용자 리뷰

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string (auto) | |
| `toiletId` | string | 참조 |
| `userId` | string | uid |
| `userName` | string | 닉네임 (denormalized) |
| `rating` | int (1~5) | 평점 |
| `cleanliness` | int (1~5) | 청결도 |
| `bidetWorks` | bool | 비데 작동함? |
| `comment` | string | 코멘트 |
| `photoUrls` | array<string> | |
| `createdAt` | long | |

**인덱스:** `toiletId ASC, createdAt DESC`

---

### 3. `users/{uid}`
사용자

| 필드 | 타입 | 설명 |
|---|---|---|
| `uid` | string | Firebase Auth uid |
| `nickname` | string | |
| `email` | string? | |
| `photoUrl` | string? | |
| `provider` | string | "google.com", "kakao.com" 등 |
| `reportCount` | int | 누적 제보 수 |
| `reviewCount` | int | 누적 리뷰 수 |
| `favoriteToiletIds` | array<string> | 즐겨찾기 |
| `createdAt` | long | |

---

### 4. `reports/{reportId}`
사용자 제보 (검토 후 toilets로 머지)

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string (auto) | |
| `toiletId` | string? | 기존 화장실 업데이트인 경우 |
| `userId` | string | |
| `type` | string | enum: `NEW_TOILET`, `BIDET_STATUS_UPDATE`, `INCORRECT_INFO`, `PERMANENTLY_CLOSED` |
| `name` | string | |
| `address` | string | |
| `lat` | double | |
| `lng` | double | |
| `hasBidet` | bool | |
| `description` | string | |
| `photoUrls` | array<string> | |
| `status` | string | enum: `PENDING`, `APPROVED`, `REJECTED`, `MERGED` |
| `createdAt` | long | |

**인덱스:** `status ASC, createdAt DESC`

---

## Firestore 보안 규칙 (제안)

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // 화장실: 누구나 읽기, 쓰기는 관리자만
    match /toilets/{id} {
      allow read: if true;
      allow write: if request.auth != null
        && request.auth.token.admin == true;
    }

    // 리뷰: 누구나 읽기, 본인만 쓰기
    match /reviews/{id} {
      allow read: if true;
      allow create: if request.auth != null
        && request.resource.data.userId == request.auth.uid;
      allow update, delete: if request.auth != null
        && resource.data.userId == request.auth.uid;
    }

    // 유저: 본인만
    match /users/{uid} {
      allow read, write: if request.auth != null
        && request.auth.uid == uid;
    }

    // 제보: 로그인 사용자 누구나 생성, 본인 것만 읽기, 관리자 수정
    match /reports/{id} {
      allow create: if request.auth != null
        && request.resource.data.userId == request.auth.uid
        && request.resource.data.status == "PENDING";
      allow read: if request.auth != null
        && (resource.data.userId == request.auth.uid
            || request.auth.token.admin == true);
      allow update: if request.auth.token.admin == true;
    }
  }
}
```

---

## 초기 데이터 구성 절차 (다음 프롬프트용 체크리스트)

다음 프롬프트에서 진행:
1. Firebase 프로젝트 생성 → Firestore 활성화 (asia-northeast3 = 서울)
2. 컬렉션 4개 위 스키마대로 생성
3. 인덱스 명시 (자동 + 복합 인덱스)
4. 보안 규칙 위 내용으로 배포
5. 시드 데이터: 한국도로공사 휴게소(비데 명시 데이터)부터 적재
6. 적재 스크립트는 별도 (Python/Node) — 모든 레코드에 `sources[]` 반드시 채울 것
