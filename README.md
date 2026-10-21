# KASE BondScope 3.0
**Fixed Income Intelligence & Exception Monitor** · KASE Championship, Stage 1 (Halyk case)

One B2B analytical add-on for KASE's information ecosystem, initially aimed at **KASE broker-dealers active in Kazakhstani corporate bonds**. The workflow: **KASE data → explainable exceptions → price/liquidity context → issuer events → auditable report**.

**Not:** an AI investment adviser, buy/sell recommendation, default/manipulation detector, new official KASE fair-value methodology, or replacement trading terminal.

## Competition contract
- One product; one primary customer segment.
- Competition demonstrator uses **publicly available data only**, with URLs, dates, units and reproducible calculations.
- Pilot: **3-person team**, development + launch **≤ 40,000,000 KZT**, production MVP launch **≤ 6 months**, investment payback **≤ 24 months AFTER launch**.
- Deliverables: ≤10 content slides plus cover (first content slide = executive recommendation); optional ≤5 appendix slides; Excel/Google Sheets with KASE source data, formulas, source URLs, and unit economics.
- Deadline stated in case: **23 Oct 2026, 12:00 Astana time**, to `academy@kase.kz`. Submission filename/email subject: `TeamName_Halyk`. Check chosen registration language.
- Never invent market observations, customer interviews, data entitlements, financial sources or demand validation.

## Start here
1. Read [project context](docs/project_context.md) and [working agreement](docs/WORKFLOW.md).
2. Read your own role contract under [docs/contracts](docs/contracts/).
3. Work only in your own branch and area; communicate cross-team results through [HANDOFF.md](HANDOFF.md) and PRs.
4. Use [DECISIONS.md](DECISIONS.md) for agreed decisions and [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) for blockers.

## Parallel responsibility
| Member | Area | Branch | Deliverables |
|---|---|---|---|
| 1 · Product & Market | `research/` | `feature/market-research` | KASE data/product map, ICP, alternatives, SAM/SOM, GTM, product slides |
| 2 · Data & MVP | `mvp/` | `feature/data-mvp` | Verified data, reproducible formulas, running demonstrator, charts, full-version mockup |
| 3 · Finance & Pitch | `finance/`, `presentation/` | `feature/financial-model` | Unit economics, 24-month payback model, scenarios, KPI/risks, final deck |

**GitHub repo is public.** Do not commit passwords, private datasets, confidential interviews, paid KASE data, client names, secrets or access tokens.

> The three roles are collaborative: nobody may independently change the one-product scope or present hypotheses as verified facts.