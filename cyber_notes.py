#!/usr/bin/env python3
"""
CyberNotes — Modern Neon Sticky Notes for Windows
Created by Kandula Paul Saketh Maurya (@MauryaKandula)
Licensed under the MIT License.

Features:
- Spacious, minimal Sticky Notes UX inspired by Microsoft Sticky Notes & Apple Stickies
  with a sleek Cyberpunk neon color palette.
- 144Hz/240Hz native OS compositor dragging & 8-edge resizing (`startSystemMove` / `startSystemResize`).
- Smooth 60fps `QPropertyAnimation` & `QVariantAnimation` transitions (window fade-in,
  sliding color drawer, animated color orbs, and smooth card hover elevation).
- Rich-Text editing (`Ctrl+B` Bold, `Ctrl+I` Italic, `Ctrl+U` Underline, `Ctrl+T` Strikethrough,
  `Ctrl+Shift+L` Bullet List) + freehand neon ink drawing mode.
- Local SQLite WAL persistence with automatic backup & optional Windows Sticky Notes import.
- Windows System Tray integration for quick access.
"""

__version__ = "2.0.0"
__author__ = "Kandula Paul Saketh Maurya"
__license__ = "MIT"

import json
import os
import re
import sqlite3
import sys
import time
import uuid
import webbrowser
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber_notes.log")
try:
    _log_f = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
    if sys.stdout is None:
        sys.stdout = _log_f
    if sys.stderr is None:
        sys.stderr = _log_f
except Exception:
    pass

# ---------------------------------------------------------------------------
# 1. Cyberpunk Neon Color Palette (Clean, Aesthetic, Lore-Free)
# ---------------------------------------------------------------------------
CYBER_THEMES = {
    "Yellow": {
        "label": "Neon Yellow",
        "accent": "#FFE600",
        "accent_glow": "rgba(255, 230, 0, 0.20)",
        "header_bg": "#1F1D0A",
        "header_fg": "#FFE600",
        "body_bg": "#16150C",
        "body_bg_bottom": "#100F09",
        "body_fg": "#FFFDF2",
        "card_bg": "#1B1A0E",
        "border": "#FFE600",
        "selection": "#5C5400",
        "ink": "#FFE600",
        "muted": "#A69F55",
    },
    "Blue": {
        "label": "Cyber Cyan",
        "accent": "#00F0FF",
        "accent_glow": "rgba(0, 240, 255, 0.20)",
        "header_bg": "#082026",
        "header_fg": "#00F0FF",
        "body_bg": "#0C161C",
        "body_bg_bottom": "#081014",
        "body_fg": "#F0FCFF",
        "card_bg": "#101E26",
        "border": "#00F0FF",
        "selection": "#004D59",
        "ink": "#00F0FF",
        "muted": "#5E9EA8",
    },
    "Pink": {
        "label": "Electric Pink",
        "accent": "#FF2A85",
        "accent_glow": "rgba(255, 42, 133, 0.20)",
        "header_bg": "#260918",
        "header_fg": "#FF2A85",
        "body_bg": "#180B13",
        "body_bg_bottom": "#11070D",
        "body_fg": "#FFF0F6",
        "card_bg": "#210E19",
        "border": "#FF2A85",
        "selection": "#660033",
        "ink": "#FF2A85",
        "muted": "#AD5E80",
    },
    "Purple": {
        "label": "Neon Violet",
        "accent": "#B845FF",
        "accent_glow": "rgba(184, 69, 255, 0.20)",
        "header_bg": "#1B0A26",
        "header_fg": "#C975FF",
        "body_bg": "#130B1C",
        "body_bg_bottom": "#0D0714",
        "body_fg": "#F7F0FF",
        "card_bg": "#1A0E26",
        "border": "#B845FF",
        "selection": "#4B0073",
        "ink": "#B845FF",
        "muted": "#9168AD",
    },
    "Green": {
        "label": "Neon Mint",
        "accent": "#00F59B",
        "accent_glow": "rgba(0, 245, 155, 0.20)",
        "header_bg": "#072418",
        "header_fg": "#00F59B",
        "body_bg": "#0B1712",
        "body_bg_bottom": "#07100C",
        "body_fg": "#EEFFF7",
        "card_bg": "#0E2018",
        "border": "#00F59B",
        "selection": "#005936",
        "ink": "#00F59B",
        "muted": "#58A684",
    },
    "White": {
        "label": "Frost Silver",
        "accent": "#E2F1FF",
        "accent_glow": "rgba(226, 241, 255, 0.18)",
        "header_bg": "#1A1F29",
        "header_fg": "#E2F1FF",
        "body_bg": "#131720",
        "body_bg_bottom": "#0D1017",
        "body_fg": "#F2F7FC",
        "card_bg": "#181D28",
        "border": "#A5B8CC",
        "selection": "#323942",
        "ink": "#E2F1FF",
        "muted": "#82909E",
    },
    "Charcoal": {
        "label": "Crimson Glow",
        "accent": "#FF3B5C",
        "accent_glow": "rgba(255, 59, 92, 0.20)",
        "header_bg": "#24090E",
        "header_fg": "#FF3B5C",
        "body_bg": "#160B0E",
        "body_bg_bottom": "#0F0709",
        "body_fg": "#FFF0F2",
        "card_bg": "#1E0E13",
        "border": "#FF3B5C",
        "selection": "#590012",
        "ink": "#FF3B5C",
        "muted": "#A35865",
    },
}

THEME_ORDER = ["Yellow", "Blue", "Pink", "Purple", "Green", "White", "Charcoal"]


