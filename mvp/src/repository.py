"""Portable, fail-closed loading of the frozen local evidence pack."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def contained_path(root, relative):
    target = (Path(root) / relative).resolve()
    if not target.is_relative_to(Path(root).resolve()):
        raise ValueError(f"Evidence path escapes pack: {relative}")
    return target


def validate_snapshot(snapshot, root=ROOT):
    sources = {}
    for source in snapshot["sources"]:
        key = source["source_id"]
        if key in sources:
            raise ValueError(f"Duplicate source ID: {key}")
        sources[key] = source
        if source.get("evidence_path"):
            file = contained_path(root, source["evidence_path"])
            if not file.is_file():
                raise FileNotFoundError(f"Missing local evidence: {source['evidence_path']}")
            if sha256(file) != source["evidence_sha256"]:
                raise ValueError(f"Evidence hash mismatch: {key}")
    ids, grains = set(), set()
    masters = {r["instrument_id"]: r for r in snapshot["instruments"]}
    if len(masters) != len(snapshot["instruments"]):
        raise ValueError("Duplicate master instrument ID")
    for master in masters.values():
        for key in ("source_id", "quotation_source_id"):
            if master[key] not in sources:
                raise ValueError("Unresolved master source")
        if master["raw_file"] != sources[master["source_id"]]["evidence_path"]:
            raise ValueError("Master source path mismatch")
    from .parsing import parse_daily_date, parse_number
    from .analytics import evaluate
    for row in snapshot["observations"]:
        if row["row_id"] in ids:
            raise ValueError("Duplicate row ID")
        ids.add(row["row_id"])
        grain = tuple(row.get(k) for k in ("instrument_id", "trade_date", "trading_mode", "price_basis", "finality"))
        if grain in grains:
            raise ValueError("Duplicate canonical grain; select a revision explicitly")
        grains.add(grain)
        parse_daily_date(row["trade_date"])
        master = masters.get(row["instrument_id"])
        if not master or master["ticker"] != row["ticker"]:
            raise ValueError("ISIN/ticker mapping mismatch")
        if master["currency"] != "KZT" or row["denomination_currency"] != "KZT":
            raise ValueError("Non-KZT row in coupon-bond universe")
        if row["instrument_type"] != "COUPON_BOND":
            raise ValueError("Unsupported instrument type")
        for source_id in row["source_ids"]:
            if source_id not in sources:
                raise ValueError(f"Unresolved source: {source_id}")
        primary = sources[row["source_id"]]
        if row["evidence_path"] != primary["evidence_path"] or row["evidence_sha256"] != primary["evidence_sha256"]:
            raise ValueError("Observation provenance mismatch")
        if row["source_file"] != row["evidence_path"]:
            raise ValueError("Observation source alias is stale")
        if row.get("turnover_mln_kzt") not in (None, ""):
            if parse_number(row["turnover_kzt"]) != parse_number(row["turnover_mln_kzt"]) * 1_000_000:
                raise ValueError("Turnover unit conversion mismatch")
        evaluate(row, [], snapshot["rules"])
    for collection in (snapshot["events"], snapshot.get("valuations", [])):
        for row in collection:
            if row["instrument_id"] not in masters or row["source_id"] not in sources:
                raise ValueError("Unresolved event/valuation mapping")
    for source in sources.values():
        url = source.get("source_url", "")
        if url and urlparse(url).scheme not in {"https", "http", "local"}:
            raise ValueError("Unsupported source URL scheme")


def load_snapshot(root=ROOT):
    root = Path(root)
    file = root / "data/processed/snapshot.json"
    snapshot = json.loads(file.read_text(encoding="utf-8"))
    manifest = json.loads((root / "data/processed/release.json").read_text(encoding="utf-8"))
    if sha256(file) != manifest["snapshot_sha256"]:
        raise ValueError("Snapshot hash mismatch")
    validate_snapshot(snapshot, root)
    snapshot["release"] = manifest
    return snapshot
