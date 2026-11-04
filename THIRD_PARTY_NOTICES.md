# Third-Party Open-Source Notices — CyberNotes

**CyberNotes** is copyright © 2026 **Kandula Paul Saketh Maurya** (`@MauryaKandula`) and licensed under the **MIT License**.

This software utilizes or interacts with the following third-party open-source packages and runtime components:

---

## 1. Python Standard Library (`Python 3.10+`)
- **Maintainer**: Python Software Foundation (PSF)
- **License**: Python Software Foundation License v2 (PSF-2.0)
- **Modules Used**: `sqlite3`, `ctypes`, `pathlib`, `re`, `json`, `uuid`, `datetime`, `unittest`
- **URL**: https://www.python.org/

## 2. PyQt6 / Qt6 Cross-Platform GUI Toolkit (`PyQt6 >= 6.5.0`)
- **Maintainer**: Riverbank Computing Limited / The Qt Company
- **License**: GNU General Public License v3 (GPL-3.0) / Qt Commercial License
- **Usage**: Dynamically imported via standard Python package bindings (`PyQt6.QtWidgets`, `PyQt6.QtCore`, `PyQt6.QtGui`) for hardware-accelerated desktop window rendering and animations. No PyQt6 or Qt source code is modified or statically linked inside this source repository.
- **URL**: https://www.riverbankcomputing.com/software/pyqt/

## 3. Pillow — Python Imaging Library Fork (`Pillow >= 10.0.0`, Development/Asset Build)
- **Maintainer**: Jeffrey A. Clark (Alex) and contributors
- **License**: MIT-CMU Permissive License
- **Usage**: Used by `generate_icons.py` during asset generation to rasterize multi-layer `.ico` (`16px`–`256px`) and `.png` application icons.
- **URL**: https://python-pillow.org/

## 4. SQLite (`sqlite3` Embedded Engine)
- **Maintainer**: D. Richard Hipp and the SQLite Consortium
- **License**: Public Domain
- **Usage**: Local ACID-compliant storage (`WAL` mode) for user notes and metadata.
- **URL**: https://www.sqlite.org/copyright.html

## 5. PyInstaller (Optional Standalone Executable Packaging)
- **Maintainer**: PyInstaller Development Team
- **License**: GPLv2 with special exception allowing unrestricted distribution of bundled executables (`PyInstaller Bootloader Exception`).
- **Usage**: Invoked optionally via `build_exe.bat` to package `CyberNotes` into a standalone Windows `.exe`.
- **URL**: https://pyinstaller.org/
