# Security Policy

## Supported Versions

Only the latest stable release of **CyberNotes** receives active security updates and patches.

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Data & Privacy Architecture

- **100% Local Persistence**: CyberNotes stores all note contents, formatting spans, and vector ink strokes locally in a crash-safe SQLite WAL database (`plum.sqlite`) on the user's machine.
- **Zero Telemetry**: CyberNotes does not transmit user notes, analytics, or telemetry over the network.
- **Safe External Link Handling**: Clicked links and phone numbers are delegated strictly through the operating system's registered handler (`QDesktopServices.openUrl`) after explicit user interaction.

## Reporting a Vulnerability

If you discover a security vulnerability in **CyberNotes**, please report it responsibly rather than opening a public GitHub issue:

- **Maintainer**: Kandula Paul Saketh Maurya ([@MauryaKandula](https://github.com/MauryaKandula))
- **Email**: [mauryakpsofficial@gmail.com](mailto:mauryakpsofficial@gmail.com)

Please include:
1. A clear description of the vulnerability and its potential impact.
2. Steps or proof-of-concept code to reproduce the issue.
3. Your operating system and Python / PyQt6 version.

You will receive an acknowledgment within **48 hours**, and a fix or mitigation plan will be coordinated promptly before public disclosure.
