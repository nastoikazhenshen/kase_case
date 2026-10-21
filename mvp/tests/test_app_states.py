"""Isolated Streamlit states; empty fixture is test-only, never market evidence."""
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from mvp.src.repository import ROOT


class AppStateTests(unittest.TestCase):
    def run_state(self, **kwargs):
        with patch("mvp.src.repository.load_snapshot", **kwargs):
            app = AppTest.from_file(str(ROOT / "src/app.py"), default_timeout=15).run()
        self.assertFalse(app.exception)
        return app

    def test_missing_pack_is_a_readable_setup_state(self):
        app = self.run_state(side_effect=FileNotFoundError("test-only missing pack"))
        self.assertIn("пакет доказательств не найден", app.info[0].value)
        self.assertFalse(app.metric)

    def test_corrupt_pack_is_a_readable_failure_state(self):
        app = self.run_state(side_effect=ValueError("test-only hash mismatch"))
        self.assertIn("не прошёл проверку целостности", app.error[0].value)
        self.assertFalse(app.metric)

    def test_empty_snapshot_does_not_invent_observations(self):
        app = self.run_state(return_value={"release": {"snapshot_id": "TEST-ONLY-EMPTY", "status": "TEST_ONLY", "limitations": []},
                                          "observations": [], "instruments": [], "events": [], "valuations": [],
                                          "sources": [], "coverage": [], "rules": {}})
        self.assertTrue(any("Нет наблюдений" in w.value for w in app.warning))
        self.assertTrue(all(m.value == "0" for m in app.metric))


if __name__ == "__main__":
    unittest.main()
