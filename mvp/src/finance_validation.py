"""Independent, deterministic check of the published base scenario assumptions."""
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]


def _money(value: Any) -> Decimal:
    return Decimal(str(value))


def load_scenario(path: Path | None = None) -> dict[str, Any]:
    source = path or ROOT / "data/base_scenario.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("status") != "ASSUMPTION" or payload.get("unit") != "paying organization":
        raise ValueError("scenario must be an ASSUMPTION measured in paying organizations")
    schedule = payload.get("monthly_new_organizations")
    if not isinstance(schedule, list) or len(schedule) != 24 or any(not isinstance(x, int) or x < 0 for x in schedule):
        raise ValueError("monthly_new_organizations must contain 24 non-negative integers")
    return payload


def compute_base_scenario(scenario: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute all checkpoints from monthly inputs; never read cached workbook totals."""
    active = 0
    cumulative = -_money(scenario["startup_expenditure_kzt"])
    revenue_total = Decimal("0")
    payback_month: int | None = None
    rows: list[dict[str, int]] = []
    churn = {int(key): int(value) for key, value in scenario.get("monthly_churn_organizations", {}).items()}
    for month, new in enumerate(scenario["monthly_new_organizations"], start=1):
        beginning = active
        lost = min(beginning, churn.get(month, 0))
        active = beginning + int(new) - lost
        revenue = _money(scenario["monthly_subscription_kzt"]) * active
        variable = _money(scenario["variable_cost_per_active_organization_kzt"]) * active
        connection = _money(scenario["connection_cost_per_new_organization_kzt"]) * int(new)
        cashflow = revenue - variable - connection - _money(scenario["monthly_opex_kzt"])
        cumulative += cashflow
        revenue_total += revenue
        if payback_month is None and cumulative >= 0:
            payback_month = month
        rows.append({"month": month, "beginning_active": beginning, "new": int(new), "churn": lost,
                     "active": active, "revenue_kzt": int(revenue), "cashflow_kzt": int(cashflow),
                     "cumulative_cashflow_kzt": int(cumulative)})
    return {"status": scenario["status"], "unit": scenario["unit"], "month_12_active_organizations": rows[11]["active"],
            "month_24_active_organizations": rows[23]["active"], "revenue_24m_kzt": int(revenue_total),
            "cumulative_cashflow_m24_kzt": int(cumulative), "payback_month": payback_month, "monthly_rows": rows}


def validate(scenario: Mapping[str, Any]) -> dict[str, Any]:
    computed = compute_base_scenario(scenario)
    checks = scenario["reference_checkpoints"]
    expected = {"month_12_active_organizations": scenario["month_12_active_organizations"],
                "month_24_active_organizations": scenario["month_24_active_organizations"],
                "revenue_24m_kzt": checks["revenue_24m_kzt"],
                "cumulative_cashflow_m24_kzt": checks["cumulative_cashflow_m24_kzt"], "payback_month": checks["payback_month"]}
    mismatches = {key: {"expected": value, "actual": computed[key]} for key, value in expected.items() if computed[key] != value}
    return {"valid": not mismatches, "expected": expected, "computed": computed, "mismatches": mismatches}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Recompute BondScope base-scenario checkpoints")
    parser.add_argument("--scenario", type=Path, default=ROOT / "data/base_scenario.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = validate(load_scenario(args.scenario))
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
