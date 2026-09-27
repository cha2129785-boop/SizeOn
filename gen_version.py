# -*- coding: utf-8 -*-
"""main.py의 __version__을 읽어 PyInstaller용 version_info.txt 생성."""
import re
import pathlib

root = pathlib.Path(__file__).parent
src = (root / "main.py").read_text(encoding="utf-8")
m = re.search(r'__version__\s*=\s*"([\d.]+)"', src)
ver = m.group(1) if m else "0.0.0"
parts = (ver.split(".") + ["0", "0", "0", "0"])[:4]
v = ", ".join(parts)  # 예: 0, 0, 38, 0

VINFO = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v}),
    prodvers=({v}),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'Shugle'),
        StringStruct('FileDescription', 'Size On - window/area size measure & capture'),
        StringStruct('FileVersion', '{ver}'),
        StringStruct('InternalName', 'Size On'),
        StringStruct('LegalCopyright', 'Copyright (c) 2026 Shugle. MIT License.'),
        StringStruct('OriginalFilename', 'Size On.exe'),
        StringStruct('ProductName', 'Size On'),
        StringStruct('ProductVersion', '{ver}')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [0x0409, 1200])])
  ]
)
"""
(root / "version_info.txt").write_text(VINFO, encoding="utf-8")
print("version_info.txt written:", ver)
