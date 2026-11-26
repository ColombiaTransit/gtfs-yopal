# Yopal urban bus GTFS research

Research for a future static GTFS feed covering urban buses in Yopal, Casanare, Colombia.

**Status (2026-11-26): research only.** No scraper, generator or published feed yet.

- [Research findings and open questions](research/status.md)
- [Source register](research/sources.md)
- [Route inventory](research/routes.csv)
- [Reported operating hours and headways](research/service_windows.csv)
- [Frequency evidence and Firebase cross-check](research/frequency-research.md)
- [Original PIMUR annex review](research/pimur-annex-review.md)
- [PIMUR update procurement review](research/pimur-update-procurement.md)

The independent Busetas Yopal website snapshot (last update displayed: 2026-02-27) lists eight enabled and six disabled routes. A municipal statement reported nine operational routes in February 2026; the discrepancy is unresolved. TUYO is the reported joint operating arrangement of four transport companies. The reported 2026 fare is COP 2,700, pending primary decree verification.

The Findeter archives have been reviewed; the operational report and numerical official headways remain missing. The user-supplied Firebase route export now confirms all 24 reported day-type records and contains both geometry branches for all eight enabled routes. ColMind remains a provisional independent source, not official validation. Priority: verify frequency semantics, applicable operating acts, geometry, stops and reuse terms.

All research data are provisional. Do not publish a GTFS feed until source verification, reuse permissions, route geometry, service semantics and stop policy have been resolved. See the source register for evidence levels.
