# Internal engine contract v1

Python 3.12, standard library for deterministic engine. Imports via `mvp.src`.
Owned by builder: `mvp/src/analytics.py`, `mvp/src/events.py`,
`mvp/src/parsing.py`, `mvp/tests/test_analytics.py`, `test_events.py`,
`test_parsing.py`. No other writes. Lead owns import, report, UI, integration.

Input: list of dict records; CSV loader keeps strings, missing as empty strings.
Engine accepts strings and numeric types using Decimal; JSON/output values must
be plain numbers/strings/null (never NaN/Infinity). Canonical fields:

`row_id, instrument_id, ticker, issuer, trade_date, trading_mode, price_basis,
price_view_status, mode_status, finality, source_id, source_url, retrieved_at,
evidence_path, evidence_sha256, last_price, weighted_avg_price, high_price,
low_price, turnover_kzt, trades_count, denomination_currency, instrument_type,
scope_status, observation_kind, turnover_precision_kzt, turnover_status`.

Accepted gates: scope_status=VERIFIED_KZT_COUPON; observation_kind=DAILY;
mode_status=VERIFIED and nonempty trading_mode. Price rules additionally require
price_view_status=VERIFIED and price_basis=CLEAN_PERCENT_OF_NOMINAL; activity
ratios do not depend on the selected price view. Separate status dimensions.
finality is CERTIFIED_EOD, HISTORICAL_PUBLISHED, AS_PUBLISHED_NOT_CERTIFIED_EOD
or INCOMPLETE_SESSION. Same-day metrics may use published snapshots with caveat;
history only CERTIFIED_EOD or HISTORICAL_PUBLISHED (retrospective, not backtest).
Current INCOMPLETE_SESSION cannot be scored against daily history.
turnover_status=MISSING, ROUNDED_ZERO, DISPLAY_ROUNDED, EXACT.
Rows with zero displayed turnover and positive trades are ROUNDED_ZERO,
not usable ratio denominators. Null turnover must remain null even with zero trades.

`evaluate(row, history, rules, planned_amount_kzt=None) -> list[dict]`.
Return all 6 rule evaluations (including blocked states): price_gap_pct,
range_pct, turnover_ratio, trades_ratio, trade_size_to_turnover,
planned_amount_to_observed_daily_turnover. History must match ISIN, mode,
price basis and finality, before scored date; deduplicate or reject revisions
explicitly, never count duplicate dates as history. n=20 target, minimum 10.
Signature rules dict:
`{"method_version":"BS3-1.0","hypothesis":true,"window":20,"minimum_n":10,
"thresholds":{"price_gap_pct":0.5,"range_pct":1.0,"turnover_ratio":3.0,
"trades_ratio":3.0,"trade_size_to_turnover":0.25,
"planned_amount_to_observed_daily_turnover":0.25}}`.
Price gap retains the signed percentage value and compares its absolute value;
range and ratios are nonnegative. Thresholds are
demonstrator hypotheses, not calibrated/predictive. None means NOT_CONFIGURED.
Optional planned amount absent means INPUT_REQUIRED for those two rules.

Every result: rule, row_id, instrument_id, ticker, trade_date, trading_mode,
as_of, value, baseline, n, window_start, window_end, threshold, units,
input_row_ids (list), source_ids (list), source_urls (list), method_version,
status (TRIGGERED / EVALUATED / blocked reason), explanation (Russian),
limitations (Russian). Same-day baseline/n/window null, not invented.
Preserve price gate separately from history insufficiency. Gate reason precedence
documented and tested. Unsafe/invalid field conditions return explicit status
or raise ValueError at ingestion, never silent repair.

`parse_number(value) -> Decimal|None`; `pct_to_excel` and `excel_to_pct`.
Reject unrecognized/ambiguous number formats; support decimal comma, NBSP,
Unicode minus. Helpers validate finite numbers and daily dates.

`event_availability(event, as_of) -> dict` with available bool, status,
available_from, limitation. Event fields: event_published_at (aware instant),
timezone_verified bool, publication_precision (SECOND|MINUTE|DATE),
instrument_id, issuer_id, mapping_scope (ISSUE|ISSUER), evidence_status.
Confirmed time zone compares aware instants including UTC equivalence.
Unverified time zone conservatively available beginning next local day
(fixed +05:00 policy clearly disclosed, not precise point-in-time correctness).
Date-only as_of means end-of-day +05:00 explicitly. Reject naive timestamps.
Provide `events_for_instrument(events, instrument_id, issuer_id, as_of)`;
issue scope never leaks to sibling bonds; issuer scope matches issuer_id.

Use unittest (no extra dependency). Tests synthetic clearly labeled and isolated.
