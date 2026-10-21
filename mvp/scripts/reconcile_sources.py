"""Cross-check retained tables against separately retrieved official JSON revisions.

Agreement of values is not proof of the selected price view, trading mode or EOD.
No canonical row is changed by this command.
"""
import json
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
from mvp.src.acquisition import comparable_daily_trade_rows
from mvp.src.build_snapshot import write_csv
from mvp.src.repository import load_snapshot


def main():
    snapshot = load_snapshot()
    source = ROOT / "data/raw/acquisition/2026-10-22"
    checks = []
    for master in snapshot["instruments"]:
        ticker = master["ticker"]
        current = json.loads((source / f"{ticker}.bond.json").read_text(encoding="utf-8-sig"))
        for field, actual, expected in (
            ("ISIN", current["characteristics"]["isin"], master["instrument_id"]),
            ("denomination_currency", current["ticker"]["currency"], master["currency"]),
            ("maturity_date", current["ticker"]["finish_date"], master["maturity_date"]),
            ("instrument_type", current["ticker"]["typesec_en"], "coupon"),
        ):
            checks.append({"ticker": ticker, "field": field, "legacy": expected, "revision": actual,
                           "result": "MATCH" if actual == expected else "DIFFERENCE"})
        payload = json.loads((source / f"{ticker}.trade-info.json").read_text(encoding="utf-8-sig"))
        revisions = comparable_daily_trade_rows(payload)
        for revision in revisions:
            old = next(r for r in snapshot["observations"] if r["ticker"] == ticker and r["trade_date"] == revision["trade_date"])
            for field, new_field in (("last_price", "last_clean_price"), ("weighted_avg_price", "weighted_avg_clean_price"),
                                     ("high_price", "high_clean_price"), ("low_price", "low_clean_price"), ("trades_count", "trades_count"),
                                     ("turnover_kzt", "turnover_mln_kzt")):
                a = None if old[field] in ("", None) else Decimal(str(old[field]))
                b = None if revision[new_field] is None else Decimal(str(revision[new_field]))
                if b is not None and field == "turnover_kzt":
                    b *= 1_000_000
                tolerance = Decimal(old["turnover_precision_kzt"] or "0") / 2 if field == "turnover_kzt" else Decimal("0")
                status = "MATCH" if a == b else "WITHIN_DISPLAY_ROUNDING" if a is not None and b is not None and abs(a-b) <= tolerance else "DIFFERENCE"
                if field == "turnover_kzt" and a is None and b == 0 and revision["trades_count"] == 0:
                    status = "NEW_EXPLICIT_ZERO_OLD_MISSING"
                checks.append({"ticker": ticker, "field": field, "legacy": str(a) if a is not None else None,
                               "revision": str(b) if b is not None else None, "result": status})
    write_csv(ROOT / "data/processed/revision_reconciliation.csv", checks)
    summary = {"snapshot_id": snapshot["release"]["snapshot_id"], "checks": len(checks),
               "outcomes": {s: sum(c["result"] == s for c in checks) for s in ("MATCH", "WITHIN_DISPLAY_ROUNDING", "NEW_EXPLICIT_ZERO_OLD_MISSING", "DIFFERENCE")},
               "interpretation": "Field consistency only. No proof of same selected mode, price view or EOD; original observations unchanged.",
               "revision_difference": "HCBNb19 old table turnover missing; new API explicitly zero with zero trades. Both retained separately; unknown mode prevents promotion into canonical observations.",
               "local_details": "mvp/data/processed/revision_reconciliation.csv"}
    (ROOT / "implementation/acquisition/reconciliation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    if any(c["result"] == "DIFFERENCE" for c in checks):
        raise SystemExit("Unexplained revision differences need review")


if __name__ == "__main__":
    main()
