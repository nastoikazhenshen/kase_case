"""No-look-ahead event availability and issue/issuer mapping."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Iterable, Mapping


KAZAKHSTAN_POLICY_TZ = timezone(timedelta(hours=5), name="+05:00")


def _aware_instant(value: Any, *, field: str) -> datetime:
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str):
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{field} must be an ISO-8601 instant") from exc
    else:
        raise ValueError(f"{field} must be an aware datetime")
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return result


def _as_of_instant(value: Any) -> datetime:
    if isinstance(value, datetime):
        return _aware_instant(value, field="as_of")
    if isinstance(value, date):
        return datetime.combine(value, time.max, tzinfo=KAZAKHSTAN_POLICY_TZ)
    if isinstance(value, str):
        try:
            return _aware_instant(value, field="as_of")
        except ValueError:
            try:
                return datetime.combine(date.fromisoformat(value), time.max, tzinfo=KAZAKHSTAN_POLICY_TZ)
            except ValueError as exc:
                raise ValueError("as_of must be an aware instant or YYYY-MM-DD") from exc
    raise ValueError("as_of must be an aware instant or YYYY-MM-DD")


def event_availability(event: Mapping[str, Any], as_of: Any) -> dict[str, Any]:
    """Determine whether an event could have been known at *as_of*.

    A date-only ``as_of`` is treated as the end of that day in fixed +05:00.
    If publication timezone is unverified, availability starts at the next
    +05:00 local day; it is deliberately not a precise intraday claim.
    """
    published = _aware_instant(event.get("event_published_at"), field="event_published_at")
    precision = event.get("publication_precision")
    if precision not in {"SECOND", "MINUTE", "DATE"}:
        raise ValueError("publication_precision must be SECOND, MINUTE, or DATE")
    if not isinstance(event.get("timezone_verified"), bool):
        raise ValueError("timezone_verified must be bool")
    current = _as_of_instant(as_of)
    if event["timezone_verified"] and precision != "DATE":
        available_from = published
        limitation = "Время публикации подтверждено; сравнение выполнено по часовому поясу источника."
        status = "AVAILABLE" if current >= available_from else "NOT_YET_AVAILABLE"
    else:
        local_day = published.astimezone(KAZAKHSTAN_POLICY_TZ).date() + timedelta(days=1)
        available_from = datetime.combine(local_day, time.min, tzinfo=KAZAKHSTAN_POLICY_TZ)
        if precision == "DATE":
            limitation = "Источник указал только дату публикации: применено консервативное правило следующего дня +05:00."
            status = "AVAILABLE_DATE_CONSERVATIVE" if current >= available_from else "NOT_YET_AVAILABLE_DATE_CONSERVATIVE"
        else:
            limitation = "Часовой пояс публикации не подтвержден: применено консервативное правило следующего дня +05:00."
            status = "AVAILABLE_CONSERVATIVE" if current >= available_from else "NOT_YET_AVAILABLE_CONSERVATIVE"
    return {
        "available": current >= available_from,
        "status": status,
        "available_from": available_from.isoformat(),
        "limitation": limitation,
    }


def events_for_instrument(
    events: Iterable[Mapping[str, Any]], instrument_id: str, issuer_id: str, as_of: Any
) -> list[dict[str, Any]]:
    """Return only mapped events that were available at *as_of*.

    ISSUE records must match the requested instrument; ISSUER records must
    match its issuer.  Unknown mapping scopes are invalid rather than broadly
    matched, preventing a sibling-bond disclosure leak.
    """
    result: list[dict[str, Any]] = []
    for event in events:
        scope = event.get("mapping_scope")
        if scope == "ISSUE":
            matched = event.get("instrument_id") == instrument_id
        elif scope == "ISSUER":
            matched = bool(issuer_id) and event.get("issuer_id") == issuer_id
        else:
            raise ValueError("mapping_scope must be ISSUE or ISSUER")
        if not matched:
            continue
        availability = event_availability(event, as_of)
        if availability["available"]:
            enriched = dict(event)
            enriched["availability"] = availability
            result.append(enriched)
    return result
