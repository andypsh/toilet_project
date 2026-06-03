# 비데앱 (BidetApp)

전국 공중화장실 중 **비데가 설치된 곳**을 지도에 표시하는 안드로이드 앱.

## 폴더 트리 (프론트/백 구분)

```
toilet_project/
├── mobile/          ← 안드로이드 앱 (Kotlin + Jetpack Compose)
│   ├── app/
│   │   └── src/main/java/com/bidet/app/
│   │       ├── ui/         ★ 프론트엔드 영역 (UI/UX) — @dododo9511
│   │       ├── data/         백엔드 영역 — @andypsh
│   │       ├── domain/       백엔드 영역 — @andypsh
│   │       ├── di/           백엔드 영역 — @andypsh
│   │       └── util/         공유
│   ├── build.gradle.kts, settings.gradle.kts, gradle/, gradlew(.bat)
│   ├── local.properties.example
│   └── scripts/
│
├── backend/         ← 데이터 수집 파이프라인 (Python) — @andypsh 전담
│   ├── collectors/             (네이버 검색·공공데이터·사용자 제보)
│   ├── pipeline.py             (오케스트레이터 CLI)
│   ├── extractor.py            (LLM 추출, Claude API)
│   ├── geocoder.py             (카카오 로컬 API)
│   ├── firestore_adapter.py    (SQLite → Firestore Toilet 변환)
│   ├── firestore_upload.py     (firebase-admin 적재)
│   ├── seed_real.py            (실데이터 시드)
│   ├── update_coords.py        (좌표 보강)
│   ├── config.py, db.py, _console.py
│   ├── requirements.txt, .env.example
│   ├── locations.json          (현재 export)
│   └── firestore_toilets.json  (Firestore 적재 대기)
│
├── docs/            ← 공유 문서
├── BRANCHING.md     ← 브랜치 전략
├── CODEOWNERS       ← 코드 영역별 리뷰 자동 할당
└── progress.html    ← 진행 대시보드
```

## 역할 분담

| 사람 | 영역 | 디렉토리 |
|---|---|---|
| **@dododo9511 (프론트)** | UI/UX, Compose 화면, 디자인 | `mobile/app/src/main/java/com/bidet/app/ui/`, `mobile/app/src/main/res/` |
| **@andypsh (백)** | 데이터 수집 파이프라인, Repository/Firestore/UseCase | `backend/`, `mobile/app/src/main/java/com/bidet/app/{data,domain,di}/` |

자세한 브랜치 규칙은 [BRANCHING.md](BRANCHING.md). 리뷰는 [CODEOWNERS](CODEOWNERS)로 자동 할당.

## 스택

| 구분 | 기술 |
|---|---|
| **mobile** | Kotlin · Jetpack Compose (Material 3) · MVVM + Clean · Hilt · Retrofit/Moshi · Firebase (Firestore/Auth/Storage) · Kakao Map SDK |
| **backend** | Python 3.9+ · SQLite · requests · firebase-admin · anthropic SDK (선택) · Kakao Local API (선택) · 네이버 검색 API (선택) |

## 데이터 원칙
**팩트만 사용. 추론(카테고리/통계 기반) 금지.**
- ✅ 블로그/리뷰/SNS 명시적 언급, 공식 데이터, 정보공개청구, 사용자 제보
- ❌ "백화점이니까 비데 있을 것" 같은 카테고리 추정

## 빠른 시작

### 프론트 (mobile/)
```powershell
cd mobile
cp local.properties.example local.properties   # 카카오 키 채우기
# Android Studio에서 mobile/ 폴더 열기
./gradlew assembleDebug
```
자세한 셋업: [docs/SETUP.md](docs/SETUP.md)

### 백 (backend/)
```powershell
cd backend
pip install -r requirements.txt
cp .env.example .env                            # API 키 채우기 (선택)
python seed_real.py                             # 실데이터 14건 시드
python update_coords.py                         # 알려진 좌표 fill
python firestore_adapter.py                    # SQLite → Firestore JSON
python firestore_upload.py --dry-run           # 검증
python firestore_upload.py                     # 실제 적재 (service-account.json 필요)
```

## 진행 대시보드
[progress.html](progress.html) — 단계별 체크리스트 (브라우저로 열기)

## 문서
- [아키텍처](docs/ARCHITECTURE.md)
- [DB 스키마 (Firestore)](docs/DB_SCHEMA.md)
- [Firebase / Kakao 셋업](docs/SETUP.md)
- [릴리즈 빌드 가이드](docs/BUILD_RELEASE.md)
- [백엔드 데모 실행](docs/RUN_DEMO.md)
