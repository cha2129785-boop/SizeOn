@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "EXE=dist\Size On.exe"
if not exist "%EXE%" set "EXE=Size On.exe"
if not exist "%EXE%" (
  echo [오류] "Size On.exe"를 찾을 수 없습니다. 먼저 build_exe.bat 실행하세요.
  pause
  exit /b 1
)
echo [Size On] SHA-256 생성 중...
powershell -NoProfile -Command "$h=(Get-FileHash -Algorithm SHA256 '%EXE%').Hash.ToLower(); Set-Content -Encoding ascii SHA256SUMS.txt ($h + '  Size On.exe'); Write-Host $h"
echo.
echo 저장: SHA256SUMS.txt
type SHA256SUMS.txt
pause
