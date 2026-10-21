"""Immutable report snapshots; UI and exports consume the identical calculations."""
from __future__ import annotations

import copy
import csv
import hashlib
import html
import io
from decimal import Decimal
from urllib.parse import urlparse

from .analytics import evaluate
from .events import events_for_instrument
from .repository import canonical_json


def safe_text(value):
    """Prevent formula injection even after Excel strips leading whitespace."""
    text = str(value)
    return "'" + text if text.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")) else text


def safe_url(value):
    parsed = urlparse(str(value))
    return str(value) if parsed.scheme in {"https", "http"} and parsed.netloc else ""


def build_report(snapshot, selected_rows, as_of, planned_amount_kzt=None):
    canonical_rows = {row["row_id"]: row for row in snapshot["observations"]}
    selected = []
    seen = set()
    for row in selected_rows:
        if row["row_id"] not in canonical_rows or canonical_json(row) != canonical_json(canonical_rows[row["row_id"]]):
            raise ValueError("Report row does not match frozen snapshot")
        if row["row_id"] in seen:
            raise ValueError("Duplicate report row")
        seen.add(row["row_id"])
        selected.append(copy.deepcopy(row))
    selected.sort(key=lambda r: (r["trade_date"], r["ticker"], r["row_id"]))
    for row in selected:
        row["average_observed_trade_size_kzt"] = None
        if row["mode_status"] == "VERIFIED" and row.get("turnover_kzt") not in (None, "") and Decimal(str(row.get("trades_count") or "0")) > 0:
            row["average_observed_trade_size_kzt"] = float(Decimal(str(row["turnover_kzt"])) / Decimal(str(row["trades_count"])))
    evaluations = [result for row in selected for result in evaluate(row, snapshot["observations"], snapshot["rules"], planned_amount_kzt)]
    source_map = {s["source_id"]: s for s in snapshot["sources"]}
    for result in evaluations:
        result["source_urls"] = list(dict.fromkeys(source_map[sid]["source_url"] for sid in result["source_ids"]))
    masters = {m["instrument_id"]: m for m in snapshot["instruments"]}
    events = {}
    for instrument_id in {r["instrument_id"] for r in selected}:
        for event in events_for_instrument(snapshot["events"], instrument_id, masters[instrument_id]["issuer_id"], as_of):
            events[event["event_id"]] = event
    source_ids = {sid for row in selected for sid in row["source_ids"]}
    source_ids.update(sid for result in evaluations for sid in result["source_ids"])
    source_ids.update(e["source_id"] for e in events.values())
    valuations = [v for v in snapshot.get("valuations", []) if any(v["instrument_id"] == r["instrument_id"] and v["valuation_date"] == r["trade_date"] for r in selected)]
    source_ids.update(v["source_id"] for v in valuations)
    report = {"snapshot_id": snapshot["release"]["snapshot_id"], "as_of": str(as_of),
              "event_as_of_policy": "Separate retrospective event context; not information known at each trade instant. Date-only = end-of-day +05:00.",
              "planned_amount_kzt": planned_amount_kzt, "rules": copy.deepcopy(snapshot["rules"]),
              "observations": selected, "evaluations": evaluations,
              "events": sorted(events.values(), key=lambda e: e["event_id"]), "valuations": valuations,
              "sources": [copy.deepcopy(s) for s in snapshot["sources"] if s["source_id"] in source_ids],
              "limitations": list(snapshot["release"]["limitations"])}
    report["report_id"] = "BS3-REPORT-" + hashlib.sha256(canonical_json(report).encode("utf-8")).hexdigest()[:20]
    return copy.deepcopy(report)


