"""Pretendard 폰트 런타임 등록 (Windows private font, 설치 불필요)"""
import os
import sys
import ctypes

_FR_PRIVATE = 0x10
FAMILY = "Pretendard"
FALLBACK = "Segoe UI"
_FILES = ["Pretendard-Regular.ttf", "Pretendard-Bold.ttf"]
_registered = False


def _rp(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def register():
    """폰트 파일을 프로세스에 private 등록. 성공 시 True. Tk() 생성 전 호출."""
    global _registered
    try:
        n = 0
        for f in _FILES:
            p = _rp(os.path.join("assets", "fonts", f))
            if os.path.exists(p):
                n += ctypes.windll.gdi32.AddFontResourceExW(p, _FR_PRIVATE, 0)
        _registered = n > 0
    except Exception:
        _registered = False  # 비Windows·등록실패 → 폴백
    return _registered


def family():
    return FAMILY if _registered else FALLBACK
