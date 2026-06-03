# 릴리즈 빌드 가이드

## 1. 키스토어 생성 (1회만)

```powershell
.\scripts\create_keystore.ps1
```

명령 실행 시 입력 받는 항목:
- **키스토어 비밀번호**: 적당히 강한 패스워드 (16자 이상 권장)
- **이름 / 조직 / 도시 / 도/특별시 / 국가코드 KR**
- **키 비밀번호**: 키스토어 비밀번호와 같게 해도 OK

생성된 파일: `keystore/bidet-release.jks`

> 🔐 **이 파일과 비밀번호 둘 다 안전한 곳에 백업.** 분실 = Play Store 업데이트 영구 불가.
> 백업 권장: 1Password, Bitwarden, 외장 SSD, 클라우드 암호화 폴더 등 **2곳 이상**.

## 2. keystore.properties 작성

```powershell
copy keystore.properties.example keystore.properties
```

`keystore.properties` 열어서:
```properties
storeFile=../keystore/bidet-release.jks
storePassword=실제_패스워드
keyAlias=bidet
keyPassword=실제_키_패스워드
```

## 3. 릴리즈 빌드

### AAB (Play Store 업로드용 — 권장)
```powershell
.\gradlew bundleRelease
```
결과: `app/build/outputs/bundle/release/app-release.aab`

### APK (직접 배포 / 사이드로드용)
```powershell
.\gradlew assembleRelease
```
결과: `app/build/outputs/apk/release/app-release.apk`

## 4. 빌드 검증

```powershell
# 서명 확인
keytool -printcert -jarfile app\build\outputs\bundle\release\app-release.aab

# APK 검증
.\gradlew lintRelease
```

## 5. Play Console 업로드 (Step 10)

1. https://play.google.com/console 가입 ($25 1회)
2. 앱 만들기 → 이름, 카테고리, 등급
3. **내부 테스트** 트랙으로 먼저 업로드 (즉시 반영, 테스터 이메일 등록)
4. 문제 없으면 **프로덕션** 트랙으로 출시

### 필수 항목 체크리스트
- [ ] 앱 이름, 짧은 설명 (80자), 자세한 설명 (4000자)
- [ ] 그래픽: 앱 아이콘 512x512, 피처 그래픽 1024x500
- [ ] 스크린샷 (폰 최소 2장, 1080x1920 권장)
- [ ] 카테고리: 도구 또는 여행 및 지역정보
- [ ] 콘텐츠 등급 설문
- [ ] **개인정보처리방침 URL** (Step 11)
- [ ] **데이터 보안 양식** (위치/이메일/사진 수집 명시)
- [ ] 대상 연령
- [ ] 광고 포함 여부

## 6. 심사 대기 (Step 12)

- 내부 테스트: 즉시
- 프로덕션 첫 출시: 보통 1~14일
- 업데이트: 보통 수시간~3일
- 반려 시 사유 보고 수정 후 재제출

## 트러블슈팅

### `signingConfig` 못 찾음
→ `keystore.properties` 파일이 루트에 있는지 확인.

### `keytool` 명령 없음
→ JDK 설치 필요. Android Studio가 설치한 JDK 경로 (예: `C:\Program Files\Android\Android Studio\jbr\bin`) 를 PATH에 추가.

### Play Store가 키 거부
→ `signingConfig`의 키 정보가 처음 업로드한 키와 다름. 처음 등록한 키로만 업데이트 가능.

### 빌드는 되는데 카카오맵이 안 뜸
→ `local.properties`에 `KAKAO_NATIVE_APP_KEY` 입력했는지 + 카카오 디벨로퍼에 릴리즈 키 해시도 등록했는지 확인.
디버그 키와 릴리즈 키 해시는 다름. 둘 다 등록 필요.

### 릴리즈 키 해시 확인
```powershell
keytool -exportcert -alias bidet -keystore keystore\bidet-release.jks `
  | openssl sha1 -binary | openssl base64
```
