<div align="center">
  <img src="assets/cybernotes.svg" alt="CyberNotes Logo" width="128" height="128" />
  <h1>✨ CyberNotes v2.1.0</h1>
  <p><b>Modern, Ultra-Smooth Hardware-Accelerated Neon Sticky Notes for Windows</b></p>

[![License: MIT](https://img.shields.io/badge/License-MIT-00F0FF.svg)](./LICENSE)
[![Version: 2.1.0](https://img.shields.io/badge/Version-2.1.0-00F59B.svg)](https://github.com/MauryaKandula/cyber-notes/releases/tag/v2.1.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-FFE600.svg)](https://www.python.org/)
[![UI: PyQt6](https://img.shields.io/badge/UI-PyQt6%20Hardware%20Accelerated-FF2A85.svg)](https://pypi.org/project/PyQt6/)
[![Author](https://img.shields.io/badge/Created%20by-Kandula%20Paul%20Saketh%20Maurya-B845FF.svg)](https://github.com/MauryaKandula)

</div>

---

**CyberNotes** is a fast, minimal, hardware-accelerated desktop sticky notes application with a sleek Cyberpunk neon aesthetic. Designed and created by **Kandula Paul Saketh Maurya** ([@MauryaKandula](https://github.com/MauryaKandula)).

It combines the effortless simplicity of Apple Stickies and Windows Sticky Notes with smooth 144Hz/240Hz OS-compositor window movement, animated glass surfaces, a gliding neon caret, live syntax highlighting for links and tags, tactile spring animations, rich-text formatting, and freehand neon ink drawing.

---

## 🌟 Key Features

- **144Hz+ Native Compositor Smoothness**: Uses native window manager move and 8-edge resize hooks (`startSystemMove` / `startSystemResize`) for zero-latency dragging across high-refresh-rate monitors.
- **Native Sticky Notes Lifecycle**: Automatically restores your open sticky notes when Windows boots (`--startup`), and keeps floating sticky notes open on your desktop when you close the main `All Notes` list window.
- **Gliding & Breathing Neon Caret**: Smoothly interpolated glowing cursor (`85ms` `OutCubic`) with idle breathing aura (`950ms` `InOutSine`) and active-line ambient illumination.
- **Live Link & Tag Highlighter**: Real-time inline highlighting for `https://` URLs and `#tags` alongside 1-click smart action pills (`↗` open in browser, right-click to copy).
- **Tactile Click Ripple & Spring Animations**: Radial neon click ripples and physics-inspired spring-eased transitions across note headers, color orbs, and formatting controls.
- **7 Cyberpunk Neon Color Themes**:
  - **Neon Yellow** (`#FFE600`) • **Cyber Cyan** (`#00F0FF`) • **Electric Pink** (`#FF2A85`) • **Neon Violet** (`#B845FF`) • **Neon Mint** (`#00F59B`) • **Frost Silver** (`#E2F1FF`) • **Crimson Glow** (`#FF3B5C`)
- **Rich-Text Formatting & Freehand Neon Ink (`✎ Draw`)**: Bold, Italic, Underline, Strikethrough, Bullet Lists, and smooth quadratic-curve vector ink drawing.
- **Local AppData SQLite WAL Storage**: Instant, crash-safe local persistence in `%LOCALAPPDATA%\CyberNotes\plum.sqlite` with 1-click import from Windows Sticky Notes.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + N` | Create a new sticky note |
| `Ctrl + B` | Toggle **Bold** text |
| `Ctrl + I` | Toggle *Italic* text |
| `Ctrl + U` | Toggle <u>Underline</u> text |
| `Ctrl + T` | Toggle ~~Strikethrough~~ text |
| `Ctrl + Shift + L` | Toggle `• Bullet List` |

---

## 🚀 Quick Start & Installation

### Option 1: Download Standalone Windows Executable
Download **`CyberNotes.exe`** directly from the [Latest Release (`v2.1.0`)](https://github.com/MauryaKandula/cyber-notes/releases/tag/v2.1.0).

### Option 2: Run from Source
```bash
git clone https://github.com/MauryaKandula/cyber-notes.git
cd cyber-notes
pip install -r requirements.txt
python cyber_notes.py
```
Or install as a package:
```bash
pip install -e .
cybernotes
```

---

## 🧪 Running Unit Tests

```bash
python test_cyber_notes.py -v
```

---

## ⚖️ License, Clean-Room Provenance & Security

- **Author & Copyright**: © 2026 **Kandula Paul Saketh Maurya** ([@MauryaKandula](https://github.com/MauryaKandula) | `mauryakpsofficial@gmail.com`).
- **License**: Released under the [MIT License](./LICENSE).
- **Clean-Room & Data Interoperability Notice**: CyberNotes is an original, clean-room software implementation written in Python and PyQt6. Optional database import interoperability with local SQLite note schemas is provided strictly for user data portability under 17 U.S.C. § 102(b) and 17 U.S.C. § 117. Microsoft, Windows, and Microsoft Sticky Notes are trademarks of Microsoft Corporation, which is not affiliated with or endorsing this project.
- **Third-Party Open-Source Notices**: Uses `PyQt6` (GPLv3 / Riverbank Computing), `SQLite3` (Public Domain), and `Python Standard Library` (PSF-2.0).
- **Security**: All notes are stored 100% locally on your device (`%LOCALAPPDATA%\CyberNotes\plum.sqlite`) with zero telemetry or cloud transmission. Report security issues to `mauryakpsofficial@gmail.com`.
