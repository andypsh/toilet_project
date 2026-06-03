# Gradle Wrapper 초기 생성 스크립트
# 시스템에 gradle이 설치되어 있어야 함 (또는 Android Studio가 처리)

$ErrorActionPreference = "Stop"

$gradleCmd = Get-Command gradle -ErrorAction SilentlyContinue
if ($null -eq $gradleCmd) {
    Write-Host "⚠️  시스템에 gradle이 설치되어 있지 않습니다." -ForegroundColor Yellow
    Write-Host "    선택지:" -ForegroundColor Yellow
    Write-Host "    1) Android Studio에서 프로젝트 열기 → 자동으로 wrapper 생성됨" -ForegroundColor Cyan
    Write-Host "    2) Chocolatey: choco install gradle" -ForegroundColor Cyan
    Write-Host "    3) https://gradle.org/install/ 에서 수동 설치" -ForegroundColor Cyan
    exit 1
}

Write-Host "Gradle Wrapper 생성 중 (8.9 버전)..." -ForegroundColor Cyan
gradle wrapper --gradle-version 8.9 --distribution-type all
Write-Host "✓ Gradle Wrapper 생성 완료. 이제 .\gradlew 명령 사용 가능." -ForegroundColor Green
