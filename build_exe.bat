@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [Size On] PyInstaller build start...
pip install pyinstaller pillow pystray
echo [Size On] version_info 생성 중...
python gen_version.py
pyinstaller --noconsole --onefile --name "Size On" --icon "icon.ico" --version-file "version_info.txt" --add-data "icon.ico;." --add-data "assets\logo.png;assets" --add-data "assets\fonts\*.ttf;assets\fonts" run.pyw
echo.
echo Done: dist\Size On.exe
echo.
echo [Size On] SHA-256 생성 중...
powershell -NoProfile -Command "$h=(Get-FileHash -Algorithm SHA256 'dist\Size On.exe').Hash.ToLower(); Set-Content -Encoding ascii 'dist\SHA256SUMS.txt' ($h + '  Size On.exe'); Write-Host ('SHA256: ' + $h)"
echo 저장: dist\SHA256SUMS.txt
echo.
echo exe 최초 실행 시 EULA 동의 후 자동 설치됩니다. (별도 install.bat 불필요)
pause
