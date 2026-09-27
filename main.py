"""Size On (사이즈온) — 창/영역 크기 측정 도구"""
import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import dpi
import capture
import fonts
import tray
import installer
import i18n
from i18n import tr

__version__ = "0.0.39"
APP_NAME = "Size On"

DONATE_URL = "https://buymeacoffee.com/reading83"        # 개발 지원
SURVEY_URL = {  # 설문 — UI 언어별 폼
    "ko": "https://docs.google.com/forms/d/e/1FAIpQLSen7s2ZqtUROkSVIJ0yHK8StXZP298yTlyxonAevw3ozhplKQ/viewform?usp=header",
    "en": "https://docs.google.com/forms/d/e/1FAIpQLSeJfZb3x1bZaigWrdYDnFhUn98S_BUbblbpybXow0EYz8paKQ/viewform?usp=publish-editor",
}

# 제작자 서명(저작권 검증용) — 제작자 식별 문자열의 SHA256 단방향 해시.
# 원본 복원 불가. 원본 문자열은 제작자가 별도 보관(소스 미포함).
# 분쟁 시 원본 제시 → 이 값과 일치로 저작권 증명.
APP_AUTHOR_SIG = "7e6911402a281c3daddbd5f41a724ca367fea7a96bb095543033988652555039"
APP_AUTHOR_DISPLAY = "슈글 (Shugle)"  # UI 표시용(이메일 비노출)

EULA_TEXT = {
    "ko": (
        "Size On 최종 사용자 사용권 계약(EULA)\n\n"
        "본 소프트웨어(Size On, 이하 '프로그램')를 설치·사용함으로써 아래 조건에 동의합니다.\n\n"
        "1. 프로그램은 MIT 라이선스에 따라 무료로 제공됩니다(저작권자 Shugle).\n"
        "2. 저작권 고지를 유지하면 사용·복사·수정·재배포·상업적 이용이 자유롭습니다.\n"
        "3. 프로그램은 '있는 그대로(AS IS)' 제공되며 어떠한 보증도 하지 않습니다.\n"
        "4. 프로그램 사용으로 발생한 직접·간접 손해에 대해 제작자는 책임지지 않습니다.\n"
        "5. 자세한 조건은 함께 배포되는 LICENSE(MIT) 파일을 따릅니다.\n\n"
        "설치 시 프로그램은 사용자 폴더(%LOCALAPPDATA%\\Programs\\Size On)에 복사되고, "
        "바탕화면·시작메뉴 바로가기와 '설정 > 앱 목록' 항목이 생성됩니다."
    ),
    "en": (
        "Size On End User License Agreement (EULA)\n\n"
        "By installing or using this software (\"Size On\"), you agree to the following:\n\n"
        "1. The software is free under the MIT License (copyright holder: Shugle).\n"
        "2. You may use, copy, modify, and redistribute it, including commercially, "
        "as long as the copyright notice is kept.\n"
        "3. The software is provided \"AS IS\" without warranty of any kind.\n"
        "4. The author is not liable for any direct or indirect damages from its use.\n"
        "5. Full terms are in the accompanying LICENSE (MIT) file.\n\n"
        "On install, the app is copied to %LOCALAPPDATA%\\Programs\\Size On and creates "
        "Desktop/Start Menu shortcuts and a 'Settings > Apps' entry."
    ),
}

UIFONT = "Segoe UI"  # main()에서 등록 성공 시 Pretendard로 교체

BG = "#1e1e1e"
FG = "#4ec9b0"
ACCENT = "#0a84ff"
ACCENT_HOVER = "#0a74e0"
SOFT = "#2d2d2d"
SOFT_HOVER = "#3a3a3a"


