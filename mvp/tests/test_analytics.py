import unittest

from mvp.src.analytics import DEFAULT_RULES, evaluate


def row(day, row_id, **updates):
    value = {"row_id": row_id, "instrument_id": "KZTEST", "ticker": "SYN", "trade_date": day,
             "trading_mode": "KASE", "price_basis": "CLEAN_PERCENT_OF_NOMINAL", "price_view_status": "VERIFIED",
             "mode_status": "VERIFIED", "scope_status": "VERIFIED_KZT_COUPON", "observation_kind": "DAILY",
             "finality": "CERTIFIED_EOD", "last_price": "101", "weighted_avg_price": "100", "high_price": "102",
             "low_price": "99", "turnover_kzt": "1000", "trades_count": "10", "turnover_status": "EXACT",
             "source_id": "S", "source_url": "https://example.test", "retrieved_at": day + "T18:00:00+05:00"}
    value.update(updates)
    return value


class AnalyticsTests(unittest.TestCase):
    # Synthetic boundary fixtures only: never market evidence.
    def setUp(self):
        self.current = row("2026-10-21", "today", turnover_kzt="3000", trades_count="30")
        self.history = [row(f"2026-09-{day:02d}", f"h{day}") for day in range(1, 11)]

    def result(self, results, name): return next(item for item in results if item["rule"] == name)

    def test_rolling_window_excludes_future_and_current_rows(self):
        history = self.history + [row("2026-10-21", "same", turnover_kzt="999999"), row("2026-10-22", "future", turnover_kzt="999999")]
        item = self.result(evaluate(self.current, history, DEFAULT_RULES), "turnover_ratio")
        self.assertEqual(item["n"], 10)
        self.assertEqual(item["baseline"], 1000.0)
        self.assertEqual(item["value"], 3.0)

    def test_price_view_gate_precedes_history_insufficiency(self):
        current = row("2026-10-21", "today", price_view_status="UNVERIFIED")
        item = self.result(evaluate(current, [], DEFAULT_RULES), "price_gap_pct")
        self.assertEqual(item["status"], "BLOCKED_PRICE_VIEW")

    def test_activity_rules_do_not_depend_on_price_view(self):
        current = row("2026-10-21", "today", price_view_status="UNVERIFIED", turnover_kzt="3000")
        results = evaluate(current, self.history, DEFAULT_RULES)
        self.assertEqual(self.result(results, "price_gap_pct")["status"], "BLOCKED_PRICE_VIEW")
        self.assertEqual(self.result(results, "turnover_ratio")["status"], "TRIGGERED")

    def test_price_gap_preserves_signed_value_but_uses_absolute_threshold(self):
        current = row("2026-10-21", "today", last_price="99", weighted_avg_price="100")
        item = self.result(evaluate(current, [], DEFAULT_RULES), "price_gap_pct")
        self.assertEqual(item["value"], -1.0)
        self.assertEqual(item["status"], "TRIGGERED")

    def test_history_requires_matching_finality_and_current_finality(self):
        blocked = row("2026-10-21", "today", finality="AS_PUBLISHED_NOT_CERTIFIED_EOD")
        self.assertEqual(self.result(evaluate(blocked, self.history, DEFAULT_RULES), "turnover_ratio")["status"], "BLOCKED_FINALITY")
        mixed = self.history + [row("2026-09-11", "other", finality="HISTORICAL_PUBLISHED")]
        self.assertEqual(self.result(evaluate(self.current, mixed, DEFAULT_RULES), "turnover_ratio")["n"], 10)

    def test_as_of_uses_observation_instant_or_explicit_day_end(self):
        item = self.result(evaluate(self.current, [], DEFAULT_RULES), "price_gap_pct")
        self.assertEqual(item["as_of"], "2026-10-21T23:59:59.999999+05:00")
        dated = row("2026-10-21", "today", observation_as_of="2026-10-21T11:00:00+05:00")
        self.assertEqual(self.result(evaluate(dated, [], DEFAULT_RULES), "price_gap_pct")["as_of"], "2026-10-21T11:00:00+05:00")

    def test_rounded_zero_turnover_is_not_a_ratio_denominator(self):
        current = row("2026-10-21", "today", turnover_kzt="0", trades_count="1", turnover_status="ROUNDED_ZERO")
        item = self.result(evaluate(current, self.history, DEFAULT_RULES), "turnover_ratio")
        self.assertEqual(item["status"], "ZERO_BASELINE")

    def test_incomplete_session_does_not_use_daily_history(self):
        current = row("2026-10-21", "today", finality="INCOMPLETE_SESSION")
        result = self.result(evaluate(current, self.history, DEFAULT_RULES), "turnover_ratio")
        self.assertEqual(result["status"], "INCOMPLETE_SESSION")

    def test_planned_rules_require_input_and_one_day_rule_has_no_baseline(self):
        results = evaluate(self.current, self.history, DEFAULT_RULES)
        self.assertEqual(self.result(results, "trade_size_to_turnover")["status"], "INPUT_REQUIRED")
        self.assertEqual(self.result(results, "planned_amount_to_observed_daily_turnover")["status"], "INPUT_REQUIRED")
        observed = self.result(evaluate(self.current, self.history, DEFAULT_RULES, "250"), "planned_amount_to_observed_daily_turnover")
        self.assertEqual(observed["baseline"], None)
        self.assertAlmostEqual(observed["value"], 1 / 12)

    def test_duplicate_prior_day_is_rejected_explicitly(self):
        with self.assertRaises(ValueError): evaluate(self.current, self.history + [dict(self.history[0], row_id="revision")], DEFAULT_RULES)
