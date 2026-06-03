# 데모 모드 실행 가이드

빌드 끝났어요. `app\build\outputs\apk\debug\app-debug.apk` 만들어진 상태.

이제 폰이나 에뮬레이터에 설치해서 실행하면 됩니다.

## 옵션 A: 본인 폰에 USB로 설치 (제일 빠름, 추천)

### 1단계: 폰에서 USB 디버깅 켜기
1. 설정 → 휴대전화 정보 → **빌드 번호** 7번 연타 → 개발자 모드 활성화
2. 설정 → 개발자 옵션 → **USB 디버깅** ON
3. 폰을 PC에 USB로 연결
4. 폰에 뜨는 "USB 디버깅을 허용하시겠습니까?" 팝업에서 **허용**

### 2단계: 연결 확인 + 설치
```powershell
cd "C:\Users\andyp\Desktop\고려대\비데앱"
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices
# 폰 시리얼이 보여야 함

& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install app\build\outputs\apk\debug\app-debug.apk
```

설치 후 폰에서 **"비데앱 (debug)"** 아이콘 실행.

## 옵션 B: 에뮬레이터로 실행

### 시스템 이미지 다운로드 (1회만, 1~2GB)
```powershell
$sdk = "$env:LOCALAPPDATA\Android\Sdk"
& "$sdk\cmdline-tools\latest\bin\sdkmanager.bat" "system-images;android-34;google_apis;x86_64"
```
> cmdline-tools가 없으면 Android Studio → SDK Manager → SDK Tools 탭에서 "Android SDK Command-line Tools (latest)" 체크해서 설치.

### AVD 생성
Android Studio에서 하는 게 훨씬 편함:
1. Android Studio 실행
2. 우상단 **Device Manager** 아이콘
3. **Create Device** → Pixel 7 선택 → API 34 (UpsideDownCake) 선택
4. Finish → 에뮬레이터 시작

### 설치
에뮬레이터 켜진 상태에서 같은 명령:
```powershell
.\gradlew.bat installDebug
```

## 옵션 C: Android Studio에서 그냥 Run

가장 정석:
1. Android Studio 열기
2. **Open** → `C:\Users\andyp\Desktop\고려대\비데앱` 선택
3. Gradle Sync 대기 (이미 wrapper 있어서 빠름)
4. 폰 연결 or AVD 실행
5. 상단 ▶️ Run 버튼

---

## 데모 모드에서 볼 수 있는 것

✅ **카카오맵 키 없어도** 앱 실행됨 (Fallback: 화장실 카드 리스트 화면)
✅ **고려대 안암동 주변 10개 화장실** 더미 데이터 표시
- 중앙도서관, SK미래관, 정경관, 안암역, 스타벅스 안암역점,
  GS25, 안암병원, 롯데마트 청량리, 성북구청, 시립대도서관
✅ 화장실 클릭 → 상세화면 (출처/평점/길찾기/리뷰)
✅ 리뷰 작성 (메모리에만 저장, 재시작하면 사라짐)
✅ 즐겨찾기 토글
✅ 제보 폼 (메모리에만 저장)

❌ **로그인은 동작 안 함** (Firebase 안 붙어있으니까 — 데모 모드)
❌ **검색 화면**은 Firestore 인덱스 필요해서 동작 안 할 수도 있음
❌ **지도는 카카오 키 없으면 표시 안 됨** (대신 카드 리스트 fallback)

## 카카오맵까지 보고 싶으면

`local.properties`의 `KAKAO_NATIVE_APP_KEY=`에 실제 키 입력만 하면 됨.
키 발급은 [docs/SETUP.md](SETUP.md)의 카카오 디벨로퍼 등록 부분 참조.

## 진짜 모드로 전환

`app/google-services.json` 파일을 받아서 `app/` 폴더에 넣으면 **자동으로 데모 모드 꺼지고 Firebase 모드로 빌드됨** (build.gradle.kts가 파일 존재 여부로 자동 분기).

---

## 빌드 다시 하기

코드 수정했을 때:
```powershell
.\gradlew.bat assembleDebug
# 또는 폰 연결된 상태면 바로 설치까지:
.\gradlew.bat installDebug
```

처음엔 1~2분, 두번째부터는 캐시 덕분에 10~30초.

## 문제 생기면

- **빌드 실패**: `.\gradlew.bat clean` 후 다시 빌드
- **앱 충돌**: `adb logcat` 으로 로그 확인
- **APK 너무 큼 (60MB)**: 데모용이라 minify 안 함. release 빌드 (Step 9) 하면 15~25MB로 줄어듦
