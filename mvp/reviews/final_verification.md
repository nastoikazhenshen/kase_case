# Final verification — limited real-data demonstrator

Status: **PARTIAL — EXTERNAL DATA BLOCKER**. This is an implemented and tested
daily snapshot demonstrator, not completion of the historical-data requirement.

Tested implementation commit: `598f14e13b42b009741e1680e326e958c03b4175`.
Branch: `feature/data-mvp`; base: `bcd24725855b92a86eb23f720bcd921b7aa5d837`.
Repository: `git@github.com:nastoikazhenshen/kase_case.git`.
Subsequent release commit adds review/verification records and documentation only.
The final lead response records the actual pushed SHA and independently queried
remote ref; this document does not pre-claim a push.

## Data and calculation result

- Snapshot `BS3-40698bfc0c453479`; full SHA-256
  `40698bfc0c45347981e358e9fee4d80a88b8f90e8f3f27dd78182035bbddbc64`.
- Default report `BS3-REPORT-8aba4eee2d9d5ac81c10`.
- Five KZT coupon instruments, ten retained rows over 20–21 October. Four date-mode
  confirmations apply only to 21 October; none backfilled to 20 October or HCBNb19.
- Five newly recovered daily API revisions remain separate. Fifty field comparisons:
  45 exact, four within displayed rounding, one explained old-missing/new-zero
  revision. No canonical trading observation was silently replaced.
- Nine official market valuations (three instruments, 19–21 October), not risk-process
  estimated prices. One full notice; issuer events are not a complete feed.
- Price-view verified rows: zero. Eligible comparable previous history: zero;
  historical window target 20, minimum 10. `From` totals, all-null current rows and
  undated sparkline arrays were not converted to daily history.
- One formal same-day planned-amount/day-turnover rule is computable for four rows
  when the user supplies an amount. An independent descriptive average observed trade
  size is available for those four rows. **The target of two computable formal rules
  is not claimed achieved.** Default planned input is absent; default 30 evaluations
  are 26 data-blocked and four INPUT_REQUIRED, not 30 market non-events.
- All thresholds are hypotheses. Signed percentage units differ explicitly from
  spreadsheet fractional percentage storage. No investment/abuse/default conclusions.

## Actual checks

Lead runtime: Python **3.12.14**, Streamlit **1.66.1**, pinned full environment in
`requirements.lock.txt`. All commands below completed successfully:

| Check | Command / evidence | Result |
|---|---|---|
| Runtime/unit/real-source/AppTest | `python -m unittest discover -s mvp/tests -v` | **47 passed**, no skipped real-source tests with local pack |
| Immutable archived baseline | `python -m unittest discover -s mvp/data/raw/archive/verification/tests -v` | **18 passed**; includes 288 independent financial-cell comparisons |
| Lint | `python -m ruff check mvp/src mvp/tests mvp/scripts --select F` | Passed |
| Source reconciliation | `python mvp/scripts/reconcile_sources.py` | 50 checks; no unexplained differences |
| Real browser | `python mvp/scripts/browser_smoke.py` | Passed; 1440/1280/420px, populated/gated/event states, keyboard focus, typed CSV/JSON parity |
| Offline input/data flow | real E2E tests patch socket creation to fail; browser blocks all non-localhost requests | Passed; collection is a separate command |
| Workbook | `node mvp/scripts/build_workbook.mjs` with bundled `@oai/artifact-tool` | Four sheets; live input recomputes; blank restored; zero preserved; no formula errors; four rendered previews inspected |
| Source input integrity | `implementation/input_integrity.json` | 46/46 verification files, 31/31 Task1 files match inner manifests; named outer ZIPs absent, their hashes NOT claimed verified |
| Publication scope | `reviews/staged_audit.json`, staged diff/path review | No raw/processed/third-party binary or private paths staged; no targeted credential-pattern matches |

Browser details: `browser_checks.json`. Artifact hashes: `visual_artifacts.json`.
Screenshots and workbook remain local, under paths listed by those records.
The current linked KASE guide's palette page was visually inspected; fonts/logo
were not copied, product is labeled competition prototype, integration is Concept.

## Clean-clone delivery

An isolated local Git clone at the tested commit was created, a **new venv** installed
from the lock, and both advertised modes exercised. Without data, the app displayed
the missing-evidence setup state. With the exact separate pack, 149 files restored;
the second restore wrote zero files. Rebuild, export, reconciliation, 47 runtime
tests, 18 archive tests and populated AppTest passed. The report equals the
development report as a full JSON object. See `clean_clone_check.json` for exact
commands/exit codes and runtime. The first attempt was made before dependency
installation finished and failed importing Streamlit; rerun after installation
completed produced this successful proof.

Local pack: `mvp/local_pack/bondscope-evidence.zip`, 2,609,532 bytes,
SHA-256 `5e3902f2decb1aaf29f1f2a20ce8a09f7caadb304dc1e12704244db3d68c9bec`.
It is not shipped in public Git. A clone alone cannot reproduce market observations
without that local dependency. Workbook regeneration additionally needs the authoring
runtime; the already generated XLSX is included in the pack.

## Review and external limitations

The mandatory separately spawned reviewer is **gpt-5.6-terra / high**, independently
verified from runtime metadata; all other workers are explicit Terra/medium, lead
remains Astra. `agent_manifest.json`, `resolutions.md`, and `adversarial_final.md`
record routing, falsification findings, remediation and independent final disposition.
No model bills or token savings are invented.

Remaining external blockers: WAF denied two distinct interactive KASE routes before
selectors; no proved price view, incomplete date-mode coverage and insufficient/finality-
unproved history. The full notice does not print its timezone, so conservative
next-day +05 availability is used. Redistribution permission remains unresolved;
market files stay local. Financial scenario/tax/version corrections were handed to
Participant 3, whose files/branch were not changed. No main push, force-push, merge,
deployment, PR or competition submission is part of this delivery.