def resource_path(rel):
    """PyInstaller onefile(sys._MEIPASS)·일반 실행 양쪽에서 리소스 경로 반환."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def apply_icon(win):
    """창 아이콘 적용 — .ico 우선, 실패 시 PNG(iconphoto) 폴백."""
    try:
        win.iconbitmap(resource_path("icon.ico"))
        return
    except Exception:
        pass
    try:
        from PIL import ImageTk
        img = ImageTk.PhotoImage(file=resource_path(os.path.join("assets", "logo.png")))
        win._icon_ref = img  # GC 방지
        win.iconphoto(True, img)
    except Exception:
        pass


def _fmt(px, d):
    return f"{int(px)} px   |   {dpi.px_to_mm(px, d):.1f} mm   |   {dpi.px_to_inch(px, d):.2f} in"


def flat_btn(parent, text, cmd, primary=False):
    """플랫 스타일 버튼(Label 기반) — hover 색 변화."""
    base = ACCENT if primary else SOFT
    hov = ACCENT_HOVER if primary else SOFT_HOVER
    b = tk.Label(parent, text=text, bg=base, fg="#ffffff",
                 font=(UIFONT, 14), padx=16, pady=8, cursor="hand2")
    b.bind("<Button-1>", lambda e: cmd())
    b.bind("<Enter>", lambda e: b.config(bg=hov))
    b.bind("<Leave>", lambda e: b.config(bg=base))
    return b


class SizeOn(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{__version__}")
        self.minsize(300, 220)
        self.geometry("460x320")
        self.configure(bg=BG)
        apply_icon(self)
        self._tray = None
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()
        self.bind("<Configure>", self._on_configure)
        self.after(120, self._on_configure)
        self.after(140, self._fit_width)

    def _on_close(self):
        if self._tray:
            self._tray.stop()
        self.destroy()

    def _toggle_lang(self):
        i18n.toggle()
        installer.save_lang(i18n.current())
        for w in self.winfo_children():
            w.destroy()
        self._build()
        self._on_configure()
        self._fit_width()

    def _fit_width(self):
        """툴바 등 콘텐츠 필요폭에 맞춰 창 폭 확장(grow-only). 사용자가 키운 폭은 유지."""
        self.update_idletasks()
        req = self.winfo_reqwidth()
        self.minsize(max(300, req), 220)
        if self.winfo_width() < req:
            self.geometry(f"{req}x{self.winfo_height()}")

    def _dpi(self):
        return dpi.effective_dpi(self.winfo_id())

    def _build(self):
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=14, pady=(12, 2))
        try:
            from PIL import Image, ImageTk
            logo = Image.open(resource_path(os.path.join("assets", "logo.png"))).convert("RGBA")
            logo = logo.resize((48, 48), Image.LANCZOS)
            self._logo = ImageTk.PhotoImage(logo)
            lg = tk.Label(head, image=self._logo, bg=BG, cursor="hand2")
            lg.pack(side="left")
            lg.bind("<Button-1>", self._open_donate)
        except Exception:
            pass
        tk.Label(head, text=f"{APP_NAME}", bg=BG, fg="#eeeeee",
                 font=(UIFONT, 14, "bold")).pack(side="left", padx=(8, 0))
        tk.Label(head, text=f"v{__version__}", bg=BG, fg="#606060",
                 font=(UIFONT, 10)).pack(side="left", padx=(6, 0), pady=(6, 0))
        lang = tk.Label(head, text=tr("lang_toggle"), bg=ACCENT, fg="#ffffff",
                        font=(UIFONT, 10, "bold"), padx=10, pady=4, cursor="hand2")
        lang.bind("<Button-1>", lambda e: self._toggle_lang())
        lang.bind("<Enter>", lambda e: lang.config(bg=ACCENT_HOVER))
        lang.bind("<Leave>", lambda e: lang.config(bg=ACCENT))
        lang.pack(side="right")
        tk.Label(head, text=tr("author"), bg=BG, fg="#707070",
                 font=(UIFONT, 10)).pack(side="right", padx=(0, 10))

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=(6, 4))
        flat_btn(top, tr("btn_area"), self._open_overlay, primary=True).pack(side="left")
        flat_btn(top, tr("btn_fixed"), self._open_fixed).pack(side="left", padx=(8, 0))
        flat_btn(top, tr("btn_full"), self._capture_full).pack(side="left", padx=(8, 0))
        flat_btn(top, tr("btn_calib"), self._open_calib).pack(side="right")

        mid = tk.Frame(self, bg="#1e1e1e")
        mid.pack(expand=True)
        tk.Label(mid, text=tr("hint"),
                 bg="#1e1e1e", fg="#808080", font=(UIFONT, 12)).pack(pady=(0, 6))
        self._editing = None
        self.vals = {"w": {}, "h": {}}  # 축별 단위별 값 라벨 참조
        self.lbl_w = self._dim_row(mid, "w", tr("w_prefix"))
        self.lbl_h = self._dim_row(mid, "h", tr("h_prefix"))
        self.lbl_dpi = tk.Label(mid, text="", bg="#1e1e1e", fg="#606060",
                                font=(UIFONT, 10))
        self.lbl_dpi.pack(pady=(8, 0))

    def _dim_row(self, parent, which, prefix):
        row = tk.Frame(parent, bg="#1e1e1e")
        row.pack(pady=2)
        tk.Label(row, text=prefix, bg="#1e1e1e", fg="#4ec9b0",
                 font=(UIFONT, 16, "bold")).pack(side="left")
        for i, u in enumerate(["px", "mm", "in"]):
            if i:
                tk.Label(row, text="|", bg="#1e1e1e", fg="#555",
                         font=(UIFONT, 14)).pack(side="left", padx=4)
            lb = tk.Label(row, text="", bg="#1e1e1e", fg="#4ec9b0",
                          font=(UIFONT, 16, "bold"), cursor="hand2")
            lb.pack(side="left")
            lb.bind("<Double-Button-1>",
                    lambda e, w=which, un=u: self._edit_dim(w, un))
            self.vals[which][u] = lb
        return row

    def _edit_dim(self, which, unit):
        if self._editing:
            return
        self._editing = (which, unit)
        lbl = self.vals[which][unit]
        px = self.winfo_width() if which == "w" else self.winfo_height()
        d = self._dpi()
        if unit == "mm":
            cur = f"{dpi.px_to_mm(px, d):.1f}"
        elif unit == "in":
            cur = f"{dpi.px_to_inch(px, d):.2f}"
        else:
            cur = str(px)
        e = tk.Entry(lbl.master, width=max(6, len(cur) + 2), font=(UIFONT, 16),
                     justify="center", bd=1, bg="#2d2d2d", fg="#4ec9b0",
                     insertbackground="#4ec9b0")
        e.insert(0, cur)
        e.select_range(0, "end")
        e.place(in_=lbl, relx=0, rely=0, relwidth=1, relheight=1)
        e.focus_set()
        e.bind("<Return>", lambda ev: self._commit_dim(which, unit, e))
        e.bind("<Escape>", lambda ev: self._cancel_dim(e))
        e.bind("<FocusOut>", lambda ev: self._cancel_dim(e))

    def _cancel_dim(self, entry):
        entry.destroy()
        self._editing = None

    def _commit_dim(self, which, unit, entry):
        d = self._dpi()
        try:
            val = float(entry.get())
            if unit == "mm":
                v = dpi.mm_to_px(val, d)
            elif unit == "in":
                v = dpi.inch_to_px(val, d)
            else:
                v = int(val)
        except ValueError:
            v = None
        self._cancel_dim(entry)
        if v and v > 0:
            w, h = self.winfo_width(), self.winfo_height()
            if which == "w":
                w = v
            else:
                h = v
            self.geometry(f"{w}x{h}")

    def _on_configure(self, e=None):
        if e is not None and e.widget is not self:
            return
        d = self._dpi()
        for which, px in (("w", self.winfo_width()), ("h", self.winfo_height())):
            self.vals[which]["px"].config(text=f"{int(px)} px")
            self.vals[which]["mm"].config(text=f"{dpi.px_to_mm(px, d):.1f} mm")
            self.vals[which]["in"].config(text=f"{dpi.px_to_inch(px, d):.2f} in")
        self.lbl_dpi.config(text=tr("dpi_note", d=d))

    def _open_overlay(self):
        Overlay(self)

    def _open_calib(self):
        CalibWindow(self, on_done=self._on_configure)

    def _open_donate(self, e=None):
        DonateDialog(self)

    def _open_fixed(self):
        if not capture.available():
            messagebox.showerror(APP_NAME, tr("err_pillow"))
            return
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        if w > sw or h > sh:  # 화면보다 크면 클램프
            w, h = min(w, sw), min(h, sh)
            messagebox.showwarning(APP_NAME, tr("warn_clamp", w=w, h=h))
        FixedCapture(self, w, h)

    def _capture_full(self):
        if not capture.available():
            messagebox.showerror(APP_NAME, tr("err_pillow"))
            return
        self.withdraw()
        self.after(250, self._do_capture_full)

    def _do_capture_full(self):
        img = capture.grab(None)
        self.deiconify()
        if img:
            PreviewWindow(self, img)


class Overlay(tk.Toplevel):
    """전체화면 반투명 오버레이 — 드래그로 임의 영역 측정. ESC 종료."""
    def __init__(self, master):
        super().__init__(master)
        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.35)
        self.attributes("-topmost", True)
        self.configure(bg="#000000", cursor="crosshair")
        self.canvas = tk.Canvas(self, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.start = None
        self.rect = None
        self.txt = None
        self.sel = None
        self._colors = ["#ffffff", "#ff0000", "#ffff00", "#00ff00", "#4ec9b0"]  # 흰/빨/노/초/청록
        saved = installer.load_color()  # 마지막 사용 색 복원
        self._ci = self._colors.index(saved) if saved in self._colors else 0
        self.canvas.create_text(self.winfo_screenwidth() // 2, 28,
                                text=tr("overlay_hint"),
                                fill="#ffffff", font=(UIFONT, 12))
        self.canvas.bind("<Button-1>", self._down)
        self.canvas.bind("<B1-Motion>", self._move)
        self.canvas.bind("<ButtonRelease-1>", self._up)
        self.canvas.bind("<Double-Button-1>", self._save_sel)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<s>", self._save_sel)
        self.bind("<S>", self._save_sel)
        self.bind("<Return>", self._save_sel)
        self.bind("<Tab>", self._cycle_color)
        self.canvas.bind("<Tab>", self._cycle_color)
        self.focus_force()

    def _cycle_color(self, e=None):
        self._ci = (self._ci + 1) % len(self._colors)
        c = self._colors[self._ci]
        if self.txt:
            self.canvas.itemconfig(self.txt, fill=c)
        if self.rect:
            self.canvas.itemconfig(self.rect, outline=c)
        installer.save_color(c)  # 마지막 색 기억
        return "break"  # 기본 포커스 이동 차단

    def _dpi(self):
        return dpi.effective_dpi(self.winfo_id())

    def _down(self, e):
        self.start = (e.x, e.y)
        if self.rect:
            self.canvas.delete(self.rect)
        if self.txt:
            self.canvas.delete(self.txt)
        self.rect = self.canvas.create_rectangle(e.x, e.y, e.x, e.y,
                                                 outline=self._colors[self._ci], width=4)
        self.txt = self.canvas.create_text(e.x, e.y, text="",
                                           fill=self._colors[self._ci],
                                           font=(UIFONT, 14, "bold"),
                                           justify="center")

    def _move(self, e):
        if not self.start:
            return
        x0, y0 = self.start
        self.canvas.coords(self.rect, x0, y0, e.x, e.y)
        w, h = abs(e.x - x0), abs(e.y - y0)
        d = self._dpi()
        self.canvas.coords(self.txt, (x0 + e.x) // 2, (y0 + e.y) // 2)
        self.canvas.itemconfig(
            self.txt,
            text=(f"{w} × {h} px\n"
                  f"{dpi.px_to_mm(w, d):.1f} × {dpi.px_to_mm(h, d):.1f} mm\n"
                  f"{dpi.px_to_inch(w, d):.2f} × {dpi.px_to_inch(h, d):.2f} in"))

    def _up(self, e):
        # 실제 드래그(>=2px)만 선택 확정 — 더블클릭의 단순 클릭이 기존 선택을 덮지 않도록
        if not self.start:
            return
        x0, y0 = self.start
        if abs(e.x - x0) >= 2 and abs(e.y - y0) >= 2:
            self.sel = (min(x0, e.x), min(y0, e.y), max(x0, e.x), max(y0, e.y))

    def _save_sel(self, e=None):
        if not self.sel:
            return
        if not capture.available():
            messagebox.showerror(APP_NAME, tr("err_pillow"))
            return
        x1, y1, x2, y2 = self.sel
        if x2 - x1 < 2 or y2 - y1 < 2:
            return
        rx, ry = self.winfo_rootx(), self.winfo_rooty()
        bbox = (rx + x1, ry + y1, rx + x2, ry + y2)
        expected = (x2 - x1, y2 - y1)
        master = self.master
        self.withdraw()
        self.update()
        img = capture.grab(bbox)
        self.destroy()
        if img:
            PreviewWindow(master, img, expected)


class DonateDialog(tk.Toplevel):
    """후원 선택 팝업 — 해외(Buy Me a Coffee) / 국내(카카오페이). 로고 클릭 시 진입.
       카카오는 QR 에셋 있으면 팝업, 없으면 링크 열기(폴백)."""
    def __init__(self, master):
        super().__init__(master)
        self.title(f"{APP_NAME} · {tr('donate_title')}")
        self.configure(bg=BG)
        apply_icon(self)
        self.resizable(False, False)
        tk.Label(self, text=tr("donate_choose"), bg=BG, fg=FG,
                 font=(UIFONT, 12, "bold"), wraplength=320,
                 justify="center").pack(padx=28, pady=(22, 16))
        flat_btn(self, tr("btn_survey"),
                 lambda: self._go(SURVEY_URL.get(i18n.current(), SURVEY_URL["ko"]))
                 ).pack(fill="x", padx=28, pady=4)
        flat_btn(self, tr("btn_donate"),
                 lambda: self._go(DONATE_URL), primary=True).pack(fill="x", padx=28, pady=4)
        flat_btn(self, tr("btn_close"), self.destroy).pack(pady=(12, 20))
        self.bind("<Escape>", lambda e: self.destroy())
        self.transient(master)
        self.grab_set()
        self.focus_force()

    def _go(self, url):
        try:
            webbrowser.open(url)
        except Exception:
            pass


class CalibWindow(tk.Toplevel):
    """물리 보정 — 3방식(기준선 실측 / 카드 맞추기 / 대각선+해상도) 탭.
       셋 다 유효 PPI 하나로 수렴, calib.json에 저장."""
    LINE_PX = 600  # 탭A 기준선 길이(px)

    def __init__(self, master, on_done=None):
        super().__init__(master)
        self.on_done = on_done
        self.title(f"{APP_NAME} · {tr('calib_title')}")
        self.configure(bg=BG)
        apply_icon(self)
        self.resizable(False, False)

        cur = dpi.get_calib()
        sysd = dpi.get_dpi_for_hwnd(self.winfo_id())
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=16, pady=(14, 6))
        self.lbl_cur = tk.Label(head, bg=BG, fg=FG, font=(UIFONT, 12, "bold"),
                                text=tr("calib_cur",
                                        eff=(f"{cur:.1f}" if cur else tr("calib_none")),
                                        sysd=sysd))
        self.lbl_cur.pack(side="left")
        flat_btn(head, tr("calib_reset"), self._reset).pack(side="right")

        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=16, pady=(6, 0))
        body = tk.Frame(self, bg=SOFT, highlightthickness=1,
                        highlightbackground="#333")
        body.pack(fill="both", expand=True, padx=16, pady=(8, 14))
        tabs = [("auto", tr("calib_tab_auto"), self._tab_auto),
                ("a", tr("calib_tab_a"), self._tab_line),
                ("b", tr("calib_tab_b"), self._tab_card),
                ("c", tr("calib_tab_c"), self._tab_diag)]
        self._panels, self._tab_btns = {}, {}
        for key, label, builder in tabs:
            self._panels[key] = builder(body)
            self._tab_btns[key] = self._seg(bar, label, key)
        self._show_tab("auto")
        self.focus_force()

    def _seg(self, parent, text, key):
        b = tk.Label(parent, text=text, bg=SOFT, fg="#cfd3d7",
                     font=(UIFONT, 11, "bold"), padx=14, pady=7, cursor="hand2")
        b.pack(side="left", padx=(0, 4))
        b.bind("<Button-1>", lambda e, k=key: self._show_tab(k))
        return b

    def _show_tab(self, key):
        for p in self._panels.values():
            p.pack_forget()
        self._panels[key].pack(fill="both", expand=True)
        for k, b in self._tab_btns.items():
            b.config(bg=(ACCENT if k == key else SOFT),
                     fg=("#ffffff" if k == key else "#cfd3d7"))

    # --- 탭 자동(EDID) ---
    def _tab_auto(self, nb):
        f = tk.Frame(nb, bg=BG)
        self._auto_ppi = None
        info = dpi.read_edid(self.winfo_screenwidth(), self.winfo_screenheight())
        tk.Label(f, text=tr("calib_auto_desc"), bg=BG, fg="#bbb",
                 font=(UIFONT, 11), justify="left", wraplength=460).pack(
                     anchor="w", padx=12, pady=(12, 6))
        if info:
            self._auto_ppi = info["ppi"]
            tk.Label(f, text=tr("calib_auto_found",
                                man=info["man"], prod=info["prod"],
                                hmm=info["hmm"], vmm=info["vmm"],
                                hpx=info["hpx"], vpx=info["vpx"],
                                ppi=info["ppi"]),
                     bg=BG, fg=FG, font=(UIFONT, 12), justify="left").pack(
                         anchor="w", padx=12, pady=8)
            flat_btn(f, tr("calib_apply"), self._apply_auto, primary=True).pack(pady=12)
        else:
            tk.Label(f, text=tr("calib_auto_fail"), bg=BG, fg="#e0a030",
                     font=(UIFONT, 11), justify="left", wraplength=460).pack(
                         padx=12, pady=24)
        return f

    def _apply_auto(self):
        if self._auto_ppi:
            self._commit(self._auto_ppi)

    # --- 탭 A: 기준선 실측 ---
    def _tab_line(self, nb):
        f = tk.Frame(nb, bg=BG)
        tk.Label(f, text=tr("calib_a_desc"), bg=BG, fg="#bbb",
                 font=(UIFONT, 11), justify="left", wraplength=460).pack(
                     anchor="w", padx=12, pady=(12, 6))
        self.line_cv = tk.Canvas(f, width=self.LINE_PX + 40, height=44, bg=SOFT,
                                 highlightthickness=0)
        self.line_cv.pack(padx=12)
        self.line_px = tk.IntVar(value=300)
        tk.Scale(f, from_=100, to=self.LINE_PX, orient="horizontal",
                 variable=self.line_px, command=lambda e: self._draw_line(),
                 bg=BG, fg=FG, highlightthickness=0, troughcolor=SOFT,
                 length=self.LINE_PX).pack(padx=12, pady=(6, 2))
        self.lbl_line = tk.Label(f, bg=BG, fg=FG, font=(UIFONT, 11))
        self.lbl_line.pack()
        row = tk.Frame(f, bg=BG)
        row.pack(pady=10)
        tk.Label(row, text=tr("calib_a_input"), bg=BG, fg=FG,
                 font=(UIFONT, 11)).pack(side="left")
        self.e_mm = tk.Entry(row, width=8, font=(UIFONT, 12))
        self.e_mm.pack(side="left", padx=6)
        flat_btn(row, tr("calib_apply"), self._apply_line, primary=True).pack(side="left")
        self._draw_line()
        return f

    def _draw_line(self):
        px = self.line_px.get()
        y = 22
        self.line_cv.delete("ln")
        self.line_cv.create_line(20, y, 20 + px, y, fill=FG, width=2, tags="ln")
        self.line_cv.create_line(20, y - 8, 20, y + 8, fill=FG, width=2, tags="ln")
        self.line_cv.create_line(20 + px, y - 8, 20 + px, y + 8, fill=FG, width=2, tags="ln")
        self.lbl_line.config(text=tr("calib_a_len", px=px))

    def _apply_line(self):
        try:
            mm = float(self.e_mm.get())
            assert mm > 0
        except (ValueError, AssertionError):
            messagebox.showerror(APP_NAME, tr("err_num"))
            return
        self._commit(dpi.ppi_from_length(self.line_px.get(), mm))

    # --- 탭 B: 카드 맞추기 ---
    def _tab_card(self, nb):
        f = tk.Frame(nb, bg=BG)
        tk.Label(f, text=tr("calib_b_desc"), bg=BG, fg="#bbb",
                 font=(UIFONT, 11), justify="left").pack(anchor="w", padx=12, pady=(12, 6))
        self.card_cv = tk.Canvas(f, width=560, height=360, bg=SOFT,
                                 highlightthickness=0)
        self.card_cv.pack(padx=12)
        self.card_rect = self.card_cv.create_rectangle(0, 0, 0, 0,
                                                       outline=FG, width=2, fill="#3a3a3a")
        self.card_w = tk.IntVar(value=340)
        s = tk.Scale(f, from_=200, to=520, orient="horizontal", variable=self.card_w,
                     command=lambda e: self._draw_card(), bg=BG, fg=FG,
                     highlightthickness=0, troughcolor=SOFT, length=520)
        s.pack(padx=12, pady=(8, 4))
        self.lbl_card = tk.Label(f, bg=BG, fg=FG, font=(UIFONT, 11))
        self.lbl_card.pack()
        flat_btn(f, tr("calib_apply"), self._apply_card, primary=True).pack(pady=10)
        self._draw_card()
        return f

    def _draw_card(self):
        w = self.card_w.get()
        h = int(w * 53.98 / dpi.CARD_MM)  # 카드 종횡비
        cx, cy = 280, 180
        self.card_cv.coords(self.card_rect, cx - w // 2, cy - h // 2,
                            cx + w // 2, cy + h // 2)
        ppi = dpi.ppi_from_card(w)
        self.lbl_card.config(text=tr("calib_b_live", px=w, ppi=ppi))

    def _apply_card(self):
        self._commit(dpi.ppi_from_card(self.card_w.get()))

    # --- 탭 C: 대각선+해상도 ---
    def _tab_diag(self, nb):
        f = tk.Frame(nb, bg=BG)
        tk.Label(f, text=tr("calib_c_desc"), bg=BG, fg="#bbb",
                 font=(UIFONT, 11), justify="left").pack(anchor="w", padx=12, pady=(12, 6))
        g = tk.Frame(f, bg=BG)
        g.pack(padx=12, pady=8)
        tk.Label(g, text=tr("calib_c_diag"), bg=BG, fg=FG,
                 font=(UIFONT, 11)).grid(row=0, column=0, sticky="e", pady=4)
        self.e_diag = tk.Entry(g, width=8, font=(UIFONT, 12))
        self.e_diag.grid(row=0, column=1, padx=6)
        tk.Label(g, text=tr("calib_c_res"), bg=BG, fg=FG,
                 font=(UIFONT, 11)).grid(row=1, column=0, sticky="e", pady=4)
        rf = tk.Frame(g, bg=BG)
        rf.grid(row=1, column=1, sticky="w", padx=6)
        self.e_rw = tk.Entry(rf, width=6, font=(UIFONT, 12))
        self.e_rw.pack(side="left")
        self.e_rw.insert(0, str(self.winfo_screenwidth()))
        tk.Label(rf, text="×", bg=BG, fg=FG).pack(side="left", padx=3)
        self.e_rh = tk.Entry(rf, width=6, font=(UIFONT, 12))
        self.e_rh.pack(side="left")
        self.e_rh.insert(0, str(self.winfo_screenheight()))
        flat_btn(f, tr("calib_apply"), self._apply_diag, primary=True).pack(pady=10)
        return f

    def _apply_diag(self):
        try:
            inch = float(self.e_diag.get())
            rw = int(self.e_rw.get())
            rh = int(self.e_rh.get())
            assert inch > 0 and rw > 0 and rh > 0
        except (ValueError, AssertionError):
            messagebox.showerror(APP_NAME, tr("err_num"))
            return
        self._commit(dpi.ppi_from_diagonal(inch, rw, rh))

    # --- 공통 ---
    def _commit(self, ppi):
        dpi.save_calib(ppi)
        messagebox.showinfo(APP_NAME, tr("calib_saved", ppi=ppi))
        if self.on_done:
            self.on_done()
        self.destroy()

    def _reset(self):
        dpi.clear_calib()
        messagebox.showinfo(APP_NAME, tr("calib_reset_done"))
        if self.on_done:
            self.on_done()
        self.destroy()


class FixedCapture(tk.Toplevel):
    """지정 크기(bw×bh px) 고정 박스를 마우스로 이동 → 클릭 시 정확히 그 크기로 캡처.
       방향키 1px, Shift+방향키 10px 미세이동. ESC 취소."""
    def __init__(self, master, bw, bh):
        super().__init__(master)
        self.bw, self.bh = int(bw), int(bh)
        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.3)
        self.attributes("-topmost", True)
        self.configure(bg="#000000", cursor="none")
        self.canvas = tk.Canvas(self, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.sw, self.sh = self.winfo_screenwidth(), self.winfo_screenheight()
        # 초기 위치: 화면 중앙
        self.bx = max(0, (self.sw - self.bw) // 2)
        self.by = max(0, (self.sh - self.bh) // 2)
        self._colors = ["#ffffff", "#ff0000", "#ffff00", "#00ff00", "#4ec9b0"]  # 흰/빨/노/초/청록
        saved = installer.load_color()
        self._ci = self._colors.index(saved) if saved in self._colors else 4
        c = self._colors[self._ci]
        self.rect = self.canvas.create_rectangle(0, 0, 0, 0, outline=c, width=4)
        self.txt = self.canvas.create_text(0, 0, text="", fill=c,
                                           font=(UIFONT, 13, "bold"),
                                           justify="center")
        self.canvas.create_text(self.sw // 2, 28, text=tr("fixed_hint"),
                                fill="#ffffff", font=(UIFONT, 12))
        self.canvas.bind("<Motion>", self._move)
        self.canvas.bind("<Button-1>", self._shoot)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Tab>", self._cycle_color)
        self.canvas.bind("<Tab>", self._cycle_color)
        for k, dx, dy in (("Left", -1, 0), ("Right", 1, 0),
                          ("Up", 0, -1), ("Down", 0, 1)):
            self.bind(f"<{k}>", lambda e, x=dx, y=dy: self._nudge(x, y))
            self.bind(f"<Shift-{k}>", lambda e, x=dx, y=dy: self._nudge(x * 10, y * 10))
        self.focus_force()
        self._draw()

    def _cycle_color(self, e=None):
        self._ci = (self._ci + 1) % len(self._colors)
        c = self._colors[self._ci]
        self.canvas.itemconfig(self.rect, outline=c)
        self.canvas.itemconfig(self.txt, fill=c)
        installer.save_color(c)
        return "break"

    def _clamp(self):
        self.bx = max(0, min(self.bx, self.sw - self.bw))
        self.by = max(0, min(self.by, self.sh - self.bh))

    def _draw(self):
        self._clamp()
        x, y = self.bx, self.by
        self.canvas.coords(self.rect, x, y, x + self.bw, y + self.bh)
        self.canvas.coords(self.txt, x + self.bw // 2, y + self.bh // 2)
        self.canvas.itemconfig(self.txt, text=f"{self.bw} × {self.bh} px")

    def _move(self, e):
        self.bx = e.x - self.bw // 2
        self.by = e.y - self.bh // 2
        self._draw()

    def _nudge(self, dx, dy):
        self.bx += dx
        self.by += dy
        self._draw()

    def _shoot(self, e=None):
        self._clamp()
        rx, ry = self.winfo_rootx(), self.winfo_rooty()
        bbox = (rx + self.bx, ry + self.by,
                rx + self.bx + self.bw, ry + self.by + self.bh)
        expected = (self.bw, self.bh)
        master = self.master
        self.withdraw()
        self.update()
        img = capture.grab(bbox)
        self.destroy()
        if img:
            PreviewWindow(master, img, expected)


class PreviewWindow(tk.Toplevel):
    """캡처 이미지 미리보기 → 저장/취소. 선택 크기 vs 캡처 크기로 좌표 자가검증."""
    def __init__(self, master, img, expected=None):
        super().__init__(master)
        self.title(f"{APP_NAME} · {tr('preview_title')}")
        self.configure(bg=BG)
        apply_icon(self)
        self.img = img
        from PIL import ImageTk
        w, h = img.size
        scale = min(900 / w, 560 / h, 1.0)
        disp = img if scale >= 1.0 else img.resize((max(1, int(w * scale)),
                                                    max(1, int(h * scale))))
        self.photo = ImageTk.PhotoImage(disp)
        tk.Label(self, image=self.photo, bg=BG,
                 highlightthickness=1, highlightbackground="#3a3a3a").pack(padx=14, pady=(14, 8))
        tk.Label(self, text=tr("cap_size", w=w, h=h), bg=BG, fg=FG,
                 font=(UIFONT, 12, "bold")).pack()
        if expected:
            ew, eh = expected
            if abs(ew - w) <= 2 and abs(eh - h) <= 2:
                txt, col = tr("verify_ok"), "#4ec9b0"
            else:
                txt, col = tr("verify_warn", ew=ew, eh=eh, w=w, h=h), "#e0a04e"
            tk.Label(self, text=txt, bg=BG, fg=col, font=(UIFONT, 9)).pack(pady=(3, 0))
        bar = tk.Frame(self, bg=BG)
        bar.pack(pady=14)
        flat_btn(bar, tr("btn_save"), self._save, primary=True).pack(side="left", padx=6)
        flat_btn(bar, tr("btn_cancel"), self.destroy).pack(side="left", padx=6)
        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        path = capture.save_image(self.img)
        if path:
            self.destroy()
            messagebox.showinfo(APP_NAME, tr("saved") + path)


def _set_app_id():
    """작업표시줄이 python이 아닌 Size On 앱으로 인식 → 창 아이콘 표시."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "CHA.SizeOn." + __version__)
    except Exception:
        pass


