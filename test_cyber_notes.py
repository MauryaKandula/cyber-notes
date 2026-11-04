"""
Unit Test Suite for CyberNotes
Author: Kandula Paul Saketh Maurya (@MauryaKandula)
License: MIT
"""

import os
import sqlite3
import tempfile
import unittest
from cyber_notes import PlumStoragePool, CYBER_THEMES, THEME_ORDER


class TestCyberNotesStorageAndThemes(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "plum.sqlite")
        self.pool = PlumStoragePool(self.db_path)

    def tearDown(self):
        self.pool.conn.close()
        self.tmp_dir.cleanup()

    def test_10_tables_created(self):
        cur = self.pool.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cur.fetchall()}
        expected = {
            "Note",
            "Stroke",
            "StrokeMetadata",
            "Media",
            "Insight",
            "Tag",
            "InkListItem",
            "SyncState",
            "UpgradedNote",
            "User",
        }
        self.assertTrue(expected.issubset(tables))

    def test_7_canonical_themes_mapped(self):
        self.assertEqual(
            THEME_ORDER,
            ["Yellow", "Blue", "Pink", "Purple", "Green", "White", "Charcoal"],
        )
        for t in THEME_ORDER:
            self.assertIn(t, CYBER_THEMES)
            self.assertIn("accent", CYBER_THEMES[t])

    def test_crud_insights_and_tags(self):
        note = self.pool.create_note(
            text="Visit https://github.com/MauryaKandula or call +1 (555) 207-7999 #project #work",
            theme="Pink",
            is_open=1,
            is_always_on_top=1,
        )
        self.assertEqual(note["Theme"], "Pink")
        self.assertEqual(note["IsAlwaysOnTop"], 1)

        tags = self.pool.get_all_tags()
        self.assertEqual(tags, ["project", "work"])

        insights = self.pool.get_insights(note["Id"])
        types = {i["InsightType"] for i in insights}
        self.assertIn("UrlInsight", types)
        self.assertIn("PhoneNumberInsight", types)

        filtered = self.pool.get_all_notes(tag_filter="project")
        self.assertEqual(len(filtered), 1)

    def test_stroke_persistence(self):
        note = self.pool.create_note(text="Drawing note", theme="Blue")
        self.pool.add_stroke(note["Id"], [(10, 20), (30, 40), (50, 60)], "#00F0FF", 2.5)
        strokes = self.pool.get_strokes(note["Id"])
        self.assertEqual(len(strokes), 1)
        self.assertEqual(len(strokes[0]["points"]), 3)
        self.pool.clear_strokes(note["Id"])
        self.assertEqual(len(self.pool.get_strokes(note["Id"])), 0)

    def test_text_note_serializer_cleaner_and_ms_import(self):
        raw = r"\id=9b12a34f-1111-2222-3333-444455556666\ \b Important Note\b0  \i details\i0"
        cleaned = PlumStoragePool.clean_ms_sticky_text(raw)
        self.assertIn("Important Note", cleaned)
        self.assertNotIn(r"\id=", cleaned)
        self.assertNotIn(r"\b", cleaned)

        ms_db = os.path.join(self.tmp_dir.name, "ms_plum.sqlite")
        conn = sqlite3.connect(ms_db)
        conn.execute(
            "CREATE TABLE Note (Id TEXT PRIMARY KEY, Text TEXT, Theme TEXT, IsOpen INTEGER, IsAlwaysOnTop INTEGER, WindowPosition TEXT)"
        )
        conn.execute(
            "INSERT INTO Note VALUES ('ms-note-1', '\\id=1234-5678\\ \\b Imported Sticky Note\\b0 #tasks', 'Purple', 1, 1, '385x350+200+200')"
        )
        conn.commit()
        conn.close()

        count = self.pool.import_from_ms_sticky_notes(ms_db)
        self.assertEqual(count, 1)
        imported = self.pool.get_note("ms-note-1")
        self.assertIsNotNone(imported)
        self.assertEqual(imported["Theme"], "Purple")
        self.assertIn("Imported Sticky Note", imported["Text"])


if __name__ == "__main__":
    unittest.main()
