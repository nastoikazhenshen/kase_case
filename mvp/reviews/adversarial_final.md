# Independent adversarial final review

**Verdict: PASS WITH DOCUMENTED EXTERNAL BLOCKERS — PARTIAL release only.**

Reviewed exact Git commit `598f14e13b42b009741e1680e326e958c03b4175`, snapshot
`BS3-40698bfc0c453479` (`40698bfc0c45347981e358e9fee4d80a88b8f90e8f3f27dd78182035bbddbc64`),
and report `BS3-REPORT-8aba4eee2d9d5ac81c10`. The routing metadata recorded by the
lead in `agent_manifest.json` identifies this assigned reviewer route as
`gpt-5.6-terra` / `high`; that record, rather than self-identification, is the
model evidence.

## Scope and evidence checked

* Engine, repository, report/export, acquisition, package/restore and Streamlit
  code; the canonical snapshot, release manifest, report and CSV; contracts and
  public-delivery documentation.
* Rendered application screenshots and regenerated workbook preview. The workbook
  visibly renders `21.10.2026`; its formula, blank-input and zero preservation
  checks pass.
* Local-only pack `mvp/local_pack/bondscope-evidence.zip`: SHA-256
  `5e3902f2decb1aaf29f1f2a20ce8a09f7caadb304dc1e12704244db3d68c9bec`,
  2,609,532 bytes, 149 payload files. I independently checked its manifest/member
  count, every payload hash and size, and allowed member prefixes.
* Independent exact-worktree run:
  `mvp/.venv/Scripts/python.exe -m unittest discover -s mvp/tests -t . -v`
  on Python 3.12.14: **47 passed**. A separate system-Python 3.13 invocation lacks
  Streamlit and therefore cannot import `test_app_states`; this is not a failure of
  the documented virtual-environment run.
* The recorded isolated clean-clone run in `clean_clone_check.json`: fresh pinned
  install, missing-pack UI state, restore of 149 files, idempotent second restore
  (0 writes), rebuild to the exact snapshot, exact report reproduction, 47 runtime
  tests, 18 archived tests, and populated-AppTest all pass.

## Rechecked remediation

| Risk | Result |
| --- | --- |
| Active price view or date-specific mode being inferred | Still blocked. All price views remain `UNVERIFIED_ACTIVE_TAB`; only four 2026-10-21 modes are verified, none are borrowed to 2026-10-20, and HCBNb19 remains unconfirmed. |
| Two rows becoming history / interim rows mixed with EOD | Still blocked by finality and comparable-history gates. No historical signal is emitted. |
| CLSGb11 publication leaking into 2026-10-21 | Still excluded on 21 October; unverified timezone policy makes it available on 22 October. Full-notice provenance and legacy provenance are distinct. |
| Valuation data misrepresented as risk estimated price | Nine 3-by-3 records remain `OFFICIAL_MARKET_VALUATION`, with `market_price` populated and `estimated_price` null. |
| Revision timestamps, stale aliases and source identity | Completion timestamps are retained; current paths/IDs are normalized while original aliases remain explicitly historical; corruption regressions pass. |
| UI/export disagreement | CSV typed EVALUATION/EVENT/VALUATION/SOURCE records match JSON context; browser checks cover both event as-of dates and illustrative input parity. |
| Public clone falsely assumed to carry evidence | The public clone displays a readable missing-pack state. The bounded path/hash/symlink-checked local pack is separately restored and was proven in an isolated clone. |

## Remaining P1 external blockers (not implementation defects)

1. KASE WAF prevents proof of the active clean-price tab and controls.
2. Matching historical, final daily data remains below the required minimum; two
   archived dates do not establish history.
3. The precise notice timezone and redistribution rights for the market evidence
   remain unconfirmed.

These prevent a full market-data acceptance and must remain surfaced as
`PARTIAL — EXTERNAL DATA BLOCKER`. They do not justify enabling price or historical
signals. I found no unresolved P0/P1 implementation failure in the reviewed commit.

## Untested boundaries

No fresh network collection or live KASE control interaction was attempted in this
final review; the saved WAF evidence and offline pack were reviewed instead. The
local ZIP is intentionally excluded from public Git, so delivery of that separate
file and any later rights authorization remain operational responsibilities outside
this commit.
