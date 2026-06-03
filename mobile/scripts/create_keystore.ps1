# 비데앱 릴리즈 키스토어 생성 스크립트 (Windows PowerShell)
# 한 번만 실행, 결과 파일과 비밀번호를 안전한 곳에 백업하세요.

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$keystoreDir = Join-Path $projectRoot "keystore"
$keystoreFile = Join-Path $keystoreDir "bidet-release.jks"

if (-not (Test-Path $keystoreDir)) {
    New-Item -ItemType Directory -Path $keystoreDir | Out-Null
}

if (Test-Path $keystoreFile) {
    Write-Host "이미 키스토어 존재: $keystoreFile" -ForegroundColor Yellow
    Write-Host "덮어쓰지 않습니다. 기존 키스토어를 사용하세요." -ForegroundColor Yellow
    exit 0
}

Write-Host "비데앱 릴리즈 키스토어 생성 시작" -ForegroundColor Cyan
Write-Host "생성 위치: $keystoreFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  중요: 키스토어 비밀번호와 키 비밀번호를 절대 잃지 마세요." -ForegroundColor Red
Write-Host "    분실 시 Play Store에 같은 패키지명으로 앱 업데이트가 영구 불가합니다." -ForegroundColor Red
Write-Host ""

$alias = "bidet"
$validity = 10000  # 약 27년 (Google Play 요구: 2033년 이후까지)

& keytool -genkeypair `
    -v `
    -keystore $keystoreFile `
    -alias $alias `
    -keyalg RSA `
    -keysize 2048 `
    -validity $validity

Write-Host ""
Write-Host "✓ 키스토어 생성 완료" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "1. $projectRoot\keystore.properties.example 을 keystore.properties 로 복사"
Write-Host "2. keystore.properties 에 위에서 입력한 비밀번호 입력"
Write-Host "3. 키스토어 파일과 비밀번호를 안전한 곳(예: 1Password, 외장 백업)에 보관"
Write-Host "4. .\gradlew bundleRelease 로 AAB 빌드"
