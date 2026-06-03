# 셋업 가이드

## 1. Firebase 프로젝트 생성

1. https://console.firebase.google.com 접속
2. **프로젝트 추가** → 이름: `bidet-app`
3. 안드로이드 앱 추가
   - 패키지명: `com.bidet.app`
   - 앱 닉네임: 비데앱
   - 디버그 서명 인증서 SHA-1: 아래 명령으로 확인
     ```
     keytool -list -v -alias androiddebugkey -keystore "%USERPROFILE%\.android\debug.keystore" -storepass android -keypass android
     ```
4. `google-services.json` 다운로드 → `app/` 폴더에 배치
5. 콘솔에서 활성화:
   - **Firestore Database** → 서울(`asia-northeast3`) 리전, 프로덕션 모드
   - **Authentication** → 이메일/구글/카카오(OIDC) 활성화
   - **Storage** → 서울 리전

## 2. 카카오 디벨로퍼 등록

1. https://developers.kakao.com 접속
2. **내 애플리케이션** → 추가
3. **앱 키**에서 발급:
   - **네이티브 앱 키** → `local.properties`의 `KAKAO_NATIVE_APP_KEY`
   - **REST API 키** → `local.properties`의 `KAKAO_REST_API_KEY`
4. **플랫폼 등록** → Android
   - 패키지명: `com.bidet.app`
   - 키 해시 (디버그):
     ```
     keytool -exportcert -alias androiddebugkey -keystore "%USERPROFILE%\.android\debug.keystore" -storepass android -keypass android | openssl sha1 -binary | openssl base64
     ```
5. **카카오 로그인** 활성화 (Profile/Email)
6. **지도 SDK** → "지도 사용 신청" (필수)

## 3. 로컬 설정

```powershell
copy local.properties.example local.properties
```
`local.properties` 열어서 키 채우기 + Android SDK 경로 수정.

`google-services.json` 을 `app/` 폴더에 배치.

## 4. Android Studio 열기

1. Android Studio (Jellyfish 이상) 실행
2. **Open** → 본 프로젝트 폴더 선택
3. **Gradle Sync** 자동 실행 — 실패 시 [Gradle Wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html) 추가 필요
   ```
   gradle wrapper --gradle-version 8.9
   ```
4. **Run 'app'** → 디버그 빌드 확인

## 5. 다음 단계 (별도 프롬프트)

- DB 스키마 적용 + 시드 데이터 적재 (`docs/DB_SCHEMA.md` 참조)
- 카카오맵 SDK 실제 통합 (`MapScreen.kt` 의 TODO)
- 카카오/구글 로그인 실제 구현 (`AuthScreen.kt` 의 TODO)
- 위치 권한 + FusedLocationProvider 연결

## Gradle Wrapper 추가 (최초 1회)

루트에 Gradle이 설치되어 있어야 함. 아니면 Android Studio의 임베디드 Gradle 사용.
```powershell
gradle wrapper --gradle-version 8.9 --distribution-type all
```
또는 Android Studio에서 프로젝트 열면 자동 생성됨.
