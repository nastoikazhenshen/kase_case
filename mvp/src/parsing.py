"""Strict, locale-aware parsing helpers for the offline analytics engine."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from numbers import Number
from typing import Any


_MISSING = {"", "na", "n/a", "null", "none", "-", "—", "–"}
_MINUS = str.maketrans({"−": "-", "﹣": "-", "－": "-"})


def parse_number(value: Any) -> Decimal | None:
    """Parse a finite number without guessing a thousands/decimal convention.

    Russian decimal commas and ordinary/NBSP/thin-space digit grouping are
    accepted.  Formats that mix comma and dot are rejected: their meaning is
    ambiguous without a source-specific schema.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("boolean is not a numeric value")
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, Number):
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"invalid numeric value: {value!r}") from exc
    elif isinstance(value, str):
        text = value.translate(_MINUS).strip()
        if text.lower() in _MISSING:
            return None
        text = text.replace("\u00a0", "").replace("\u202f", "").replace(" ", "")
        if not text or text.count(",") > 1 or text.count(".") > 1:
            raise ValueError(f"unrecognized number format: {value!r}")
        if "," in text and "." in text:
            raise ValueError(f"ambiguous number format: {value!r}")
        if "," in text:
            text = text.replace(",", ".")
        try:
            number = Decimal(text)
        except InvalidOperation as exc:
            raise ValueError(f"unrecognized number format: {value!r}") from exc
    else:
        raise ValueError(f"unsupported numeric type: {type(value).__name__}")
    if not number.is_finite():
        raise ValueError(f"number must be finite: {value!r}")
    return number


def pct_to_excel(value: Any) -> Decimal | None:
    """Convert percentage units (e.g. ``0.5`` for 0.5%) to Excel fractions."""
    number = parse_number(value)
    return None if number is None else number / Decimal("100")


def excel_to_pct(value: Any) -> Decimal | None:
    """Convert an Excel percentage fraction to percentage units."""
    number = parse_number(value)
    return None if number is None else number * Decimal("100")


def parse_daily_date(value: Any) -> date:
    """Return an ISO daily date and reject timestamps or locale-dependent dates."""
    if isinstance(value, datetime):
        raise ValueError("daily date must not include a timestamp")
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("daily date must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid daily date: {value!r}") from exc
    return parsed
