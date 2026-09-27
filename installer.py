"""앱 내장 최초 실행 설치 — self-install(LOCALAPPDATA 복사 + 바로가기 + HKCU 앱 목록).
   exe(frozen)에서만 동작. run.pyw(개발)에선 무시."""
import os
import sys
import json
import shutil
import subprocess

APP = "Size On"
_NOWIN = 0x08000000  # CREATE_NO_WINDOW


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def _appdata_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "SizeOn")


def _cfg_path() -> str:
    return os.path.join(_appdata_dir(), "config.json")


def install_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "Programs", "Size On")


def installed_exe() -> str:
    return os.path.join(install_dir(), "Size On.exe")


def _load_cfg() -> dict:
    try:
        with open(_cfg_path(), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_cfg(d: dict) -> None:
    os.makedirs(_appdata_dir(), exist_ok=True)
    with open(_cfg_path(), "w", encoding="utf-8") as f:
        json.dump(d, f)


def is_installed() -> bool:
    return os.path.normcase(sys.executable) == os.path.normcase(installed_exe())


def load_lang():
    return _load_cfg().get("lang")


def save_lang(lang: str) -> None:
    c = _load_cfg()
    c["lang"] = lang
    _save_cfg(c)


def load_color():
    return _load_cfg().get("overlay_color")


def save_color(hex_color: str) -> None:
    c = _load_cfg()
    c["overlay_color"] = hex_color
    _save_cfg(c)


def eula_accepted() -> bool:
    return bool(_load_cfg().get("eula"))


def set_eula() -> None:
    c = _load_cfg()
    c["eula"] = True
    _save_cfg(c)


def _shortcuts(exe: str) -> None:
    ps = (
        "$W=New-Object -ComObject WScript.Shell;$E='%s';$D='%s';"
        "foreach($p in @([Environment]::GetFolderPath('Desktop'),"
        "[Environment]::GetFolderPath('StartMenu')+'\\Programs')){"
        "$l=$W.CreateShortcut((Join-Path $p 'Size On.lnk'));$l.TargetPath=$E;"
        "$l.WorkingDirectory=$D;$l.IconLocation=$E+',0';$l.Save()}"
        % (exe, os.path.dirname(exe))
    )
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-Command", ps], creationflags=_NOWIN, timeout=15)
    except Exception:
        pass


def _reg_uninstall(exe: str, version: str) -> None:
    try:
        import winreg
    except ImportError:
        return
    key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SizeOn"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key) as k:
        def s(n, v):
            winreg.SetValueEx(k, n, 0, winreg.REG_SZ, v)

        def d(n, v):
            winreg.SetValueEx(k, n, 0, winreg.REG_DWORD, v)
        s("DisplayName", "Size On")
        s("DisplayVersion", version)
        s("Publisher", "Shugle")
        s("DisplayIcon", exe)
        s("InstallLocation", os.path.dirname(exe))
        s("UninstallString", '"%s" --uninstall' % exe)
        d("NoModify", 1)
        d("NoRepair", 1)


def do_install(version: str) -> str:
    """self-copy → 바로가기 → 레지스트리 → EULA 기록. 설치본 경로 반환."""
    dst = installed_exe()
    os.makedirs(install_dir(), exist_ok=True)
    if os.path.normcase(sys.executable) != os.path.normcase(dst):
        shutil.copy2(sys.executable, dst)
    _shortcuts(dst)
    _reg_uninstall(dst, version)
    set_eula()
    return dst


def launch(path: str) -> None:
    try:
        subprocess.Popen([path])
    except Exception:
        try:
            os.startfile(path)  # noqa
        except Exception:
            pass


def do_uninstall() -> None:
    """바로가기·레지스트리 삭제 후 설치 폴더 자기삭제."""
    ps = ("foreach($p in @([Environment]::GetFolderPath('Desktop'),"
          "[Environment]::GetFolderPath('StartMenu')+'\\Programs')){"
          "$l=Join-Path $p 'Size On.lnk'; if(Test-Path $l){Remove-Item $l -Force}}")
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-Command", ps], creationflags=_NOWIN, timeout=15)
    except Exception:
        pass
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SizeOn")
    except Exception:
        pass
    try:
        subprocess.Popen('cmd /c timeout /t 1 >nul & rmdir /s /q "%s"' % install_dir(),
                         shell=True, creationflags=_NOWIN)
    except Exception:
        pass
