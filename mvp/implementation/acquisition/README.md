# Public KASE recovery — 2026-10-22

## What was actually recovered

The anonymous KASE server-rendered instrument pages exposed these read-only
routes in their public response state:

* `/api/instruments/trade-info/{ticker}/` — current row, a dated prior row and
  a cumulative `From …` aggregate;
* `/api/instruments/bonds/{ticker}/` — instrument master response;
* `/api/indicators/market-valuations/` — official valuation response;
* public notice page `information/news/show/1578268` — full CLSGb11 coupon
  notice, unlike the earlier search-only excerpt.

The saved local byte responses are in the ignored
`mvp/data/raw/acquisition/2026-10-22/` folder. They are not committed because
the KASE footer states copying requires written permission. Their hashes and
non-sensitive provenance are in `evidence_manifest.json`.

## Data contract and limits

`trade-info` response fields are `period`, `date0`, `high`, `low`,
`average_price`, `dirty_high`, `dirty_low`, `dirty_average_price`, `bid`,
`dirty_bid`, `offer`, `dirty_offer`, `price`, `dirty_price`, `bid_income`,
`offer_income`, `last_income`, `high_income`, `low_income`,
`average_income`, `deals_count`, `volume`, `volume_kzt`, `volume_usd`.

The direct public response includes clean, dirty and yield values concurrently.
It is not evidence that a human selected the clean-price tab, so all price
rules remain `BLOCKED_PRICE_VIEW`. The `From …` rows are cumulative summaries,
not daily observations, and must not be used as history. The response exposes
only one usable prior observation per ticker in this recovery; therefore
history remains `INSUFFICIENT_DATA` for the 10/20 observation rule.

The KASE public valuation response returned BIGDb5, HCBNb19 and MFKMb10 for
2026-10-19 through 2026-10-21. It did not contain CLSGb11 or CLSGb15 in that
response. Treat this as response coverage, not a claim that those valuations
do not exist.

## Browser and event evidence

The first required supported-browser attempt failed before a browser surface
opened: the computer-use runtime attempted to enumerate a locked `D:` BitLocker
volume. A separate permitted headless Chrome attempt reached KASE, but rendered
its WAF block page (Attack ID `20000051`) before the price controls appeared.
Its screenshot/DOM are retained locally as blocker evidence; no active-tab click
was possible. Neither host/access outcome justifies unblocking price rules.

The optional capture helper uses Playwright only with explicit local runtime
paths: set `PLAYWRIGHT_NODE_MODULES` to the directory containing the
`playwright` package and, when needed, `PLAYWRIGHT_EXECUTABLE_PATH` to a local
Chrome/Chromium executable. It records an anonymous public page, a screenshot,
DOM and only public API URLs/statuses. Do not pass cookies, credentials or a
browser profile.

The full public notice confirms CLSGb11 / ISIN `KZ2P00016504`, payment date
2026-10-19, publication time `2026-10-21 12:20`, and payment amount
KZT 287,500,000. The page does not print its timezone; `Asia/Almaty` remains a
documented assumption for point-in-time comparisons.
