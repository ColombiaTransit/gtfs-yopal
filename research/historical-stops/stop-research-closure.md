# Stop research closure — 2026-11-26

## Scope and sources

All eight enabled InfoBusetas Yopal routes (2, 3, 6, 7, 8, 9, 10, 13) and both Firebase shape keys were compared to the 109 conservative historical location candidates. Input: archived historical stop research in this directory and user-supplied yopal-rutas.json (26 November 2026). Source details and attribution are in README.md and deduplication-review.md. No raw Firebase coordinates or crowdsource telemetry are redistributed.

## Method and limits

Use an approximately local metric equirectangular projection (5.32 degrees north; 111319.49 m/degree longitude multiplied by cos(latitude), 110574 m/degree latitude). Remove invalid coordinate slots; straight connections across internal missing slots are approximate and flagged. Calculate minimum point-to-segment distance and corresponding chainage; retain representative candidate positions within 50 m. Recalculate distances using the conservative group's representative rather than all original source positions. A loop or repeated pass can yield multiple plausible positions; the nearest projection alone is used, so chainage is not verified stop order. All results are approximate. Gap endpoints include shape start and end, not asserted boarding stops. No new stop locations invented. A 500 m reporting threshold is an analytical choice, not a local regulatory requirement; a 1 km threshold highlights major gaps.

Scenarios: all nearby candidates (optimistic proximity only), own historical route candidates (independent of direction), own candidates compatible with known direction or unresolved, and own direction hypotheses from shape-distance and road-side review. Cross-route proximity is not boarding evidence. Counts are location-direction associations, not unique physical stops or observed passengers.

## Results

- Route 2 llegada: 44 nearby locations (30 own historical), largest optimistic gap 2.15 km, 19 invalid slots, 9 internal gap bridges.
- Route 2 salida: 41 nearby locations (31 own historical), largest optimistic gap 2.65 km, 7 invalid slots, 6 internal gap bridges.
- Route 3 llegada: 68 nearby locations (42 own historical), largest optimistic gap 1.35 km, 0 invalid slots, 0 internal gap bridges.
- Route 3 salida: 60 nearby locations (39 own historical), largest optimistic gap 2.21 km, 1 invalid slots, 1 internal gap bridges.
- Route 6 llegada: 20 nearby locations (0 own historical), largest optimistic gap 2.12 km, 1 invalid slots, 0 internal gap bridges.
- Route 6 salida: 20 nearby locations (0 own historical), largest optimistic gap 2.10 km, 107 invalid slots, 0 internal gap bridges.
- Route 7 llegada: 12 nearby locations (0 own historical), largest optimistic gap 3.89 km, 2 invalid slots, 2 internal gap bridges.
- Route 7 salida: 6 nearby locations (0 own historical), largest optimistic gap 3.94 km, 0 invalid slots, 0 internal gap bridges.
- Route 8 llegada: 8 nearby locations (0 own historical), largest optimistic gap 3.69 km, 1 invalid slots, 0 internal gap bridges.
- Route 8 salida: 17 nearby locations (0 own historical), largest optimistic gap 3.51 km, 1 invalid slots, 0 internal gap bridges.
- Route 9 llegada: 25 nearby locations (0 own historical), largest optimistic gap 1.95 km, 1 invalid slots, 0 internal gap bridges.
- Route 9 salida: 21 nearby locations (0 own historical), largest optimistic gap 1.94 km, 5 invalid slots, 0 internal gap bridges.
- Route 10 llegada: 6 nearby locations (0 own historical), largest optimistic gap 4.87 km, 0 invalid slots, 0 internal gap bridges.
- Route 10 salida: 9 nearby locations (0 own historical), largest optimistic gap 4.96 km, 0 invalid slots, 0 internal gap bridges.
- Route 13 llegada: 55 nearby locations (29 own historical), largest optimistic gap 2.52 km, 122 invalid slots, 0 internal gap bridges.
- Route 13 salida: 54 nearby locations (29 own historical), largest optimistic gap 2.44 km, 3 invalid slots, 3 internal gap bridges.

All 16 shapes have an optimistic gap greater than 1 km. There are 30 such intervals, including start/end gaps, across the optimistic scenarios. There are 466 nearby direction associations; only 29 shape-distance direction hypotheses and 24 additional side hypotheses for their own historical routes. None are verified operational stops. The other five routes have no own historical stop maps in the available sources. The three historical maps show real stop symbols but do not establish contemporary boarding policy or complete implementation. OSM has only four bus-stop nodes, of which one unnamed candidate warrants attention, but does not establish urban route stop coverage.

## Decision for the generator

Fixed-stop-only routing is not supported by available evidence for any of the eight routes. Do not publish the 109 historical candidates or the 104 expanded alternative as a complete current stop inventory. Do not fill gaps with regularly spaced fictional stops or reassign stops based on proximity. Retain the original historical data and the twenty outliers.

Recommended **provisional modeling option**, subject to explicit acceptance of the boarding-policy assumption: continuous pickup/drop-off on route shapes, with technical origin/end anchors derived from validated endpoints and separate handling of loop continuity. GTFS continuous_pickup and continuous_drop_off can represent continuous boarding/alighting where applicable; use a shape and only appropriate endpoint anchors, not pretend verified intermediate stops. This does not establish that Yopal actually permits boarding anywhere along the route. No operational confirmation of continuous boarding was found in the reviewed sources; if not accepted, keep the feed in research/testing status until policy is resolved. Do not mix fixed stops with continuous boarding as a workaround without evidence. A MobilityData validator checks syntax/consistency, not actual stop operation.

The stop-research phase can be closed with this explicit data-quality limitation. Further work should focus on validated shape continuity (especially the null slots), schedules, generator and release gating; current boarding policy and source reuse rights remain open verification items. Future authoritative stop data can replace the provisional model.

## Outputs

- yopal_stop_coverage_by_direction.csv: 16 shape summaries.
- yopal_stop_coverage_associations.csv: 466 proximity associations; no verified service.
- yopal_stop_coverage_gaps.csv: 125 intervals greater than 500 m across three scenarios (overlap possible).
- yopal_shape_null_bridges.csv: 21 internal missing-slot straight connections.
- yopal_route_boarding_model_review.csv: 8 provisional modeling decisions.
