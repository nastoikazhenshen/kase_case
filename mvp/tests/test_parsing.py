import unittest
from decimal import Decimal

from mvp.src.parsing import excel_to_pct, parse_daily_date, parse_number, pct_to_excel


class ParsingTests(unittest.TestCase):
    def test_russian_number_and_unicode_minus_are_exact(self):
        self.assertEqual(parse_number("−1\u202f234,50"), Decimal("-1234.50"))

    def test_missing_is_not_zero_and_nonfinite_is_rejected(self):
        self.assertIsNone(parse_number(""))
        self.assertEqual(parse_number("0"), Decimal("0"))
        with self.assertRaises(ValueError): parse_number("NaN")

    def test_ambiguous_separator_is_rejected(self):
        with self.assertRaises(ValueError): parse_number("1,234.56")

    def test_percentage_units_round_trip(self):
        self.assertEqual(pct_to_excel("0,5"), Decimal("0.005"))
        self.assertEqual(excel_to_pct(Decimal("0.005")), Decimal("0.500"))

    def test_daily_date_requires_iso_date(self):
        self.assertEqual(parse_daily_date("2026-10-21").isoformat(), "2026-10-21")
        with self.assertRaises(ValueError): parse_daily_date("21.10.2026")
