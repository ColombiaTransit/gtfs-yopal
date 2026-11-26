# Research status — 2026-11-26

## Scope and observations

Urban bus service in Yopal, Casanare, Colombia. Research first; no scraper or generator at this stage.

The ColMind snapshot lists route numbers 1–14, of which 2, 3, 6, 7, 8, 9, 10 and 13 are enabled. Routes 1, 4, 5, 11, 12 and 14 are disabled according to that source. Earlier research reported a February 2026 municipal statement of 13 established and 9 operational routes; the missing ninth route and definition of the total remain unresolved. Do not assume the independent catalog is exhaustive or current.

Operating windows and headways are transcribed in service_windows.csv (24 day-type records; 21 with service and three without). Local time is America/Bogota. The website groups Sundays and public holidays. It does not establish whether headways are per direction, per full loop, or for the corridor as a whole, or whether the end time is inclusive. No peak/off-peak split is shown. Route 2 detail confirms its route-level values and says departure estimates may vary with traffic.

## Route selection policy (user decision, 2026-11-26)

Applicable municipal operating acts govern route inclusion and authorized headways. Apply acts chronologically, retaining the latest applicable provision unless superseded, withdrawn or expired. A ColMind enabled=false flag alone is never grounds to exclude a legally authorized route; enabled=true alone does not prove authorization. Where a valid act establishes operation, include the route even if ColMind disables it, subject to obtaining enough data to generate a valid feed. Use ColMind only to fill missing timetable/geometry information provisionally. Keep source status separate from legal status. A planning proposal is not an operating authorization. Verify explicit suspensions, withdrawals and expiry; document contradictory operational evidence separately.

All 14 route IDs remain in scope. Route-level authorization evidence is still incomplete, so the six ColMind-disabled routes are not yet classified as legally active or inactive. See routes.csv for separate source and legal status fields.

## Operators and fares (earlier research, pending primary verification)

TUYO — Transporte Urbano de Yopal — reportedly coordinates Coocatrans Ltda., Cootrallanero Ltda., Llano Líneas and Flota Sugamuxi S.A. under Resolución 130/2010. Historical assignments are preserved in routes.csv, not claimed as current or exclusive.

Proposed modelling: one TUYO agency if joint operation is confirmed, route-level attributions for verified individual companies. Timezone America/Bogota; language es. Confirm agency URL and actual operating arrangement first.

Reported uniform fare: COP 2,200 (2024), COP 2,400 (2025), COP 2,700 (2026). Confirm original tariff decrees and applicability before generating fare data.

## Geometry and stops

The route 2 snapshot shows Leaflet/OpenStreetMap and a legend with Recorrido de Subida, Recorrido de Bajada and Inicio. The route description returns to La Bendición, so the operating pattern (loop versus separately scheduled directions) needs verification. The legend alone is not proof of independently dispatched trips. The original polyline data were not recovered from the MHT. Earlier approximate map-marker reconstruction (not official stops or suitable for production): north 5.341899/-72.407198 and 5.341985/-72.407198; south 5.290537/-72.420845.

Findeter maps reportedly show routes 2 and 3 on printed p. 40 and route 13 on p. 41, with stop symbols. Verify map date, planned vs operational stops, and geometry before use. Decreto 267/2018 reportedly references 14 route maps. The 2024 route 8 survey reportedly describes a round trip starting/ending in Villa Lucía with observed travel times roughly 60–75 minutes; original tables still need review.

All eight ColMind-enabled routes have descriptive itineraries in the local ColMind index snapshot. The later user-supplied Firebase export contains both original geometry branches for all eight enabled routes. Geometry quality and verified stop coordinates remain open. Do not create fictitious stops. Consider continuous pickup/dropoff only if actual boarding policy supports it. Use GraphHopper for geometry/travel time only where needed after checking original evidence.

## Frequency research update (2026-11-26)

See [frequency-research.md](frequency-research.md): 24/24 day-type records match Firebase, but 0/8 ColMind-enabled routes have independently verified numerical legal headways. User reports estimateTime=false. The independent source is provisional. Both Findeter archive inventories and selected annexes have been reviewed; the PIMUR operational report remains missing. Further administrative contract-document review is parked pending a direct technical lead.

## Work list

