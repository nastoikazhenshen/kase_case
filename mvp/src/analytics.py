"""Deterministic exception rules with explicit quality and history gates."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from statistics import median
from typing import Any, Iterable, Mapping

from .parsing import parse_daily_date, parse_number


RULES = (
    "price_gap_pct", "range_pct", "turnover_ratio", "trades_ratio",
    "trade_size_to_turnover", "planned_amount_to_observed_daily_turnover",
)
HISTORY_RULES = {"turnover_ratio", "trades_ratio", "trade_size_to_turnover"}
DEFAULT_RULES = {
    "method_version": "BS3-1.0", "hypothesis": True, "window": 20, "minimum_n": 10,
    "thresholds": {"price_gap_pct": 0.5, "range_pct": 1.0, "turnover_ratio": 3.0,
                   "trades_ratio": 3.0, "trade_size_to_turnover": 0.25,
                   "planned_amount_to_observed_daily_turnover": 0.25},
}
# The first applicable reason is returned, so quality failures remain stable and auditable.
GATE_PRECEDENCE = ("BLOCKED_SCOPE", "BLOCKED_OBSERVATION_KIND", "BLOCKED_MODE",
                   "BLOCKED_PRICE_VIEW", "BLOCKED_PRICE_BASIS", "INCOMPLETE_SESSION", "BLOCKED_FINALITY")
_POLICY_TZ = timezone(timedelta(hours=5), name="+05:00")


def _text(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    return value.strip() if isinstance(value, str) else ""


def _row_gate(row: Mapping[str, Any], *, needs_history: bool, needs_price: bool) -> str | None:
    if row.get("scope_status") != "VERIFIED_KZT_COUPON": return "BLOCKED_SCOPE"
    if row.get("observation_kind") != "DAILY": return "BLOCKED_OBSERVATION_KIND"
    if row.get("mode_status") != "VERIFIED" or not _text(row, "trading_mode"): return "BLOCKED_MODE"
    if needs_price:
        # The observed tab is the more specific price-quality failure.
        if row.get("price_view_status") != "VERIFIED": return "BLOCKED_PRICE_VIEW"
        if row.get("price_basis") != "CLEAN_PERCENT_OF_NOMINAL": return "BLOCKED_PRICE_BASIS"
    if needs_history and row.get("finality") == "INCOMPLETE_SESSION": return "INCOMPLETE_SESSION"
    if needs_history and row.get("finality") not in {"CERTIFIED_EOD", "HISTORICAL_PUBLISHED"}: return "BLOCKED_FINALITY"
    return None


def _decimal(row: Mapping[str, Any], field: str, *, nonnegative: bool = False) -> Decimal | None:
    number = parse_number(row.get(field))
    if number is not None and nonnegative and number < 0:
        raise ValueError(f"{field} must be non-negative")
    return number


def _base_result(rule: str, row: Mapping[str, Any], method_version: str, threshold: Any) -> dict[str, Any]:
    trade_date = parse_daily_date(row.get("trade_date")).isoformat()
    return {"rule": rule, "row_id": row.get("row_id"), "instrument_id": row.get("instrument_id"),
            "ticker": row.get("ticker"), "trade_date": trade_date, "trading_mode": row.get("trading_mode"),
            "as_of": _observation_as_of(row, trade_date), "value": None, "baseline": None, "n": None,
            "window_start": None, "window_end": None, "threshold": _plain_number(threshold), "units": "%" if rule in {"price_gap_pct", "range_pct"} else "ratio",
            "input_row_ids": [row.get("row_id")] if row.get("row_id") is not None else [],
            "source_ids": _row_source_ids(row), "source_urls": _row_source_urls(row),
            "method_version": method_version, "status": "", "explanation": "", "limitations": ""}


def _plain_number(value: Any) -> int | float | None:
    if value is None: return None
    number = parse_number(value)
    return float(number) if number is not None else None


def _sources(rows: Iterable[Mapping[str, Any]], field: str) -> list[str]:
    return list(dict.fromkeys(str(value) for row in rows if (value := row.get(field)) not in (None, "")))


def _row_source_ids(row: Mapping[str, Any]) -> list[str]:
    """Preserve every row-level proof reference, including mode confirmation."""
    values = row.get("source_ids")
    listed = values if isinstance(values, (list, tuple)) else []
    primary = row.get("source_id")
    return list(dict.fromkeys(str(value) for value in [*listed, primary] if value not in (None, "")))


def _row_source_urls(row: Mapping[str, Any]) -> list[str]:
    values = row.get("source_urls")
    listed = values if isinstance(values, (list, tuple)) else []
    return list(dict.fromkeys(str(value) for value in [*listed, row.get("source_url")] if value not in (None, "")))


def _observation_as_of(row: Mapping[str, Any], trade_date: str) -> str:
    """Use an explicit observation instant, or the documented +05:00 day-end policy."""
    value = row.get("observation_as_of")
    if value not in (None, ""):
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("observation_as_of must be an aware ISO-8601 instant") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("observation_as_of must include a timezone")
        return parsed.isoformat()
    return datetime.combine(parse_daily_date(trade_date), time.max, tzinfo=_POLICY_TZ).isoformat()


def _blocked(result: dict[str, Any], status: str) -> dict[str, Any]:
    result.update(status=status, explanation=f"Расчёт заблокирован: {status}.",
                  limitations="Качество или сопоставимость входных данных не подтверждены; исключение не является рыночным сигналом.")
    return result


def _history(row: Mapping[str, Any], history: Iterable[Mapping[str, Any]], field: str) -> list[Mapping[str, Any]]:
    current_date = parse_daily_date(row.get("trade_date"))
    selected: list[Mapping[str, Any]] = []
    seen_dates: set[date] = set()
    for candidate in history:
        if candidate.get("instrument_id") != row.get("instrument_id") or candidate.get("trading_mode") != row.get("trading_mode") or candidate.get("price_basis") != row.get("price_basis"):
            continue
        day = parse_daily_date(candidate.get("trade_date"))
        if day >= current_date:
            continue
        if day in seen_dates:
            raise ValueError(f"duplicate historical revision for {day.isoformat()}")
        seen_dates.add(day)
        _validate_row_enums(candidate)
        if _row_gate(candidate, needs_history=False, needs_price=False) is not None:
            continue
        if candidate.get("finality") != row.get("finality"):
            continue
        value = _decimal(candidate, field, nonnegative=True)
        if value is None:
            continue
        if field == "turnover_kzt" and candidate.get("turnover_status") == "ROUNDED_ZERO":
            continue
        selected.append(candidate)
    return sorted(selected, key=lambda item: parse_daily_date(item["trade_date"]))


def _validate_row_enums(row: Mapping[str, Any]) -> None:
    """Reject invalid controlled values before a caller can mistake them for data gaps."""
    if row.get("finality") not in {
        "CERTIFIED_EOD", "HISTORICAL_PUBLISHED", "AS_PUBLISHED_NOT_CERTIFIED_EOD", "INCOMPLETE_SESSION",
    }:
        raise ValueError("invalid finality")
    turnover_status = row.get("turnover_status")
    if turnover_status not in {"MISSING", "ROUNDED_ZERO", "DISPLAY_ROUNDED", "EXACT", None}:
        raise ValueError("invalid turnover_status")
    turnover = _decimal(row, "turnover_kzt", nonnegative=True)
    trades = _decimal(row, "trades_count", nonnegative=True)
    if trades is not None and trades != trades.to_integral_value():
        raise ValueError("trades_count must be an integer")
    if turnover is None and turnover_status not in {"MISSING", None}:
        raise ValueError("missing turnover must have MISSING turnover_status")
    if turnover is not None and turnover_status == "MISSING":
        raise ValueError("present turnover cannot have MISSING turnover_status")
    if turnover == 0 and trades is not None and trades > 0 and turnover_status != "ROUNDED_ZERO":
        raise ValueError("zero displayed turnover with positive trades must be ROUNDED_ZERO")
    if turnover_status == "ROUNDED_ZERO" and (turnover != 0 or trades is None or trades <= 0):
        raise ValueError("ROUNDED_ZERO requires zero turnover and positive trades")


def _finish(result: dict[str, Any], *, value: Decimal, threshold: Any, rows: list[Mapping[str, Any]] = (), baseline: Decimal | None = None, threshold_value: Decimal | None = None) -> dict[str, Any]:
    result["value"] = _plain_number(value)
    result["baseline"] = _plain_number(baseline)
    if rows:
        result["n"] = len(rows)
        result["window_start"] = parse_daily_date(rows[0]["trade_date"]).isoformat()
        result["window_end"] = parse_daily_date(rows[-1]["trade_date"]).isoformat()
        all_rows = [*([{"row_id": result["row_id"], "source_id": None, "source_url": None}]), *rows]
        result["input_row_ids"] = [x.get("row_id") for x in all_rows if x.get("row_id") is not None]
        # Current-source lists already exist; merge baseline provenance deterministically.
        result["source_ids"] = list(dict.fromkeys([*result["source_ids"], *(sid for row in rows for sid in _row_source_ids(row))]))
        result["source_urls"] = list(dict.fromkeys([*result["source_urls"], *(url for row in rows for url in _row_source_urls(row))]))
    if threshold is None:
        return _blocked(result, "NOT_CONFIGURED")
    threshold_d = parse_number(threshold)
    if threshold_d is None or threshold_d < 0:
        raise ValueError("threshold must be a non-negative finite number or None")
    comparison = value if threshold_value is None else threshold_value
    result["status"] = "TRIGGERED" if comparison >= threshold_d else "EVALUATED"
    result["explanation"] = "Значение правила рассчитано по подтверждённым сопоставимым данным." if result["status"] == "EVALUATED" else "Значение правила достигло демонстрационного порога и требует проверки аналитиком."
    result["limitations"] = "Порог является гипотезой метода, а не прогнозом или доказательством нарушения."
    return result


def evaluate(row: Mapping[str, Any], history: Iterable[Mapping[str, Any]], rules: Mapping[str, Any], planned_amount_kzt: Any = None) -> list[dict[str, Any]]:
    """Evaluate all six rules.  All rolling windows are strictly before ``trade_date``."""
    parse_daily_date(row.get("trade_date"))
    if not _text(row, "instrument_id"):
        raise ValueError("instrument_id is required")
    _validate_row_enums(row)
    method_version = str(rules.get("method_version", DEFAULT_RULES["method_version"]))
    window, minimum = rules.get("window", 20), rules.get("minimum_n", 10)
    if not isinstance(window, int) or not isinstance(minimum, int) or window < 1 or minimum < 1 or minimum > window:
        raise ValueError("window and minimum_n must be positive integers with minimum_n <= window")
    thresholds = rules.get("thresholds", {})
    if not isinstance(thresholds, Mapping): raise ValueError("thresholds must be a mapping")
    material_history = list(history)
    results: list[dict[str, Any]] = []
    for rule in RULES:
        threshold = thresholds.get(rule)
        result = _base_result(rule, row, method_version, threshold)
        gate = _row_gate(row, needs_history=rule in HISTORY_RULES, needs_price=rule in {"price_gap_pct", "range_pct"})
        if gate:
            results.append(_blocked(result, gate)); continue
        try:
            if rule == "price_gap_pct":
                last, average = _decimal(row, "last_price", nonnegative=True), _decimal(row, "weighted_avg_price", nonnegative=True)
                if last is None or average is None: results.append(_blocked(result, "MISSING_FIELD")); continue
                if average == 0: results.append(_blocked(result, "ZERO_BASELINE")); continue
                value = Decimal("100") * (last / average - 1)
                results.append(_finish(result, value=value, threshold=threshold, threshold_value=abs(value))); continue
            if rule == "range_pct":
                high, low, average = _decimal(row, "high_price", nonnegative=True), _decimal(row, "low_price", nonnegative=True), _decimal(row, "weighted_avg_price", nonnegative=True)
                if high is None or low is None or average is None: results.append(_blocked(result, "MISSING_FIELD")); continue
                if high < low: results.append(_blocked(result, "INVALID_RANGE")); continue
                if average == 0: results.append(_blocked(result, "ZERO_BASELINE")); continue
                results.append(_finish(result, value=Decimal("100") * (high - low) / average, threshold=threshold)); continue
            if rule == "planned_amount_to_observed_daily_turnover":
                planned, turnover = parse_number(planned_amount_kzt), _decimal(row, "turnover_kzt", nonnegative=True)
                if planned is None: results.append(_blocked(result, "INPUT_REQUIRED")); continue
                if planned < 0: raise ValueError("planned_amount_kzt must be non-negative")
                if turnover is None: results.append(_blocked(result, "MISSING_FIELD")); continue
                if turnover == 0 or row.get("turnover_status") == "ROUNDED_ZERO": results.append(_blocked(result, "ZERO_BASELINE")); continue
                results.append(_finish(result, value=planned / turnover, threshold=threshold)); continue
            field = "turnover_kzt" if rule in {"turnover_ratio", "trade_size_to_turnover"} else "trades_count"
            current = _decimal(row, field, nonnegative=True)
            if current is None and rule != "trade_size_to_turnover": results.append(_blocked(result, "MISSING_FIELD")); continue
            if field == "turnover_kzt" and row.get("turnover_status") == "ROUNDED_ZERO": results.append(_blocked(result, "ZERO_BASELINE")); continue
            selected = _history(row, material_history, field)[-window:]
            if len(selected) < minimum: results.append(_blocked(result, "INSUFFICIENT_DATA")); continue
            baseline = Decimal(str(median([_decimal(item, field, nonnegative=True) for item in selected])))
            if baseline <= 0: results.append(_blocked(result, "ZERO_BASELINE")); continue
            if rule == "trade_size_to_turnover":
                planned = parse_number(planned_amount_kzt)
                if planned is None: results.append(_blocked(result, "INPUT_REQUIRED")); continue
                if planned < 0: raise ValueError("planned_amount_kzt must be non-negative")
                value = planned / baseline
            else:
                value = current / baseline
            results.append(_finish(result, value=value, threshold=threshold, rows=selected, baseline=baseline))
        except ValueError:
            raise
    return results
