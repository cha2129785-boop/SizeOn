"""DPI 감지 및 px/mm/inch 변환 — Windows Per-Monitor V2 기준
   + 사용자 물리 보정(PPI) 계층: 보정값 있으면 시스템 DPI 대신 사용."""
import ctypes
import os
import json
import math
from ctypes import wintypes

MM_PER_INCH = 25.4
DEFAULT_DPI = 96  # 감지 실패 시 폴백값
CARD_MM = 85.6    # ISO/IEC 7810 ID-1 카드 폭

_calib = None  # 사용자 보정 PPI(float) 또는 None

_user32 = ctypes.windll.user32
_gdi32 = ctypes.windll.gdi32

_user32.GetForegroundWindow.restype = wintypes.HWND
_user32.GetDC.argtypes = [wintypes.HWND]
_user32.GetDC.restype = wintypes.HDC
_user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
_gdi32.GetDeviceCaps.argtypes = [wintypes.HDC, ctypes.c_int]
_gdi32.GetDeviceCaps.restype = ctypes.c_int


def enable_dpi_awareness() -> None:
    """프로세스 DPI 인식 설정. Win10 1703+ Per-Monitor V2 우선, 구버전 순차 폴백."""
    try:
        # ✅확신: DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
        _user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        _user32.SetProcessDpiAwarenessContext.restype = wintypes.BOOL
        _user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except (AttributeError, OSError):
        pass
    try:
        # ⚠️추정: Win8.1+ shcore 폴백, PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except (AttributeError, OSError):
        pass
    try:
        _user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass  # Win7 이하 — DPI API 자체 없음, 96 고정 취급


def get_dpi_for_hwnd(hwnd: int) -> int:
    """창이 위치한 모니터 DPI. 실패 시 DEFAULT_DPI 반환."""
    try:
        # ✅확신: GetDpiForWindow, Win10 1607+, 모니터별 값
        _user32.GetDpiForWindow.argtypes = [wintypes.HWND]
        _user32.GetDpiForWindow.restype = ctypes.c_uint
        dpi = _user32.GetDpiForWindow(wintypes.HWND(hwnd))
        if dpi > 0:
            return dpi
    except (AttributeError, OSError):
        pass
    try:
        # ⚠️추정: 구버전 폴백 — 시스템 전역 DC LOGPIXELSX (모니터별 아님)
        LOGPIXELSX = 88
        hdc = _user32.GetDC(wintypes.HWND(0))
        dpi = _gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
        _user32.ReleaseDC(wintypes.HWND(0), hdc)
        if dpi > 0:
            return dpi
    except (AttributeError, OSError):
        pass
    return DEFAULT_DPI


def px_to_inch(px: float, dpi: int) -> float:
    return px / dpi


def px_to_mm(px: float, dpi: int) -> float:
    return px_to_inch(px, dpi) * MM_PER_INCH


def inch_to_px(inch: float, dpi: int) -> int:
    return round(inch * dpi)


def mm_to_px(mm: float, dpi: int) -> int:
    return inch_to_px(mm / MM_PER_INCH, dpi)


# ---- 물리 보정(PPI) 계층 ----
def _calib_path() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "SizeOn", "calib.json")


def load_calib():
    """저장된 보정 PPI 로드. 없거나 오류 시 None."""
    global _calib
    try:
        with open(_calib_path(), "r", encoding="utf-8") as f:
            v = json.load(f).get("ppi")
        _calib = float(v) if v and float(v) > 0 else None
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        _calib = None
    return _calib


def save_calib(ppi: float) -> None:
    global _calib
    _calib = float(ppi)
    p = _calib_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"ppi": _calib}, f)


def clear_calib() -> None:
    global _calib
    _calib = None
    try:
        os.remove(_calib_path())
    except OSError:
        pass


def get_calib():
    return _calib


def effective_dpi(hwnd) -> float:
    """보정 PPI 있으면 그 값, 없으면 시스템 DPI(정수)."""
    return _calib if _calib else get_dpi_for_hwnd(hwnd)


# ---- 보정 방식별 PPI 산출 (셋 다 유효 PPI 하나로 수렴) ----
def ppi_from_length(px: float, mm: float) -> float:
    """A: 화면 기준선 px를 실측 mm로 나눠 PPI 산출."""
    return px * MM_PER_INCH / mm


def ppi_from_card(px: float) -> float:
    """B: 카드 폭에 맞춘 px로 PPI 산출."""
    return px * MM_PER_INCH / CARD_MM


def ppi_from_diagonal(inch: float, res_w: int, res_h: int) -> float:
    """C: 대각선(inch)과 해상도로 PPI 산출."""
    return math.hypot(res_w, res_h) / inch


