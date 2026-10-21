"""Normalize immutable legacy evidence; join new sources without changing old rows.

Run from repository root: python -m mvp.src.build_snapshot
Market-bearing outputs deliberately stay local while redistribution rights are unresolved.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .repository import ROOT, canonical_json, read_csv, sha256, validate_snapshot

VERIFICATION = ROOT / "data/raw/archive/verification"
TASK1 = ROOT / "data/raw/archive/task1"
NEW = ROOT / "data/raw/acquisition/2026-10-22"


def retrieval_metadata(entry):
    """Retain collector timing; a revision's completion is its retrieval instant."""
    instant = entry.get("retrieval_completed_at_utc") or entry.get("retrieved_at_utc", "")
    return {"retrieved_at": instant,
            "retrieval_started_at_utc": entry.get("retrieval_started_at_utc", ""),
            "retrieval_completed_at_utc": entry.get("retrieval_completed_at_utc", ""),
            "retrieval_timestamp_status": entry.get("retrieval_timestamp_status", "RECORDED" if instant else "NOT_RECORDED")}


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})


def build():
    sources, migrations = [], []
    for namespace, registry in (("LEGACY", VERIFICATION / "inputs/source_register.csv"),
                                ("VERIFY", VERIFICATION / "source_register.csv")):
        for source in read_csv(registry):
            original = source.get("local_file") or source.get("local_evidence", "")
            resolved = VERIFICATION / original if original else None
            if namespace == "LEGACY" and original.startswith("data/raw_extracted/"):
                resolved = VERIFICATION / "inputs/task1_raw_extracted" / Path(original).name
            elif namespace == "LEGACY" and original.startswith("data/metadata/"):
                resolved = TASK1 / original
            record = {"source_id": f"{namespace}:{source['source_id']}", "legacy_source_id": source["source_id"],
                      "source_url": source["URL"], "retrieved_at": source.get("captured_at_utc", ""),
                      "retrieval_date": source.get("date_accessed", ""),
                      "retrieval_timestamp_status": "RECORDED" if source.get("captured_at_utc") else "DATE_ONLY",
                      "kind": source.get("source_kind", "VERIFICATION_TRANSCRIPTION"),
                      "status": source.get("access_status", source.get("status", "")),
                      "units": source["units"], "notes": source.get("notes", ""), "original_path": original,
                      "evidence_path": str(resolved.relative_to(ROOT)).replace("\\", "/") if resolved else "",
                      "evidence_sha256": sha256(resolved) if resolved else ""}
            sources.append(record)
            if original:
                migrations.append({"source_id": record["source_id"], "original_path": original,
                                   "resolved_path": record["evidence_path"], "sha256": record["evidence_sha256"]})
    registry_map = {r["source_id"]: r for r in sources}
    raw_masters = read_csv(VERIFICATION / "data/instrument_master.csv")
    masters = []
    for master in raw_masters:
        row = dict(master)
        row["issuer_id"] = "CLSG" if row["ticker"].startswith("CLSG") else row["ticker"].split("b")[0]
        row["instrument_type"] = "COUPON_BOND"
        row["source_id"] = f"LEGACY:{row['source_id']}"
        row["quotation_source_id"] = f"LEGACY:{row['quotation_source_id']}"
        row["original_raw_file"] = row.get("raw_file", "")
        row["raw_file"] = registry_map[row["source_id"]]["evidence_path"]
        row["metadata_status"] = "VERIFIED_FROM_RETAINED_OFFICIAL_TRANSCRIPTION"
        masters.append(row)
    observations = []
    for raw in read_csv(VERIFICATION / "data/observations_reviewed.csv"):
        primary = registry_map[f"LEGACY:{raw['source_id']}"]
        row = dict(raw)
        row.update(row_id=f"LEGACY-{raw['ticker']}-{raw['trade_date']}",
                   source_id=primary["source_id"], source_ids=[primary["source_id"], f"VERIFY:QUOTE_{raw['ticker']}"],
                   price_basis="UNVERIFIED_ACTIVE_TAB", price_view_status="UNVERIFIED_ACTIVE_TAB",
                   mode_status="VERIFIED" if raw["trading_mode_status"] == "CONFIRMED_FOR_THIS_DATE" else "UNCONFIRMED",
                   finality="AS_PUBLISHED_NOT_CERTIFIED_EOD", denomination_currency=raw["currency"],
                   trade_currency="KZT", instrument_type="COUPON_BOND", scope_status="VERIFIED_KZT_COUPON",
                   observation_kind="DAILY", retrieved_at=raw["captured_at_utc"],
                   observation_as_of=f"{raw['trade_date']}T23:59:59.999999+05:00",
                   observation_as_of_policy="DATE_ONLY_EOD_RETROSPECTIVE_NOT_CERTIFIED_EOD",
                   evidence_path=primary["evidence_path"], evidence_sha256=primary["evidence_sha256"],
                   source_file=primary["evidence_path"],
                   original_source_path=raw["source_file"], original_fields=dict(raw), extraction_version="BS3-import-1.0",
                   turnover_precision_kzt=raw["turnover_source_display_step_kzt"],
                   turnover_status="DISPLAY_ROUNDED" if raw["turnover_kzt"] else "MISSING")
        if raw["mode_evidence_id"]:
            row["source_ids"].append(f"VERIFY:{raw['mode_evidence_id']}")
        observations.append(row)
    events = []
    for raw in read_csv(VERIFICATION / "data/issuer_events.csv"):
        events.append({**raw, "title": "Сообщение о выплате второго купона CLSGb11", "issuer_id": "CLSG",
                       "mapping_scope": "ISSUE", "source_id": f"VERIFY:{raw['evidence_id']}",
                       "timezone_verified": False, "publication_precision": "MINUTE",
                       "evidence_status": raw["verified_via"], "retrieved_at": "", "retrieval_date": raw["review_date"]})
    # Fresh sources remain revisions/context; they never establish the old selected tab.
    manifest_file = ROOT / "implementation/acquisition/evidence_manifest.json"
    fresh = json.loads(manifest_file.read_text(encoding="utf-8-sig")) if manifest_file.exists() else []
    fresh_sources = {}
    for entry in fresh:
        target = NEW / entry["artifact"]
        if not target.is_file() or sha256(target) != entry["sha256"]:
            raise ValueError(f"Fresh evidence hash mismatch: {entry['artifact']}")
        key = "PUBLIC:" + entry["artifact"]
        record = {"source_id": key, "source_url": entry["source_url"], **retrieval_metadata(entry),
                  "kind": entry["type"], "status": "RECOVERED_PUBLIC_LOCAL_ONLY",
                  "evidence_path": str(target.relative_to(ROOT)).replace("\\", "/"), "evidence_sha256": entry["sha256"]}
        sources.append(record)
        fresh_sources[entry["artifact"]] = record
    notice = next((s for name, s in fresh_sources.items() if name.endswith("CLSGb11-event-1578268.reverified.html")), fresh_sources.get("CLSGb11-event-1578268.html"))
    if notice:
        events[0].update(source_id=notice["source_id"], evidence_status="OFFICIAL_FULL_NOTICE",
                         legacy_evidence_id=events[0]["evidence_id"], evidence_id=notice["source_id"],
                         legacy_verified_via=events[0]["verified_via"], verified_via="OFFICIAL_FULL_NOTICE",
                         retrieved_at=notice["retrieved_at"], full_page_access="RECOVERED_PUBLIC",
                         evidence_path=notice["evidence_path"], evidence_sha256=notice["evidence_sha256"])
    valuations = []
    val_source = next((s for name, s in fresh_sources.items() if name.endswith("market-valuations.reverified.json")), fresh_sources.get("market-valuations.json"))
    if val_source:
        allowed = {x["instrument_id"] for x in masters}
        payload = json.loads((ROOT / val_source["evidence_path"]).read_text(encoding="utf-8-sig"))
        for valuation_date, records in payload.items():
            for raw in records:
                if raw["isin"] not in allowed:
                    continue
                valuations.append({"instrument_id": raw["isin"], "ticker": raw["code"],
                                   "valuation_date": valuation_date, "market_price": raw["settlement_price"],
                                   "dirty_market_price": raw["settlement_dirty_price"], "estimated_price": None,
                                   "valuation_type": "OFFICIAL_MARKET_VALUATION", "unit": raw["unit_en"],
                                   "source_id": val_source["source_id"], "source_url": "https://kase.kz/ru/markets/markets-valuation",
                                   "retrieved_at": val_source["retrieved_at"], "original_fields": raw})
    coverage = [{"instrument_id": m["instrument_id"], "ticker": m["ticker"], "legacy_dates": "2026-10-20;2026-10-21",
                 "retained_daily_rows": sum(r["instrument_id"] == m["instrument_id"] for r in observations),
                 "verified_price_rows": 0, "eligible_prior_history": 0, "history_status": "INSUFFICIENT_DATA",
                 "mode_verified_dates": ";".join(r["trade_date"] for r in observations if r["instrument_id"] == m["instrument_id"] and r["mode_status"] == "VERIFIED"),
                 "valuation_dates": ";".join(v["valuation_date"] for v in valuations if v["instrument_id"] == m["instrument_id"]),
                 "event_coverage": "ONE_NOTICE_NOT_COMPLETE_FEED" if m["ticker"] == "CLSGb11" else "NOT_LOADED"} for m in masters]
    rules = json.loads((ROOT / "data/rules.json").read_text(encoding="utf-8"))
    snapshot = {"schema_version": "BS3-1.0", "observations": observations, "instruments": masters,
                "events": events, "valuations": valuations, "sources": sources, "coverage": coverage, "rules": rules}
    validate_snapshot(snapshot)
    processed = ROOT / "data/processed"
    processed.mkdir(parents=True, exist_ok=True)
    data = canonical_json(snapshot).encode("utf-8")
    snapshot_hash = hashlib.sha256(data).hexdigest()
    (processed / "snapshot.json").write_bytes(data)
    release = {"snapshot_id": f"BS3-{snapshot_hash[:16]}", "snapshot_sha256": snapshot_hash,
               "status": "PARTIAL — EXTERNAL DATA BLOCKER", "selection_policy": "Legacy dated snapshots retained unchanged; fresh API revisions are separately archived and reconciled. Valuations and full notice added as context.",
               "limitations": ["Активная ценовая вкладка не доказана: KASE WAF блокирует браузер до появления контролов.",
                               "Два снимка не являются историей: нет 10 сопоставимых предыдущих наблюдений.",
                               "Снимки не сертифицированы как окончательные итоги дня.",
                               "Часовой пояс публикации не указан: событие доступно со следующего дня +05:00.",
                               "Публичное распространение материалов KASE требует письменного разрешения; рыночный пакет хранится локально."]}
    (processed / "release.json").write_text(json.dumps(release, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, rows in (("cleaned_bonds", observations), ("instrument_master", masters), ("issuer_events", events),
                       ("coverage_report", coverage), ("valuations", valuations)):
        write_csv(processed / f"{name}.csv", rows)
    write_csv(ROOT / "source_register.csv", sources)
    write_csv(ROOT / "implementation/source_path_migration.csv", migrations)
    write_csv(ROOT / "implementation/coverage_report.csv", coverage)
    # Public manifest contains hashes, counts and limitations, no copied market values.
    (ROOT / "implementation/release_manifest.json").write_text(json.dumps({**release, "observation_count": len(observations),
        "instrument_count": len(masters), "valuation_count": len(valuations), "event_count": len(events)}, ensure_ascii=False, indent=2), encoding="utf-8")
    return snapshot, release


if __name__ == "__main__":
    _, release = build()
    print(json.dumps(release, ensure_ascii=False, indent=2))
