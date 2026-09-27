"""시스템 트레이 아이콘 — pystray. 미설치·실패 시 무시(앱은 정상 동작)."""
import os
import sys
import threading

import i18n

try:
    import pystray
    from PIL import Image
    _HAS = True
except ImportError:
    _HAS = False


def _rp(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


class Tray:
    def __init__(self, app):
        self.app = app
        self.icon = None

    def start(self):
        if not _HAS:
            return
        try:
            img = Image.open(_rp(os.path.join("assets", "logo.png")))
        except Exception:
            return
        menu = pystray.Menu(
            pystray.MenuItem(i18n.tr("tray_open"), self._show, default=True),
            pystray.MenuItem(i18n.tr("tray_exit"), self._quit))
        self.icon = pystray.Icon("SizeOn", img, "Size On", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
            self.icon = None

    def _show(self, icon, item):
        self.app.after(0, lambda: (self.app.deiconify(),
                                   self.app.lift(),
                                   self.app.focus_force()))

    def _quit(self, icon, item):
        self.app.after(0, self.app._on_close)