# ---------------------------------------------------------------------------
# 2. Local SQLite Storage Engine (`plum.sqlite`)
# ---------------------------------------------------------------------------
class PlumStoragePool:
    """
    Fast, local SQLite storage engine in WAL mode supporting rich text,
    freehand vector strokes, tags, and smart link/phone insights.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "Note" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36),
                "Text" varchar DEFAULT '',
                "RichSpansJson" varchar DEFAULT '[]',
                "Theme" varchar DEFAULT 'Yellow',
                "IsOpen" integer DEFAULT 1,
                "IsAlwaysOnTop" integer DEFAULT 0,
                "WindowPosition" varchar DEFAULT '',
                "CreationNoteIdAnchor" varchar DEFAULT '',
                "Type" varchar DEFAULT 'Text',
                "CreatedAt" bigint NOT NULL,
                "CreatedById" varchar DEFAULT '',
                "UpdatedAt" bigint NOT NULL,
                "UpdatedById" varchar DEFAULT '',
                "DeletedAt" bigint DEFAULT 0,
                "DeletedById" varchar DEFAULT '',
                "Revision" bigint DEFAULT 1,
                "SyncRevision" bigint DEFAULT 0,
                "RemoteId" varchar DEFAULT '',
                "RemoteSchemaVersion" integer DEFAULT 0,
                "IsRemoteDataInvalid" integer DEFAULT 0,
                "CreationWidth" float DEFAULT 380.0,
                "CreationHeight" float DEFAULT 360.0,
                "ChangeKey" varchar DEFAULT ''
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "Stroke" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36) NOT NULL,
                "Type" varchar DEFAULT 'Stroke',
                "PointsJson" varchar NOT NULL,
                "Data" blob,
                "FormatVersion" integer DEFAULT 1,
                "InkColor" varchar DEFAULT '#00F0FF',
                "StrokeThickness" float DEFAULT 2.5,
                "CreatedAt" bigint NOT NULL,
                "UpdatedAt" bigint DEFAULT 0,
                "Revision" bigint DEFAULT 1,
                "SyncRevision" bigint DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "StrokeMetadata" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36) NOT NULL,
                "StrokeId" varchar(36),
                "InkListItemId" varchar(36),
                "InsightId" varchar(36),
                "ReminderId" varchar(36),
                "OffsetX" float DEFAULT 0.0,
                "OffsetY" float DEFAULT 0.0,
                "OffsetAngle" float DEFAULT 0.0,
                "RotationPointX" float DEFAULT 0.0,
                "RotationPointY" float DEFAULT 0.0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "Media" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36) NOT NULL,
                "LocalFile" varchar NOT NULL,
                "LocalFileRelativePath" varchar DEFAULT '',
                "MimeType" varchar DEFAULT 'image/png',
                "AltText" varchar DEFAULT '',
                "Description" varchar DEFAULT '',
                "ImageDimensions" varchar DEFAULT '',
                "RemoteId" varchar DEFAULT '',
                "RemoteSource" varchar DEFAULT '',
                "ThumbnailBase64" varchar DEFAULT '',
                "CreatedAt" bigint NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "Insight" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36) NOT NULL,
                "InsightScope" integer DEFAULT 0,
                "StartContentBlockId" varchar DEFAULT '',
                "EndContentBlockId" varchar DEFAULT '',
                "InsightType" varchar NOT NULL,
                "InsightContent" varchar NOT NULL,
                "LaunchAction" varchar NOT NULL,
                "JsonData" varchar DEFAULT '{}'
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "Tag" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36) NOT NULL,
                "TagName" varchar NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "InkListItem" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36) NOT NULL,
                "ListItemOrder" integer DEFAULT 0,
                "InkListItemId" varchar(36),
                "IsStrikethrough" integer DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "SyncState" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36),
                "OutboundQueueJson" varchar DEFAULT '[]',
                "UnverifiedNotesJson" varchar DEFAULT '[]'
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "UpgradedNote" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "OldNoteId" varchar,
                "NewNoteId" varchar,
                "UpgradeManagerVersion" integer DEFAULT 1,
                "UpgraderVersion" integer DEFAULT 1,
                "ModifiedByUser" integer DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS "User" (
                "Id" varchar(36) PRIMARY KEY NOT NULL,
                "ParentId" varchar(36),
                "Type" varchar DEFAULT 'User',
                "Revision" bigint DEFAULT 1,
                "SyncRevision" bigint DEFAULT 0
            )
            """
        )
        cur.execute('CREATE INDEX IF NOT EXISTS "idx_note_updated" ON "Note"("UpdatedAt" DESC)')
        cur.execute('CREATE INDEX IF NOT EXISTS "idx_stroke_parent" ON "Stroke"("ParentId")')
        cur.execute('CREATE INDEX IF NOT EXISTS "idx_insight_parent" ON "Insight"("ParentId")')
        cur.execute('CREATE INDEX IF NOT EXISTS "idx_tag_parent" ON "Tag"("ParentId")')
        self.conn.commit()

    @staticmethod
    def now_ms() -> int:
        return int(time.time() * 1000)

    def get_all_notes(self, search_query: str = "", tag_filter: str = "") -> list[dict]:
        cur = self.conn.cursor()
        sql = 'SELECT * FROM "Note" WHERE "DeletedAt" = 0'
        params = []
        if search_query.strip():
            sql += ' AND "Text" LIKE ?'
            params.append(f"%{search_query.strip()}%")
        if tag_filter.strip():
            sql += ' AND "Id" IN (SELECT "ParentId" FROM "Tag" WHERE LOWER("TagName") = LOWER(?))'
            params.append(tag_filter.strip().lstrip("#"))
        sql += ' ORDER BY "UpdatedAt" DESC'
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

    def get_note(self, note_id: str) -> dict | None:
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM "Note" WHERE "Id" = ? AND "DeletedAt" = 0', (note_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def create_note(
        self,
        text: str = "",
        theme: str = "Yellow",
        is_open: int = 1,
        is_always_on_top: int = 0,
        window_position: str = "",
        note_id: str | None = None,
    ) -> dict:
        nid = note_id or str(uuid.uuid4())
        now = self.now_ms()
        if theme not in CYBER_THEMES:
            theme = "Yellow"
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO "Note"
            ("Id", "ParentId", "Text", "RichSpansJson", "Theme", "IsOpen",
             "IsAlwaysOnTop", "WindowPosition", "Type", "CreatedAt", "UpdatedAt", "DeletedAt")
            VALUES (?, ?, ?, '[]', ?, ?, ?, ?, 'Text', ?, ?, 0)
            """,
            (nid, nid, text, theme, is_open, is_always_on_top, window_position, now, now),
        )
        self.conn.commit()
        self._rebuild_insights_and_tags(nid, text)
        return self.get_note(nid)

    def update_note(self, note_id: str, **fields) -> dict | None:
        allowed = {
            "Text",
            "RichSpansJson",
            "Theme",
            "IsOpen",
            "IsAlwaysOnTop",
            "WindowPosition",
            "Type",
            "DeletedAt",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get_note(note_id)
        if "WindowPosition" not in updates or len(updates) > 1:
            updates["UpdatedAt"] = self.now_ms()

        set_clause = ", ".join(f'"{k}" = ?' for k in updates.keys())
        values = list(updates.values()) + [note_id]
        cur = self.conn.cursor()
        cur.execute(f'UPDATE "Note" SET {set_clause} WHERE "Id" = ?', values)
        self.conn.commit()

        if "Text" in updates:
            self._rebuild_insights_and_tags(note_id, updates["Text"])
        return self.get_note(note_id)

    def delete_note(self, note_id: str, hard: bool = True):
        cur = self.conn.cursor()
        if hard:
            cur.execute('DELETE FROM "Note" WHERE "Id" = ?', (note_id,))
            cur.execute('DELETE FROM "Stroke" WHERE "ParentId" = ?', (note_id,))
            cur.execute('DELETE FROM "Insight" WHERE "ParentId" = ?', (note_id,))
            cur.execute('DELETE FROM "Tag" WHERE "ParentId" = ?', (note_id,))
            cur.execute('DELETE FROM "Media" WHERE "ParentId" = ?', (note_id,))
        else:
            cur.execute(
                'UPDATE "Note" SET "DeletedAt" = ?, "IsOpen" = 0 WHERE "Id" = ?',
                (self.now_ms(), note_id),
            )
        self.conn.commit()

    def add_stroke(self, parent_id: str, points: list[tuple[float, float]], color: str, width: float = 2.5):
        sid = str(uuid.uuid4())
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO "Stroke" ("Id", "ParentId", "PointsJson", "InkColor", "StrokeThickness", "CreatedAt")
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (sid, parent_id, json.dumps(points), color, width, self.now_ms()),
        )
        self.conn.commit()
        return sid

    def get_strokes(self, parent_id: str) -> list[dict]:
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM "Stroke" WHERE "ParentId" = ? ORDER BY "CreatedAt" ASC', (parent_id,))
        res = []
        for r in cur.fetchall():
            d = dict(r)
            try:
                d["points"] = json.loads(d["PointsJson"])
            except Exception:
                d["points"] = []
            res.append(d)
        return res

    def clear_strokes(self, parent_id: str):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM "Stroke" WHERE "ParentId" = ?', (parent_id,))
        self.conn.commit()

    def _rebuild_insights_and_tags(self, note_id: str, text: str):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM "Insight" WHERE "ParentId" = ?', (note_id,))
        cur.execute('DELETE FROM "Tag" WHERE "ParentId" = ?', (note_id,))

        if not text:
            self.conn.commit()
            return

        tags = sorted(set(re.findall(r"(?:^|\s)#([A-Za-z0-9_\-]+)", text)))
        for t in tags:
            cur.execute(
                'INSERT INTO "Tag" ("Id", "ParentId", "TagName") VALUES (?, ?, ?)',
                (str(uuid.uuid4()), note_id, t),
            )

        urls = re.findall(r"https?://[^\s<>\"']+", text)
        for u in urls:
            cur.execute(
                """
                INSERT INTO "Insight" ("Id", "ParentId", "InsightType", "InsightContent", "LaunchAction")
                VALUES (?, ?, 'UrlInsight', ?, ?)
                """,
                (str(uuid.uuid4()), note_id, u, u),
            )

        phones = re.findall(r"(?:\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4}", text)
        for p in phones:
            cur.execute(
                """
                INSERT INTO "Insight" ("Id", "ParentId", "InsightType", "InsightContent", "LaunchAction")
                VALUES (?, ?, 'PhoneNumberInsight', ?, ?)
                """,
                (str(uuid.uuid4()), note_id, p.strip(), f"tel:{p.strip()}"),
            )

        self.conn.commit()

    def get_insights(self, note_id: str) -> list[dict]:
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM "Insight" WHERE "ParentId" = ?', (note_id,))
        return [dict(r) for r in cur.fetchall()]

    def get_all_tags(self) -> list[str]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT "TagName" FROM "Tag"
            WHERE "ParentId" IN (SELECT "Id" FROM "Note" WHERE "DeletedAt" = 0)
            ORDER BY LOWER("TagName") ASC
            """
        )
        return [r[0] for r in cur.fetchall()]

    @staticmethod
    def clean_ms_sticky_text(raw_text: str) -> str:
        if not raw_text:
            return ""
        cleaned = re.sub(r"\\id=[a-fA-F0-9\-]+\\?", "", raw_text)
        cleaned = re.sub(
            r"\\(?:b0?|i0?|ul0?|strike0?|l0?|nosupersub|super|sub|ql|qr|qc|qj|ltrpar|rtlpar)\s?",
            "",
            cleaned,
        )
        return cleaned.strip("\r")

    def import_from_ms_sticky_notes(self, ms_plum_path: str | None = None) -> int:
        if ms_plum_path is None:
            ms_plum_path = os.path.expandvars(
                r"%LOCALAPPDATA%\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite"
            )
        if not os.path.exists(ms_plum_path):
            return 0

        imported = 0
        try:
            ext = sqlite3.connect(f"file:{ms_plum_path}?mode=ro", uri=True)
            ext.row_factory = sqlite3.Row
            ecur = ext.cursor()
            ecur.execute("SELECT name FROM sqlite_master WHERE type='table' AND lower(name)='note'")
            if not ecur.fetchone():
                ext.close()
                return 0

            ecur.execute("SELECT * FROM Note")
            for row in ecur.fetchall():
                rdict = dict(row)
                nid = str(rdict.get("Id") or uuid.uuid4())
                raw_text = str(rdict.get("Text") or "")
                text = self.clean_ms_sticky_text(raw_text)
                theme = str(rdict.get("Theme") or "Yellow").capitalize()
                if theme in ("Grey", "Gray"):
                    theme = "White"
                if theme not in CYBER_THEMES:
                    theme = "Yellow"
                is_open = int(rdict.get("IsOpen", 1) or 0)
                is_top = int(rdict.get("IsAlwaysOnTop", 0) or 0)
                win_pos = str(rdict.get("WindowPosition") or "")

                if not self.get_note(nid):
                    self.create_note(
                        text=text,
                        theme=theme,
                        is_open=is_open,
                        is_always_on_top=is_top,
                        window_position=win_pos,
                        note_id=nid,
                    )
                    imported += 1
            ext.close()
        except Exception:
            pass
        return imported


