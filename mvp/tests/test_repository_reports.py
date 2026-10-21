"""Real saved KASE end-to-end checks; network is disabled inside the test.

Synthetic adversarial strings are test-only. Local source pack is intentionally
not redistributed in git; integration tests report a skip when it is absent.
"""
import copy
import csv
import io
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from mvp.src.repository import ROOT, contained_path, load_snapshot, validate_snapshot
from mvp.src.reports import build_report, report_csv, report_html, safe_text
from mvp.src.build_snapshot import retrieval_metadata


class ExportSecurityTests(unittest.TestCase):
    def test_revision_retrieval_uses_actual_collector_completion(self):
        revision = {"retrieval_started_at_utc": "2026-10-21T21:59:06.1891198Z",
                    "retrieval_completed_at_utc": "2026-10-21T21:59:06.5431045Z",
                    "retrieval_timestamp_status": "COLLECTOR_CLOCK_UTC"}
        normalized = retrieval_metadata(revision)
        self.assertEqual(normalized["retrieved_at"], revision["retrieval_completed_at_utc"])
        self.assertEqual(normalized["retrieval_started_at_utc"], revision["retrieval_started_at_utc"])
        self.assertEqual(retrieval_metadata({})["retrieval_timestamp_status"], "NOT_RECORDED")

    def test_spreadsheet_formula_strings_are_neutralized(self):
        for attack in ("=1+1", "+SUM(A1:A2)", "-2+3", "@SUM(A1:A2)", " \t=HYPERLINK(1)"):
            self.assertTrue(safe_text(attack).startswith("'"))
        self.assertEqual(safe_text("CLSGb11"), "CLSGb11")

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            contained_path(ROOT, "../outside")

    def test_missing_clone_pack_is_explicit(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                load_snapshot(Path(td))


@unittest.skipUnless((ROOT / "data/processed/snapshot.json").exists(), "Real local evidence pack not present; run documented import first")
class RealSourceE2ETests(unittest.TestCase):
    def setUp(self):
        with patch("socket.socket", side_effect=AssertionError("network disabled")):
            self.snapshot = load_snapshot()
        self.rows = [r for r in self.snapshot["observations"] if r["trade_date"] == "2026-10-21"]

    def test_real_offline_rounding_and_independent_ratio(self):
        with patch("socket.socket", side_effect=AssertionError("network disabled")):
            report = build_report(self.snapshot, self.rows, "2026-10-21", 100_000)
        row = next(r for r in self.rows if r["ticker"] == "BIGDb5")
        # Independent arithmetic directly on the source-scale turnover, not engine helper.
        expected = Decimal("100000") / (Decimal(row["turnover_mln_kzt"]) * Decimal("1000000"))
        result = next(r for r in report["evaluations"] if r["ticker"] == "BIGDb5" and r["rule"] == "planned_amount_to_observed_daily_turnover")
        self.assertAlmostEqual(result["value"], float(expected), places=12)
        self.assertIn(result["status"], ("TRIGGERED", "EVALUATED"))
        self.assertIsNone(result["n"])
        self.assertEqual(report["events"], [])  # UTC assumption => next-day availability

    def test_csv_and_report_evaluation_parity(self):
        report = build_report(self.snapshot, self.rows, "2026-10-22", 100_000)
        exported = list(csv.DictReader(io.StringIO(report_csv(report).decode("utf-8-sig"))))
        evaluations = [r for r in exported if r["record_type"] == "EVALUATION"]
        self.assertEqual(len(evaluations), len(report["evaluations"]))
        for x, y in zip(evaluations, report["evaluations"]):
            self.assertEqual(x["status"], y["status"])
            self.assertEqual(x["rule"], y["rule"])
            if y["value"] is not None:
                self.assertAlmostEqual(float(x["value"]), y["value"], places=12)
        self.assertEqual(len(report["events"]), 1)
        self.assertEqual(report["events"][0]["evidence_status"], "OFFICIAL_FULL_NOTICE")
        self.assertEqual(report["events"][0]["verified_via"], "OFFICIAL_FULL_NOTICE")
        for context in report["events"] + report["valuations"]:
            self.assertTrue(context["retrieved_at"].endswith("Z"))

    def test_csv_context_and_provenance_match_json_on_both_event_dates(self):
        for day in ("2026-10-21", "2026-10-22"):
            report = build_report(self.snapshot, self.rows, day)
            exported = list(csv.DictReader(io.StringIO(report_csv(report).decode("utf-8-sig"))))
            self.assertEqual({r["event_id"] for r in exported if r["record_type"] == "EVENT"}, {r["event_id"] for r in report["events"]})
            self.assertEqual({(r["instrument_id"], r["valuation_date"], r["valuation_type"]) for r in exported if r["record_type"] == "VALUATION"},
                             {(r["instrument_id"], r["valuation_date"], r["valuation_type"]) for r in report["valuations"]})
            sources = {r["source_id"]: r for r in report["sources"]}
            self.assertEqual({r["source_id"] for r in exported if r["record_type"] == "SOURCE"}, set(sources))
            for result in report["evaluations"]:
                self.assertEqual(set(result["source_urls"]), {sources[sid]["source_url"] for sid in result["source_ids"]})

    def test_report_is_immutable_and_filter_changes_identifier(self):
        report = build_report(self.snapshot, self.rows, "2026-10-21")
        again = build_report(self.snapshot, self.rows, "2026-10-21")
        self.assertEqual(report["report_id"], again["report_id"])
        self.assertNotEqual(report["report_id"], build_report(self.snapshot, self.rows[:1], "2026-10-21")["report_id"])
        self.snapshot["rules"]["window"] = 999
        self.assertEqual(report["rules"]["window"], 20)

    def test_real_source_gates_and_mode_dates_preserved(self):
        report = build_report(self.snapshot, self.snapshot["observations"], "2026-10-20")
        self.assertFalse(report["events"])
        for row in self.snapshot["observations"]:
            if row["trade_date"] == "2026-10-20":
                self.assertEqual(row["mode_status"], "UNCONFIRMED")
            if row["ticker"] == "HCBNb19":
                self.assertEqual(row["turnover_kzt"], "")
        prices = [r for r in report["evaluations"] if r["rule"] in ("price_gap_pct", "range_pct")]
        self.assertTrue(all(r["status"] not in ("TRIGGERED", "EVALUATED") for r in prices))

    def test_scope_grain_registry_corruption_rejected(self):
        for mutate in (
            lambda s: s["observations"].append(copy.deepcopy(s["observations"][0])),
            lambda s: s["observations"][0].update(instrument_id="NOT_AN_ISIN"),
            lambda s: s["observations"][0].update(denomination_currency="USD"),
            lambda s: s["observations"][0]["source_ids"].append("UNKNOWN"),
            lambda s: s["sources"][0].update(evidence_sha256="0" * 64),
            lambda s: s["observations"][0].update(source_file="data/raw_extracted/stale.tsv"),
            lambda s: s["instruments"][0].update(raw_file="data/raw_extracted/stale.tsv"),
        ):
            bad = copy.deepcopy(self.snapshot)
            mutate(bad)
            with self.assertRaises(ValueError):
                validate_snapshot(bad)

    def test_html_escapes_source_strings(self):
        report = build_report(self.snapshot, self.rows, "2026-10-22")
        report["events"][0]["title"] = "<script>alert(1)</script>"
        rendered = report_html(report)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)


if __name__ == "__main__":
    unittest.main()