def _first_run_dialog():
    """최초 실행 설치 마법사 — EULA 동의 → 반환: 'install'|'run'|'cancel'."""
    root = tk.Tk()
    root.title(f"{APP_NAME} · {tr('eula_title')}")
    root.configure(bg=BG)
    apply_icon(root)
    root.resizable(False, False)
    res = {"a": "cancel"}
    agree = tk.BooleanVar(value=False)
    box = tk.Frame(root, bg=BG)
    box.pack(fill="both", expand=True)

    def do(a):
        res["a"] = a
        root.destroy()

    def try_install():
        if agree.get():
            do("install")
        else:
            messagebox.showwarning(APP_NAME, tr("eula_need"))

    def render():
        for w in box.winfo_children():
            w.destroy()
        top = tk.Frame(box, bg=BG)
        top.pack(fill="x", padx=22, pady=(16, 4))
        tk.Label(top, text=tr("eula_title"), bg=BG, fg=FG,
                 font=(UIFONT, 15, "bold")).pack(side="left")
        lang = tk.Label(top, text=tr("lang_toggle"), bg=ACCENT, fg="#ffffff",
                        font=(UIFONT, 10, "bold"), padx=10, pady=4, cursor="hand2")
        lang.pack(side="right")
        lang.bind("<Button-1>",
                  lambda e: (i18n.toggle(), installer.save_lang(i18n.current()), render()))
        txt = tk.Text(box, width=62, height=15, bg=SOFT, fg="#dddddd", bd=0,
                      wrap="word", font=(UIFONT, 10), padx=12, pady=10)
        txt.insert("1.0", EULA_TEXT.get(i18n.current(), EULA_TEXT["ko"]))
        txt.config(state="disabled")
        txt.pack(padx=22, pady=4)
        tk.Checkbutton(box, text=tr("eula_agree"), variable=agree, bg=BG, fg="#dddddd",
                       selectcolor=SOFT, activebackground=BG, activeforeground="#ffffff",
                       font=(UIFONT, 11)).pack(anchor="w", padx=24, pady=(8, 2))
        btns = tk.Frame(box, bg=BG)
        btns.pack(fill="x", padx=22, pady=(8, 18))
        flat_btn(btns, tr("eula_install"), try_install, primary=True).pack(side="right")
        flat_btn(btns, tr("eula_runonly"), lambda: do("run")).pack(side="right", padx=(0, 8))
        flat_btn(btns, tr("btn_close"), lambda: do("cancel")).pack(side="left")

    render()
    root.bind("<Escape>", lambda e: do("cancel"))
    root.eval("tk::PlaceWindow . center")
    root.mainloop()
    return res["a"]


def main():
    global UIFONT
    # 설치본 제거 요청(--uninstall)
    if "--uninstall" in sys.argv:
        installer.do_uninstall()
        return
    _set_app_id()
    dpi.enable_dpi_awareness()
    dpi.load_calib()
    fonts.register()
    UIFONT = fonts.family()
    _saved_lang = installer.load_lang()  # 저장된 UI 언어 복원
    if _saved_lang:
        i18n.set_lang(_saved_lang)
    # exe(frozen) + 미설치 상태면 최초 실행 설치 마법사
    if installer.is_frozen() and not installer.is_installed():
        action = _first_run_dialog()
        if action == "cancel":
            return
        if action == "install":
            dst = installer.do_install(__version__)
            installer.launch(dst)
            return
        # 'run' → 설치 없이 계속 실행
    app = SizeOn()
    app._tray = tray.Tray(app)
    app._tray.start()
    app.mainloop()


if __name__ == "__main__":
    main()
