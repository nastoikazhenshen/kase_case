"""KASE BondScope competition-prototype interface (offline snapshot only).

Exports are generated from the report module's immutable typed-record snapshot.
"""

from __future__ import annotations

import html
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

RULE_LABELS = {"price_gap_pct": "Отклонение последней цены", "range_pct": "Дневной ценовой диапазон", "turnover_ratio": "Оборот к исторической медиане", "trades_ratio": "Сделки к исторической медиане", "trade_size_to_turnover": "Планируемая сумма к историческому обороту", "planned_amount_to_observed_daily_turnover": "Планируемая сумма к обороту дня"}
STATUS_LABELS = {"TRIGGERED": "Требует проверки", "EVALUATED": "Рассчитано", "INPUT_REQUIRED": "Нужна сумма сделки", "INSUFFICIENT_DATA": "Недостаточно истории", "BLOCKED_PRICE_VIEW": "Вид цены не подтверждён", "BLOCKED_SCOPE": "Вне подтверждённого охвата", "BLOCKED_MODE": "Режим не подтверждён", "BLOCKED_PRICE_BASIS": "База цены не подтверждена", "BLOCKED_OBSERVATION_KIND": "Неверный вид наблюдения", "INCOMPLETE_SESSION": "Неполная сессия", "BLOCKED_FINALITY": "Нет подтверждённой окончательности", "MISSING_FIELD": "Нет поля", "ZERO_BASELINE": "Нулевой/округлённый знаменатель", "INVALID_RANGE": "Несогласованный диапазон", "NOT_CONFIGURED": "Порог не задан"}


def _safe_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else None


def _table_rows(rows: list[dict], fields: list[tuple[str, str]]) -> list[dict]:
    return [{label: row.get(key) for key, label in fields} for row in rows]


def _display(value: object) -> str:
    """Keep UI table columns homogeneous without altering report data or exports."""
    return "—" if value is None or value == "" else str(value)


def _load() -> dict | None:
    try:
        from mvp.src.repository import load_snapshot
        return load_snapshot()
    except FileNotFoundError:
        st.info("Локальный пакет доказательств не найден. Подготовьте его по инструкции MVP и запустите приложение снова.")
    except ValueError as exc:
        st.error(f"Локальный пакет не прошёл проверку целостности: {html.escape(str(exc))}")
    except ImportError:
        st.info("Слой локального снимка ещё не подключён. Интерфейс ожидает `mvp.src.repository.load_snapshot`.")
    return None