def report_csv(report):
    """Typed CSV preserves the evaluated rows and their event/valuation/source context."""
    fields = ["record_type", "report_id", "snapshot_id", "event_context_as_of", "ticker", "instrument_id", "trade_date", "trading_mode",
              "rule", "status", "value", "units", "baseline", "n", "window_start", "window_end", "threshold", "as_of",
              "method_version", "last_price", "weighted_avg_price", "high_price", "low_price", "turnover_kzt", "trades_count",
              "planned_amount_kzt", "average_observed_trade_size_kzt", "input_row_ids", "source_ids", "source_urls", "explanation", "limitations"]
    lookup = {r["row_id"]: r for r in report["observations"]}
    rows = []
    for result in report["evaluations"]:
        rows.append({**lookup[result["row_id"]], **result, "record_type": "EVALUATION"})
    for collection, kind in (("events", "EVENT"), ("valuations", "VALUATION"), ("sources", "SOURCE")):
        rows.extend({**row, "record_type": kind} for row in report[collection])
    fields = list(dict.fromkeys([*fields, *(key for row in rows for key in row)]))
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for original in rows:
        row = {**original, "report_id": report["report_id"], "snapshot_id": report["snapshot_id"],
               "event_context_as_of": report["as_of"], "planned_amount_kzt": report["planned_amount_kzt"]}
        writer.writerow({k: safe_text(canonical_json(v) if isinstance(v, (list, dict)) else v) if isinstance(v, (str, list, dict)) else v for k, v in row.items()})
    return ("\ufeff" + output.getvalue()).encode("utf-8")


def _table(rows, columns):
    headings = "".join(f"<th>{html.escape(label)}</th>" for _, label in columns)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(key) if row.get(key) not in (None, '') else '—'))}</td>" for key, _ in columns) + "</tr>" for row in rows)
    return f"<table><thead><tr>{headings}</tr></thead><tbody>{body}</tbody></table>" if rows else "<p>Нет доступных записей в выбранном срезе.</p>"


def report_html(report):
    title = html.escape(report["report_id"])
    limitations = "".join(f"<li>{html.escape(s)}</li>" for s in report["limitations"])
    links = "".join(f'<li>{html.escape(s["source_id"])} <a href="{html.escape(safe_url(s["source_url"]), quote=True)}">Источник</a> · {html.escape(s.get("retrieved_at", "") or s.get("retrieval_date", "") or "точное время получения не записано")} · SHA-256 {html.escape(s.get("evidence_sha256", ""))}</li>' for s in report["sources"])
    return f'''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>body{{font:15px Arial,sans-serif;color:#45464F;margin:32px;line-height:1.5}}h1{{color:#038726}}table{{border-collapse:collapse;width:100%;font-size:12px;margin:16px 0}}td,th{{border-bottom:1px solid #d1d1d1;padding:8px;text-align:left;vertical-align:top}}th{{background:#edf5ee}}li{{overflow-wrap:anywhere}}@media print{{body{{margin:10mm}}}}</style>
<h1>KASE BondScope · отчёт аналитика</h1><p>Конкурсный прототип предлагаемого модуля. Не инвестиционная рекомендация.</p>
<p>{title}<br>Снимок: {html.escape(report['snapshot_id'])}<br>Контекст событий на {html.escape(report['as_of'])}; дата означает конец дня +05:00. Это ретроспективный контекст, не утверждение об осведомлённости на момент сделки.</p>
<h2>Наблюдения</h2>{_table(report['observations'], [('ticker','Тикер'),('instrument_id','ISIN'),('trade_date','Дата'),('trading_mode','Режим'),('turnover_kzt','Оборот, KZT'),('trades_count','Сделки'),('average_observed_trade_size_kzt','Средний наблюдаемый размер сделки, KZT'),('price_view_status','База наблюдаемой цены'),('finality','Окончательность')])}<p>Средний размер = опубликованный округлённый оборот / число сделок; описательный расчёт, не историческая норма и не прогноз исполнения.</p>
<h2>Правила и основания</h2>{_table(report['evaluations'], [('ticker','Тикер'),('rule','Правило'),('value','Значение'),('units','Единицы'),('status','Статус'),('baseline','База'),('n','n'),('threshold','Порог-гипотеза'),('explanation','Объяснение')])}
<h2>Официальная рыночная оценка</h2>{_table(report['valuations'], [('ticker','Тикер'),('valuation_date','Дата оценки'),('market_price','Рыночная цена'),('unit','Единицы'),('valuation_type','Назначение')])}
<h2>Опубликованные события</h2>{_table(report['events'], [('ticker','Выпуск'),('title','Событие'),('event_date','Дата события'),('event_published_at','Публикация'),('evidence_status','Доказательство')])}
<h2>Ограничения</h2><ul>{limitations}</ul><h2>Источники</h2><ul>{links}</ul></html>'''
