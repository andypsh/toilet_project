# 비데앱 (BidetApp)

전국 공중화장실 중 **비데가 설치된 곳**을 지도에 표시하는 안드로이드 앱.

## 스택
- **Android**: Kotlin + Jetpack Compose (Material 3)
- **Architecture**: MVVM + Clean Architecture (UI → Domain → Data)
- **DI**: Hilt
- **Backend**: Firebase (Firestore, Auth, Storage)
- **Map**: Kakao Map SDK + Kakao Local REST API
- **Async**: Coroutines + Flow
- **Network**: Retrofit + Moshi

## 데이터 원칙
**팩트만 사용. 추론(카테고리/통계 기반) 금지.**
- ✅ 블로그/리뷰/SNS 명시적 언급, 공식 데이터, 정보공개청구, 사용자 제보
- ❌ "백화점이니까 있을것" 같은 카테고리 추정

## 👥 협업
- 브랜치 전략: [BRANCHING.md](BRANCHING.md)
- @andypsh → `feature_andy` / @dododo9511 → `feature_dodo` → `dev` → `main`

## 진행 대시보드
[progress.html](progress.html) — 1~12 단계 체크리스트 (브라우저로 열어보세요)

## 문서
- [아키텍처](docs/ARCHITECTURE.md)
- [DB 스키마 (Firestore)](docs/DB_SCHEMA.md) — 별도 프롬프트에서 구현
- [Firebase / Kakao 셋업](docs/SETUP.md)
- [릴리즈 빌드 가이드](docs/BUILD_RELEASE.md)

## 다음 단계
1. `docs/SETUP.md` 따라 Firebase 프로젝트 생성 + 카카오 키 발급
2. `local.properties.example` → `local.properties` 복사 후 키 입력
3. `google-services.json` 다운받아 `app/` 폴더에 배치
4. DB 스키마(`docs/DB_SCHEMA.md`) 따라 Firestore 구성 — **별도 프롬프트에서 진행**
5. Android Studio에서 열고 Gradle sync
