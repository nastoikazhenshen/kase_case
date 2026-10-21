"""Small, auditable adapters for KASE's anonymously accessible public pages.

This module deliberately does not attempt to infer a price-tab selection.  The
instrument trade-info response exposes clean, dirty and yield fields together;
only an independently captured UI selection can make a trade price eligible for
a clean-price rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


KASE_ORIGIN = "https://kase.kz"
USER_AGENT = "BondScope-MVP/0.1 public-evidence collection"
PROVENANCE_HEADERS = frozenset({"cache-control", "content-length", "content-type", "date", "etag", "expires", "last-modified", "retry-after"})
MAX_RETRIES = 1
MAX_RETRY_AFTER_SECONDS = 5
VERIFIED_TICKERS = frozenset({"BIGDb5", "CLSGb11", "CLSGb15", "MFKMb10", "HCBNb19"})


class AcquisitionError(RuntimeError):
    """A safe, recorded acquisition failure."""


@dataclass(frozen=True)
class PublicSource:
    """A read-only route observed in KASE server-rendered public HTML."""

    source_id: str
    url: str
    purpose: str


def trade_info_source(ticker: str) -> PublicSource:
    """Return the observed public endpoint; the trailing slash is significant."""
    if ticker not in VERIFIED_TICKERS:
        raise AcquisitionError("ticker is outside the observed five-instrument route set")
    return PublicSource(
        source_id=f"KASE_TRADE_INFO_{ticker}",
        url=f"{KASE_ORIGIN}/api/instruments/trade-info/{ticker}/",
        purpose="instrument trade summary; contains current, prior-date and aggregate rows",
    )


def bond_source(ticker: str) -> PublicSource:
    if ticker not in VERIFIED_TICKERS:
        raise AcquisitionError("ticker is outside the observed five-instrument route set")
    return PublicSource(
        source_id=f"KASE_BOND_MASTER_{ticker}",
        url=f"{KASE_ORIGIN}/api/instruments/bonds/{ticker}/",
        purpose="instrument master data",
    )


MARKET_VALUATION_SOURCE = PublicSource(
    source_id="KASE_MARKET_VALUATIONS",
    url=f"{KASE_ORIGIN}/api/indicators/market-valuations/",
    purpose="official market valuation response, currently published dates only",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_public_source(source: PublicSource) -> None:
    """Only permit fixed anonymous HTTPS routes observed in public KASE SSR."""
    parsed = urlparse(source.url)
    allowed = {f"/api/instruments/{kind}/{ticker}/" for kind in ("trade-info", "bonds") for ticker in VERIFIED_TICKERS}
    allowed.add("/api/indicators/market-valuations/")
    if (parsed.scheme, parsed.hostname, parsed.port, parsed.username, parsed.password) != ("https", "kase.kz", None, None, None):
        raise AcquisitionError("source must be anonymous HTTPS on kase.kz")
    if parsed.path not in allowed or parsed.query or parsed.fragment or parsed.params:
        raise AcquisitionError("source path is outside observed-route allowlist")


def safe_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Persist only a deliberate public provenance-header allowlist."""
    return {
        key.lower(): value
        for key, value in headers.items()
        if key.lower() in PROVENANCE_HEADERS
    }


def _append_attempt(path: Path | None, record: Mapping[str, Any]) -> None:
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def validate_trade_info_payload(payload: Any) -> list[Mapping[str, Any]]:
    if not isinstance(payload, list) or not payload:
        raise AcquisitionError("trade-info response must be a non-empty JSON list")
    if any(not isinstance(row, Mapping) or "period" not in row or "date0" not in row for row in payload):
        raise AcquisitionError("trade-info response has malformed or partial rows")
    return payload


