"""다국어 문자열 — LANGUAGES 상단 명시, tr()로 조회."""
LANGUAGES = ["ko", "en"]
_lang = "ko"

_TR = {
    "hint":         {"ko": "숫자 더블클릭 → 입력 · 창 드래그로도 조절", "en": "Double-click a number to type · or drag to resize"},
    "edit_unit":    {"ko": "입력 단위", "en": "Input unit"},
    "btn_area":     {"ko": "영역 측정 / 캡처", "en": "Measure/Area"},
    "btn_fixed":    {"ko": "지정 크기 캡처", "en": "Fixed"},
    "btn_full":     {"ko": "전체화면 캡처", "en": "Full"},
    "btn_calib":    {"ko": "보정", "en": "Calibrate"},
    "eula_title":   {"ko": "Size On 설치", "en": "Install Size On"},
    "eula_agree":   {"ko": "위 사용권 계약에 동의합니다", "en": "I agree to the license agreement"},
    "eula_install": {"ko": "동의 후 설치", "en": "Agree & Install"},
    "eula_runonly": {"ko": "설치 없이 실행", "en": "Run without installing"},
    "eula_need":    {"ko": "설치하려면 먼저 동의에 체크하세요.", "en": "Please check agreement to install."},
    "donate_title": {"ko": "개발 지원", "en": "Support"},
    "donate_choose":{"ko": "유용하셨다면 ❤️  개발을 응원해 주세요", "en": "If this helped ❤️  please support development"},
    "btn_survey":   {"ko": "📝 설문 참여 (의견 보내기)", "en": "📝 Take the survey"},
    "btn_donate":   {"ko": "☕ Buy Me a Coffee", "en": "☕ Buy Me a Coffee"},
    "btn_close":    {"ko": "닫기", "en": "Close"},
    "calib_title":  {"ko": "물리 크기 보정", "en": "Physical Calibration"},
    "calib_cur":    {"ko": "현재 유효 PPI: {eff}  ·  시스템 DPI: {sysd}",
                     "en": "Effective PPI: {eff}  ·  System DPI: {sysd}"},
    "calib_none":   {"ko": "미보정(시스템)", "en": "none (system)"},
    "calib_reset":  {"ko": "초기화", "en": "Reset"},
    "calib_tab_auto": {"ko": "자동(EDID)", "en": "Auto (EDID)"},
    "calib_auto_desc": {"ko": "연결된 모니터의 EDID에서 물리 크기를 읽어 PPI를 자동 산출합니다. (단일 모니터·정상 EDID 기준)",
                        "en": "Reads physical size from the monitor's EDID to compute PPI automatically. (single monitor, valid EDID)"},
    "calib_auto_found": {"ko": "감지: {man} {prod}  ·  {hmm}×{vmm} mm  ·  {hpx}×{vpx} px\n산출 PPI: {ppi:.1f}",
                         "en": "Detected: {man} {prod}  ·  {hmm}×{vmm} mm  ·  {hpx}×{vpx} px\nComputed PPI: {ppi:.1f}"},
    "calib_auto_fail": {"ko": "EDID를 읽지 못했거나 물리 크기 정보가 없습니다. 아래 수동 방식(기준선/카드/대각선)을 사용하세요.",
                        "en": "Could not read EDID or physical size is missing. Use a manual method (line/card/diagonal) instead."},
    "calib_tab_a":  {"ko": "기준선 실측", "en": "Reference Line"},
    "calib_tab_b":  {"ko": "카드 맞추기", "en": "Card Match"},
    "calib_tab_c":  {"ko": "대각선+해상도", "en": "Diagonal+Res"},
    "calib_a_desc": {"ko": "슬라이더로 선 길이를 조절한 뒤, 그 선의 실제 길이를 자로 재서 mm로 입력하세요. (길수록 정확)",
                     "en": "Adjust the line length with the slider, then measure it with a ruler and enter mm. (longer = more accurate)"},
    "calib_a_len":  {"ko": "선 길이: {px} px", "en": "Line length: {px} px"},
    "calib_a_input":{"ko": "실측 길이(mm)", "en": "Measured (mm)"},
    "calib_b_desc": {"ko": "실물 신용카드(폭 85.6mm)를 화면 사각형에 맞을 때까지 슬라이더로 조절하세요.",
                     "en": "Adjust the slider until a real credit card (85.6mm wide) matches the rectangle."},
    "calib_b_live": {"ko": "폭 {px}px → PPI {ppi:.1f}", "en": "Width {px}px → PPI {ppi:.1f}"},
    "calib_c_desc": {"ko": "모니터 대각선(인치)과 해상도를 입력하세요. (베젤·비표준 비율서 오차 가능)",
                     "en": "Enter monitor diagonal (inch) and resolution. (bezel/non-standard ratio may cause error)"},
    "calib_c_diag": {"ko": "대각선(inch)", "en": "Diagonal (inch)"},
    "calib_c_res":  {"ko": "해상도(px)", "en": "Resolution (px)"},
    "calib_apply":  {"ko": "적용", "en": "Apply"},
    "calib_saved":  {"ko": "보정 완료 · PPI {ppi:.1f} 저장", "en": "Calibrated · PPI {ppi:.1f} saved"},
    "calib_reset_done": {"ko": "보정 초기화 — 시스템 DPI 사용", "en": "Reset — using system DPI"},
    "fixed_hint":   {"ko": "마우스로 위치 이동 · 방향키 미세이동(Shift 10px) · Tab 색상 변경 · 클릭 캡처 · ESC 취소",
                     "en": "Move with mouse · arrows to nudge (Shift 10px) · Tab to change color · click to capture · ESC to cancel"},
    "warn_clamp":   {"ko": "지정 크기가 화면보다 커서 {w}×{h} px로 축소했습니다",
                     "en": "Requested size exceeds screen; clamped to {w}×{h} px"},
    "btn_resize":   {"ko": "리사이즈", "en": "Resize"},
    "w_prefix":     {"ko": "가로  ", "en": "W  "},
    "h_prefix":     {"ko": "세로  ", "en": "H  "},
    "dpi_note":     {"ko": "DPI {d} · mm/in은 시스템 DPI 기준 근사치",
                     "en": "DPI {d} · mm/in are approximate (system DPI)"},
    "author":       {"ko": "제작: Shugle(슈글)", "en": "By Shugle"},
    "overlay_hint": {"ko": "드래그하여 측정  ·  S · Enter · 더블클릭 캡처  ·  ESC 종료",
                     "en": "Drag to measure  ·  S · Enter · Double-click to capture  ·  ESC to exit"},
    "preview_title": {"ko": "캡처 미리보기", "en": "Capture Preview"},
    "cap_size":     {"ko": "캡처 크기   {w} × {h} px", "en": "Capture size   {w} × {h} px"},
    "verify_ok":    {"ko": "좌표 정확 ✔  (선택 = 캡처 일치)",
                     "en": "Coordinates accurate ✔ (selection = capture)"},
    "verify_warn":  {"ko": "⚠ 선택 {ew}×{eh} ≠ 캡처 {w}×{h} — DPI 배율 보정 필요",
                     "en": "⚠ selection {ew}×{eh} ≠ capture {w}×{h} — DPI scaling correction needed"},
    "btn_save":     {"ko": "저장", "en": "Save"},
    "btn_cancel":   {"ko": "취소", "en": "Cancel"},
    "saved":        {"ko": "저장됨:\n", "en": "Saved:\n"},
    "err_num":      {"ko": "W, H에 숫자를 입력하세요.", "en": "Enter numbers for W and H."},
    "err_pos":      {"ko": "0보다 큰 값을 입력하세요.", "en": "Enter values greater than 0."},
    "err_pillow":   {"ko": "Pillow 미설치.\n명령: pip install pillow",
                     "en": "Pillow not installed.\nRun: pip install pillow"},
    "tray_open":    {"ko": "열기", "en": "Open"},
    "tray_exit":    {"ko": "종료", "en": "Exit"},
    "lang_toggle":  {"ko": "EN", "en": "한국어"},
}


def set_lang(lang):
    global _lang
    if lang in LANGUAGES:
        _lang = lang


def current():
    return _lang


def toggle():
    global _lang
    i = LANGUAGES.index(_lang)
    _lang = LANGUAGES[(i + 1) % len(LANGUAGES)]
    return _lang


def tr(key, **kw):
    s = _TR.get(key, {}).get(_lang, key)
    return s.format(**kw) if kw else s