# ---------------------------------------------------------------------------
# 3. PyQt6 Spacious, Animated, Ultra-Smooth Desktop UI
# ---------------------------------------------------------------------------
from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRectF,
    QSize,
    Qt,
    QTimer,
    QVariantAnimation,
)
from PyQt6.QtGui import (
    QAction,
    QColor,
    QFont,
    QIcon,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QShortcut,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextListFormat,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

RESIZE_MARGIN = 10


def create_cybernotes_icon() -> QIcon:
    """Generates a crisp, high-DPI neon sticky-note application icon."""
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    rect = QRectF(6, 6, 52, 52)
    path = QPainterPath()
    path.addRoundedRect(rect, 13, 13)

    grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    grad.setColorAt(0.0, QColor("#1A1F2B"))
    grad.setColorAt(1.0, QColor("#0D1017"))
    p.fillPath(path, grad)

    p.save()
    p.setClipPath(path)
    p.fillRect(QRectF(6, 6, 52, 10), QColor("#FFE600"))
    p.restore()

    p.setPen(QPen(QColor("#FFE600"), 2.2))
    p.drawPath(path)

    p.setPen(QPen(QColor("#00F0FF"), 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(18, 28), QPointF(46, 28))
    p.drawLine(QPointF(18, 38), QPointF(40, 38))
    p.drawLine(QPointF(18, 48), QPointF(32, 48))
    p.end()
    return QIcon(pix)


def compute_resize_edges(pos: QPoint, width: int, height: int) -> Qt.Edge:
    edges = Qt.Edge(0)
    if pos.x() <= RESIZE_MARGIN:
        edges |= Qt.Edge.LeftEdge
    elif pos.x() >= width - RESIZE_MARGIN:
        edges |= Qt.Edge.RightEdge
    if pos.y() <= RESIZE_MARGIN:
        edges |= Qt.Edge.TopEdge
    elif pos.y() >= height - RESIZE_MARGIN:
        edges |= Qt.Edge.BottomEdge
    return edges


def cursor_for_edges(edges: Qt.Edge) -> Qt.CursorShape:
    if edges in (
        Qt.Edge.TopEdge | Qt.Edge.LeftEdge,
        Qt.Edge.BottomEdge | Qt.Edge.RightEdge,
    ):
        return Qt.CursorShape.SizeFDiagCursor
    if edges in (
        Qt.Edge.TopEdge | Qt.Edge.RightEdge,
        Qt.Edge.BottomEdge | Qt.Edge.LeftEdge,
    ):
        return Qt.CursorShape.SizeBDiagCursor
    if edges in (Qt.Edge.LeftEdge, Qt.Edge.RightEdge):
        return Qt.CursorShape.SizeHorCursor
    if edges in (Qt.Edge.TopEdge, Qt.Edge.BottomEdge):
        return Qt.CursorShape.SizeVerCursor
    return Qt.CursorShape.ArrowCursor


class GlassNoteSurface(QFrame):
    """
    Smooth rounded glass surface with a 5px top color bar and animated focus glow.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = CYBER_THEMES["Yellow"]
        self.focus_progress = 0.0
        self.corner_radius = 16.0

        self._focus_anim = QVariantAnimation(self)
        self._focus_anim.setDuration(180)
        self._focus_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._focus_anim.valueChanged.connect(self._on_focus_anim)

    def _on_focus_anim(self, val):
        self.focus_progress = float(val)
        self.update()

    def set_theme(self, theme_dict: dict):
        self.theme = theme_dict
        self.update()

    def set_focused(self, focused: bool):
        self._focus_anim.stop()
        self._focus_anim.setStartValue(self.focus_progress)
        self._focus_anim.setEndValue(1.0 if focused else 0.0)
        self._focus_anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        path = QPainterPath()
        path.addRoundedRect(rect, self.corner_radius, self.corner_radius)

        # 1. Soft vertical gradient background
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        c_top = QColor(self.theme["body_bg"])
        c_top.setAlpha(248)
        c_bot = QColor(self.theme["body_bg_bottom"])
        c_bot.setAlpha(252)
        grad.setColorAt(0.0, c_top)
        grad.setColorAt(1.0, c_bot)
        painter.fillPath(path, grad)

        # 2. Top soft ambient tint from the accent bar
        glow_grad = QLinearGradient(rect.topLeft(), QPointF(rect.left(), rect.top() + 75.0))
        c_accent_glow = QColor(self.theme["accent"])
        alpha = int(16 + 22 * self.focus_progress)
        c_accent_glow.setAlpha(alpha)
        glow_grad.setColorAt(0.0, c_accent_glow)
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillPath(path, glow_grad)

        # 3. Clean 5px top color bar (Microsoft/Apple Sticky Notes style)
        painter.save()
        painter.setClipPath(path)
        top_strip = QRectF(rect.left(), rect.top(), rect.width(), 5.0)
        painter.fillRect(top_strip, QColor(self.theme["accent"]))
        painter.restore()

        # 4. Smooth interpolated border
        border_color = QColor(self.theme["accent"])
        border_alpha = int(50 + 130 * self.focus_progress)
        border_color.setAlpha(border_alpha)
        pen = QPen(border_color, 1.0 + 0.4 * self.focus_progress)
        painter.setPen(pen)
        painter.drawPath(path)


class NeonInkCanvas(QWidget):
    """
    Smooth anti-aliased freehand drawing overlay.
    """

    def __init__(self, note_window):
        super().__init__(note_window)
        self.note_win = note_window
        self.strokes: list[dict] = []
        self.current_points: list[tuple[float, float]] = []
        self.ink_enabled = False
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_ink_enabled(self, enabled: bool):
        self.ink_enabled = enabled
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, not enabled)
        self.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor)
        self.update()

    def load_strokes(self, strokes: list[dict]):
        self.strokes = strokes
        self.update()

    def mousePressEvent(self, event):
        if not self.ink_enabled or event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        pos = event.position()
        self.current_points = [(round(pos.x(), 1), round(pos.y(), 1))]
        self.update()

    def mouseMoveEvent(self, event):
        if not self.ink_enabled or not (event.buttons() & Qt.MouseButton.LeftButton):
            return super().mouseMoveEvent(event)
        pos = event.position()
        self.current_points.append((round(pos.x(), 1), round(pos.y(), 1)))
        self.update()

    def mouseReleaseEvent(self, event):
        if not self.ink_enabled or event.button() != Qt.MouseButton.LeftButton:
            return super().mouseReleaseEvent(event)
        if len(self.current_points) >= 2:
            color = self.note_win.theme["ink"]
            self.note_win.pool.add_stroke(self.note_win.note_id, self.current_points, color, 2.6)
            self.strokes.append(
                {"points": list(self.current_points), "InkColor": color, "StrokeThickness": 2.6}
            )
        self.current_points = []
        self.update()

    def _draw_polyline(self, painter: QPainter, pts: list[tuple[float, float]], color_hex: str, width: float):
        if len(pts) < 2:
            return
        path = QPainterPath()
        path.moveTo(pts[0][0], pts[0][1])
        for i in range(1, len(pts)):
            p0 = pts[i - 1]
            p1 = pts[i]
            mid_x = (p0[0] + p1[0]) / 2.0
            mid_y = (p0[1] + p1[1]) / 2.0
            path.quadTo(p0[0], p0[1], mid_x, mid_y)
        path.lineTo(pts[-1][0], pts[-1][1])

        glow = QColor(color_hex)
        glow.setAlpha(55)
        pen_glow = QPen(glow, width * 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_glow)
        painter.drawPath(path)

        core = QColor(color_hex)
        core.setAlpha(245)
        pen_core = QPen(core, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_core)
        painter.drawPath(path)

    def paintEvent(self, event):
        if not self.strokes and not self.current_points and not self.ink_enabled:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self.ink_enabled:
            pen = QPen(QColor(self.note_win.theme["accent"]), 1.0, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(4, 4, -4, -4), 10, 10)

        for s in self.strokes:
            self._draw_polyline(
                painter,
                s.get("points", []),
                s.get("InkColor") or self.note_win.theme["ink"],
                float(s.get("StrokeThickness") or 2.6),
            )
        if len(self.current_points) >= 2:
            self._draw_polyline(painter, self.current_points, self.note_win.theme["ink"], 2.6)


class AnimatedColorOrb(QPushButton):
    """Smoothly animated circular color swatch button."""

    def __init__(self, theme_key: str, theme_data: dict, on_select):
        super().__init__()
        self.theme_key = theme_key
        self.theme_data = theme_data
        self.is_active_theme = False
        self.hover_scale = 0.0
        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(theme_data["label"])
        self.clicked.connect(lambda: on_select(self.theme_key))

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._anim.valueChanged.connect(self._on_anim)

    def _on_anim(self, val):
        self.hover_scale = float(val)
        self.update()

    def enterEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self.hover_scale)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self.hover_scale)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)

    def set_active(self, active: bool):
        self.is_active_theme = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        center = QPointF(self.width() / 2.0, self.height() / 2.0)

        base_r = 10.5 if self.is_active_theme else 9.0
        radius = base_r + 2.0 * self.hover_scale
        c = QColor(self.theme_data["accent"])

        if self.hover_scale > 0.05 or self.is_active_theme:
            glow = QColor(c)
            glow.setAlpha(int(45 + 45 * max(self.hover_scale, 0.7 if self.is_active_theme else 0.0)))
            painter.setBrush(glow)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, radius + 3.0, radius + 3.0)

        painter.setBrush(c)
        border = QColor("#FFFFFF") if self.is_active_theme else QColor(0, 0, 0, 100)
        painter.setPen(QPen(border, 1.8 if self.is_active_theme else 1.0))
        painter.drawEllipse(center, radius, radius)

        if self.is_active_theme:
            painter.setPen(QPen(QColor("#090B10"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(center.x() - 3.8, center.y() + 0.5), QPointF(center.x() - 1.0, center.y() + 3.2))
            painter.drawLine(QPointF(center.x() - 1.0, center.y() + 3.2), QPointF(center.x() + 4.2, center.y() - 2.8))


class CyberStickyNoteWindow(QWidget):
    """
    Spacious, minimal, ultra-smooth Sticky Note window.
    """

    def __init__(self, app_controller, note_data: dict):
        super().__init__(None)
        self.app = app_controller
        self.pool: PlumStoragePool = app_controller.pool
        self.note_id: str = note_data["Id"]
        self.note_data: dict = note_data
        self.theme_name: str = note_data.get("Theme") or "Yellow"
        if self.theme_name not in CYBER_THEMES:
            self.theme_name = "Yellow"
        self.theme = CYBER_THEMES[self.theme_name]

        self.is_always_on_top: bool = bool(note_data.get("IsAlwaysOnTop", 0))
        self.ink_mode: bool = False
        self.palette_open: bool = False
        self._loading_content: bool = False

        # Debounce timers so typing & moving never touch disk during animation
        self._save_text_timer = QTimer(self)
        self._save_text_timer.setSingleShot(True)
        self._save_text_timer.setInterval(250)
        self._save_text_timer.timeout.connect(self._commit_text_to_db)

        self._save_geom_timer = QTimer(self)
        self._save_geom_timer.setSingleShot(True)
        self._save_geom_timer.setInterval(350)
        self._save_geom_timer.timeout.connect(self._commit_geometry_to_db)

        self._configure_window_flags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setMinimumSize(310, 270)

        self._build_ui()
        self._restore_geometry(note_data.get("WindowPosition", ""))
        self._apply_theme()
        self._load_content()
        self._animate_open()

    def _animate_open(self):
        self.setWindowOpacity(0.0)
        self.show()
        self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self._fade_anim.setDuration(210)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_anim.start()

    def _configure_window_flags(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        if self.is_always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    def _restore_geometry(self, pos_str: str):
        m = re.match(r"^(\d+)x(\d+)\+(-?\d+)\+(-?\d+)$", str(pos_str).strip())
        if m:
            w, h, x, y = map(int, m.groups())
            w = max(340, min(w, 1000))
            h = max(320, min(h, 1000))
            x = max(20, min(x, 2200))
            y = max(20, min(y, 1200))
            self.setGeometry(x, y, w, h)
        else:
            idx = len(self.app.open_windows)
            x = 540 + (idx % 2) * 415
            y = 80 + (idx // 2) * 410
            self.setGeometry(x, y, 400, 395)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(0)

        self.card = GlassNoteSurface(self)
        self.card.setMouseTracking(True)
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 165))
        self.card.setGraphicsEffect(shadow)
        outer.addWidget(self.card)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 12, 18, 14)
        card_layout.setSpacing(8)

        # --- 1. Clean, Spacious Top Header ---
        self.header_widget = QWidget(self.card)
        self.header_widget.setFixedHeight(32)
        self.header_widget.setCursor(Qt.CursorShape.SizeAllCursor)
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(0, 2, 0, 0)
        header_layout.setSpacing(6)

        self.btn_new = QPushButton("＋")
        self.btn_new.setFixedSize(30, 28)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setToolTip("New Note (Ctrl+N)")
        self.btn_new.clicked.connect(self.app.spawn_new_note)
        header_layout.addWidget(self.btn_new)

        self.btn_hub = QPushButton("☷")
        self.btn_hub.setFixedSize(30, 28)
        self.btn_hub.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hub.setToolTip("All Notes")
        self.btn_hub.clicked.connect(self.app.show_hub)
        header_layout.addWidget(self.btn_hub)

        header_layout.addStretch(1)

        # Color Theme Button
        self.btn_palette = QPushButton("●")
        self.btn_palette.setFixedSize(30, 28)
        self.btn_palette.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_palette.setToolTip("Change Color")
        self.btn_palette.clicked.connect(self._toggle_palette_drawer)
        header_layout.addWidget(self.btn_palette)

        # Pin Always-on-Top
        self.btn_pin = QPushButton("📌")
        self.btn_pin.setFixedSize(30, 28)
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setToolTip("Keep on Top")
        self.btn_pin.clicked.connect(self._toggle_always_on_top)
        header_layout.addWidget(self.btn_pin)

        # Close Note Window
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 28)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("Close Note")
        self.btn_close.clicked.connect(self._close_note_window)
        header_layout.addWidget(self.btn_close)

        card_layout.addWidget(self.header_widget)

        # --- 2. Smooth Animated Color Picker Drawer ---
        self.palette_drawer = QFrame(self.card)
        self.palette_drawer.setMaximumHeight(0)
        self.palette_drawer.setVisible(False)
        pal_layout = QHBoxLayout(self.palette_drawer)
        pal_layout.setContentsMargins(12, 6, 12, 6)
        pal_layout.setSpacing(10)
        self.orb_buttons: dict[str, AnimatedColorOrb] = {}
        for t_key in THEME_ORDER:
            orb = AnimatedColorOrb(t_key, CYBER_THEMES[t_key], self._select_theme)
            self.orb_buttons[t_key] = orb
            pal_layout.addWidget(orb)
        pal_layout.addStretch(1)
        card_layout.addWidget(self.palette_drawer)

        self._drawer_anim = QPropertyAnimation(self.palette_drawer, b"maximumHeight")
        self._drawer_anim.setDuration(180)
        self._drawer_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._drawer_anim.finished.connect(self._on_drawer_anim_finished)

        # --- 3. Spacious Rich-Text Editor + Ink Overlay ---
        self.editor_container = QWidget(self.card)
        self.editor_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        editor_stack_layout = QVBoxLayout(self.editor_container)
        editor_stack_layout.setContentsMargins(2, 4, 2, 4)

        self.editor = QTextEdit(self.editor_container)
        self.editor.setFrameShape(QFrame.Shape.NoFrame)
        self.editor.setFont(QFont("Segoe UI", 11))
        self.editor.document().setDocumentMargin(8)
        self.editor.setPlaceholderText("Take a note...")
        self.editor.textChanged.connect(self._on_editor_text_changed)
        self.editor.cursorPositionChanged.connect(self._sync_format_buttons)
        editor_stack_layout.addWidget(self.editor)

        self.ink_canvas = NeonInkCanvas(self)
        self.ink_canvas.setParent(self.editor_container)
        card_layout.addWidget(self.editor_container, 1)

        # --- 4. Smart Clickable Links Bar (Only shown when a URL/phone is present) ---
        self.insights_bar = QWidget(self.card)
        self.insights_layout = QHBoxLayout(self.insights_bar)
        self.insights_layout.setContentsMargins(0, 0, 0, 0)
        self.insights_layout.setSpacing(6)
        self.insights_bar.setVisible(False)
        card_layout.addWidget(self.insights_bar)

        # --- 5. Clean Bottom Formatting Bar ---
        self.toolbar_frame = QFrame(self.card)
        self.toolbar_frame.setFixedHeight(36)
        tb_layout = QHBoxLayout(self.toolbar_frame)
        tb_layout.setContentsMargins(8, 3, 8, 3)
        tb_layout.setSpacing(6)

        self.btn_bold = self._make_fmt_btn("B", "Bold (Ctrl+B)", self.toggle_bold, bold=True)
        self.btn_italic = self._make_fmt_btn("I", "Italic (Ctrl+I)", self.toggle_italic, italic=True)
        self.btn_under = self._make_fmt_btn("U", "Underline (Ctrl+U)", self.toggle_underline, underline=True)
        self.btn_strike = self._make_fmt_btn("S", "Strikethrough (Ctrl+T)", self.toggle_strike, strike=True)
        self.btn_list = self._make_fmt_btn("• List", "Bullet List (Ctrl+Shift+L)", self.toggle_bullets, width=54)
        self.btn_ink = self._make_fmt_btn("✎ Draw", "Freehand Draw", self._toggle_ink_mode, width=62)

        tb_layout.addWidget(self.btn_bold)
        tb_layout.addWidget(self.btn_italic)
        tb_layout.addWidget(self.btn_under)
        tb_layout.addWidget(self.btn_strike)
        tb_layout.addWidget(self.btn_list)
        tb_layout.addStretch(1)
        tb_layout.addWidget(self.btn_ink)

        self.btn_clear_ink = QPushButton("Clear")
        self.btn_clear_ink.setFixedHeight(26)
        self.btn_clear_ink.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_ink.setVisible(False)
        self.btn_clear_ink.clicked.connect(self._clear_ink_strokes)
        tb_layout.addWidget(self.btn_clear_ink)

        card_layout.addWidget(self.toolbar_frame)

        # Standard Shortcuts
        QShortcut(QKeySequence("Ctrl+B"), self, activated=self.toggle_bold)
        QShortcut(QKeySequence("Ctrl+I"), self, activated=self.toggle_italic)
        QShortcut(QKeySequence("Ctrl+U"), self, activated=self.toggle_underline)
        QShortcut(QKeySequence("Ctrl+T"), self, activated=self.toggle_strike)
        QShortcut(QKeySequence("Ctrl+Shift+L"), self, activated=self.toggle_bullets)
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.app.spawn_new_note)

    def _make_fmt_btn(
        self, text: str, tooltip: str, slot, bold=False, italic=False, underline=False, strike=False, width=32
    ) -> QPushButton:
        b = QPushButton(text)
        b.setCheckable(True)
        b.setFixedSize(width, 28)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setToolTip(tooltip)
        f = QFont("Segoe UI", 10)
        f.setBold(bold)
        f.setItalic(italic)
        f.setUnderline(underline)
        f.setStrikeOut(strike)
        b.setFont(f)
        b.clicked.connect(slot)
        return b

    def _apply_theme(self):
        t = CYBER_THEMES.get(self.theme_name, CYBER_THEMES["Yellow"])
        self.theme = t
        self.card.set_theme(t)

        for k, orb in self.orb_buttons.items():
            orb.set_active(k == self.theme_name)

        self.palette_drawer.setStyleSheet(
            "QFrame { background-color: rgba(255, 255, 255, 0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); }"
        )

        hdr_btn_qss = """
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.65);
                border: none;
                border-radius: 7px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.10);
                color: #FFFFFF;
            }
        """
        for b in (self.btn_new, self.btn_hub):
            b.setStyleSheet(hdr_btn_qss)

        self.btn_palette.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: {t['accent']};
                border: none;
                border-radius: 7px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.10);
            }}
            """
        )

        pin_active_qss = f"""
            QPushButton {{
                background: {t['accent_glow'] if self.is_always_on_top else 'transparent'};
                color: {t['accent'] if self.is_always_on_top else 'rgba(255, 255, 255, 0.55)'};
                border: none;
                border-radius: 7px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.12);
                color: {t['accent']};
            }}
        """
        self.btn_pin.setStyleSheet(pin_active_qss)

        self.btn_close.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.55);
                border: none;
                border-radius: 7px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255, 59, 92, 0.85);
                color: #FFFFFF;
            }
            """
        )

        self.editor.setStyleSheet(
            f"""
            QTextEdit {{
                background: transparent;
                color: {t['body_fg']};
                selection-background-color: {t['selection']};
                selection-color: #FFFFFF;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 5px;
                margin: 4px 0 4px 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.18);
                min-height: 28px;
                border-radius: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['accent']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: transparent;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            """
        )

        self.toolbar_frame.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.035);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }
            """
        )

        fmt_qss = f"""
            QPushButton {{
                background: transparent;
                color: rgba(255, 255, 255, 0.65);
                border: none;
                border-radius: 6px;
                padding: 0 5px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.09);
                color: #FFFFFF;
            }}
            QPushButton:checked {{
                background: {t['accent_glow']};
                color: {t['accent']};
            }}
        """
        for fb in (self.btn_bold, self.btn_italic, self.btn_under, self.btn_strike, self.btn_list, self.btn_ink):
            fb.setStyleSheet(fmt_qss)

        self.btn_ink.setChecked(self.ink_mode)

        self.btn_clear_ink.setStyleSheet(
            """
            QPushButton {
                background: rgba(255, 59, 92, 0.18);
                color: #FF8096;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: rgba(255, 59, 92, 0.38);
                color: #FFFFFF;
            }
            """
        )
        self._refresh_insight_chips()
        self.ink_canvas.update()

    def _load_content(self):
        self._loading_content = True
        raw_text = self.note_data.get("Text") or ""
        rich_meta = self.note_data.get("RichSpansJson") or ""
        if rich_meta and rich_meta.startswith("<!DOCTYPE HTML"):
            self.editor.setHtml(rich_meta)
        else:
            self.editor.setPlainText(raw_text)
        self._loading_content = False

        strokes = self.pool.get_strokes(self.note_id)
        self.ink_canvas.load_strokes(strokes)
        self.btn_clear_ink.setVisible(bool(strokes) or self.ink_mode)
        self._refresh_insight_chips()

    def _on_editor_text_changed(self):
        if self._loading_content:
            return
        self._save_text_timer.start()

    def _commit_text_to_db(self):
        plain = self.editor.toPlainText()
        html = self.editor.toHtml()
        self.pool.update_note(self.note_id, Text=plain, RichSpansJson=html)
        self._refresh_insight_chips()
        self.app.refresh_hub_cards()

    def _commit_geometry_to_db(self):
        g = self.geometry()
        pos_str = f"{g.width()}x{g.height()}+{g.x()}+{g.y()}"
        self.pool.update_note(self.note_id, WindowPosition=pos_str)

    # --- Rich Text Actions ---
    def toggle_bold(self):
        fmt = QTextCharFormat()
        is_bold = self.editor.fontWeight() > QFont.Weight.Normal
        fmt.setFontWeight(QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
        self._merge_format(fmt)
        self._sync_format_buttons()

    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self._merge_format(fmt)
        self._sync_format_buttons()

    def toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self._merge_format(fmt)
        self._sync_format_buttons()

    def toggle_strike(self):
        cursor = self.editor.textCursor()
        cur_fmt = cursor.charFormat()
        fmt = QTextCharFormat()
        fmt.setFontStrikeOut(not cur_fmt.fontStrikeOut())
        self._merge_format(fmt)
        self._sync_format_buttons()

    def toggle_bullets(self):
        cursor = self.editor.textCursor()
        cur_list = cursor.currentList()
        if cur_list:
            block_fmt = QTextBlockFormat()
            block_fmt.setIndent(0)
            cursor.setBlockFormat(block_fmt)
        else:
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.Style.ListDisc)
            cursor.createList(list_fmt)
        self._sync_format_buttons()
        self._save_text_timer.start()

    def _merge_format(self, fmt: QTextCharFormat):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)
        self._save_text_timer.start()

    def _sync_format_buttons(self):
        cursor = self.editor.textCursor()
        cf = cursor.charFormat()
        self.btn_bold.setChecked(cf.fontWeight() > QFont.Weight.Normal)
        self.btn_italic.setChecked(cf.fontItalic())
        self.btn_under.setChecked(cf.fontUnderline())
        self.btn_strike.setChecked(cf.fontStrikeOut())
        self.btn_list.setChecked(cursor.currentList() is not None)

    def _refresh_insight_chips(self):
        while self.insights_layout.count():
            item = self.insights_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        insights = self.pool.get_insights(self.note_id)
        if not insights:
            self.insights_bar.setVisible(False)
            return

        self.insights_bar.setVisible(True)
        t = self.theme

        for ins in insights[:2]:
            label_txt = ins["InsightContent"]
            if len(label_txt) > 30:
                label_txt = label_txt[:28] + "…"
            icon = "↗" if ins["InsightType"] == "UrlInsight" else "📞"
            btn = QPushButton(f"{icon}  {label_txt}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(24)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background: {t['accent_glow']};
                    color: {t['accent']};
                    border: none;
                    border-radius: 7px;
                    font-size: 11px;
                    padding: 0 10px;
                }}
                QPushButton:hover {{
                    background: {t['accent']};
                    color: #090B10;
                }}
                """
            )
            action = ins["LaunchAction"]
            btn.clicked.connect(lambda checked=False, a=action: webbrowser.open(a))
            self.insights_layout.addWidget(btn)

        self.insights_layout.addStretch(1)

    # --- Animated Color Drawer & Window Controls ---
    def _toggle_palette_drawer(self):
        self.palette_open = not self.palette_open
        self._drawer_anim.stop()
        if self.palette_open:
            self.palette_drawer.setVisible(True)
            self._drawer_anim.setStartValue(self.palette_drawer.maximumHeight())
            self._drawer_anim.setEndValue(44)
        else:
            self._drawer_anim.setStartValue(self.palette_drawer.maximumHeight())
            self._drawer_anim.setEndValue(0)
        self._drawer_anim.start()

    def _on_drawer_anim_finished(self):
        if not self.palette_open:
            self.palette_drawer.setVisible(False)

    def _select_theme(self, theme_key: str):
        self.theme_name = theme_key
        if self.palette_open:
            self._toggle_palette_drawer()
        self.pool.update_note(self.note_id, Theme=theme_key)
        self._apply_theme()
        self.app.refresh_hub_cards()

    def _toggle_ink_mode(self):
        self.ink_mode = not self.ink_mode
        self.ink_canvas.set_ink_enabled(self.ink_mode)
        self.btn_clear_ink.setVisible(self.ink_mode or bool(self.ink_canvas.strokes))
        self._apply_theme()

    def _clear_ink_strokes(self):
        self.pool.clear_strokes(self.note_id)
        self.ink_canvas.load_strokes([])
        self.btn_clear_ink.setVisible(self.ink_mode)

    def _toggle_always_on_top(self):
        self.is_always_on_top = not self.is_always_on_top
        self.pool.update_note(self.note_id, IsAlwaysOnTop=int(self.is_always_on_top))
        geom = self.geometry()
        self._configure_window_flags()
        self.setGeometry(geom)
        self._apply_theme()
        self.show()
        self.app.refresh_hub_cards()

    def _close_note_window(self):
        self._commit_geometry_to_db()
        self.pool.update_note(self.note_id, IsOpen=0)
        if self.note_id in self.app.open_windows:
            del self.app.open_windows[self.note_id]
        self.close()
        self.app.refresh_hub_cards()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "ink_canvas") and hasattr(self, "editor_container"):
            self.ink_canvas.setGeometry(self.editor_container.rect())
        self._save_geom_timer.start()

    def moveEvent(self, event):
        super().moveEvent(event)
        self._save_geom_timer.start()

    def changeEvent(self, event):
        super().changeEvent(event)
        if hasattr(self, "card"):
            self.card.set_focused(self.isActiveWindow())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            edges = compute_resize_edges(pos, self.width(), self.height())
            if edges and self.windowHandle():
                self.windowHandle().startSystemResize(edges)
                event.accept()
                return
            hdr_pos = self.header_widget.mapFrom(self, pos)
            if self.header_widget.rect().contains(hdr_pos) and self.windowHandle():
                self.windowHandle().startSystemMove()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        edges = compute_resize_edges(pos, self.width(), self.height())
        self.setCursor(cursor_for_edges(edges))
        super().mouseMoveEvent(event)


# ---------------------------------------------------------------------------
# 4. Smooth Animated Note Card in Hub
# ---------------------------------------------------------------------------
class SmoothNoteCard(QFrame):
    """Spacious, animated note preview card in the main Notes Hub."""

    def __init__(self, app_controller, note_data: dict):
        super().__init__()
        self.app = app_controller
        self.note_data = note_data
        self.note_id = note_data["Id"]
        self.theme_name = note_data.get("Theme") or "Yellow"
        self.theme = CYBER_THEMES.get(self.theme_name, CYBER_THEMES["Yellow"])
        self.hover_progress = 0.0

        self._hover_anim = QVariantAnimation(self)
        self._hover_anim.setDuration(150)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._hover_anim.valueChanged.connect(self._on_hover_anim)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._build_card()

    def _on_hover_anim(self, val):
        self.hover_progress = float(val)
        self.update()

    def _build_card(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 16, 16)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        ts_ms = self.note_data.get("UpdatedAt") or 0
        ts_str = datetime.fromtimestamp(ts_ms / 1000.0).strftime("%I:%M %p  •  %b %d")

        lbl_meta = QLabel(ts_str)
        lbl_meta.setFont(QFont("Segoe UI", 9))
        lbl_meta.setStyleSheet(f"color: {self.theme['accent']}; background: transparent;")
        top_row.addWidget(lbl_meta)
        top_row.addStretch(1)

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(24, 24)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setToolTip("Delete Note")
        btn_del.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.35);
                border: none;
                border-radius: 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 59, 92, 0.25);
                color: #FF4D6A;
            }
            """
        )
        btn_del.clicked.connect(lambda: self.app.delete_note(self.note_id))
        top_row.addWidget(btn_del)
        layout.addLayout(top_row)

        raw_preview = (self.note_data.get("Text") or "").strip()
        if not raw_preview:
            preview = "Empty note..."
        else:
            lines = [ln.strip() for ln in raw_preview.splitlines() if ln.strip()]
            if len(lines) > 3:
                preview = "\n".join(lines[:3]) + " …"
            else:
                preview = "\n".join(lines)
            if len(preview) > 160:
                preview = preview[:157].rsplit(" ", 1)[0] + " …"

        lbl_body = QLabel(preview)
        lbl_body.setWordWrap(True)
        lbl_body.setFont(QFont("Segoe UI", 10))
        lbl_body.setStyleSheet(
            f"color: {self.theme['body_fg']}; background: transparent; padding-bottom: 2px;"
        )
        layout.addWidget(lbl_body)

    def enterEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self.hover_progress)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self.hover_progress)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.app.open_note_window(self.note_id)
            event.accept()
            return
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        path = QPainterPath()
        path.addRoundedRect(rect, 13.0, 13.0)

        bg = QColor(self.theme["card_bg"])
        bg.setAlpha(int(205 + 42 * self.hover_progress))
        painter.fillPath(path, bg)

        # Left 5px neon accent bar
        painter.save()
        painter.setClipPath(path)
        left_strip = QRectF(rect.left(), rect.top(), 5.0, rect.height())
        painter.fillRect(left_strip, QColor(self.theme["accent"]))
        painter.restore()

        c_accent = QColor(self.theme["accent"])
        border_col = QColor(
            int(255 + (c_accent.red() - 255) * self.hover_progress),
            int(255 + (c_accent.green() - 255) * self.hover_progress),
            int(255 + (c_accent.blue() - 255) * self.hover_progress),
            int(22 + 135 * self.hover_progress),
        )
        painter.setPen(QPen(border_col, 1.0 + 0.3 * self.hover_progress))
        painter.drawPath(path)


