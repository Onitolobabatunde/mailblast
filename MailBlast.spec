# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files

datas, binaries, hiddenimports = [], [], []

for pkg in ('PyQt6', 'cryptography'):
    d, b, h = collect_all(pkg)
    datas     += d
    binaries  += b
    hiddenimports += h

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + [
        'cryptography.fernet',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.backends.openssl.backend',
        'cryptography.hazmat.primitives.ciphers',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'email.mime.text',
        'email.mime.multipart',
        'email.mime.base',
        'email.encoders',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MailBlast Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MailBlast Pro',
)

app = BUNDLE(
    coll,
    name='MailBlast Pro.app',
    icon=None,
    bundle_identifier='com.mailblast.pro',
    info_plist={
        'CFBundleName':               'MailBlast Pro',
        'CFBundleDisplayName':        'MailBlast Pro',
        'CFBundleVersion':            '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSPrincipalClass':           'NSApplication',
        'NSHighResolutionCapable':    True,
        'NSSupportsAutomaticGraphicsSwitching': True,
        'NSAppleScriptEnabled':       False,
        'LSMinimumSystemVersion':     '11.0',
        'LSApplicationCategoryType':  'public.app-category.productivity',
        'NSHumanReadableCopyright':   'Copyright © 2025 MailBlast Pro',
    },
)
