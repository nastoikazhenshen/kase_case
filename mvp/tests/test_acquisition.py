import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from email.message import Message

from mvp.src.acquisition import (AcquisitionError, comparable_daily_trade_rows, fetch_public_json,
                                 safe_headers, sha256_bytes, trade_info_source, validate_public_source)


class FakeResponse:
    def __init__(self, payload, headers=None):
        self.payload = payload
        self.status = 200
        self.headers = Message()
        for key, value in (headers or {"Date": "Wed"}).items():
            self.headers[key] = value
    def read(self): return self.payload
    def getcode(self): return self.status
    def __enter__(self): return self
    def __exit__(self, *_): return False


class AcquisitionTests(unittest.TestCase):
    def test_trade_info_route_preserves_required_trailing_slash(self):
        self.assertEqual(
            trade_info_source("BIGDb5").url,
            "https://kase.kz/api/instruments/trade-info/BIGDb5/",
        )

    def test_cumulative_from_row_is_not_treated_as_daily_history(self):
        rows = comparable_daily_trade_rows([
            {"period": "22.10.26", "date0": "2026-10-22", "price": None, "average_price": None, "deals_count": None},
            {"period": "21.10.26", "date0": "2026-10-21 17:28:27", "price": 100.0, "average_price": 100.2},
            {"period": "From 02.06.25", "date0": "2025-06-02 17:00:21", "price": 100.0, "average_price": 100.0},
        ])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["trade_date"], "2026-10-21")
        self.assertEqual(rows[0]["price_view_status"], "BLOCKED_PRICE_VIEW")

    def test_provenance_header_filter_never_retains_credentials(self):
        headers = safe_headers({"Date": "Wed", "Cookie": "secret", "Authorization": "Bearer secret"})
        self.assertEqual(headers, {"date": "Wed"})

    def test_sha256_is_stable(self):
        self.assertEqual(sha256_bytes(b"KASE"), "e38ac435c163fda4e0a70740c8ab9c9f96f1f89e4d704b93c2287eb673aa4804")

    def test_cache_is_idempotent_and_preserves_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "row.json"
            cache.write_bytes(b'[{"period":"21.10.26","date0":"2026-10-21"}]')
            data, metadata = fetch_public_json(trade_info_source("BIGDb5"), cache_path=cache,
                                                opener=lambda *_args, **_kwargs: self.fail("network called"))
        self.assertEqual(data[0]["period"], "21.10.26")
        self.assertEqual(metadata["cache_status"], "HIT")

    def test_malformed_partial_response_is_recorded_as_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            attempts = Path(directory) / "attempts.jsonl"
            with self.assertRaises(AcquisitionError):
                fetch_public_json(trade_info_source("BIGDb5"), attempts_path=attempts,
                                  opener=lambda *_args, **_kwargs: FakeResponse(b'[{"period":"21.10.26"}]'))
            self.assertIn("MALFORMED_OR_PARTIAL_RESPONSE", attempts.read_text(encoding="utf-8"))

    def test_one_bounded_retry_after_is_honored(self):
        calls, waits = [], []
        headers = Message(); headers["Retry-After"] = "1"
        def opener(*_args, **_kwargs):
            calls.append(1)
            if len(calls) == 1:
                raise HTTPError("https://kase.kz/api/instruments/trade-info/BIGDb5/", 429, "busy", headers, None)
            return FakeResponse(json.dumps([{"period":"21.10.26", "date0":"2026-10-21"}]).encode())
        fetch_public_json(trade_info_source("BIGDb5"), opener=opener, sleeper=waits.append)
        self.assertEqual((len(calls), waits), (2, [1]))

    def test_fixed_host_validation_rejects_untrusted_url(self):
        with self.assertRaises(AcquisitionError):
            validate_public_source(type("S", (), {"url": "https://example.com/api/x"})())

    def test_unobserved_ticker_and_path_query_are_rejected(self):
        with self.assertRaises(AcquisitionError):
            trade_info_source("../escape")
        for url in ("https://kase.kz/api/instruments/bonds/../../private/", "https://kase.kz/api/instruments/bonds/BIGDb5/?date=guessed"):
            with self.assertRaises(AcquisitionError):
                validate_public_source(type("S", (), {"url": url})())

    def test_cache_does_not_trust_a_stale_sidecar_hash(self):
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / "data.json"
            cache.write_bytes(b'[{"period":"21.10.26","date0":"2026-10-21"}]')
            cache.with_suffix(".json.provenance.json").write_text(json.dumps({"response_sha256": "0" * 64, "source_url": trade_info_source("BIGDb5").url}))
            with self.assertRaisesRegex(AcquisitionError, "hash/URL"):
                fetch_public_json(trade_info_source("BIGDb5"), cache_path=cache,
                                  opener=lambda *_a, **_k: self.fail("network called"))
