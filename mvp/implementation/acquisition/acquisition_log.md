# Acquisition log — 2026-10-22

| UTC / sequence | Route or action | Outcome | Decision |
|---|---|---|---|
| 1 | `cua_repl` supported-browser launch | Failed before a browser surface opened: runtime enumerated locked `D:` BitLocker volume. | Do not treat as KASE denial; attempt local permitted Playwright. |
| 2 | Public KASE SSR pages via anonymous HTTP | Success. BIGDb5 SSR state exposed `/api/instruments/trade-info/BIGDb5/`, `/api/instruments/bonds/BIGDb5/`, and other public routes. | Preserve only local hashed bytes; do not publish raw third-party content. |
| 3 | Direct `trade-info` route without trailing slash | 301 with `Location` adding `/`; body empty. | Adapter retains the observed trailing slash. |
| 4 | Five `trade-info/` and `bonds/` public routes | Success. Each trade response held a current empty 22.10 row, a 21.10 row, and a cumulative `From …` row. | Exclude `From …` rows from daily history; history remains insufficient. |
| 5 | `/api/indicators/market-valuations/` | Success. Official valuation response contains BIGDb5, HCBNb19 and MFKMb10 for 19–21 October; CLSGb11 and CLSGb15 absent from this response. | Store coverage as returned, not as evidence that absent valuations do not exist. |
| 6 | Public notice 1578268 | Success. Full KASE HTML says published 21.10.2026 12:20, CLSGb11 ISIN KZ2P00016504, payment date 19.10.2026, KZT 287,500,000. | Upgrade from search excerpt to full-page evidence; timezone remains an explicit source-timezone assumption. |
| 7 | Headless installed Chrome through Playwright on BIGDb5 | KASE WAF returned `Web Page Blocked`, Attack ID `20000051`, before any UI controls rendered. Screenshot and DOM saved locally. | Stop identical browser retries; no active clean-price tab is proved. |
| 8 | `https://kase.kz/robots.txt` | 404. KASE page footer says copying materials requires written permission. | No raw response is committed; source links, hashes and derivative records remain separate. |
| 9 | Public daily-results SSR page | Success. DOM has the `Облигации` tab but `aria-selected=false`; default payload route is `/api/trade-results/shares`. | The selector's corporate-bond request/date parameters were not observed, so no guessed route is called. |
| 10 | Headless Chrome on distinct daily-results page | Same KASE WAF block before UI: Attack ID `20000051`, Message ID `000806684902`. | Stop browser retries for the route; no selector/date/basis proof. |
| 11 | Public settlement-prices information page | Success. Page describes current/historical settlement-price product and links an API specification, but supplies no public instrument-value response. | Do not substitute settlement prices for trades or infer a data API route/access right. |

No credentials, cookies, authorization headers, browser profiles, or session tokens were retained.

The bond payload's `monthly_spark_line` contains an undated semicolon-separated
sequence. Without timestamps, aggregation and mode proof it is not eligible daily
history. No chart interpolation or fabricated dates were used. Separate revisions
were cross-checked against the retained official-table representation: 50 checks,
45 exact matches, four differences within display rounding and one explicit-zero
API revision where the old table was missing (HCBNb19). These checks do not prove
mode/view/finality equivalence. Details: `reconciliation_summary.json` and the
local `data/processed/revision_reconciliation.csv`.