def _date(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _event_as_of(selected_dates: list[str], all_dates: list[str]) -> date:
    """Default to the selected trade date, rather than a later retrieval instant."""
    candidates = selected_dates or all_dates[-1:]
    return _date(max(candidates)) if candidates else date.today()


def main() -> None:
    st.set_page_config(page_title="KASE BondScope", page_icon="◈", layout="wide")
    css = Path(__file__).with_name("theme.css")
    if css.exists():
        st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    st.title("KASE BondScope")
    st.caption("Конкурсный прототип предлагаемого модуля для анализа корпоративных облигаций. Не является инвестиционной рекомендацией.")
    snapshot = _load()
    if snapshot is None:
        return
    observations = snapshot.get("observations", [])
    release = snapshot.get("release", {})
    st.caption(f"Снимок: {html.escape(str(release.get('snapshot_id', 'не указан')))} · статус: {html.escape(str(release.get('status', 'не указан')))}")
    dates = sorted({str(row.get("trade_date")) for row in observations if _date(row.get("trade_date"))})
    tickers = sorted({str(row.get("ticker")) for row in observations if row.get("ticker")})
    with st.sidebar:
        st.subheader("Фильтры очереди")
        selected_dates = st.multiselect("Дата наблюдения", dates, default=dates[-1:] if dates else [])
        selected_tickers = st.multiselect("Тикер", tickers)
        event_as_of = st.date_input("События по состоянию на", value=_event_as_of(selected_dates, dates), help="По умолчанию — выбранная торговая дата; поздняя дата показывает отдельный ретроспективный контекст.")
        use_planned = st.checkbox("Сопоставить с планируемой суммой")
        planned = st.number_input("Планируемая сумма, KZT", min_value=0.0, step=1000.0, disabled=not use_planned, help="Ввод пользователя, не рыночное наблюдение.") if use_planned else None
    selected = [row for row in observations if (not selected_dates or row.get("trade_date") in selected_dates) and (not selected_tickers or row.get("ticker") in selected_tickers)]
    try:
        from mvp.src.reports import build_report, report_csv, report_html
        from mvp.src.repository import canonical_json
        report = build_report(snapshot, selected, event_as_of.isoformat(), planned_amount_kzt=planned)
    except (ImportError, ValueError) as exc:
        st.error(f"Отчёт недоступен: {html.escape(str(exc))}")
        return
    evaluations = report.get("evaluations", [])
    triggered = sum(item.get("status") == "TRIGGERED" for item in evaluations)
    evaluated = sum(item.get("status") == "EVALUATED" for item in evaluations)
    input_required = sum(item.get("status") == "INPUT_REQUIRED" for item in evaluations)
    blocked = len(evaluations) - triggered - evaluated - input_required
    a, b, c, d = st.columns(4)
    a.metric("Требуют проверки", triggered)
    b.metric("Рассчитано", evaluated)
    c.metric("Нужен ввод суммы", input_required)
    d.metric("Заблокировано данными", blocked)
    tabs = st.tabs(["Очередь", "Инструмент", "Активность", "События", "Качество и источники", "Концепция"])
    with tabs[0]:
        queue = [{"Тикер": item.get("ticker"), "Дата": item.get("trade_date"), "Правило": RULE_LABELS.get(item.get("rule"), item.get("rule")), "Значение": _display(item.get("value")), "Статус": STATUS_LABELS.get(item.get("status"), item.get("status"))} for item in evaluations]
        st.dataframe(queue, width="stretch", hide_index=True)
        st.caption("«Требует проверки» означает правило-исключение для аналитика, а не вывод о нарушении или прогноз.")
    with tabs[1]:
        if not selected:
            st.warning("Нет наблюдений для выбранного фильтра.")
        else:
            ids = [row["row_id"] for row in selected]
            by_id = {row["row_id"]: row for row in selected}
            row_id = st.selectbox("Наблюдение", ids, format_func=lambda value: f"{by_id[value]['ticker']} · {by_id[value]['trade_date']} · {by_id[value]['instrument_id']}")
            item = by_id[row_id]
            st.subheader(f"{item.get('ticker', '—')} · {item.get('instrument_id', 'ISIN не указан')}")
            st.caption(f"Режим: {item.get('trading_mode') or 'не подтверждён'} · База цены: {item.get('price_basis') or 'не подтверждена'} · Вид цены: {item.get('price_view_status') or 'не подтверждён'}")
            st.dataframe(_table_rows([item], [("last_price", "Последняя цена"), ("weighted_avg_price", "Средневзвешенная"), ("high_price", "Максимум"), ("low_price", "Минимум"), ("turnover_kzt", "Оборот, KZT"), ("trades_count", "Сделок")]), hide_index=True, width="stretch")
            st.info("Ценовые правила доступны только при подтверждённом виде цены. Оборот и число сделок оцениваются отдельно при подтверждённом режиме торгов.")
            item_rules = [result for result in evaluations if result.get("row_id") == row_id]
            st.dataframe([{"Правило": RULE_LABELS.get(result["rule"], result["rule"]), "Статус": STATUS_LABELS.get(result["status"], result["status"]), "Значение": _display(result.get("value")), "База": _display(result.get("baseline")), "n": _display(result.get("n")), "Порог": _display(result.get("threshold")), "Объяснение": result.get("explanation"), "Ограничение": result.get("limitations")} for result in item_rules], hide_index=True, width="stretch")
            values = [value for value in report.get("valuations", []) if value.get("instrument_id") == item.get("instrument_id") and value.get("valuation_date") == item.get("trade_date")]
            st.subheader("Официальная рыночная оценка")
            st.dataframe(_table_rows(values, [("valuation_date", "Дата"), ("valuation_type", "Тип"), ("market_price", "Значение"), ("unit", "Единицы")]), hide_index=True, width="stretch")
    with tabs[2]:
        st.caption("Датированный снимок активности. Исторический график не строится без достаточной подтверждённой сопоставимой истории.")
        st.dataframe(_table_rows(selected, [("trade_date", "Дата"), ("ticker", "Тикер"), ("turnover_kzt", "Оборот, KZT"), ("trades_count", "Сделок"), ("finality", "Окончательность")]), hide_index=True, width="stretch")
        context = []
        for item in selected:
            if item.get("mode_status") != "VERIFIED" or item.get("turnover_status") == "ROUNDED_ZERO" or item.get("trades_count") in (None, "", 0, "0") or item.get("turnover_kzt") in (None, ""):
                continue
            try:
                from mvp.src.parsing import parse_number
                turnover, count = parse_number(item["turnover_kzt"]), parse_number(item["trades_count"])
                if turnover is not None and count is not None and count > 0:
                    context.append({"Тикер": item["ticker"], "Дата": item["trade_date"], "Средний размер сделки, KZT": float(turnover / count)})
            except (TypeError, ValueError, ZeroDivisionError):
                continue
        if context:
            st.dataframe(context, hide_index=True, width="stretch")
            st.caption("Контекстный расчёт «оборот / число сделок» по отображаемым данным; при округлённом отображении это не отдельное правило-исключение.")
    with tabs[3]:
        st.caption(f"Контекст событий на {event_as_of.isoformat()}; дата трактуется как конец дня +05:00. Поздняя дата — отдельный ретроспективный контекст, не знание в момент сделки.")
        st.dataframe(_table_rows(report.get("events", []), [("event_date", "Дата события"), ("event_published_at", "Опубликовано"), ("title", "Событие"), ("evidence_status", "Доказательство")]), hide_index=True, width="stretch")
        for event in report.get("events", []):
            availability = event.get("availability", {})
            st.caption(f"{event.get('title', 'Событие')}: {availability.get('limitation', 'Ограничение доступности не записано')}")
            link = _safe_url(event.get("source_url"))
            if link: st.link_button("Открыть источник события", link, key=f"event-{event.get('event_id')}")
        if not report.get("events"): st.info("В выбранном контексте нет загруженных доступных событий; это не означает отсутствия событий у эмитента.")
    with tabs[4]:
        st.subheader("Покрытие и источники")
        st.dataframe(snapshot.get("coverage", []), hide_index=True, width="stretch")
        for source in report.get("sources", []):
            url = _safe_url(source.get("source_url"))
            label = html.escape(str(source.get("source_id", "источник")))
            retrieved = source.get("retrieved_at") or source.get("retrieval_date") or "точное время получения не записано"
            st.write(f"{label} · получено: {retrieved} · статус: {source.get('status', '—')}")
            if url: st.link_button("Открыть источник", url, key=f"source-{source.get('source_id')}")
        st.caption("Локальные рыночные файлы не включены в публичный репозиторий до подтверждения прав на распространение.")
    with tabs[5]:
        st.subheader("Concept · будущая полная версия")
        st.write("A — монитор исключений, B — контекст ликвидности до сделки, C — события эмитента. Интеграция с IRIS не реализована в этом прототипе.")
    downloads = st.columns(3)
    report_key = report.get("report_id", "bondscope-report")
    downloads[0].download_button("CSV отчёта", report_csv(report), file_name=f"{report_key}.csv", mime="text/csv", key=f"csv-{report_key}")
    downloads[1].download_button("HTML отчёта", report_html(report), file_name=f"{report_key}.html", mime="text/html", key=f"html-{report_key}")
    downloads[2].download_button("JSON снимка отчёта", canonical_json(report).encode("utf-8"), file_name=f"{report_key}.json", mime="application/json", key=f"json-{report_key}")
    st.caption(f"Идентификатор неизменяемого отчёта: {report.get('report_id', 'не указан')}")


if __name__ == "__main__":
    main()
