# ✨ CyberNotes

[![License: MIT](https://img.shields.io/badge/License-MIT-00F0FF.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-FFE600.svg)](https://www.python.org/)
[![UI: PyQt6](https://img.shields.io/badge/UI-PyQt6%20Hardware%20Accelerated-FF2A85.svg)](https://pypi.org/project/PyQt6/)
[![Author](https://img.shields.io/badge/Created%20by-Kandula%20Paul%20Saketh%20Maurya-B845FF.svg)](https://github.com/MauryaKandula)

**CyberNotes** is a fast, minimal, hardware-accelerated desktop sticky notes application with a sleek Cyberpunk neon aesthetic. Designed and created by **Kandula Paul Saketh Maurya** ([@MauryaKandula](https://github.com/MauryaKandula)).

It combines the effortless simplicity of Apple Stickies and Windows Sticky Notes with smooth 144Hz/240Hz OS-compositor window movement, animated glass surfaces, rich-text formatting, and freehand neon ink drawing.

---

## 🌟 Key Features

- **144Hz+ Native Compositor Smoothness**: Uses native window manager move and 8-edge resize hooks (`startSystemMove` / `startSystemResize`) for zero-latency dragging across high-refresh-rate monitors.
- **Spacious, Minimal Glass UI**: Anti-aliased rounded dark-glass surfaces (`16px` radius), ambient drop shadows, and smooth `QPropertyAnimation` / `QVariantAnimation` transitions.
- **7 Cyberpunk Neon Color Themes**:
  - **Neon Yellow** (`#FFE600`)
  - **Cyber Cyan** (`#00F0FF`)
  - **Electric Pink** (`#FF2A85`)
  - **Neon Violet** (`#B845FF`)
  - **Neon Mint** (`#00F59B`)
  - **Frost Silver** (`#E2F1FF`)
  - **Crimson Glow** (`#FF3B5C`)
- **Rich-Text Formatting & Lists**: Bold, Italic, Underline, Strikethrough, and Bullet Lists with instant keyboard shortcuts.
- **Freehand Neon Ink Mode (`✎ Draw`)**: Sketch smooth quadratic-curve vector ink notes directly over any sticky note.
- **Smart Link & Phone Actions**: Automatically detects URLs and phone numbers and surfaces 1-click action pills.
- **Local SQLite WAL Storage**: Instant, crash-safe local persistence (`plum.sqlite`) with debounced auto-save and optional 1-click import from existing sticky notes databases.
- **System Tray Integration**: Lives quietly in the system tray for instant note creation and management.

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

### 1. Clone the Repository
```bash
git clone https://github.com/MauryaKandula/cyber-notes.git
cd cyber-notes
```

### 2. One-Click Windows Setup
Run the included setup script to install dependencies and create a Desktop shortcut:
```bat
setup_app.bat
```

### 3. Manual Python Installation
```bash
pip install -r requirements.txt
python cyber_notes.py
```
Or install as a global CLI/GUI package:
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

## 📄 Legal & License

- **Author**: **Kandula Paul Saketh Maurya** ([@MauryaKandula](https://github.com/MauryaKandula))
- **License**: Released under the [MIT License](./LICENSE). See [`NOTICE.md`](./NOTICE.md) for full open-source declaration.
