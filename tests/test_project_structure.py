import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestProjectStructure(unittest.TestCase):
    def test_required_directories_exist(self):
        required = [
            PROJECT_ROOT / "data",
            PROJECT_ROOT / "data" / "health_records",
            PROJECT_ROOT / "digital_twin",
            PROJECT_ROOT / "tests",
        ]

        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_dir(), f"Missing directory: {path}")

    def test_required_existing_modules_exist(self):
        required = [
            PROJECT_ROOT / "digital_twin" / "patient.py",
            PROJECT_ROOT / "digital_twin" / "health_state.py",
            PROJECT_ROOT / "digital_twin" / "history.py",
            PROJECT_ROOT / "digital_twin" / "risk_tracker.py",
        ]

        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"Missing module: {path}")

    def test_health_history_file_exists(self):
        path = PROJECT_ROOT / "data" / "health_records" / "history.json"
        self.assertTrue(path.is_file(), f"Missing health history: {path}")

    def test_python_package_initializers_exist(self):
        self.assertTrue((PROJECT_ROOT / "digital_twin" / "__init__.py").is_file())
        self.assertTrue((PROJECT_ROOT / "tests" / "__init__.py").is_file())

    def test_history_file_is_not_empty(self):
        path = PROJECT_ROOT / "data" / "health_records" / "history.json"
        self.assertGreater(path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
