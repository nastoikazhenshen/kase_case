# Full-product concept — not implemented

This competition prototype implements an offline snapshot queue, instrument data, activity context, event availability, source traceability, and reproducible report downloads. It does not connect to IRIS, execute trades, maintain server-side watchlists, or claim real-time coverage.

The proposed future module has three clearly separate areas: **A. Исключения активности** (rule-based review queue), **B. Контекст ликвидности до сделки** (historical and current evidence, without an execution promise), and **C. События эмитента** (published disclosures with availability time and source). Watchlists, notes, and proposed trade amounts remain private user inputs and would require an approved authenticated storage design before production.

The screen style follows the KASE-reference palette documented in `mvp/docs/design_system.md`; it uses text identification rather than a copied logo. This is a concept for later integration, not an implemented KASE or IRIS service.

The actual rendered Concept screen is supplied locally as `mvp/mvp_screenshots/concept-1440.png`
inside the separate evidence package; it is excluded from public Git. Overview/card/activity/event
and narrow screenshots in the same directory show the running application, not a design mockup.
