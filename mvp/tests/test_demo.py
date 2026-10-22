"""The opt-in preset must use the canonical observation and the normal engine."""
import csv
import io
import unittest
from decimal import Decimal

from streamlit.testing.v1 import AppTest

from mvp.src.demo import DEMO_RULE, demo_report
from mvp.src.repository import ROOT, load_snapshot
from mvp.src.reports import report_csv, report_html


@unittest.skipUnless((ROOT / "data/processed/snapshot.json").exists(), "Real local evidence pack required")
class DemonstrationTests(unittest.TestCase):
    def test_explicit_example_keeps_all_data_gates_and_matches_exports(self):
        snapshot = load_snapshot()
        report = demo_report(snapshot)
        row, = report["observations"]
        self.assertEqual((row["ticker"], row["trade_date"], row["trading_mode"]), ("BIGDb5", "2026-10-21", "TQOB"))
        result = next(r for r in report["evaluations"] if r["rule"] == DEMO_RULE)
        source_turnover = Decimal(row["turnover_mln_kzt"]) * Decimal("1000000")
        self.assertAlmostEqual(result["value"], float(Decimal("100000") / source_turnover), places=12)
        self.assertEqual(result["status"], "TRIGGERED")
        self.assertIsNone(result["baseline"])  # no historical baseline is claimed
        self.assertIsNone(result["n"])
        self.assertEqual(len([r for r in report["evaluations"] if r["status"] not in {"EVALUATED", "TRIGGERED"}]), 5)
        self.assertEqual(report["events"], [])
        rows = list(csv.DictReader(io.StringIO(report_csv(report).decode("utf-8-sig"))))
        exported = next(r for r in rows if r.get("rule") == DEMO_RULE)
        self.assertEqual(float(exported["planned_amount_kzt"]), 100000)
        self.assertEqual(Decimal(exported["turnover_kzt"]), source_turnover)
        self.assertEqual(float(exported["value"]), result["value"])
        self.assertIn("Условный ввод пользователя", report_html(report))

    def test_preset_requires_action_and_reset_does_not_make_zero_input(self):
        app = AppTest.from_file(str(ROOT / "src/app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.checkbox(key="use_planned").value)
        self.assertEqual(len(app.number_input), 0)
        next(b for b in app.button if b.label == "Показать расчётный пример").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.multiselect(key="selected_tickers").value, ["BIGDb5"])
        self.assertEqual(app.number_input(key="planned_amount").value, 100000.0)
        self.assertTrue(any("100 000 KZT ÷" in m.value for m in app.markdown))
        app.checkbox(key="use_planned").uncheck().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.number_input)
        self.assertEqual(next(m.value for m in app.metric if m.label == "Нужен ввод суммы"), "1")


if __name__ == "__main__":
    unittest.main()
