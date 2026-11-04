# Changelog

All notable changes to **CyberNotes** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-11-04

### Added
- **Gliding Neon Caret**: Hardware-accelerated custom glowing text cursor with smooth position interpolation, breathing neon aura, and adaptive color theming.
- **Live Link & Tag Highlighter (`CyberHighlighter`)**: Real-time `QSyntaxHighlighter` highlighting `https://` URLs, `#tags`, and `@mentions` directly inside sticky notes with cyberpunk accent styling.
- **Tactile Click Ripple & Spring Animations**: Interactive radial neon ripple feedback (`ClickRippleOverlay`) and physical spring-eased hover/press micro-animations across toolbar and header controls.
- **Multi-Resolution Brand & Icon Suite**: Official vector badge (`assets/cybernotes.svg`), high-DPI raster icons (`assets/cybernotes_256.png`, `assets/cybernotes_512.png`), and multi-frame Windows icon (`assets/cybernotes.ico` containing 16x16 through 256x256 PNG-compressed layers).
- **Native Windows Taskbar Identity (`AppUserModelID`)**: Explicit `SetCurrentProcessExplicitAppUserModelID("KandulaPaulSakethMaurya.CyberNotes.Desktop.2")` binding so CyberNotes displays its own neon icon in the Windows Taskbar, Alt+Tab switcher, and System Tray instead of grouping under `python.exe`.
- **Release & Governance Metadata**: Added `CITATION.cff`, `SECURITY.md`, `CHANGELOG.md`, `version_info.txt`, and GitHub Actions CI workflow (`.github/workflows/ci.yml`).

### Changed
- Updated `setup_app.bat` to bind `assets\cybernotes.ico` to both Windows Desktop and Start Menu shortcuts (`CyberNotes.lnk`).
- Bumped package version to `2.1.0` across `pyproject.toml`, `setup.py`, and Windows resource definitions.

## [2.0.0] - 2026-11-04

### Added
- **Initial PyQt6 Hardware-Accelerated Release**: Complete desktop sticky notes engine designed and created by **Kandula Paul Saketh Maurya** (`@MauryaKandula`).
- **144Hz/240Hz Native Window Movement & Resize**: Direct OS compositor move and 8-edge resize via `startSystemMove()` and `startSystemResize()`.
- **7 Cyberpunk Neon Color Themes**: Neon Yellow, Cyber Cyan, Electric Pink, Neon Violet, Neon Mint, Frost Silver, and Crimson Glow.
- **Rich-Text Formatting & Lists**: Bold, Italic, Underline, Strikethrough, and Bullet Lists with keyboard shortcuts (`Ctrl+B`, `Ctrl+I`, `Ctrl+U`, `Ctrl+T`, `Ctrl+Shift+L`).
- **Freehand Neon Ink Mode (`✎ Draw`)**: Smooth quadratic-curve vector ink sketching over sticky notes.
- **Smart Link & Phone Action Pills**: Automatic detection and 1-click launch buttons for URLs and phone numbers.
- **Crash-Safe SQLite WAL Storage**: Debounced auto-save persistence in `plum.sqlite` with system tray integration.
