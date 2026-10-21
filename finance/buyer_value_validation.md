# BondScope 3.0 — buyer value, premium data, commercialization test

**Owner:** participant 3 (Finance & Pitch) · **Status:** working hypothesis, not validated sales · 22 Oct 2026.

## What is actually sold
**One B2B subscription licensed per broker-dealer organization:** a reproducible pre-trade check of KASE corporate bonds combining unusual market activity, liquidity context for a proposed transaction and issuer disclosures. The tangible deliverable is an analyst-ready evidence pack with date, price definitions, sources, rule versions, flags and limitations. Not a trading recommendation, fair-value engine, price guarantee, insider/manipulation classifier or new exchange terminal.

## Premium data dependency
KASE already publishes daily trading results AND sells trade/order-history datasets. Commercial BondScope must process those historical observations into usable, explainable alerts and audit-ready reports rather than merely resell an existing archive. **Exact fields, granularity, Level 2/3 depth, cancellation events, use/distribution rights and pricing are still unverified**; collect data specifications and sample from KASE.

- Archive: https://kase.kz/ru/information/archived-trade-information
- Derived information terms: https://kase.kz/ru/information/non-display
- Public corporate bonds: https://kase.kz/ru/markets/corporate-bonds
- Existing IRIS: https://kase.kz/ru/information/iris-finance
- Existing Cbonds features: https://cbonds.ru/watchlist/

## Pricing gate: 600,000 KZT monthly is NOT verified willingness to pay
From the team's v4 financial scenario: 96 paid client-months over M1–M24, 4 clients M12 and 6 clients M24 (all scenario, not real), 26.348m KZT startup budget, monthly fixed OPEX 1.87m, variable plus displaced revenue 70k/customer-month, CAC 150k/new org, six new accounts total.

**Base cumulative cash M24 = -21.248m KZT: fails competition payback.** Required price with everything else fixed ≈ 821,333 KZT/month; at 600k the allowed fixed OPEX is only ≈ 984,667 KZT/month, requiring ≈ 885,333 KZT/month justified reduction. **Neither is validated or achieved.**

From the *illustrative* buyer workload of 60 reviews × 18 minutes saved × 12k KZT/hour, value of released time is just **216k KZT/month**, below proposed price by **384k KZT**. At that time saving and labor cost, 167 reviews monthly would be needed to equate to 600k. Released analyst time is not the same thing as cash saved; DO NOT invent prevented losses.

## What must be tested before full rollout
1. Qualify buyer and budget owner; select prospects from the 8-source-backed shortlist in `customer_segment.md`. Their ability/willingness to pay is **unknown**.
2. Run the same 20–30 ISIN pre-trade workflow in the customer's current KASE/IRIS/Excel tools and BondScope demonstrator (real public data only for competition).
3. Measure elapsed minutes, number of manual steps, coverage, material exceptions missed, explainability/source reproducibility.
4. **Pilot targets, not observed achievements:** median review-time reduction ≥30%, no missed material exceptions on the agreed control set, evidence trail for ≥95% of alerts.
5. Discuss willingness to pay at 300k/450k/600k with actual budget owners. Seek **two paid pilots** as a post-competition target; interest alone is not a sale.
6. Only approve rollout if licensing/data rights, 3-person ≤6-month MVP plan, ≤40m KZT launch budget and payback ≤24 months AFTER launch are supported.

## Ownership / handoffs
Member 1: business interviews, shortlist, competitive gap; Member 2: actual public-data MVP and controlled demo; Member 3: financial scenarios, pricing and board decision. Workbook v5 also includes sheets `11 Buyer Value`, `12 Data Moat`, `13 Buyer Pilot`, `14 Decision Gate`; add binary XLSX separately (GitHub text connector cannot upload binaries).

**Contest limit:** public data only in submitted working fragment. Licensed KASE data can be a production dependency, never invented inputs to contest calculations.
