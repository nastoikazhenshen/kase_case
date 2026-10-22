"""An explicit, hypothetical input on an unchanged real observation.

The preset is never applied on page load. It is not a customer order or a
market observation; both the UI action and the reproducible export opt in.
"""
from .reports import build_report

DEMO_DATE = "2026-10-21"
DEMO_TICKER = "BIGDb5"
DEMO_AMOUNT_KZT = 100000.0
DEMO_RULE = "planned_amount_to_observed_daily_turnover"


def demo_report(snapshot):
    rows = [row for row in snapshot["observations"]
            if row["trade_date"] == DEMO_DATE and row["ticker"] == DEMO_TICKER]
    if len(rows) != 1:
        raise ValueError("The demonstration requires exactly one frozen BIGDb5 observation")
    return build_report(snapshot, rows, DEMO_DATE, planned_amount_kzt=DEMO_AMOUNT_KZT)
