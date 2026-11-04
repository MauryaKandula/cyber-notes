#!/usr/bin/env python3
"""
Official Multi-Resolution App Icon Generator for CyberNotes
Author: Kandula Paul Saketh Maurya (@MauryaKandula)
Generates:
- assets/cybernotes.ico (Multi-resolution 16, 24, 32, 48, 64, 128, 256px Windows Icon)
- assets/cybernotes_256.png (256x256 High-DPI PNG)
- assets/cybernotes_512.png (512x512 App Store / GitHub Social Preview PNG)
- assets/cybernotes.svg (Scalable Vector Graphics Icon)
"""

import os
import struct
import sys
from PyQt6.QtCore import QBuffer, QIODevice, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)


def render_cybernotes_master_image(size: int) -> QImage:
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    s = float(size)
    pad = s * 0.08
    card_w = s - 2 * pad
    card_h = s - 2 * pad
    radius = s * 0.21
    fold = s * 0.19

    # 1. Outer soft ambient drop shadow
    shadow_rect = QRectF(pad, pad + s * 0.025, card_w, card_h)
    shadow_path = QPainterPath()
    shadow_path.addRoundedRect(shadow_rect, radius, radius)
    p.fillPath(shadow_path, QColor(0, 0, 0, 115))

    # 2. Sticky Note Body with bottom-right folded corner clip
    rect = QRectF(pad, pad, card_w, card_h)
    full_round = QPainterPath()
    full_round.addRoundedRect(rect, radius, radius)

    cut_poly = QPolygonF(
        [
            QPointF(rect.left() - 10, rect.top() - 10),
            QPointF(rect.right() + 10, rect.top() - 10),
            QPointF(rect.right() + 10, rect.bottom() - fold),
            QPointF(rect.right() - fold, rect.bottom() + 10),
            QPointF(rect.left() - 10, rect.bottom() + 10),
        ]
    )
    cut_path = QPainterPath()
    cut_path.addPolygon(cut_poly)
    note_path = full_round.intersected(cut_path)

    # Deep Obsidian-Slate Gradient Background
    bg_grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    bg_grad.setColorAt(0.0, QColor("#1D2230"))
    bg_grad.setColorAt(0.55, QColor("#121620"))
    bg_grad.setColorAt(1.0, QColor("#0B0D14"))
    p.fillPath(note_path, bg_grad)

    # Ambient top-left cyan/yellow radial glow inside the card
    glow = QRadialGradient(QPointF(rect.left() + card_w * 0.3, rect.top() + card_h * 0.25), card_w * 0.7)
    glow.setColorAt(0.0, QColor(0, 240, 255, 38))
    glow.setColorAt(1.0, QColor(0, 0, 0, 0))
    p.fillPath(note_path, glow)

    # 3. Top Neon Yellow Sticky Header Strip
    p.save()
    p.setClipPath(note_path)
    hdr_h = s * 0.165
    hdr_grad = QLinearGradient(rect.topLeft(), QPointF(rect.right(), rect.top()))
    hdr_grad.setColorAt(0.0, QColor("#FFE600"))
    hdr_grad.setColorAt(1.0, QColor("#00F0FF"))
    p.fillRect(QRectF(rect.left(), rect.top(), rect.width(), hdr_h), hdr_grad)
    p.restore()

    # 4. Crisp Neon Border around the Note
    border_grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    border_grad.setColorAt(0.0, QColor("#FFE600"))
    border_grad.setColorAt(0.5, QColor("#00F0FF"))
    border_grad.setColorAt(1.0, QColor("#FF2A85"))
    pen_w = max(1.2, s * 0.032)
    p.setPen(QPen(border_grad, pen_w))
    p.drawPath(note_path)

    # 5. Bottom-Right Folded Sticky Corner Flap
    flap_path = full_round.subtracted(note_path)
    flap_grad = QLinearGradient(
        QPointF(rect.right() - fold, rect.bottom() - fold),
        QPointF(rect.right(), rect.bottom()),
    )
    flap_grad.setColorAt(0.0, QColor("#00F0FF"))
    flap_grad.setColorAt(1.0, QColor("#FF2A85"))
    p.fillPath(flap_path, flap_grad)

    # Fold crease highlight
    crease = QPainterPath()
    crease.moveTo(rect.right() - fold, rect.bottom())
    crease.quadTo(
        rect.right() - fold,
        rect.bottom() - fold * 0.85,
        rect.right(),
        rect.bottom() - fold,
    )
    p.setPen(QPen(QColor("#FFE600"), max(1.0, s * 0.025), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawPath(crease)

    # 6. Glowing Note Lines + Checkmark Bullet inside the card
    line_w = max(1.5, s * 0.058)
    x_left = rect.left() + card_w * 0.20
    y1 = rect.top() + card_h * 0.42
    y2 = rect.top() + card_h * 0.58
    y3 = rect.top() + card_h * 0.74

    # Line 1 (Neon Yellow accent dot + bright cyan bar)
    dot_r = s * 0.036
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#FFE600"))
    p.drawEllipse(QPointF(x_left, y1), dot_r, dot_r)

    p.setPen(QPen(QColor("#00F0FF"), line_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(x_left + card_w * 0.11, y1), QPointF(rect.left() + card_w * 0.80, y1))

    # Line 2 (Electric Pink dot + white-cyan bar)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#FF2A85"))
    p.drawEllipse(QPointF(x_left, y2), dot_r, dot_r)

    p.setPen(QPen(QColor("#E2F1FF"), line_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(x_left + card_w * 0.11, y2), QPointF(rect.left() + card_w * 0.68, y2))

    # Line 3 (Neon Mint dot + short bar)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#00F59B"))
    p.drawEllipse(QPointF(x_left, y3), dot_r, dot_r)

    p.setPen(QPen(QColor("#00F59B"), line_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(x_left + card_w * 0.11, y3), QPointF(rect.left() + card_w * 0.50, y3))

    p.end()
    return img


def save_multi_res_ico(ico_path: str, sizes=(16, 24, 32, 48, 64, 128, 256)):
    png_blobs = []
    for sz in sizes:
        img = render_cybernotes_master_image(sz)
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buf, "PNG")
        png_blobs.append((sz, bytes(buf.data())))

    count = len(png_blobs)
    # ICONDIR header: Reserved(2)=0, Type(2)=1 (ICO), Count(2)=count
    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + count * 16
    entries = []
    for sz, blob in png_blobs:
        w_byte = 0 if sz >= 256 else sz
        h_byte = 0 if sz >= 256 else sz
        # ICONDIRENTRY: bWidth, bHeight, bColorCount, bReserved, wPlanes, wBitCount, dwBytesInRes, dwImageOffset
        entry = struct.pack("<BBBBHHII", w_byte, h_byte, 0, 0, 1, 32, len(blob), offset)
        entries.append(entry)
        offset += len(blob)

    with open(ico_path, "wb") as f:
        f.write(header)
        for e in entries:
            f.write(e)
        for _, blob in png_blobs:
            f.write(blob)


SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1D2230"/>
      <stop offset="55%" stop-color="#121620"/>
      <stop offset="100%" stop-color="#0B0D14"/>
    </linearGradient>
    <linearGradient id="hdrGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FFE600"/>
      <stop offset="100%" stop-color="#00F0FF"/>
    </linearGradient>
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFE600"/>
      <stop offset="50%" stop-color="#00F0FF"/>
      <stop offset="100%" stop-color="#FF2A85"/>
    </linearGradient>
    <clipPath id="cardClip">
      <rect x="42" y="42" width="428" height="428" rx="105" ry="105"/>
    </clipPath>
  </defs>
  <rect x="42" y="42" width="428" height="428" rx="105" ry="105" fill="url(#bgGrad)" stroke="url(#borderGrad)" stroke-width="16"/>
  <g clip-path="url(#cardClip)">
    <rect x="42" y="42" width="428" height="84" fill="url(#hdrGrad)"/>
  </g>
  <circle cx="128" cy="215" r="18" fill="#FFE600"/>
  <line x1="175" y1="215" x2="384" y2="215" stroke="#00F0FF" stroke-width="28" stroke-linecap="round"/>
  <circle cx="128" cy="296" r="18" fill="#FF2A85"/>
  <line x1="175" y1="296" x2="332" y2="296" stroke="#E2F1FF" stroke-width="28" stroke-linecap="round"/>
  <circle cx="128" cy="378" r="18" fill="#00F59B"/>
  <line x1="175" y1="378" x2="256" y2="378" stroke="#00F59B" stroke-width="28" stroke-linecap="round"/>
</svg>
"""


def main():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    ico_path = os.path.join(assets_dir, "cybernotes.ico")
    png_256 = os.path.join(assets_dir, "cybernotes_256.png")
    png_512 = os.path.join(assets_dir, "cybernotes_512.png")
    svg_path = os.path.join(assets_dir, "cybernotes.svg")

    save_multi_res_ico(ico_path)
    render_cybernotes_master_image(256).save(png_256, "PNG")
    render_cybernotes_master_image(512).save(png_512, "PNG")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(SVG_TEMPLATE)

    print(f"Generated: {ico_path} ({os.path.getsize(ico_path)} bytes)")
    print(f"Generated: {png_256} ({os.path.getsize(png_256)} bytes)")
    print(f"Generated: {png_512} ({os.path.getsize(png_512)} bytes)")
    print(f"Generated: {svg_path} ({os.path.getsize(svg_path)} bytes)")


if __name__ == "__main__":
    main()
