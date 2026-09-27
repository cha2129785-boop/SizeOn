"""화면 캡처 — Pillow ImageGrab 기반. grab()은 저장하지 않고 이미지만 반환."""
import datetime
from tkinter import filedialog

try:
    from PIL import ImageGrab
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False


def available():
    return _HAS_PIL


def _default_name():
    return "SizeOn_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"


def grab(bbox=None):
    """bbox=(x1,y1,x2,y2) 가상화면 좌표, None이면 전체화면. PIL Image 반환(미저장).
    ⚠️추정: per-monitor DPI 배율 환경에서 tkinter 논리좌표와 ImageGrab 물리픽셀이
    어긋날 수 있음(주 모니터 100% 배율에선 일치)."""
    if not _HAS_PIL:
        return None
    return ImageGrab.grab(bbox=bbox, all_screens=True)


def save_image(img):
    """미리보기에서 확인한 이미지를 파일로 저장. 성공 시 경로 반환."""
    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialfile=_default_name(),
        filetypes=[("PNG 이미지", "*.png"), ("모든 파일", "*.*")])
    if not path:
        return None
    img.save(path)
    return path
