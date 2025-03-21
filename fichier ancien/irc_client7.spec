# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Utiliser le répertoire courant comme base
current_dir = os.getcwd()

# Collect data files from the 'irc' package
datas = collect_data_files('irc')

# Add other data files
datas += [
    (os.path.join(current_dir, 'users.json'), '.'),
    (os.path.join(current_dir, 'cards.json'), '.'),
    (os.path.join(current_dir, 'selected_cards.json'), '.'),
    (os.path.join(current_dir, 'Img', '*'), 'Img'),
    (os.path.join(current_dir, 'test_jeux_tt2.py'), '.'),
    (os.path.join(current_dir, 'irc_client7.py'), '.'),
    (os.path.join(current_dir, 'ai_logic.py'), '.'),
    (os.path.join(current_dir, 'capture_manager.py'), '.'),
    (os.path.join(current_dir, 'drawing.py'), '.'),
    (os.path.join(current_dir, 'gamelogic.py'), '.'),
    (os.path.join(current_dir, 'inventory_manager.py'), '.'),
    (os.path.join(current_dir, 'rules.py'), '.'),
    (os.path.join(current_dir, 'ai.py'), '.'),
    (os.path.join(current_dir, 'utils.py'), '.'),
    (os.path.join(current_dir, 'bgm.mp3'), '.'),
    (os.path.join(current_dir, 'sound-turn.wav'), '.'),
]

a = Analysis(
    ['irc_client7.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pygame',
        'PyQt5',
        'zmq',
        'irc.client',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='irc_client7',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='irc_client7',
)