def fetch_public_json(source: PublicSource, *, cache_path: Path | None = None, attempts_path: Path | None = None,
                      timeout_seconds: int = 30, opener: Callable[..., Any] = urlopen,
                      sleeper: Callable[[float], None] = time.sleep) -> tuple[Any, dict[str, Any]]:
    """Use an exact cache or at most one bounded Retry-After retry for HTTP 429."""
    validate_public_source(source)
    if cache_path is not None and cache_path.exists():
        payload = cache_path.read_bytes()
        try:
            data = json.loads(payload.decode("utf-8"))
            if "/api/instruments/trade-info/" in source.url:
                validate_trade_info_payload(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise AcquisitionError(f"cached response is malformed: {error}") from error
        metadata: dict[str, Any] = {"source_id": source.source_id, "source_url": source.url,
                                    "cache_status": "HIT", "response_sha256": sha256_bytes(payload),
                                    "retrieval_timestamp_status": "FROM_CACHED_PROVENANCE_OR_UNKNOWN"}
        sidecar = cache_path.with_suffix(cache_path.suffix + ".provenance.json")
        if sidecar.exists():
            recorded = json.loads(sidecar.read_text(encoding="utf-8"))
            if recorded.get("response_sha256") != sha256_bytes(payload) or recorded.get("source_url") != source.url:
                raise AcquisitionError("cached provenance hash/URL does not match requested source")
            metadata.update(recorded)
            metadata["cache_status"] = "HIT"
        _append_attempt(attempts_path, {"attempted_at_utc": utc_now(), "source_url": source.url, "outcome": "CACHE_HIT"})
        return data, metadata
    request = Request(source.url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt in range(MAX_RETRIES + 1):
        attempted_at = utc_now()
        try:
            with opener(request, timeout=timeout_seconds) as response:  # nosec B310: fixed allowlisted host
                payload = response.read()
                metadata = {"source_id": source.source_id, "source_url": source.url, "cache_status": "MISS",
                            "retrieved_at_utc": utc_now(), "retrieval_timestamp_status": "COLLECTOR_CLOCK_UTC",
                            "status": getattr(response, "status", response.getcode()),
                            "content_type": response.headers.get_content_type(), "response_sha256": sha256_bytes(payload),
                            "headers": safe_headers(dict(response.headers.items()))}
        except HTTPError as error:
            raw = error.headers.get("Retry-After")
            wait = int(raw) if raw and raw.isdigit() and int(raw) <= MAX_RETRY_AFTER_SECONDS else None
            _append_attempt(attempts_path, {"attempted_at_utc": attempted_at, "source_url": source.url,
                                            "status": error.code, "retry_after_seconds": wait, "outcome": "HTTP_ERROR"})
            if error.code == 429 and attempt < MAX_RETRIES and wait is not None:
                sleeper(wait)
                continue
            raise AcquisitionError(f"HTTP {error.code} while retrieving {source.source_id}") from error
        except (URLError, TimeoutError) as error:
            _append_attempt(attempts_path, {"attempted_at_utc": attempted_at, "source_url": source.url,
                                            "outcome": "NETWORK_ERROR", "error": str(error)})
            raise AcquisitionError(f"network failure while retrieving {source.source_id}") from error
        try:
            data = json.loads(payload.decode("utf-8"))
            if "/api/instruments/trade-info/" in source.url:
                validate_trade_info_payload(data)
        except (UnicodeDecodeError, json.JSONDecodeError, AcquisitionError) as error:
            _append_attempt(attempts_path, {"attempted_at_utc": attempted_at, "source_url": source.url,
                                            "outcome": "MALFORMED_OR_PARTIAL_RESPONSE", "error": str(error)})
            raise AcquisitionError(f"malformed or partial response for {source.source_id}") from error
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(payload)
            cache_path.with_suffix(cache_path.suffix + ".provenance.json").write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _append_attempt(attempts_path, {"attempted_at_utc": attempted_at, "source_url": source.url,
                                        "status": metadata["status"], "outcome": "SUCCESS", "response_sha256": metadata["response_sha256"]})
        return data, metadata
    raise AssertionError("unreachable bounded retry loop")


def comparable_daily_trade_rows(payload: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return dated rows only, excluding the cumulative ``From …`` summary.

    This is intentionally a filter, not a history builder.  A pair of recent
    rows cannot establish the MVP's 10/20-observation rolling baseline.
    """
    rows: list[dict[str, Any]] = []
    for raw in payload:
        date0 = raw.get("date0")
        period = raw.get("period")
        if not isinstance(date0, str) or not isinstance(period, str):
            continue
        if period.strip().lower().startswith("from "):
            continue
        # A dated all-null current-session placeholder is not an EOD row.
        if raw.get("deals_count") is None and raw.get("price") is None and raw.get("average_price") is None:
            continue
        try:
            trade_date = datetime.fromisoformat(date0).date().isoformat()
        except ValueError:
            continue
        rows.append({
            "trade_date": trade_date,
            "period_label": period,
            "last_clean_price": raw.get("price"),
            "weighted_avg_clean_price": raw.get("average_price"),
            "high_clean_price": raw.get("high"),
            "low_clean_price": raw.get("low"),
            "last_dirty_price": raw.get("dirty_price"),
            "weighted_avg_dirty_price": raw.get("dirty_average_price"),
            "trades_count": raw.get("deals_count"),
            "turnover_mln_kzt": raw.get("volume_kzt"),
            "price_view_status": "BLOCKED_PRICE_VIEW",
            "history_status": "INSUFFICIENT_DATA",
        })
    return rows


def write_manifest(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    """Write a deterministic, credential-free evidence manifest."""
    material = list(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(material, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Explicit refresh command; cache makes repeated runs idempotent."""
    parser = argparse.ArgumentParser(description="Bounded KASE public-response refresh")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--attempts", required=True, type=Path)
    args = parser.parse_args(argv)
    source = trade_info_source(args.ticker)
    payload, metadata = fetch_public_json(
        source,
        cache_path=args.cache_dir / f"{args.ticker}.trade-info.json",
        attempts_path=args.attempts,
    )
    print(json.dumps({"source_id": source.source_id, "metadata": metadata,
                      "daily_rows": comparable_daily_trade_rows(payload)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
