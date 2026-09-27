<div align="center">

<img src="assets/logo.png" width="96" alt="Size On logo">

# Size On

**Window / area size measurement + fixed-size capture tool**

Live `px` · `mm` · `inch` readout / DPI physical calibration · Windows

![version](https://img.shields.io/badge/version-0.0.34-4ec9b0)
![platform](https://img.shields.io/badge/platform-Windows-0a84ff)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

**English** | [한국어](#한국어)

</div>

---

## Features

- **Window size measurement** — drag the window, or double-click a shown value to type it in `px/mm/in` → the window resizes to it
- **Measure / capture area** — full-screen overlay: drag to select, capture with `S`/`Enter`/double-click, cycle text color with `Tab`
- **Fixed-size capture** — move a box of the current window size and capture at that exact size
- **Full-screen capture**
- **Physical calibration (4 methods)** — Auto (EDID) / Reference line / Card match / Diagonal+resolution → accurate real-world `mm/in`
- **Bilingual** — Korean / English, instant toggle
- **System tray** (when pystray is installed)

## Install

1. Download the latest `Size On.exe` from [Releases](../../releases)
2. Run it → **agree to the EULA and it self-installs** (`%LOCALAPPDATA%\Programs\Size On`, Desktop/Start-menu shortcuts, "Settings > Apps" entry)
3. Uninstall from **Settings > Apps** → "Size On"

> If Windows SmartScreen warns (unsigned free app), choose **More info → Run anyway**.

## Verify integrity

```powershell
Get-FileHash -Algorithm SHA256 "Size On.exe"
```

The output must match the `SHA256` in the release notes (or `SHA256SUMS.txt`).

## Antivirus / False positives

A few antivirus engines may flag this app. This is a **false positive** common to
PyInstaller-built, unsigned executables — the PyInstaller bootloader and self-extracting
onefile format resemble packers, so heuristic engines over-flag them.

- Major engines (Microsoft Defender, Kaspersky, ESET, BitDefender) report it clean.
- The full source is public here — you can review it and build the exe yourself.
- Scan report: [VirusTotal](https://www.virustotal.com/gui/file/a2f76ac614c84a37d265cb88f9f7e90fff5d9b5b1d0a50ffb7c1160be077a59f)
- If unsure, build from source (below) instead of using the prebuilt exe.

## Build from source

```bat
:: requires Python 3.11+
build_exe.bat
```

- Builds `dist\Size On.exe` (PyInstaller onefile)
- Generates `dist\SHA256SUMS.txt` after the build
- Dev run: `run.pyw` (runs directly, no install wizard)

**Dependencies**: `pyinstaller` `pillow` `pystray` (installed by build_exe.bat)

## License

[MIT](LICENSE) © 2026 Shugle — free to use, modify, and redistribute, including commercially, provided the copyright notice is kept. Provided "AS IS", no warranty.

## Author

**Shugle** — if this helped, ☕ [Buy Me a Coffee](https://buymeacoffee.com/reading83)

---

<div align="center">

## 한국어

[English](#size-on) | **한국어**

</div>

**창·영역 크기 측정 + 지정 크기 캡처 도구** · `px` · `mm` · `inch` 실시간 표시 / DPI 물리 보정 · Windows

### 기능

- **창 크기 측정** — 창을 드래그하거나 표시된 숫자를 더블클릭해 `px/mm/in`으로 직접 입력 → 창 리사이즈
- **영역 측정/캡처** — 전체화면 오버레이에서 드래그 선택, `S`/`Enter`/더블클릭 캡처, `Tab`으로 글자색 순환
- **지정 크기 캡처** — 현재 창 크기 박스를 이동해 정확히 그 크기로 캡처
- **전체화면 캡처**
- **물리 보정 (4방식)** — 자동(EDID) / 기준선 실측 / 카드 맞추기 / 대각선+해상도 → 실제 `mm/in` 정확도 향상
- **다국어** — 한국어 / English 즉시 전환
- **시스템 트레이 상주** (pystray 설치 시)

### 설치

1. [Releases](../../releases)에서 최신 `Size On.exe` 다운로드
2. exe 실행 → **EULA 동의 후 자동 설치** (`%LOCALAPPDATA%\Programs\Size On`, 바탕화면·시작메뉴 바로가기, 설정 > 앱 목록 등록)
3. 제거: **설정 > 앱**에서 "Size On" 제거

> Windows SmartScreen 경고가 뜨면(서명 없는 무료 프로그램) **추가 정보 → 실행**을 선택하세요.

### 무결성 검증

```powershell
Get-FileHash -Algorithm SHA256 "Size On.exe"
```

출력 해시가 릴리스의 `SHA256`(또는 `SHA256SUMS.txt`)과 일치하면 정상입니다.

### 백신 오탐 안내

일부 백신이 이 프로그램을 탐지할 수 있습니다. 이는 **PyInstaller로 빌드된 서명 없는
실행 파일에서 흔한 오탐(false positive)**입니다 — PyInstaller 부트로더와 onefile 자기
압축 해제 방식이 패커와 비슷해 휴리스틱 엔진이 과탐지합니다.

- 주요 엔진(Microsoft Defender, Kaspersky, ESET, BitDefender)은 정상으로 판정.
- 소스 전체가 공개돼 있어 직접 검토·빌드 가능합니다.
- 검사 결과: [VirusTotal](https://www.virustotal.com/gui/file/a2f76ac614c84a37d265cb88f9f7e90fff5d9b5b1d0a50ffb7c1160be077a59f)
- 불안하면 아래 "소스에서 빌드"로 직접 빌드해 사용하세요.

### 소스에서 빌드

```bat
:: 필요: Python 3.11+
build_exe.bat
```

- `dist\Size On.exe` 생성(PyInstaller onefile), 빌드 후 `dist\SHA256SUMS.txt` 자동 생성
- 개발 실행: `run.pyw` (설치 마법사 없이 바로 실행)

### 라이선스

[MIT](LICENSE) © 2026 Shugle — 저작권 고지를 유지하면 상업적 사용·수정·재배포 자유. '있는 그대로(AS IS)' 제공, 무보증.

### 제작

**Shugle(슈글)** — 유용하셨다면 ☕ [Buy Me a Coffee](https://buymeacoffee.com/reading83)
