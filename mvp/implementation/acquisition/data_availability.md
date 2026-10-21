# Recovered-data availability matrix — 2026-10-22

This is a bounded public-source recovery record. It does not assert that an
unreturned KASE field or page does not exist.

| Instrument | ISIN | Dated trade row recovered | Usable daily-history count | Mode proved for this observation | Active clean-price selection proved | Official valuation in current response | Result |
|---|---|---|---:|---|---|---|---|
| BIGDb5 | KZ2D00012861 | 2026-10-21 | 1 | no | no | 2026-10-19, 20, 21 | daily display only; no rolling rule |
| CLSGb11 | KZ2P00016504 | 2026-10-21 | 1 | no | no | absent | daily display only; event recovered |
| CLSGb15 | KZ2P00016744 | 2026-10-21 | 1 | no | no | absent | daily display only |
| MFKMb10 | KZ2C00018034 | 2026-10-21 | 1 | no | no | 2026-10-19, 20, 21 | daily display only; no rolling rule |
| HCBNb19 | KZ2C00014124 | 2026-10-21 (zero/empty trade fields) | 1 | no | no | 2026-10-19, 20, 21 | sparse display; no rolling rule |

The public `trade-info` response adds a 2026-10-22 current-session row with
null trade fields and a `From …` cumulative summary. The null current row is
not an end-of-day observation; the aggregate is not a daily observation and is
excluded. One prior dated row is below both the minimum `n=10` and target
`N=20` comparable-observation requirements.

The response does not supply a trading-board/mode field. No mode is inferred
from the prior archive or from a ticker's current page. The response supplies
clean (`price`, `average_price`, `high`, `low`) and dirty (`dirty_*`) fields,
but this alone does not identify a user-selected active price tab. Existing
observations therefore retain `BLOCKED_PRICE_VIEW`.

## Times and valuation dates

KASE HTTP `Date` headers recorded in the response state are UTC/GMT, while
instrument `date0` values have no offset. They are treated as source local
display times, not point-in-time instants. The full CLSGb11 notice prints
`2026-10-21 12:20` with no timezone. The event adapter may use its documented
`Asia/Almaty` assumption only as an assumption and must keep it visible.

The market-valuations response is a mapping keyed by valuation date. Its
returned values for BIGDb5/HCBNb19/MFKMb10 have valuation dates 2026-10-19,
2026-10-20 and 2026-10-21. Those dates belong to the valuation, not to the
retrieval time or a trade record.