# ---------------------------------------------------------------------------
# 5. Main Notes Hub Window & System Tray Controller
# ---------------------------------------------------------------------------
class CyberNotesHubWindow(QWidget):
    """Spacious, minimal All Notes window with native OS drag/resize."""

    def __init__(self, app_controller):
        super().__init__(None)
        self.app = app_controller
        self.setWindowTitle("CyberNotes")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setMinimumSize(400, 500)
        self.setGeometry(75, 85, 430, 640)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            edges = compute_resize_edges(pos, self.width(), self.height())
            if edges and self.windowHandle():
                self.windowHandle().startSystemResize(edges)
                event.accept()
                return
            if pos.y() <= 72 and self.windowHandle():
                self.windowHandle().startSystemMove()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        edges = compute_resize_edges(pos, self.width(), self.height())
        self.setCursor(cursor_for_edges(edges))
        super().mouseMoveEvent(event)


class CyberNotesApp:
    """
    Main Application Controller, Hub Window & System Tray Manager.
    """

    def __init__(self, db_path: str | None = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plum.sqlite")
        self.pool = PlumStoragePool(db_path)
        self.open_windows: dict[str, CyberStickyNoteWindow] = {}
        self.active_tag_filter: str = ""

        self.qt_app = QApplication.instance() or QApplication(sys.argv)
        self.app_icon = create_cybernotes_icon()
        self.qt_app.setWindowIcon(self.app_icon)
        self.qt_app.setQuitOnLastWindowClosed(False)

        if not self.pool.get_all_notes():
            self._seed_default_notes()

        self.hub = CyberNotesHubWindow(self)
        self._build_hub_ui()
        self._setup_system_tray()
        self.refresh_hub_cards()
        self._restore_open_note_windows()
        self._animate_hub_open()

    def _animate_hub_open(self):
        self.hub.setWindowOpacity(0.0)
        self.hub.show()
        self._hub_fade = QPropertyAnimation(self.hub, b"windowOpacity")
        self._hub_fade.setDuration(220)
        self._hub_fade.setStartValue(0.0)
        self._hub_fade.setEndValue(1.0)
        self._hub_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hub_fade.start()

    def _seed_default_notes(self):
        self.pool.create_note(
            text=(
                "Welcome to CyberNotes ✨\n\n"
                "• Drag the top bar to move smoothly across your screen\n"
                "• Click the color dot (●) to switch neon themes\n"
                "• Format with Bold (Ctrl+B), Italic (Ctrl+I), or Lists\n"
                "• Toggle ✎ Draw to sketch freehand neon notes"
            ),
            theme="Yellow",
            is_open=1,
            is_always_on_top=1,
            window_position="405x395+535+80",
        )
        self.pool.create_note(
            text=(
                "Quick Tasks & Links\n\n"
                "• Check project repository: https://github.com/MauryaKandula\n"
                "• Pin important notes using 📌 so they stay on top while working"
            ),
            theme="Blue",
            is_open=1,
            is_always_on_top=0,
            window_position="405x355+535+495",
        )

    def _setup_system_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self.app_icon, self.qt_app)
        self.tray.setToolTip("CyberNotes")

        menu = QMenu()
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #12161F;
                color: #F0F6FC;
                border: 1px solid rgba(0, 240, 255, 0.3);
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 7px 20px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 240, 255, 0.2);
                color: #00F0FF;
            }
            """
        )
        act_new = QAction("＋  New Sticky Note", menu)
        act_new.triggered.connect(self.spawn_new_note)
        menu.addAction(act_new)

        act_hub = QAction("☷  Open All Notes", menu)
        act_hub.triggered.connect(self.show_hub)
        menu.addAction(act_hub)

        menu.addSeparator()

        act_quit = QAction("✕  Quit CyberNotes", menu)
        act_quit.triggered.connect(self.qt_app.quit)
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_hub()

    def _build_hub_ui(self):
        outer = QVBoxLayout(self.hub)
        outer.setContentsMargins(12, 12, 12, 12)

        self.hub_card = GlassNoteSurface(self.hub)
        self.hub_card.set_theme(CYBER_THEMES["Blue"])
        self.hub_card.set_focused(True)

        shadow = QGraphicsDropShadowEffect(self.hub_card)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 185))
        self.hub_card.setGraphicsEffect(shadow)
        outer.addWidget(self.hub_card)

        layout = QVBoxLayout(self.hub_card)
        layout.setContentsMargins(20, 16, 20, 18)
        layout.setSpacing(14)

        # --- Top Bar ---
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 2, 0, 0)

        lbl_title = QLabel("CyberNotes")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.DemiBold))
        lbl_title.setStyleSheet("color: #FFFFFF; background: transparent;")
        top_bar.addWidget(lbl_title)

        top_bar.addStretch(1)

        btn_new = QPushButton("＋  New Note")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.setFixedHeight(32)
        btn_new.setFont(QFont("Segoe UI Semibold", 10))
        btn_new.setStyleSheet(
            """
            QPushButton {
                background: #00F0FF;
                color: #090B10;
                border: none;
                border-radius: 8px;
                padding: 0 14px;
            }
            QPushButton:hover {
                background: #5CF6FF;
            }
            """
        )
        btn_new.clicked.connect(self.spawn_new_note)
        top_bar.addWidget(btn_new)

        btn_min = QPushButton("—")
        btn_min.setFixedSize(30, 30)
        btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_min.setToolTip("Minimize")
        btn_min.setStyleSheet(
            """
            QPushButton { background: transparent; color: rgba(255,255,255,0.60); border: none; border-radius: 7px; }
            QPushButton:hover { background: rgba(255,255,255,0.10); color: #FFFFFF; }
            """
        )
        btn_min.clicked.connect(self.hub.showMinimized)
        top_bar.addWidget(btn_min)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setToolTip("Quit CyberNotes")
        btn_close.setStyleSheet(
            """
            QPushButton { background: transparent; color: rgba(255,255,255,0.60); border: none; border-radius: 7px; }
            QPushButton:hover { background: rgba(255,59,92,0.85); color: #FFFFFF; }
            """
        )
        btn_close.clicked.connect(self.qt_app.quit)
        top_bar.addWidget(btn_close)
        layout.addLayout(top_bar)

        # --- Spacious Search Input ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedHeight(38)
        self.search_input.setFont(QFont("Segoe UI", 11))
        self.search_input.setStyleSheet(
            """
            QLineEdit {
                background: rgba(255, 255, 255, 0.055);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 10px;
                padding: 0 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00F0FF;
                background: rgba(0, 240, 255, 0.05);
            }
            """
        )
        self.search_input.textChanged.connect(self.refresh_hub_cards)
        layout.addWidget(self.search_input)

        # --- Smooth Scroll Area for Note Cards ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(
            """
            QScrollArea { background: transparent; border: none; }
            QWidget#scroll_content { background: transparent; }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px 0 2px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.16);
                min-height: 28px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00F0FF;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.cards_layout = QVBoxLayout(self.scroll_content)
        self.cards_layout.setContentsMargins(0, 2, 4, 2)
        self.cards_layout.setSpacing(12)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll, 1)

        # --- Subtle Bottom Footer ---
        footer = QHBoxLayout()
        footer.setContentsMargins(2, 0, 2, 0)

        self.lbl_count = QLabel("2 notes")
        self.lbl_count.setFont(QFont("Segoe UI", 9))
        self.lbl_count.setStyleSheet("color: rgba(255, 255, 255, 0.45); background: transparent;")
        footer.addWidget(self.lbl_count)

        footer.addStretch(1)

        btn_import = QPushButton("Import Sticky Notes")
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.setFixedHeight(26)
        btn_import.setFont(QFont("Segoe UI", 9))
        btn_import.setStyleSheet(
            """
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.65);
                border: none;
                border-radius: 6px;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: rgba(0, 240, 255, 0.15);
                color: #00F0FF;
            }
            """
        )
        btn_import.clicked.connect(self._import_ms_notes_dialog)
        footer.addWidget(btn_import)
        layout.addLayout(footer)

    def filter_hub_by_tag(self, tag: str):
        self.search_input.setText(f"#{tag}")
        self.show_hub()

    def refresh_hub_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        q = self.search_input.text().strip() if hasattr(self, "search_input") else ""
        notes = self.pool.get_all_notes(search_query=q, tag_filter=self.active_tag_filter)
        if hasattr(self, "lbl_count"):
            self.lbl_count.setText(f"{len(notes)} note{'s' if len(notes) != 1 else ''}")

        for n in notes:
            card = SmoothNoteCard(self, n)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch(1)

    def _restore_open_note_windows(self):
        for n in self.pool.get_all_notes():
            if n.get("IsOpen", 0):
                self.open_note_window(n["Id"])

    def open_note_window(self, note_id: str):
        if note_id in self.open_windows:
            win = self.open_windows[note_id]
            if win.isVisible():
                win.showNormal()
                win.raise_()
                win.activateWindow()
                return
            else:
                del self.open_windows[note_id]

        note = self.pool.update_note(note_id, IsOpen=1)
        if note:
            win = CyberStickyNoteWindow(self, note)
            self.open_windows[note_id] = win
            self.refresh_hub_cards()

    def spawn_new_note(self):
        used_themes = [n.get("Theme") for n in self.pool.get_all_notes()]
        next_theme = THEME_ORDER[len(used_themes) % len(THEME_ORDER)]
        idx = len(self.open_windows)
        pos = f"385x350+{540 + (idx % 3) * 40}+{95 + (idx % 4) * 40}"
        note = self.pool.create_note(text="", theme=next_theme, is_open=1, window_position=pos)
        self.open_note_window(note["Id"])
        self.refresh_hub_cards()

    def delete_note(self, note_id: str):
        if note_id in self.open_windows:
            try:
                self.open_windows[note_id].close()
            except Exception:
                pass
            del self.open_windows[note_id]
        self.pool.delete_note(note_id, hard=True)
        self.refresh_hub_cards()

    def show_hub(self):
        self.hub.showNormal()
        self.hub.raise_()
        self.hub.activateWindow()

    def _import_ms_notes_dialog(self):
        default_ms = os.path.expandvars(
            r"%LOCALAPPDATA%\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite"
        )
        count = self.pool.import_from_ms_sticky_notes(default_ms)
        if count > 0:
            self.refresh_hub_cards()
            self._restore_open_note_windows()
            QMessageBox.information(
                self.hub,
                "CyberNotes",
                f"Imported {count} note(s) from Windows Sticky Notes!",
            )
        else:
            chosen, _ = QFileDialog.getOpenFileName(
                self.hub,
                "Select Sticky Notes Database (plum.sqlite)",
                "",
                "SQLite Database (*.sqlite *.db);;All Files (*.*)",
            )
            if chosen:
                count = self.pool.import_from_ms_sticky_notes(chosen)
                self.refresh_hub_cards()
                self._restore_open_note_windows()
                QMessageBox.information(
                    self.hub,
                    "CyberNotes",
                    f"Imported {count} note(s) from {os.path.basename(chosen)}!",
                )

    def run(self):
        sys.exit(self.qt_app.exec())


def main_entry():
    app = CyberNotesApp()
    app.run()


if __name__ == "__main__":
    try:
        main_entry()
    except Exception as e:
        import traceback

        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash.log")
        with open(log_path, "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        raise