- [x] Obtain local file inventories for both Findeter annex ZIPs (each approximately 400 MB according to user).
- [x] Compare file lists and, if needed, SHA-256 hashes; avoid duplicate downloads and raw archive commits.
- [ ] Locate Anexo 15 / PIMUR and nested archives. Prioritize GIS layers, route maps, stops, frequencies, dispatch windows, travel times and operator assignments.
- [ ] Recover Decreto 090/2019 and Decreto 267/2018 with annexes; check later amendments and PIMUR update. Reconcile every route against applicable operating acts, prioritizing IDs 1, 4, 5, 11, 12, 14; never filter solely on ColMind enabled.
- [ ] Obtain original 2026 fare decree and verify effective date and scope.
- [ ] Recover exact references for historical operator assignments and municipal statement; identify ninth operational route and verify current assignments.
- [ ] Check official stop inventory and planned vs existing stop status.
- [ ] Review all route directions, loops, service windows and frequency semantics.
- [ ] Resolve licensing/reuse rights for each source.
- [ ] Consider a read-only Firebase collector with a strict transit-field allowlist and no telemetry retention; resolve reuse rights before publication. Prefer authoritative source files when available.
- [ ] Later: generate GTFS with Colombia public holidays (Python holidays), appropriate day-type exceptions, MobilityData validation and stable release filename/tag. No publication until prerequisites are met.

## Local archive triage (Windows CMD)

```cmd
tar -tf "AnexosPT_Yopal.zip" > inhoud_zip1.txt
tar -tf "Anexos PT Yopal.zip" > inhoud_zip2.txt
```

Search for PIMUR, rutas, paraderos, transporte público, frecuencias, despachos, recorridos and cartografía; look for SHP/DBF/SHX/PRJ, GDB, KML/KMZ, spreadsheets, PDFs, DWG/DXF and nested ZIP/RAR files. Upload file inventories first; extract relevant files only.

## Parked source

TransOriente / LogiRuta is parked: the tested Logirastreo city service listed Armenia, La Tebaida and Barranquilla, but both distinct route queries returned empty FeatureCollections. It is not a Yopal data source.

## Follow-up — route status and geometry

See [route-status-reconciliation.md](route-status-reconciliation.md) for the newly located restricted Decreto 090/2019 record, historical acts, 14-route status matrix and frequency evidence. Prioritize routes 11 and 12; the ninth current route remains unidentified. Stop and operator research stages completed with explicit limitations; see [historical-stops/stop-research-closure.md](historical-stops/stop-research-closure.md) and [operator-research.md](operator-research.md). Shape screening completed for all 26 available shapes; see [shape-validation/README.md](shape-validation/README.md). Preserve route 3 correction and terminal verification in [correction-register.csv](correction-register.csv). No route activation changes or current legal headways established.

## Authoritative baseline recovered — 2026-11-26

The full municipal Decreto 090/2019 is now recovered; see [review](decreto_090_2019_review.md), [official route assignments](decreto_090_2019_routes.csv), [42 official day-type schedules](decreto_090_2019_service_windows.csv) and [comparison](decreto_090_2019_comparison.csv). This supersedes earlier missing-document statements and provisional historical operator assignments as a 2019 legal baseline. All 14 adopted; current status and later acts still pending. Article 8 evaluation applies to 6,12,14 without explicit expiry. Article 9 refers to legal stopping sites; unrestricted continuous boarding is not supported by this document. Original ColMind observations retained separately. Official full-circuit descriptions require geometry reconciliation.

## Post-2019 amendment search

See [post-2019-amendments-review.md](post-2019-amendments-review.md). No later permanent route or headway modification found in targeted indexed search; municipal archive index was not readable. April 2026 reporting describes 14 authorized and 9 operating routes; route 14 has historical launch evidence circa February 2020. No evaluation acts found for 6,12,14. Retain all 14 legal-baseline candidates and official schedules unchanged; actual operation remains separate. New leads: enforcement procedure MI8-PR18 and municipal Movilidad Inteligente TUYO application.

## Consolidation of collected acts

See [legal-act-consolidation.md](legal-act-consolidation.md), [chronology](legal-act-chronology.csv) and [route baseline](legal-route-baseline.csv). All 42 official service windows remain unchanged. Decreto 090/2019 is the latest verified route-specific baseline in the collected material; no current service or absence of missing acts is asserted. Targeted follow-up before any municipal archive scrape. Decreto 152/2019 urban fare transcription recovered; 151/2019 remains unverified.

## First selected original acts review

See [selected-legal-acts-review.md](selected-legal-acts-review.md). 18 selected acts / 21 PDFs retrieved successfully; operative articles and unrelated case subjects screened. Six original urban fare acts verified, latest COP 2700 under 090/2019. 031/2026 modifies terminal planning only; 142/2026 does not repeal 030/031 and does not cover 2019. 343/2022 is taxi tariffs despite title. No permanent urban route change established. Retain 14 legal candidates and 42 windows, actual operation separately unresolved. Remaining evaluation/withdrawal evidence, other metadata candidates, and technical annex review pending.
