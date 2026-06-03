# 아키텍처

## 레이어 구조

```
┌──────────────── UI Layer (Compose) ────────────────┐
│  Screens (Map, Detail, Search, Report, Profile)    │
│   ↕                                                │
│  ViewModels (StateFlow<UiState>)                   │
└────────────────────────┬───────────────────────────┘
                         │ 호출
┌────────────────── Domain Layer ────────────────────┐
│  UseCases (GetNearby, GetDetail, Search, Submit)   │
└────────────────────────┬───────────────────────────┘
                         │ 호출
┌─────────────────── Data Layer ─────────────────────┐
│  Repository (인터페이스) ← Impl                    │
│   ↕                                                │
│  Remote Sources:                                   │
│   - FirestoreSource  (DB)                          │
│   - FirebaseAuthSource  (로그인)                   │
│   - FirebaseStorageSource (사진)                   │
│   - KakaoLocalApi (Retrofit, 주소/POI 검색)        │
└────────────────────────────────────────────────────┘
```

## DI(Hilt) 구성
- `FirebaseModule` — Firestore/Auth/Storage 제공
- `RepositoryModule` — Repository 인터페이스 ↔ Impl 바인딩
- `NetworkModule` — OkHttp/Retrofit/KakaoLocalApi 제공
- `@HiltViewModel` 로 ViewModel에 UseCase 주입
- `@AndroidEntryPoint` 로 Activity에 DI 활성

## 네비게이션
- `BidetNavGraph` 에 Routes 정의
- 시작 화면: `MapScreen`
- 화면: Map → Search/Detail/Report/Profile → Auth

## 화면별 흐름

### MapScreen
1. 위치 권한 요청 (TODO)
2. FusedLocationProviderClient로 현위치 획득
3. `MapViewModel.loadNearby(lat,lng)` 호출
4. Firestore에서 geohash 범위로 비데 화장실 조회
5. KakaoMap에 마커 표시 (TODO)

### ToiletDetailScreen
1. `toiletId` 받아서 상세 + 리뷰 로드
2. 출처(`DataSource`) 명시 표시 — 팩트 검증 목적
3. 길찾기 버튼 (TODO: 카카오맵/티맵 인텐트)

### ReportScreen
1. 사용자가 새 비데 화장실 제보
2. 사진 첨부 → Storage 업로드 → URL 저장
3. `reports` 컬렉션에 PENDING 상태로 추가
4. Cloud Function 또는 관리자가 검토 후 `toilets`로 머지 (TODO)

## 데이터 수집 파이프라인 (외부, 별도 구현)
앱 자체에 포함 안 됨. 별도 도구로 운영:
- 네이버 검색 API → 블로그/카페 글 수집
- 카카오/네이버 지도 리뷰 크롤링
- LLM으로 "장소명 + 비데 유무 + 출처" 추출
- 공공데이터/도로공사/공항/지하철 데이터 파싱
- 결과를 Firestore `toilets` 컬렉션에 적재
- 모든 레코드에 `sources[]` 필수 → 팩트 추적 가능

## 보안 / API 키
- `local.properties` 에서 카카오 키 읽음 (커밋 X)
- `google-services.json` 도 커밋 X
- Firestore 보안 규칙은 `docs/DB_SCHEMA.md` 참조
