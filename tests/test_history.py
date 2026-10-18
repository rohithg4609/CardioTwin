"""
Tests for CardioTwin HealthHistory.
"""

import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from digital_twin.history import HealthHistory


class TestHealthHistory(unittest.TestCase):

    def setUp(self):
        """Create an isolated temporary history file for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()

        self.history_file = (
            Path(self.temp_dir.name) / "history.json"
        )

        self.history = HealthHistory(self.history_file)

    def tearDown(self):
        """Remove the temporary test directory."""
        self.temp_dir.cleanup()

    def test_new_history_is_empty(self):
        self.assertTrue(self.history.is_empty())
        self.assertEqual(
            self.history.get_record_count(),
            0,
        )

    def test_missing_file_creates_empty_history(self):
        self.assertFalse(
            self.history.filename.exists()
        )

        self.assertEqual(
            self.history.get_all_records(),
            [],
        )

    def test_add_record(self):
        record = {
            "date": "2026-09-24",
            "heart_rate": 80,
            "spo2": 98,
        }

        result = self.history.add_record(record)

        self.assertEqual(result, record)
        self.assertEqual(
            self.history.get_record_count(),
            1,
        )

    def test_add_record_saves_to_file(self):
        record = {
            "date": "2026-09-24",
            "heart_rate": 82,
        }

        self.history.add_record(record)

        self.assertTrue(
            self.history.filename.exists()
        )

        with self.history.filename.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.assertEqual(data, [record])

    def test_add_record_without_saving(self):
        record = {
            "date": "2026-09-24",
            "heart_rate": 82,
        }

        self.history.add_record(
            record,
            save=False,
        )

        self.assertEqual(
            self.history.get_record_count(),
            1,
        )

        self.assertFalse(
            self.history.filename.exists()
        )

    def test_get_all_records(self):
        record1 = {
            "date": "2026-09-23",
            "heart_rate": 78,
        }

        record2 = {
            "date": "2026-09-24",
            "heart_rate": 82,
        }

        self.history.add_record(
            record1,
            save=False,
        )

        self.history.add_record(
            record2,
            save=False,
        )

        records = self.history.get_all_records()

        self.assertEqual(
            records,
            [record1, record2],
        )

    def test_get_latest_record(self):
        first = {
            "date": "2026-09-23",
            "heart_rate": 78,
        }

        latest = {
            "date": "2026-09-24",
            "heart_rate": 82,
        }

        self.history.add_record(
            first,
            save=False,
        )

        self.history.add_record(
            latest,
            save=False,
        )

        self.assertEqual(
            self.history.get_latest_record(),
            latest,
        )

    def test_get_first_record(self):
        first = {
            "date": "2026-09-23",
            "heart_rate": 78,
        }

        latest = {
            "date": "2026-09-24",
            "heart_rate": 82,
        }

        self.history.add_record(
            first,
            save=False,
        )

        self.history.add_record(
            latest,
            save=False,
        )

        self.assertEqual(
            self.history.get_first_record(),
            first,
        )

    def test_latest_record_on_empty_history(self):
        self.assertIsNone(
            self.history.get_latest_record()
        )

    def test_first_record_on_empty_history(self):
        self.assertIsNone(
            self.history.get_first_record()
        )

    def test_get_records_by_date_string(self):
        record1 = {
            "date": "2026-09-23",
            "heart_rate": 78,
        }

        record2 = {
            "date": "2026-09-24",
            "heart_rate": 82,
        }

        record3 = {
            "date": "2026-09-24",
            "heart_rate": 85,
        }

        self.history.add_record(
            record1,
            save=False,
        )

        self.history.add_record(
            record2,
            save=False,
        )

        self.history.add_record(
            record3,
            save=False,
        )

        result = self.history.get_records_by_date(
            "2026-09-24"
        )

        self.assertEqual(
            result,
            [record2, record3],
        )

    def test_get_records_by_date_object(self):
        record = {
            "date": "2026-09-24",
            "heart_rate": 80,
        }

        self.history.add_record(
            record,
            save=False,
        )

        result = self.history.get_records_by_date(
            date(2026, 9, 24)
        )

        self.assertEqual(
            result,
            [record],
        )

    def test_get_records_by_datetime_object(self):
        record = {
            "date": "2026-09-24",
            "heart_rate": 80,
        }

        self.history.add_record(
            record,
            save=False,
        )

        result = self.history.get_records_by_date(
            datetime(2026, 9, 24, 15, 30)
        )

        self.assertEqual(
            result,
            [record],
        )

    def test_invalid_date_format_is_rejected(self):
        with self.assertRaises(ValueError):
            self.history.get_records_by_date(
                "24-09-2026"
            )

    def test_empty_date_is_rejected(self):
        with self.assertRaises(ValueError):
            self.history.get_records_by_date("")

    def test_invalid_date_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.history.get_records_by_date(12345)

    def test_record_must_be_dictionary(self):
        with self.assertRaises(TypeError):
            self.history.add_record(
                "not a dictionary"
            )

    def test_record_date_must_be_string(self):
        with self.assertRaises(TypeError):
            self.history.add_record(
                {
                    "date": 20260924,
                    "heart_rate": 80,
                }
            )

    def test_record_date_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            self.history.add_record(
                {
                    "date": "",
                    "heart_rate": 80,
                }
            )

    def test_remove_record(self):
        record1 = {
            "date": "2026-09-23",
            "heart_rate": 78,
        }

        record2 = {
            "date": "2026-09-24",
            "heart_rate": 82,
        }

        self.history.add_record(
            record1,
            save=False,
        )

        self.history.add_record(
            record2,
            save=False,
        )

        removed = self.history.remove_record(
            0,
            save=False,
        )

        self.assertEqual(
            removed,
            record1,
        )

        self.assertEqual(
            self.history.get_all_records(),
            [record2],
        )

    def test_remove_invalid_index(self):
        with self.assertRaises(IndexError):
            self.history.remove_record(
                0,
                save=False,
            )

    def test_remove_non_integer_index(self):
        with self.assertRaises(TypeError):
            self.history.remove_record(
                "0",
                save=False,
            )

    def test_clear_history(self):
        self.history.add_record(
            {
                "date": "2026-09-24",
                "heart_rate": 80,
            },
            save=False,
        )

        self.history.clear(save=False)

        self.assertTrue(
            self.history.is_empty()
        )

        self.assertEqual(
            self.history.get_record_count(),
            0,
        )

    def test_reload(self):
        record = {
            "date": "2026-09-24",
            "heart_rate": 80,
            "spo2": 98,
        }

        self.history.add_record(record)

        new_history = HealthHistory(
            self.history_file
        )

        self.assertEqual(
            new_history.get_all_records(),
            [record],
        )

    def test_invalid_json_raises_error(self):
        self.history.filename.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.history.filename.write_text(
            "{invalid json",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            HealthHistory(self.history_file)

    def test_json_root_must_be_list(self):
        self.history.filename.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.history.filename.write_text(
            '{"heart_rate": 80}',
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            HealthHistory(self.history_file)

    def test_get_all_records_returns_copies(self):
        record = {
            "date": "2026-09-24",
            "heart_rate": 80,
        }

        self.history.add_record(
            record,
            save=False,
        )

        records = self.history.get_all_records()

        records[0]["heart_rate"] = 999

        self.assertEqual(
            self.history.get_latest_record()[
                "heart_rate"
            ],
            80,
        )

    def test_add_record_returns_copy(self):
        record = {
            "date": "2026-09-24",
            "heart_rate": 80,
        }

        result = self.history.add_record(
            record,
            save=False,
        )

        result["heart_rate"] = 999

        self.assertEqual(
            self.history.get_latest_record()[
                "heart_rate"
            ],
            80,
        )

    def test_len(self):
        self.assertEqual(
            len(self.history),
            0,
        )

        self.history.add_record(
            {
                "date": "2026-09-24",
                "heart_rate": 80,
            },
            save=False,
        )

        self.assertEqual(
            len(self.history),
            1,
        )

    def test_repr(self):
        representation = repr(self.history)

        self.assertIn(
            "HealthHistory",
            representation,
        )

        self.assertIn(
            "records=0",
            representation,
        )


if __name__ == "__main__":
    unittest.main()