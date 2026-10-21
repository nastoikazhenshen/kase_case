# Project context — KASE BondScope 3.0

**One product:** paid B2B fixed-income exception-monitoring module in KASE information ecosystem.

**Primary segment:** KASE broker-dealer members active in Kazakhstan corporate bonds. Potential later: bank treasury and asset managers, not counted in base SAM automatically.

**Workflow:** verified KASE data → explainable anomaly/exception detection → instrument price and liquidity context → linked issuer events → reproducible analyst report.

## Module scope
A. **Market Activity & Anomaly Monitor** — turnover, trade-count, last-vs-weighted price, price range, revival after sparse trading; intraday patterns only if matching data genuinely available.
B. **Price & Liquidity Context** — last executed price, KASE official market price and separately designated estimate/settlement price, relative trade size vs historical turnover. Never guarantee actual execution.
C. **Issuer Event Intelligence** — public defaults, credit rating changes, financial statements and bond-terms disclosures with citation and publication date, without inferring causation.

## Not in MVP
No investment buy/sell recommendations, chatbot, default probability promises, manipulation/insider identification, automated fair value valuation, or mandatory paid-data access in the competition demonstrator.

## Data & fairness
- Public data only for competition MVP; commercial datasets may be described for post-competition production only, with permissions and exact field coverage *unconfirmed* until checked.
- Existing KASE services include trading results, IRIS Finance, information APIs and trade archives: differentiation MUST be established against these.
- Each metric must include instrument identifiers, date range, units, formula, source URL and caveats.
- Empty history / missing observations stay missing: don't fill artificially.
- No trading anomaly proves manipulation or predicts a future price move.

## Competition requirements
6 tasks: map data/gap; client pain and reachable market size; product/format/data/frequency and differentiation; working public-data MVP plus full mockup; pricing/unit economics; board recommendation, first customers, 3–5 KPIs, risks.
40m KZT maximum pilot cost, 3-person team, ≤6m launch, payback within 24 months AFTER launch.
10 content slides + cover, first content slide executive recommendation, optional ≤5 appendix; source-referenced spreadsheet with formulas.
Deadline in supplied case: 23 Oct 2026, 12:00 Astana, academy@kase.kz; use TeamName_Halyk naming.

## Shared field names — verify actual source meaning
`instrument_id`, `trade_date`, `turnover_kzt`, `trades_count`, `last_price`, `weighted_avg_price`, `market_price`, `estimated_price`, `issuer_event`.
Never conflate share count vs turnover; trading vs calendar dates; price types.

For full role-specific task contracts, see `docs/contracts/`.