# ---- 자동 보정: EDID 파싱 ----
def _parse_edid(edid: bytes):
    """EDID 바이너리 → 물리크기·해상도·PPI. 유효하지 않으면 None."""
    if len(edid) < 128 or edid[0:8] != b"\x00\xff\xff\xff\xff\xff\xff\x00":
        return None
    m = (edid[8] << 8) | edid[9]  # 제조사 ID(5bit×3)
    man = "".join(chr(64 + ((m >> s) & 0x1F)) for s in (10, 5, 0))
    prod = "%04X" % (edid[10] | (edid[11] << 8))
    o = 54  # 첫 상세 타이밍 디스크립터(DTD)
    hpx = ((edid[o + 4] >> 4) << 8) | edid[o + 2]
    vpx = ((edid[o + 7] >> 4) << 8) | edid[o + 5]
    hmm = ((edid[o + 14] >> 4) << 8) | edid[o + 12]
    vmm = ((edid[o + 14] & 0x0F) << 8) | edid[o + 13]
    if hpx == 0 or vpx == 0 or hmm == 0 or vmm == 0:  # DTD 무효 → cm 필드 폴백
        hcm, vcm = edid[21], edid[22]
        if hcm and vcm and hpx and vpx:
            hmm, vmm = hcm * 10, vcm * 10
        else:
            return None
    return {"man": man, "prod": prod, "hpx": hpx, "vpx": vpx,
            "hmm": hmm, "vmm": vmm,
            "ppi": math.hypot(hpx, vpx) / (math.hypot(hmm, vmm) / MM_PER_INCH)}


def _active_instance():
    """WMI로 현재 활성 모니터의 InstanceName 획득. 실패 시 None.
       예: 'DISPLAY\\DELA0F0\\5&abcd&0&UID4352_0' → 레지스트리 인스턴스키 매핑용."""
    import subprocess
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance -Namespace root/wmi -ClassName "
             "WmiMonitorBasicDisplayParams | Where-Object {$_.Active} | "
             "Select-Object -First 1 -ExpandProperty InstanceName"],
            capture_output=True, text=True, timeout=6,
            creationflags=0x08000000)  # CREATE_NO_WINDOW
        s = out.stdout.strip()
        return s or None
    except Exception:
        return None


def _edid_from_active():
    """활성 모니터 InstanceName → 해당 레지스트리 키의 EDID만 파싱. 실패 시 None."""
    try:
        import winreg
    except ImportError:
        return None
    inst = _active_instance()
    if not inst:
        return None
    parts = inst.split("\\")  # ['DISPLAY','DELA0F0','5&..&UID4352_0']
    if len(parts) < 3:
        return None
    dev_id = parts[2].rsplit("_", 1)[0]  # 끝 '_0' 제거
    key = r"SYSTEM\CurrentControlSet\Enum\DISPLAY\%s\%s\Device Parameters" % (
        parts[1], dev_id)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as k:
            raw, _ = winreg.QueryValueEx(k, "EDID")
        return _parse_edid(bytes(raw))
    except OSError:
        return None


def read_edid(cur_w: int = 0, cur_h: int = 0):
    """EDID 파싱. ①활성 모니터(WMI) 직접 지정 우선 → ②해상도 매칭 → ③첫 항목.
       (레지스트리엔 과거·다중 모니터 EDID가 잔존하므로 활성 지정이 가장 정확) 실패 시 None."""
    active = _edid_from_active()
    if active:
        return active
    try:
        import winreg
    except ImportError:
        return None
    base = r"SYSTEM\CurrentControlSet\Enum\DISPLAY"
    found = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as k0:
            i = 0
            while True:
                try:
                    model = winreg.EnumKey(k0, i)
                except OSError:
                    break
                i += 1
                try:
                    with winreg.OpenKey(k0, model) as k1:
                        j = 0
                        while True:
                            try:
                                inst = winreg.EnumKey(k1, j)
                            except OSError:
                                break
                            j += 1
                            try:
                                with winreg.OpenKey(k1, inst + r"\Device Parameters") as k2:
                                    raw, _ = winreg.QueryValueEx(k2, "EDID")
                                    p = _parse_edid(bytes(raw))
                                    if p:
                                        found.append(p)
                            except OSError:
                                pass
                except OSError:
                    pass
    except OSError:
        return None
    if not found:
        return None
    if cur_w and cur_h:  # 현재 해상도와 네이티브 일치 항목 우선
        for p in found:
            if p["hpx"] == cur_w and p["vpx"] == cur_h:
                return p
    return found[0]


if __name__ == "__main__":
    enable_dpi_awareness()
    hwnd = _user32.GetForegroundWindow()
    d = get_dpi_for_hwnd(hwnd)
    print(f"DPI: {d}")
    print(f"1920px -> {px_to_inch(1920, d):.3f}in / {px_to_mm(1920, d):.1f}mm")
